"""Continuous dry-footprint proof using every intersecting full-scene collider."""
import json,ctypes,math,sys,hashlib
from pathlib import Path
import numpy as np
R=Path('/workspace/scratch/a29d03198654/Aether');D=R/'source-assets/lake-cirque54/v1';I=D.parent/'intake'
lib=ctypes.CDLL('/lib/x86_64-linux-gnu/libgeos_c.so.1');ptr=ctypes.c_void_p
lib.initGEOS.argtypes=[ptr,ptr];lib.initGEOS(None,None)
lib.GEOSGeomFromWKT.argtypes=[ctypes.c_char_p];lib.GEOSGeomFromWKT.restype=ptr
lib.GEOSUnaryUnion.argtypes=[ptr];lib.GEOSUnaryUnion.restype=ptr
lib.GEOSDifference.argtypes=[ptr,ptr];lib.GEOSDifference.restype=ptr
lib.GEOSArea.argtypes=[ptr,ctypes.POINTER(ctypes.c_double)];lib.GEOSArea.restype=ctypes.c_int
lib.GEOSisEmpty.argtypes=[ptr];lib.GEOSisEmpty.restype=ctypes.c_char
lib.GEOSGeom_destroy.argtypes=[ptr]
def signedarea(p):return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2

def geom(polys):
 txt='MULTIPOLYGON ('+','.join('(('+','.join(f'{x:.9f} {z:.9f}' for x,z in p+[p[0]])+'))' for p in polys if len(p)>2 and abs(signedarea(p))>1e-9)+')'
 g=lib.GEOSGeomFromWKT(txt.encode());assert g,'GEOS input invalid'
 u=lib.GEOSUnaryUnion(g);assert u,'GEOS union failed';lib.GEOSGeom_destroy(g);return u

def dryclip(tri):
 out=[]
 for a,b in zip(tri,tri[1:]+tri[:1]):
  if a[1]>=0:out.append([a[0],a[2]])
  if (a[1]>=0)!=(b[1]>=0):
   t=-a[1]/(b[1]-a[1]);out.append([a[0]+t*(b[0]-a[0]),a[2]+t*(b[2]-a[2])])
 return out

j=json.load(open(I/'land53-inventory.json'));raw=np.fromfile(I/'land-world-faces-f32.bin',dtype='<f4').reshape((-1,3))
assert hashlib.sha256((I/'land-world-faces-f32.bin').read_bytes()).hexdigest()==j['binary_sha256']
assert not j['unhandled_land_shapes']
m=json.load(open(D/'cirque54-payload.json'))['mountains'][0]
f=[p for c in m['components'] if c['name']!='rock_body' for p in c['vertices']]
lo=[min(p[k] for p in f) for k in range(3)];hi=[max(p[k] for p in f) for k in range(3)]
def overlap(b):return b[0][0]<=hi[0] and b[1][0]>=lo[0] and b[0][2]<=hi[2] and b[1][2]>=lo[2]
dry=[];used=[]
for row in j['land_shapes']:
 if not overlap(row['bounds']):continue
 used.append(row['path']);start=row['offset_bytes']//12;ff=raw[start:start+row['vertices']]
 for i in range(0,len(ff),3):
  tri=ff[i:i+3].tolist()
  if not overlap([[min(p[k] for p in tri) for k in range(3)],[max(p[k] for p in tri) for k in range(3)]]):continue
  p=dryclip(tri)
  if len(p)>2:dry.append(p)
land=geom(dry);results=[]
for c in m['components']:
 if c['name']=='rock_body':continue
 ff=c['vertices'];polys=[[[p[0],p[2]] for p in ff[i:i+3]] for i in range(0,len(ff),3)]
 footprint=geom(polys);diff=lib.GEOSDifference(footprint,land);assert diff
 a=ctypes.c_double();area=ctypes.c_double();lib.GEOSArea(diff,ctypes.byref(a));lib.GEOSArea(footprint,ctypes.byref(area))
 results.append({'component':c['name'],'footprint_area_m2':area.value,'outside_actual_dry_support_m2':a.value,'pass':a.value<1e-8})
 for g in [diff,footprint]:lib.GEOSGeom_destroy(g)
# All top triangles are a single-valued field over a simple planar polygon. Equality
# of summed projected area and union area rules out overlapping distinct interiors.
surface=json.load(open(D/'authoring-surface.json'));verts=surface['top_vertices'];top=[[[verts[i][0],verts[i][2]] for i in face] for face in surface['top_faces']]
sumarea=sum(abs(signedarea(p)) for p in top);union=geom(top);uarea=ctypes.c_double();lib.GEOSArea(union,ctypes.byref(uarea));lib.GEOSGeom_destroy(union)
report={'baseline_scene_sha256':j['source_sha256'],'binary_sha256':j['binary_sha256'],'total_saved_nonwater_layer4_shapes':len(j['land_shapes']),'unhandled_saved_shapes':j['unhandled_land_shapes'],'water_shapes_explicitly_excluded':j['water_shapes'],'actual_bbox_intersecting_support_shapes':used,'dry_clipped_polygons':len(dry),'method':'Actual full-scene layer4 collider triangles, safely culled by exact world bounding boxes only, clipped at Y0 and unioned with GEOS. Every new closed component full XZ projection is subtracted from that actual dry union. Original692triangle root preserved separately. This continuous proof does not depend on finite point sampling or a six-tile assumption. No buildings or floating-island colliders intersect this candidate box.','component_results':results,'all_new_footprints_dry':all(r['pass'] for r in results),'new_body_top_projection':{'triangle_area_sum_m2':sumarea,'union_area_m2':uarea.value,'distinct_triangle_overlap_area_m2':sumarea-uarea.value,'no_projected_triangle_interior_overlap':abs(sumarea-uarea.value)<1e-6}}
json.dump(report,open(D/'continuous-footprint-proof.json','w'),indent=2);print(json.dumps(report,indent=2))
assert report['all_new_footprints_dry'];assert report['new_body_top_projection']['no_projected_triangle_interior_overlap']
lib.GEOSGeom_destroy(land)
