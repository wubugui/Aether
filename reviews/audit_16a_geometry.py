"""Independent, read-only exported GLB comparison; writes only its new review JSON."""
from pathlib import Path
import json, struct, hashlib, math, collections
import numpy as np
from shapely.geometry import Polygon

ROOT=Path(r'E:\FeiTing')
def read(path):
    b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);start=28+n
    def acc(i):
        a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];k={'VEC3':3,'VEC4':4,'SCALAR':1}[a['type']]
        return np.frombuffer(b,dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']],count=a['count']*k,offset=start+v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,k)
    assert all(set(x)<=set(['mesh','name']) for x in g['nodes']),g['nodes']
    assert len(g['meshes'])==1 and len(g['meshes'][0]['primitives'])==1
    prim=g['meshes'][0]['primitives'][0];raw=acc(prim['attributes']['POSITION']).astype(float);ix=acc(prim['indices']).reshape(-1,3)
    p,inv=np.unique(raw,axis=0,return_inverse=True);f=inv[ix]
    return p,f,acc(prim['attributes']['COLOR_0'])[ix].mean(axis=1),hashlib.sha256(b).hexdigest()
def normals(p,f):
    t=p[f];c=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(c,axis=1)
    return c/length[:,None],length/2
def rings(p,f):
    floor=p[:,1]<-14.;mix=f[np.any(floor[f],axis=1)&~np.all(floor[f],axis=1)]
    return set(np.unique(mix[~floor[mix]])),set(np.where(floor)[0])
def stat(p,f):
    edges=collections.defaultdict(list)
    for i,(a,b,c) in enumerate(f):
        for x,y in ((a,b),(b,c),(c,a)):edges[tuple(sorted((int(x),int(y))))].append((int(x),int(y)))
    n,area=normals(p,f);t=p[f]
    return {'welded_exact_positions':len(p),'triangles':len(f),'edges':len(edges),'euler':len(p)-len(edges)+len(f),'edge_incidence_not_2':sum(len(x)!=2 for x in edges.values()),'paired_edge_same_orientation':sum(len(x)==2 and x[0]==x[1] for x in edges.values()),'degenerate_area_lt_1e_8':int(sum(area<1e-8)),'min_triangle_area_m2':float(min(area)),'signed_volume_m3':float(np.sum(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])))/6)}
def intersections(p,f,include_shared=False):
    t=p[f];low=t.min(axis=1);high=t.max(axis=1);out=[];cop=[]
    def segment_triangle(a,b,tri):
        d=b-a;e1=tri[1]-tri[0];e2=tri[2]-tri[0];h=np.cross(d,e2);det=np.dot(e1,h)
        if abs(det)<1e-10:return False
        s=a-tri[0];u=np.dot(s,h)/det;q=np.cross(s,e1);v=np.dot(d,q)/det;dist=np.dot(e2,q)/det
        return u>=-1e-8 and v>=-1e-8 and u+v<=1+1e-8 and dist>1e-8 and dist<1-1e-8
    for i in range(len(t)):
        candidates=np.where(np.all(high[i]>=low-1e-8,axis=1)&np.all(high>=low[i]-1e-8,axis=1))[0]
        for j in candidates[candidates>i]:
            if not include_shared and set(f[i])&set(f[j]):continue
            a,b=t[i],t[j];na=np.cross(a[1]-a[0],a[2]-a[0]);na/=np.linalg.norm(na)
            if np.max(np.abs((b-a[0])@na))<1e-7:
                axes=[k for k in range(3) if k!=int(np.argmax(abs(na)))];area=Polygon(a[:,axes]).intersection(Polygon(b[:,axes])).area
                if area>1e-6:cop.append([i,int(j),float(area)])
            elif any(segment_triangle(x[k],x[(k+1)%3],y) for x,y in ((a,b),(b,a)) for k in range(3)):out.append([i,int(j)])
    return {'nonadjacent_triangle_crossings':out,'nonadjacent_coplanar_overlap_projected_m2':cop,'include_shared_vertex_pairs':include_shared,'scope':'AABB broad phase and segment/triangle crossings, plus coplanar area. Field names retained for schema stability; include_shared_vertex_pairs states pair coverage. Not an exact arithmetic proof against self-intersection, and not inter-asset intersection.'}

manifest=json.loads((ROOT/'captures/foreground_study_16a/manifest.json').read_text());cat={x['name']:x for x in json.loads((ROOT/'assets/cliff_kit.json').read_text())};control_audit=json.loads((ROOT/'reviews/restore-20260908-cliff-upper-control-audit.json').read_text());report={'scope':'Independent actual source GLB versus 16a GLB; no Blender or Godot launched, no production writes. Visual acceptance pending screenshots.','assets':{}}
for item in manifest:
    name=item['name'];p,f,color,sha=read(ROOT/'assets/models'/f'{name}.glb');q,h,newcolor,newsha=read(ROOT/item['path']);assert newsha==item['glb_sha256']
    expected=p.copy();moves=[]
    for edit in item['controls']:
        before=np.array(edit['before'])[[0,2,1]]*np.array([1,1,-1]);after=np.array(edit['after'])[[0,2,1]]*np.array([1,1,-1]);i=int(np.argmin(np.linalg.norm(p-before,axis=1)));j=int(np.argmin(np.linalg.norm(q-after,axis=1)))
        assert np.linalg.norm(p[i]-before)<1e-5 and np.linalg.norm(q[j]-after)<1e-5
        expected[i]=q[j];moves.append({'native_control_index':edit['index'],'source_match_m':float(np.linalg.norm(p[i]-before)),'candidate_match_m':float(np.linalg.norm(q[j]-after)),'actual_displacement_m':float(np.linalg.norm(q[j]-p[i])),'glb_before_xyz':p[i].tolist(),'glb_after_xyz':q[j].tolist()})
    dist=np.linalg.norm(q[:,None,:]-expected[None,:,:],axis=2);q_to_p=dist.argmin(axis=1);assert np.max(dist.min(axis=1))<1e-5 and len(set(q_to_p))==len(p)==len(q)
    hf=q_to_p[h];face_map={tuple(sorted(t)):i for i,t in enumerate(f)};reorder=[face_map[tuple(sorted(t))] for t in hf];newfaces=np.empty_like(f);newfaces[reorder]=hf;newcolors=np.empty_like(color);newcolors[reorder]=newcolor
    source_rim,source_floor=rings(p,f);candidate_rim,candidate_floor=rings(q,h);rim_match={tuple(p[i]) for i in source_rim}=={tuple(q[i]) for i in candidate_rim};floor_match={tuple(p[i]) for i in source_floor}=={tuple(q[i]) for i in candidate_floor}
    oldn,oldarea=normals(p,f);newn,newarea=normals(expected,newfaces);dots=np.einsum('ij,ij->i',oldn,newn);changed=np.where(np.linalg.norm(newn-oldn,axis=1)>1e-7)[0]
    oldinter=intersections(p,f,True);newinter=intersections(expected,newfaces,True)
    entry={'source_glb_sha256':sha,'candidate_glb_sha256':newsha,'source_geometry':stat(p,f),'candidate_geometry':stat(q,h),'entire_rim_exact_equal':rim_match,'entire_floor_exact_equal':floor_match,'rim_count':len(source_rim),'floor_count':len(source_floor),'all_positions_accounted_for_by_controls':True,'triangle_connectivity_same_after_control_mapping':True,'moved_controls':moves,'normal_dot_negative_faces':[{'face':int(i),'old_dot_new':float(dots[i]),'old_normal':oldn[i].tolist(),'new_normal':newn[i].tolist()} for i in np.where(dots<0)[0]],'max_face_normal_rotation_degrees':float(np.degrees(np.arccos(np.clip(min(dots),-1,1)))),'source_intersections':oldinter,'candidate_intersections':newinter,'new_nonadjacent_crossings':sorted(list(set(map(tuple,newinter['nonadjacent_triangle_crossings']))-set(map(tuple,oldinter['nonadjacent_triangle_crossings']))))}
    if name=='cliff_crown':
        origin=np.array(cat[name]['position']);ids={}
        for c in control_audit['assets'][name]['upper_controls']:
            if c['row'] not in ('front','ridge'):continue
            target=np.array(c['actual_world_xyz'])-origin;i=int(np.argmin(np.linalg.norm(p-target,axis=1)));assert np.linalg.norm(p[i]-target)<1e-4;ids[i]=(8 if c['row']=='front' else 16)+c['k']
        grass=[]
        for i,face in enumerate(f):
            if not all(int(v) in ids for v in face):continue
            native=[ids[int(v)] for v in face]
            if not (any(k<16 for k in native) and any(k>=16 for k in native)):continue
            strip=min(k%8 for k in native)
            if strip not in (0,1,2,6):continue
            grass.append({'face':i,'strip':strip,'native_vertices':native,'normal_y':float(newn[i,1]),'slope_degrees_from_horizontal':float(np.degrees(np.arccos(np.clip(newn[i,1],-1,1)))),'old_slope_degrees':float(np.degrees(np.arccos(np.clip(oldn[i,1],-1,1)))),'area_m2':float(newarea[i]),'linear_vertex_color':newcolors[i].tolist()})
        cross_sections=[]
        reverse={k:v for v,k in ids.items()}
        for k in range(8):
            a,b=reverse[8+k],reverse[16+k];delta=expected[b]-expected[a];cross_sections.append({'column':k,'horizontal_width_xz_m':float(np.linalg.norm(delta[[0,2]])),'rise_m':float(delta[1]),'slope_degrees':float(np.degrees(np.arctan2(delta[1],np.linalg.norm(delta[[0,2]])))),'prior_horizontal_width_xz_m':float(np.linalg.norm((p[b]-p[a])[[0,2]]))})
        entry['new_grass_strip_triangles']=grass;entry['front_to_ridge_cross_section']=cross_sections
    report['assets'][name]=entry
    print(name,json.dumps({k:entry[k] for k in ('candidate_geometry','entire_rim_exact_equal','entire_floor_exact_equal','normal_dot_negative_faces','new_nonadjacent_crossings')}),flush=True)
    if name=='cliff_crown':print('CROWN_GRASS',json.dumps(grass));print('CROWN_WIDTHS',json.dumps(cross_sections))
(ROOT/'reviews/round-16a-independent-geometry-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
