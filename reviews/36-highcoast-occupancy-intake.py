"""Read actual saved scene and local scatter buffers only; no engine/production writes."""
from pathlib import Path
import re,json,struct,hashlib
from collections import Counter
from functools import lru_cache
import numpy as np
from shapely.geometry import box,Polygon,Point,mapping
from shapely import union_all
R=Path(__file__).resolve().parents[1]
def text(p):return p.read_text(encoding='utf-8-sig')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(text(p))
XMIN=-3750;region=box(XMIN,-4400,-900,-2150)
intake=load(R/'reviews/36-highcoast-source-intake.json')
world=text(R/'scenes/world/World.tscn')
exec(text(R/'reviews/round-32b-asset-footprint-decoder.py'),globals())
def matrix(block):
    m=np.eye(4);hit=re.search(r'^transform = Transform3D\((.*?)\)',block,re.M)
    if hit:
        v=np.array([float(v) for v in hit[1].split(',')]);m[:3,:3]=v[:9].reshape(3,3).T;m[:3,3]=v[9:]
    return m
def parse_scene(s):
    ext={m[2]:m[1] for m in re.finditer(r'^\[ext_resource .*?path="([^"]+)" id="([^"]+)"\]',s,re.M)}
    nodes=[]
    for block in re.split(r'(?=^\[node )',s,flags=re.M)[1:]:
        head=block.splitlines()[0];attrs=dict(re.findall(r'(\w+)="([^"]+)"',head));ins=re.search(r'instance=ExtResource\("([^"]+)"\)',head)
        nodes.append(dict(name=attrs['name'],parent=attrs.get('parent',''),type=attrs.get('type',''),resource=ext[ins[1]] if ins else None,block=block,matrix=matrix(block)))
    return ext,nodes
ext,nodes=parse_scene(world);parents={'':np.eye(4),'.':np.eye(4)}
for n in nodes:
    path=n['name'] if n['parent'] in ['', '.'] else n['parent']+'/'+n['name']
    n['path']=path;n['world_matrix']=parents[n['parent']]@n['matrix'];parents[path]=n['world_matrix']
@lru_cache(None)
def scene_geometry(resource):
    p=R/resource.removeprefix('res://')
    if p.suffix=='.glb':
        b=asset_world_triangles(p);return b[:,:,[0,2,1]]*np.array([1,1,-1]),[resource]
    assert p.suffix=='.tscn',resource
    ex,ns=parse_scene(text(p));ms={'':np.eye(4),'.':np.eye(4)};tri=[];sources=[]
    for n in ns:
        path=n['name'] if n['parent'] in ['', '.'] else n['parent']+'/'+n['name'];m=ms[n['parent']]@n['matrix'];ms[path]=m
        if n['parent']=='':ms['.']=m
        if n['resource']:
            t,src=scene_geometry(n['resource']);tri.extend(t@m[:3,:3].T+m[:3,3]);sources+=src
    return np.array(tri).reshape(-1,3,3),sorted(set(sources))
class MultiReader:
    """Strict actual uncompressed RSRC MultiMesh subset; no guessed props fallback."""
    def __init__(self,path):
        self.raw=path.read_bytes();self.i=0
        assert self.raw[:4]==b'RSRC' and self.raw[4:12]==b'\0'*8
        assert struct.unpack_from('<III',self.raw,12)==(4,5,6)
        self.i=self.raw.index(b'resource_local_to_scene')-8
        self.strings=[self.string() for _ in range(self.u32())];self.ext=[]
        for _ in range(self.u32()):self.ext.append(dict(type=self.string(),path=self.string(),uid=self.u64()))
        internals=[(self.string(),self.u64()) for _ in range(self.u32())]
        assert len(internals)==1;self.i=internals[0][1];assert self.string()=='MultiMesh';self.props={}
        for _ in range(self.u32()):
            name=self.strings[self.u32()];self.props[name]=self.variant()
        assert self.raw[self.i:]==b'RSRC',(path,self.i,len(self.raw))
        assert self.props['transform_format']==1 and not self.props.get('use_colors',False) and not self.props.get('use_custom_data',False)
        self.props.setdefault('instance_count',0)
        if 'buffer' not in self.props:
            assert self.props['instance_count']==0,(path,self.props)
            self.props['buffer']=np.array([])
        self.transforms=np.array(self.props['buffer']).reshape(self.props['instance_count'],3,4)
        assert np.isfinite(self.transforms).all() and np.all(np.abs(np.linalg.det(self.transforms[:,:,:3]))>.00001)
        self.mesh=self.props['mesh']['path']
    def u32(self):
        v=struct.unpack_from('<I',self.raw,self.i)[0];self.i+=4;return v
    def u64(self):
        v=struct.unpack_from('<Q',self.raw,self.i)[0];self.i+=8;return v
    def string(self):
        n=self.u32();v=self.raw[self.i:self.i+n].rstrip(b'\0').decode();self.i+=n;return v
    def variant(self):
        typ=self.u32()
        if typ==1:return None
        if typ==2:return bool(self.u32())
        if typ==3:return struct.unpack('<i',struct.pack('<I',self.u32()))[0]
        if typ==5:return self.string()
        if typ==24:
            sub=self.u32()
            if sub==0:return None
            assert sub==3,sub
            return self.ext[self.u32()]
        if typ==33:
            count=self.u32();data=np.frombuffer(self.raw,dtype='<f4',count=count,offset=self.i).copy();self.i+=count*4;return data
        raise ValueError(('Unexpected actual variant',typ,self.i))
details=[];excluded=[];counts=Counter();markers=[]
for n in nodes:
    if n['parent'] not in ['LandDetails','Settlements','Cliffs','Mountains']:continue
    counts[n['parent']]+=1;t,paths=scene_geometry(n['resource']);m=n['world_matrix'];t=t@m[:3,:3].T+m[:3,3]
    xy=t[:,:,[0,2]];lo=xy.min(axis=(0,1));hi=xy.max(axis=(0,1));bounds=box(*lo,*hi)
    if not bounds.intersects(region):
        excluded.append(dict(path=n['path'],bounds_xz=[lo.tolist(),hi.tolist()],aabb_distance_to_region_m=region.distance(bounds)));continue
    hits=[Polygon(q).intersection(region) for q in xy if box(*q.min(axis=0),*q.max(axis=0)).intersects(region)]
    foot=union_all([x for x in hits if x.area>1e-10])
    details.append(dict(path=n['path'],resource=n['resource'],glb_resources=paths,world_transform=m[:3].tolist(),world_bounds_xyz=[t.min(axis=(0,1)).tolist(),t.max(axis=(0,1)).tolist()],actual_projected_intersection_area_m2=foot.area,actual_projected_intersection=mapping(foot),aabb_only_overlap=foot.is_empty))
for n in nodes:
    if n['parent']=='Ports':
        p=n['world_matrix'][:3,3];markers.append(dict(path=n['path'],world_position=p.tolist(),origin_in_region=region.covers(Point(p[0],p[2]))))
chunks={(x,z) for x in [-5,-4,-3,-2] for z in [-6,-5,-4,-3]}
groups=[];selected_total=0
for n in nodes:
    if n['parent']!='Vegetation':continue
    match=re.search(r'_(-?\d+)_(-?\d+)$',n['name']);cell=tuple(map(int,match.groups())) if match else None
    if cell is not None and cell not in chunks:continue
    def ref(prop):return ext[re.search(r'^'+prop+r' = ExtResource\("([^"]+)"\)',n['block'],re.M)[1]]
    resource=ref('multimesh');prefab=ref('model_scene');reader=MultiReader(R/resource.removeprefix('res://'));selected_total+=reader.props['instance_count']
    model,modelpaths=scene_geometry(prefab);unique=np.unique(model.reshape(-1,3),axis=0)
    m=n['world_matrix'];tr=reader.transforms;origins=tr[:,:,3]@m[:3,:3].T+m[:3,3];hits=[];axis_count=0;box_count=0
    for i,local in enumerate(tr):
        wm=np.eye(4);wm[:3]=local;wm=m@wm;p=origins[i]
        inside=XMIN<=p[0]<=-900 and -4400<=p[2]<=-2150
        if inside:axis_count+=1
        v=unique@wm[:3,:3].T+wm[:3,3];lo=v[:,[0,2]].min(axis=0);hi=v[:,[0,2]].max(axis=0);overlap=box(*lo,*hi).intersects(region)
        if overlap:box_count+=1
        if inside or overlap:hits.append(dict(index=i,world_origin=p.tolist(),world_basis_rows=wm[:3,:3].tolist(),axis_in_region=inside,whole_prefab_aabb_intersects=overlap,whole_prefab_bounds_xz=[lo.tolist(),hi.tolist()]))
    groups.append(dict(path=n['path'],kind=re.search(r'metadata/asset_kind = "([^"]+)"',n['block'])[1],chunk=list(cell) if cell else None,chunk_grouped=cell is not None,world_group_transform=m[:3].tolist(),multimesh_resource=resource,multimesh_sha256=sha(R/resource.removeprefix('res://')),actual_referenced_arraymesh=reader.mesh,model_scene=prefab,model_glb_resources=modelpaths,instance_count=reader.props['instance_count'],buffer_floats=len(reader.props['buffer']),actual_buffer_stride_floats=12,axis_count_inside=axis_count,whole_prefab_aabb_count_intersecting=box_count,actual_origins_bounds_xyz=[origins.min(axis=0).tolist(),origins.max(axis=0).tolist()] if len(origins) else None,instances_relevant=hits))
routes=[]
for n in nodes:
    if n['parent']!='Routes':continue
    rid=re.search(r'curve = SubResource\("([^"]+)"\)',n['block'])[1]
    sub=re.search(r'^\[sub_resource type="Curve3D" id="'+rid+r'"\]\n(.*?)(?=^\[)',world,re.M|re.S)[1]
    packed=re.search(r'"points": PackedVector3Array\((.*?)\)',sub,re.S)
    if not packed:raise ValueError('Unparsed Curve3D '+rid)
    v=np.array([float(v) for v in packed[1].split(',')]).reshape(-1,3,3);controls=np.concatenate([v[:,2],v[:,2]+v[:,0],v[:,2]+v[:,1]])
    m=n['world_matrix'];controls=controls@m[:3,:3].T+m[:3,3];width=float(re.search(r'metadata/width_metres = (.*)',n['block'])[1]);lo=controls[:,[0,2]].min(axis=0)-width/2;hi=controls[:,[0,2]].max(axis=0)+width/2
    routes.append(dict(path=n['path'],curve_subresource=rid,control_points=len(v),width_m=width,conservative_control_hull_aabb_xz=[lo.tolist(),hi.tolist()],aabb_intersects_region=box(*lo,*hi).intersects(region),distance_to_region_m=region.distance(box(*lo,*hi))))
summary=dict(examined_saved_nodes=dict(counts),actual_mesh_projection_intersections=[x['path'] for x in details if x['actual_projected_intersection_area_m2']>0],candidate_scatter_groups=len(groups),candidate_scatter_instances_decoded=selected_total,groups_with_actual_axes_inside=sum(g['axis_count_inside']>0 for g in groups),actual_axes_inside=sum(g['axis_count_inside'] for g in groups),whole_prefab_aabb_overlaps=sum(g['whole_prefab_aabb_count_intersecting'] for g in groups),axis_count_by_kind={k:sum(g['axis_count_inside'] for g in groups if g['kind']==k) for k in sorted({g['kind'] for g in groups})},routes_potentially_intersecting=[r['path'] for r in routes if r['aabb_intersects_region']])
report=dict(scope='Read-only saved World occupancy, Godot Y up; only16 candidate chunk scatter resources plus individually authored groves, no engine/Blender/GPU/production write.',initial_region_xz=[[-2600,-4400],[-900,-2150]],region_xz=[[XMIN,-4400],[-900,-2150]],region_revision='Parent expanded west only to-3750 and added Ground_-5_-6/-5/-4/-3, because actual coastline lies west of initial rectangle. Parent evidence36-terrain-savedmesh-intake.json; no new independent terrain scan.',world_sha256=sha(R/'scenes/world/World.tscn'),matches_parent_intake=sha(R/'scenes/world/World.tscn')==intake['source_world_sha256'],summary=summary,land_details_and_structures_intersections=details,nonintersecting_saved_model_bounds=excluded,route_controls=routes,port_markers=markers,scatter_groups=groups,scatter_decode_contract='Actual uncompressed RSRC4.5 format6 named property table, external mesh resource, instance_count,12-float row-major3x4 buffer. Terminal marker, finite/nonzero determinants checked. No world_layout.props fallback.',update_entries=[dict(file='scripts/scatter_group.gd',methods=['copy_data','apply_selected','extract_selected'],purpose='Allocate first, preserve data, modify selected resource-local transform using inverse grove global transform.'),dict(file='scripts/open_world.gd',method='_ready',purpose='Rebuilds props, prop_transforms and collision buckets from actual saved grove transforms; world_layout.props overwritten.'),dict(file='tools/cliff_refresh.gd',method='reseat_grove',purpose='Existing affected-region helper; its vegetation removal thresholds are author assumptions, not requirements for new highland.'),dict(file='tools/install_cliff_kit.gd',purpose='Example of saving only changed grove resources and saved World references; do not run whole kit.'),dict(file='tools/export_land_detail_layout.gd',purpose='Actual saved LandDetails export for Blender drape. Historical assets/land_detail_authoring.json includes legacy Roads and is not current scene truth.')],limitations=['Whole prefab AABB is conservative for MultiMesh first ArrayMesh, not actual trunk support domain; exact saved root axes/transforms separately reported.','No new terrain clearance. Final deformation footprint must select affected instance indices, not blindly every instance of a chunk.','No world/GPU/physics validation;33f headland north Z=-2050 remains outside.','Cloud/FlightRing aerial content excluded from grounded occupancy. Routes/Ports separately bounded.'],production_modified=False,full_reference_accepted=False)
report['scatter_prefab_bound_qualification']='The corresponding current prefab GLB supplies a proxy AABB only. Equivalence to the referenced saved ArrayMesh geometry was not decoded; do not claim this proxy proves all true foliage geometry outside-axis overlaps or complete trunk feet.'
report['limitations'][0]=report['scatter_prefab_bound_qualification']
report['summary']['axes_inside_initial_rectangle']=sum(p['axis_in_region'] and p['world_origin'][0]>=-2600 for g in groups for p in g['instances_relevant'])
report['summary']['axes_added_by_west_expansion']=summary['actual_axes_inside']-report['summary']['axes_inside_initial_rectangle']
report['chunk_summary']=[dict(chunk=[x,z],saved_groups=sum(g['chunk']==[x,z] for g in groups),resource_instances=sum(g['instance_count'] for g in groups if g['chunk']==[x,z]),axis_inside=sum(g['axis_count_inside'] for g in groups if g['chunk']==[x,z])) for x,z in sorted(chunks)]
report['summary']['nonchunk_authored_groups']=sum(not g['chunk_grouped'] for g in groups)
report['summary']['nonchunk_authored_instances']=sum(g['instance_count'] for g in groups if not g['chunk_grouped'])
(R/'reviews/36-highcoast-occupancy-intake.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,default=lambda x:x.item()))
