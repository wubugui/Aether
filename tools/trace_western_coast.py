"""Survey the reference coastline as fixed metre-space geography.

Only the shore's curve is traced. No image or per-pixel color is delivered as
a terrain material. The result changes actual independent terrain geometry.
"""
from pathlib import Path
import json,math,hashlib
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'assets/reference.jpg';image=cv2.imread(str(path));hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
water=((hsv[:,:,0]>=90)&(hsv[:,:,0]<=118)&(hsv[:,:,1]>45)&(hsv[:,:,2]>95)).astype(np.uint8)
water=cv2.morphologyEx(water,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
survey=[]
for y in range(680,941):
    xs=np.flatnonzero(water[y,230:850])+230
    if len(xs)<30:continue
    # The farthest water edge in this near-coast band; the UI and the little
    # offshore island are left of the mainland shore and cannot erase it.
    survey.append([int(xs[-1])+1,y])
curve=cv2.approxPolyDP(np.asarray(survey,np.float32).reshape(-1,1,2),1.5,False).reshape(-1,2)
F=941/(2*math.tan(math.radians(25)));pitch=math.radians(-3.5)
world=[]
for u,v in curve:
    x=(float(u)-836)/F;y=(470.5-float(v))/F
    ray=np.array([x,math.cos(pitch)*y+math.sin(pitch),math.sin(pitch)*y-math.cos(pitch)])
    point=np.array([0,145,250])+ray*(-145/ray[1])
    world.append([float(point[2]),float(point[0])])
world.sort()
art_path=ROOT/'blender/art_layout.json';art=json.loads(art_path.read_text())
coast=[p for p in art['coast'] if p[0]<world[0][0]]+world+[p for p in art['coast'] if p[0]>world[-1][0]]
art['coast']=coast;art['coast_survey_bounds']=[world[0][0],world[-1][0]];art_path.write_text(json.dumps(art,indent=2))
layout_path=ROOT/'assets/world_layout.json';layout=json.loads(layout_path.read_text());layout['coast']=coast;layout['coast_survey_bounds']=art['coast_survey_bounds'];layout_path.write_text(json.dumps(layout,separators=(',',':')))
report={'reference_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pixel_shore_curve':curve.tolist(),
        'world_shore_curve_z_x':world,'scope':'Geometry-only shore survey. Runtime reads metre coordinates, never this image.'}
(ROOT/'blender/western_shore_survey.json').write_text(json.dumps(report,indent=2))
print('WESTERN COAST',len(curve),'control points')
print('SURVEY x at rows 706,773,826,882,920:',[survey[y-680][0] for y in [706,773,826,882,920]])
