"""Fresh raw C source readback: topology, actual valleys, sections, camera."""
import hashlib,json,sys,time
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
P=Path(__file__).resolve().parent;ROOT=P.parents[3];sys.path.insert(0,str(P))
from native_geometry58c import geometry
from triangle_checks58c import valley_report,cross_sections
from geometry58c import world_coordinate
start=time.monotonic()
def stage(name):
 row=dict(complete=False,current_operation=name,elapsed_seconds=time.monotonic()-start);(P/'verify-stage58c.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
def write(name,data):(P/name).write_text(json.dumps(data,indent=2)+'\n')
path=P/'cloud_bank58c_union.blend';digest=hashlib.sha256(path.read_bytes()).hexdigest();stage('open_saved_C_union_fresh')
bpy.ops.wm.open_mainfile(filepath=str(path));bank=bpy.data.objects['CloudBank58C_four_root_density_and_folds'];stage('full57_union_topology_and_actual_intersections')
row,v,ids,tri,tree=geometry(bank);write('union-geometry58c.json',dict(source_sha256=digest,geometry=row,native_union_geometry_passed=row['closed_geometry_passed'],visual_acceptance=False))
stage('fresh_native_control_vertex_topology_correspondence');specs=json.loads((P/'native-control-input58c.json').read_text());controls=[]
for s in specs['controls']:
 ob=bpy.data.objects['EDIT58C_'+s['id']];actual=np.array([world_coordinate(ob.matrix_world@q.co) for q in ob.data.vertices]);error=float(np.linalg.norm(actual-np.array(s['vertices']),axis=1).max());same=[list(p.vertices) for p in ob.data.polygons]==[list(f) for f in s['faces']]
 controls.append(dict(id=s['id'],maximum_authored_world_vertex_error_m=error,ordered_oriented_faces_exact=same,passed=bool(error<.00025 and same)))
write('native-control-fresh58c.json',dict(controls=controls,passed=all(r['passed'] for r in controls)))
stage('actual_valley_25m_three_lane_entry_exit_intervals');plan=json.loads((P/'authoring-plan58c.json').read_text());valleys=valley_report(tri,plan['valley_corridors']);write('actual-valley-support58c.json',valleys)
stage('actual_triangle_cross_sections');sections=cross_sections(tri,plan['section_planes']);write('actual-sections58c.json',sections)
stage('actual_camera_point_classification');camera=np.array(plan['camera_godot_world']);nearest=tree.find_nearest(Vector(camera));directions=[Vector((.817,.431,.382)).normalized(),Vector((-.239,.881,.408)).normalized(),Vector((.337,-.287,.897)).normalized()];rays=[]
for direction in directions:
 p=Vector(camera);hits=[]
 for _ in range(1000):
  co,no,face,distance=tree.ray_cast(p,direction,20000)
  if co is None:break
  hits.append(dict(world=list(co),triangle_id=int(face)));p=co+direction*.001
 rays.append(dict(direction=list(direction),hits=hits,count=len(hits),inside=bool(len(hits)%2)))
classification='boundary' if nearest[3]<.001 else 'inside' if all(r['inside'] for r in rays) else 'outside' if all(not r['inside'] for r in rays) else 'ambiguous'
cam=dict(world=camera.tolist(),classification=classification,nearest_surface_distance_m=nearest[3],rays=rays,point_only=True,ship_or_swept_route_checked=False)
write('camera-point58c.json',cam)
passed=bool(row['closed_geometry_passed'] and valleys['passed'] and all(r['passed'] for r in controls) and classification=='outside')
summary=dict(passed=passed,source_sha256=digest,source_unchanged=hashlib.sha256(path.read_bytes()).hexdigest()==digest,geometry_passed=bool(row['closed_geometry_passed']),valley_support_passed=valleys['passed'],native_control_passed=all(r['passed'] for r in controls),camera=cam,
 world_bounds=row.get('world_bounds'),saved_ocean_y_m=0,external21roots_contact_not_yet_checked=True,world_loaded=False,rendered=False,visual_acceptance=False,finished_source=False)
write('union-fresh-readback58c.json',summary);write('verify-stage58c.json',dict(complete=True,current_operation='fresh_geometry_terminal',passed=passed,elapsed_seconds=time.monotonic()-start))
print(json.dumps(dict(passed=passed,geometry_passed=summary['geometry_passed'],valley_support_passed=valleys['passed'],camera_classification=classification),indent=2),flush=True)
assert passed,'Keep failedCsourceandall reports; no automatic cavity cleanup, simplification or preview'
