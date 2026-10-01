import bpy,json,ctypes,hashlib
from pathlib import Path
D=Path('/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/v1');bpy.ops.wm.open_mainfile(filepath=str(D/'massif_cirque_wall_cirque54.blend'))
l=ctypes.CDLL('/lib/x86_64-linux-gnu/libgeos_c.so.1');p=ctypes.c_void_p;l.initGEOS.argtypes=[p,p];l.initGEOS(None,None);l.GEOSGeomFromWKT.argtypes=[ctypes.c_char_p];l.GEOSGeomFromWKT.restype=p;l.GEOSDistance.argtypes=[p,p,ctypes.POINTER(ctypes.c_double)];l.GEOSDistance.restype=ctypes.c_int;l.GEOSGeom_destroy.argtypes=[p]
src=D/'actual-triangle-self-intersection-proof-v3.json';j=json.load(open(src));out=[]
for c in j['components']:
 o=bpy.data.objects[c['component']];m=o.data;m.calc_loop_triangles()
 for row in c['other_zero_area_contacts_or_disjoint_coplanar_candidates']:
  ai,bi=row['triangles'];aa=[m.vertices[i].co for i in m.loop_triangles[ai].vertices];bb=[m.vertices[i].co for i in m.loop_triangles[bi].vertices];n=(aa[1]-aa[0]).cross(aa[2]-aa[0]);axis=max(range(3),key=lambda k:abs(n[k]));keep=[k for k in range(3) if k!=axis]
  ge=[]
  for tri in [aa,bb]:
   wkt='POLYGON (('+','.join(f'{v[keep[0]]:.17g} {v[keep[1]]:.17g}' for v in tri+[tri[0]])+'))';g=l.GEOSGeomFromWKT(wkt.encode());assert g;ge.append(g)
  d=ctypes.c_double();assert l.GEOSDistance(ge[0],ge[1],ctypes.byref(d));out.append({'component':c['component'],'triangles':[ai,bi],'projected_triangle_distance_m':d.value,'strictly_disjoint':d.value>1e-5})
  for g in ge:l.GEOSGeom_destroy(g)
report={'actual_triangle_report_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'method':'Native re-open of the8zero-area coplanar broad-phase candidates; GEOS projected polygon distance distinguishes disjoint triangles from contacts. Positive projected distance guarantees no3Dcontact for these coplanar pairs.','pairs':out,'all8_strictly_disjoint':len(out)==8 and all(r['strictly_disjoint'] for r in out)}
json.dump(report,open(D/'zero-area-candidates-diagnostic.json','w'),indent=2);print(report);assert report['all8_strictly_disjoint']
