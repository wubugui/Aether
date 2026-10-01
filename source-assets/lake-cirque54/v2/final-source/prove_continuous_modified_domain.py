import json,ctypes,math,sys,struct,collections,hashlib
from pathlib import Path
import numpy as np
R=Path('/workspace/scratch/a29d03198654/Aether');D=R/'source-assets/lake-cirque54/v2/final-source';I=R/'source-assets/lake-cirque54/intake'
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

lib.GEOSIntersection.argtypes=[ptr,ptr];lib.GEOSIntersection.restype=ptr
lib.GEOSDistance.argtypes=[ptr,ptr,ctypes.POINTER(ctypes.c_double)];lib.GEOSDistance.restype=ctypes.c_int
j=json.load(open(I/'land53-inventory.json'));auth=json.load(open(D.parent/'native-authority/cirque-native-authority.json'));raw=np.fromfile(I/'land-world-faces-f32.bin',dtype='<f4').reshape((-1,3));m=json.load(open(D/'cirque54v2-payload.json'))['mountains'][0]
def key(t):return tuple(sorted(struct.pack('<fff',*p) for p in t))
old=collections.Counter(key(auth['faces'][i:i+3]) for i in range(0,len(auth['faces']),3));parts=[]
for c in m['components']:
 ff=c['vertices'];selected=[]
 for i in range(0,len(ff),3):
  tri=ff[i:i+3]
  if c['name']=='remodeled_cirque_body' and old[key(tri)]:continue
  selected.append(tri)
 parts.append((c['name'],selected))
novel=[v for _,ts in parts for t in ts for v in t];lo=[min(p[k] for p in novel) for k in range(3)];hi=[max(p[k] for p in novel) for k in range(3)]
assert lo[1]>0,'A new or modified triangle touches water'
def overlaps(bounds):return bounds[0][0]<=hi[0] and bounds[1][0]>=lo[0] and bounds[0][2]<=hi[2] and bounds[1][2]>=lo[2]
dry=[];used=[]
for row in j['land_shapes']:
 if not overlaps(row['bounds']):continue
 used.append(row['path']);start=row['offset_bytes']//12;ff=raw[start:start+row['vertices']]
 for i in range(0,len(ff),3):
  tri=ff[i:i+3].tolist()
  if not overlaps([[min(p[k] for p in tri) for k in range(3)],[max(p[k] for p in tri) for k in range(3)]]):continue
  p=dryclip(tri)
  if len(p)>2:dry.append(p)
land=geom(dry);regs=json.load(open(R/'source-assets/lake-rim53/revision-d/sculpt-report.json'))['buildings_protected'];region=geom([[[b['xmin'],b['zmin']],[b['xmax'],b['zmin']],[b['xmax'],b['zmax']],[b['xmin'],b['zmax']]] for b in regs]);results=[]
for name,triangles in parts:
 footprint=geom([[[p[0],p[2]] for p in t] for t in triangles]);outside=lib.GEOSDifference(footprint,land);protected=lib.GEOSIntersection(footprint,region);oa=ctypes.c_double();pa=ctypes.c_double();area=ctypes.c_double();distance=ctypes.c_double();lib.GEOSArea(outside,ctypes.byref(oa));lib.GEOSArea(protected,ctypes.byref(pa));lib.GEOSArea(footprint,ctypes.byref(area));lib.GEOSDistance(footprint,region,ctypes.byref(distance))
 results.append({'component':name,'new_or_modified_triangles':len(triangles),'modified_projection_area_m2':area.value,'outside_actual_saved_dry_union_m2':oa.value,'overlap_with_actual_protected_rectangles_m2':pa.value,'distance_to_protected_rectangles_m':distance.value,'dry_containment_pass':oa.value<1e-8,'protected_continuous_exclusion_pass':pa.value<1e-8})
 for g in [footprint,outside,protected]:lib.GEOSGeom_destroy(g)
report={'source_gpu_collision_authority':auth['authority'],'baseline_sha256':j['source_sha256'],'full_nonwater_land_shape_count':len(j['land_shapes']),'actual_intersecting_support_shapes':used,'all_modified_triangles_minimum_y_m':lo[1],'unmodified_body_triangles_excluded_only_after_exact_float32_match':len(m['components'][0]['vertices'])//3-len(parts[0][1]),'method':'Every modified/new triangle in the full remodelled body and every snow layer is identified by exact original float32triangle comparison. All such projected triangle footprints must lie in the complete saved-scene nonwater collider dry union and have no positive-area intersection with19protected regions. Original wet/protected triangles are separately proven unchanged. GEOS continuous polygon union/difference/intersection, no finite point replacement for footprint checks.','results':results,'all_new_modified_footprints_dry':all(r['dry_containment_pass'] for r in results),'all_protected_regions_continuously_excluded':all(r['protected_continuous_exclusion_pass'] for r in results)}
json.dump(report,open(D/'continuous-modified-domain-proof.json','w'),indent=2);print(json.dumps(report,indent=2));assert report['all_new_modified_footprints_dry'] and report['all_protected_regions_continuously_excluded']
