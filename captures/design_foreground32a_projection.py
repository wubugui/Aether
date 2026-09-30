from pathlib import Path
import json,math,numpy as np
R=Path(__file__).resolve().parents[1]
base=R/'captures/validation_runs/lantern-island-31i-20260908T214100Z-02d75d5cf747426d88e00816dda55bd0/images/night-reference.png.json'
d=json.loads(base.read_text(encoding='utf-8'));c=d['camera'];pitch,yaw,roll=c['rotation'];assert abs(roll)<1e-6
cy,sy=math.cos(yaw),math.sin(yaw);cx,sx=math.cos(pitch),math.sin(pitch)
B=np.array([[cy,sy*sx,sy*cx],[0,cx,-sx],[-sy,cy*sx,cy*cx]])
cam=np.array(c['position']);origin=np.array([-2350,0,-1650]);f=941/(2*math.tan(math.radians(c['fov']/2)))
def project(p):
 x,z,y=p;q=B.T@(origin+np.array([x,y,-z])-cam)
 return [836+f*q[0]/-q[2],470.5-f*q[1]/-q[2]]
def point(px,py,h):
 ray=B@np.array([(px-836)/f,-(py-470.5)/f,-1]);w=cam+ray*((h-cam[1])/ray[1])-origin
 return [float(w[0]),float(-w[2]),float(w[1])]
out={'camera':c,'scope':'Exact current camera projection. Inverse points at chosen heights are authored composition aids, not known original geography.','authored_inverse':[{'pixel':[px,py],'height_m':h,'blender_xy_z':point(px,py,h)} for px,py,h in [(200,785,28),(390,781,29),(475,798,27),(700,850,20),(280,800,30)]], 'current_buildings':[{'position':p['position'],'pixel':project([p['position'][0]+2350,-p['position'][2]-1650,p['position'][1]])} for p in d['placements'] if p.get('island')=='island_a' and p['kind'] in ['lighthouse','keeper_house']]}
p=R/'captures/foreground32a-projection-design.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
