"""Reference analysis: trace lake shore curves into editable metre geometry.

Only shoreline topology is measured. No image colors, UVs or reference image
are exported to the 3D world. Blender triangulates these fixed geographic
curves into independent terrain modules; Godot owns their assembly.
"""
from pathlib import Path
import cv2,numpy as np,math,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
image=cv2.imread(str(ROOT/'assets/reference.jpg'));hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
mask=((hsv[:,:,0]>=91)&(hsv[:,:,0]<=116)&(hsv[:,:,1]>45)&(hsv[:,:,2]>100)).astype('uint8')
mask[:493]=0
mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
count,labels,stats,centers=cv2.connectedComponentsWithStats(mask)
selected=[i for i in range(1,count) if stats[i,4]>5000 and stats[i,0]>300 and stats[i,1]<600]
assert len(selected)==2,[(stats[i].tolist()) for i in selected]
F=941/(2*math.tan(math.radians(25)));pitch=math.radians(-3.5)
def world(p):
    u,v=map(float,p);x=(u-836)/F;y=(470.5-v)/F
    ray=np.array([x,math.cos(pitch)*y+math.sin(pitch),math.sin(pitch)*y-math.cos(pitch)])
    point=np.array([0,145,250])+ray*(-145/ray[1])
    if u>=1670:point[0]+=400 # Lake continues naturally beyond the reference frame.
    return [round(float(point[0]),4),round(float(point[2]),4)]
regions=[];audit=[]
for index,component in enumerate(sorted(selected,key=lambda i:centers[i,0])):
    contours,hierarchy=cv2.findContours((labels==component).astype('uint8'),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    outer=max(range(len(contours)),key=lambda i:cv2.contourArea(contours[i]))
    def curve(i):return cv2.approxPolyDP(contours[i],1.35,True).reshape(-1,2).tolist()
    outline=curve(outer)
    holes=[curve(i) for i in range(len(contours)) if hierarchy[0,i,3]==outer and cv2.contourArea(contours[i])>=16]
    regions.append({'name':['Crownreach Lake','Eastern Lake'][index],'outer':[world(p) for p in outline],'holes':[[world(p) for p in h] for h in holes]})
    audit.append({'name':regions[-1]['name'],'outline_pixels':outline,'islands_pixels':holes,'water_area_pixels':int(stats[component,4])})
(ROOT/'assets/water_geography.json').write_text(json.dumps(regions,indent=2))
(ROOT/'blender/lake_shore_survey.json').write_text(json.dumps({'source_sha256':hashlib.sha256((ROOT/'assets/reference.jpg').read_bytes()).hexdigest(),'method':'Blue-water component contours simplified to 1.35 pixel survey curves; converted once to fixed sea-level metre coordinates. Full terrain volumes built separately.','regions':audit},indent=2))
print('LAKE GEOGRAPHY',[(r['name'],len(r['outer']),len(r['holes'])) for r in regions])
