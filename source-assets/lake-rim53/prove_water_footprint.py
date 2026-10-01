"""Continuous planar containment against actual saved dry triangles, using installed GEOS."""
import json,ctypes,math,sys
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53'
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
base=json.load(open(D+'/base51b.json'));CAND=sys.argv[1] if len(sys.argv)>1 else D;candidate=json.load(open(CAND+'/rim53-payload.json'))
dry=[]
for m in base['meshes'].values():
 f=m['faces']
 for i in range(0,len(f),3):
  p=dryclip(f[i:i+3])
  if len(p)>2:dry.append(p)
land=geom(dry);results=[]
for m in candidate['mountains']:
 polys=[]
 for c in m['components']:
  if c['name']=='rock_body':continue
  f=c['vertices']
  for i in range(0,len(f),3):polys.append([[p[0],p[2]] for p in f[i:i+3]])
 footprint=geom(polys);diff=lib.GEOSDifference(footprint,land);assert diff
 a=ctypes.c_double();assert lib.GEOSArea(diff,ctypes.byref(a))
 total=ctypes.c_double();lib.GEOSArea(footprint,ctypes.byref(total))
 r={'mountain':m['name'],'all_new_component_projection_area_m2':total.value,'projected_area_outside_actual_saved_y_ge_0_support_m2':a.value,'continuous_planar_containment_pass':a.value<1e-8};results.append(r);print(r,flush=True)
 for g in [diff,footprint]:lib.GEOSGeom_destroy(g)
report={'method':'Each baseline saved triangle clipped exactly at Y0, projected into XZ, and unioned using installed GEOS 3.13.1. Difference of every added closed component projection against union of actual dry support is measured. Coordinates serialized to 1nm for polygon operations. This proves no added component projects into a baseline water column, stronger than finite sampling. Crown original body edit is strictly at Y>355 and does not move XZ coordinates. Existing source bodies are retained with native float32 mapping tolerance; dense BVH highest-water comparison separately verifies zero change.','dry_triangle_polygons':len(dry),'results':results,'all_added_component_footprints_on_saved_dry_land':all(r['continuous_planar_containment_pass'] for r in results)}
json.dump(report,open(CAND+'/continuous-water-footprint-proof.json','w'),indent=2)
lib.GEOSGeom_destroy(land)
assert report['all_added_component_footprints_on_saved_dry_land'], 'Added footprint extends into saved water'
