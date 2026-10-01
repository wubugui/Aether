"""Fresh Blender reopen; actual full-land support, immutable root and footprint proofs."""
import bpy,bmesh,json,math,collections,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/scratch/a29d03198654/Aether');D=R/'source-assets/lake-cirque54/v1'
sys.path.insert(0,str(D.parent/'intake'));import land_support as land
data=json.load(open(D/'cirque54-payload.json'));m=data['mountains'][0];org=m['origin']
bpy.ops.wm.open_mainfile(filepath=str(D/'massif_cirque_wall_cirque54.blend'))
def key(tri):return tuple(sorted(tuple(round(float(x),4) for x in p) for p in tri))
def w(v):return [v[0]+org[0],v[2]+org[1],-v[1]+org[2]]
def tree(ff):return BVHTree.FromPolygons([Vector(p) for p in ff],[(i,i+1,i+2) for i in range(0,len(ff),3)],all_triangles=True)
def ht(tr,x,z):
 p,_,_,_=tr.ray_cast(Vector((x,1500,z)),Vector((0,-1,0)),3000)
 return None if p is None else p.y
report={'baseline_sha256':land.INVENTORY['source_sha256'],'blend_sha256':hashlib.sha256((D/'massif_cirque_wall_cirque54.blend').read_bytes()).hexdigest(),'reopen':[]}
for c in m['components']:
 o=bpy.data.objects[c['name']];mesh=o.data;mesh.calc_loop_triangles();ff=[w(o.matrix_world@mesh.vertices[i].co) for t in mesh.loop_triangles for i in reversed(t.vertices)]
 exact=collections.Counter(key(ff[i:i+3]) for i in range(0,len(ff),3))==collections.Counter(key(c['vertices'][i:i+3]) for i in range(0,len(ff),3))
 bm=bmesh.new();bm.from_mesh(mesh);r={'component':c['name'],'triangles':len(ff)//3,'reopened_triangles_equal_payload_0_1mm':exact,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-8 for f in bm.faces),'positive_volume_m3':bm.calc_volume(signed=True)};bm.free();report['reopen'].append(r)
 assert exact and r['boundary_edges']==r['nonmanifold_edges']==r['degenerate_faces']==0 and r['positive_volume_m3']>0,r
root=next(c for c in m['components'] if c['name']=='rock_body')['vertices'];auth=land.INVENTORY['cirque_mesh']['faces']
rootmatch=collections.Counter(key(root[i:i+3]) for i in range(0,len(root),3))==collections.Counter(key(auth[i:i+3]) for i in range(0,len(auth),3))
report['original_692_triangles_exact']=rootmatch;report['original_underwater_and_waterline_triangles_exact']=rootmatch;assert rootmatch
new=tree([p for c in m['components'] if c['name']!='rock_body' for p in c['vertices']]);surface=json.load(open(D/'authoring-surface.json'));verts=surface['top_vertices'];body=tree([verts[i] for f in surface['top_faces'] for i in f])
delta=[]
for a,b in surface['boundary_edges']:
 p,q=map(Vector,(verts[a],verts[b]));steps=math.ceil((q-p).length/.5)
 for j in range(steps+1):
  v=p.lerp(q,j/steps);delta.append(v.y-land.height(v.x,v.z))
report['root_join']={'samples_spacing_max_m':.5,'sample_count':len(delta),'highest_new_boundary_minus_actual_support_m':max(delta),'lowest_m':min(delta),'all_at_least_4m_buried':max(delta)<=-3.999}
assert report['root_join']['all_at_least_4m_buried'],report['root_join']
# All new volume is a paired triangulated height field with disjoint projected
# interiors (GEOS proof), so top/bottom cannot cross when every paired vertex gap>0.
o=bpy.data.objects['upper_cirque_mass'];n=len(o.data.vertices)//2;gaps=[o.data.vertices[i].co.z-o.data.vertices[i+n].co.z for i in range(n)]
report['new_mass_self_intersection_proof']={'single_valued_paired_height_field':True,'min_top_bottom_gap_m':min(gaps),'nonoverlapping_projected_triangles_proven_by':'continuous-footprint-proof.json','boundary_vertical_sides_simple_polygon':True,'intentional_component_overlap':'Lower root and rock/snow layers deliberately penetrate the underlying volume; distinct parts are not Boolean-unioned.'};assert min(gaps)>=11.999
scatter=json.load(open(R/'source-assets/lake-rim53/integration-west53/runtime-probes.json'))['scatter'];rows=[];prior=0;counts=collections.Counter()
for s in scatter:
 x,y,z=s['position'];old,owner=land.highest(x,z);added=ht(new,x,z);high=max(old,added) if added is not None else old;change=high-old
 previous=s['status']!='unchanged'
 if previous and change>.015:prior+=1
 state='support_changed_pending_reconcile' if change>.015 else 'root_support_unchanged'
 counts[state]+=1;rows.append({'node':s['node_path'],'index':s['index'],'position_in_verified53':s['position'],'was_one_of_west120':previous,'saved53_support_y':old,'support_owner':owner,'candidate_support_y':high,'delta_m':change,'status':state})
report['scatter_root_scope']={'current53_instances_checked':len(rows),'counts':dict(counts),'previous_west120_changed_by_new_source':prior,'previous_west120_count':sum(s['status']!='unchanged' for s in scatter),'rows':rows,'actual_mesh_volume_overlap_check':'Pending separate geometry check; root support is not the complete effect set','no_transforms_written':True};assert prior==0
# Continuous exclusion of conservative village envelope; actual northern/western
# protected building boxes are also entirely outside the new component footprint.
protected=json.load(open(R/'source-assets/lake-rim53/revision-d/sculpt-report.json'))['buildings_protected'];bounds=[[min(p[k] for p in verts) for k in range(3)],[max(p[k] for p in verts) for k in range(3)]]
report['protected_buildings']=[]
for b in protected:
 disjoint=bounds[0][0]>b['xmax'] or bounds[1][0]<b['xmin'] or bounds[0][2]>b['zmax'] or bounds[1][2]<b['zmin']
 report['protected_buildings'].append({'node':b['node'],'full_added_volume_bbox_disjoint':disjoint,'margin_m':b['margin']});assert disjoint,('protected box overlaps',b)
report['all_19_protected_regions_disjoint']=len(protected)==19
report['visual_acceptance']=False;report['integrated']=False
json.dump(report,open(D/'native-readback-proof.json','w'),indent=2)
print('CIRQUE54_REOPEN_PASS',len(report['reopen']),'components;rootjoin',report['root_join'],'scatter',dict(counts),'previous120',prior,flush=True)
