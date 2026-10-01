"""Authored medium-scale positive cages; no random surface noise."""
from pathlib import Path
import copy,json,math
P=Path(__file__).resolve().parent
base=json.loads((P.parent/'cloud-sea52h-revision-b-plan/cage52h_b.json').read_text())
parts=copy.deepcopy(base['parts']);edits=[]
for role,changes in {
 'M_main':{10:(0,0,-15),11:(0,0,-25),12:(0,0,-20),13:(0,0,-15),14:(0,0,-10)},
 'S_medium_rear_oblique':{8:(0,0,-10),9:(0,0,-12),10:(0,0,-6),11:(0,0,-10)},
 'T_small_front_fold':{6:(0,0,-8)},
}.items():
 for i,delta in changes.items():
  old=parts[role]['vertices_blender_m'][i][:]
  parts[role]['vertices_blender_m'][i]=[a+b for a,b in zip(old,delta)]
  edits.append({'role':role,'index':i,'before':old,'after':parts[role]['vertices_blender_m'][i]})
# Each silhouette has an offset short crown and an unequal lower wedge.
# These are hand-authored templates, never spherical/ellipsoidal primitives.
profiles={
 'broad_fold':[[-.95,-.3,-.15],[-.52,-.93,-.20],[.25,-.86,-.06],[.96,-.15,-.12],[.73,.73,-.05],[-.2,.96,-.2],[-.87,.51,-.1],[-.55,-.3,.62],[.16,-.42,.88],[.54,.12,.72],[-.16,.55,.50],[-.39,-.19,-.82],[.33,.18,-.65]],
 'oblique_cap':[[-.92,-.52,-.12],[-.18,-.96,.04],[.68,-.61,-.16],[.91,.2,-.13],[.22,.82,-.04],[-.63,.72,-.10],[-.6,-.3,.57],[-.05,-.38,.81],[.47,.16,.66],[-.16,.50,.91],[-.52,.1,-.80],[.30,-.2,-.69]],
 'low_knot':[[-.96,-.13,-.08],[-.60,-.69,-.18],[.15,-.88,-.1],[.94,-.2,-.15],[.67,.52,-.1],[-.1,.91,-.08],[-.76,.57,-.24],[-.40,-.24,.82],[.18,-.34,.55],[.51,.26,.66],[-.15,.41,.58],[-.33,-.11,-.66],[.31,.21,-.60]],
}
# Coordinates m, full design box dimensions, XYZ rotations degrees. Directions
# and intervals deliberately differ; the shoulders are deeply embedded.
shoulders=[
 ('P1_main_front_left','M_main',[-535,-545,205],[170,135,145],[8,-13,-23],'broad_fold'),
 ('P2_main_front_upper','M_main',[-375,-490,275],[145,145,130],[-17,9,36],'oblique_cap'),
 ('P3_main_top_offset','M_main',[-450,-305,330],[165,145,105],[14,-9,-38],'low_knot'),
 ('P4_main_outer_left','M_main',[-650,-335,185],[130,170,125],[-8,23,57],'oblique_cap'),
 ('P5_main_rear_short','M_main',[-425,-190,215],[140,115,150],[19,11,-61],'broad_fold'),
 ('P6_medium_forward','S_medium_rear_oblique',[-145,-260,225],[115,105,95],[-22,-8,17],'low_knot'),
 ('P7_medium_rear','S_medium_rear_oblique',[-205,-115,155],[90,105,110],[11,20,73],'oblique_cap'),
 ('P8_small_outer','T_small_front_fold',[-170,-500,150],[75,95,85],[-16,12,-47],'low_knot'),
]
def rotate(v,angles):
 x,y,z=v
 a,b,c=[math.radians(t) for t in angles]
 y,z=y*math.cos(a)-z*math.sin(a),y*math.sin(a)+z*math.cos(a)
 x,z=x*math.cos(b)+z*math.sin(b),-x*math.sin(b)+z*math.cos(b)
 x,y=x*math.cos(c)-y*math.sin(c),x*math.sin(c)+y*math.cos(c)
 return x,y,z
for name,parent,center,dims,rotation,profile in shoulders:
 points=[]
 for v in profiles[profile]:
  q=rotate([v[k]*dims[k]/2 for k in range(3)],rotation)
  points.append([center[k]+q[k] for k in range(3)])
 parts[name]={'vertices_blender_m':points,'hull_native':True,'parent_mass':parent,'center_m':center,'design_box_m':dims,'rotation_xyz_degrees':rotation,'profile':profile,'purpose':'Broad short positive shoulder; no narrow bevel, sphere or subtractive pit'}
out={'status':'Authored C design; visual review pending','reference':'ref/1216.png','reference_pixels_viewed':True,'B_five_views_viewed':True,'parts':parts,'macro_vertex_edits':edits,'shoulder_count':8,'macro_cages':3,'random_noise':False,'negative_volume':False,'bevel':False,'sphere_or_ellipsoid_primitives':False,'world_integration':False,'visual_acceptance':False,'construction':'Keep B three-dimensional offsets; lower ten old roof controls by6–25m; add8 positive nonparallel polyhedral shoulders; native union,10m surface sample, two voxel-step relaxation passes, native isotropic retopology. Preserve all editable cages and exact pre-remesh union.'}
(P/'plan52h-c.json').write_text(json.dumps(out,indent=2)+'\n')
print('Authored C plan: 3 adjusted macro cages and8 asymmetric shoulder cages')
