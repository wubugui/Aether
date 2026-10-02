"""One explicitly authored metric-plane candidate; no search and no engine.

Authoring happens once. design58j.json is the persistent local-plane table;
rebuild never consults metric authoring normals to counteract control edits.
Each tuple is (role, azimuth_deg, plane_inclination_deg, support_m, up_sign).
"""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
# Independent per-cage directions and distances, not a common bevel/ring.
CAGES=[
 ('Main_Crown',[-98,0,766],[145,110,91],-9,
  'Wide irregular high mound; four short sloping crown facets and unequal broad shoulders',[
  ('upper',12,29,72,1),('upper',111,37,74,1),('upper',211,32,77,1),('upper',292,43,81,1),
  ('shoulder',-20,56,116,1),('shoulder',59,64,116,1),('shoulder',136,59,113,1),('shoulder',218,68,130,1),('shoulder',286,53,106,1),
  ('return',25,45,78,-1),('return',124,53,77,-1),('return',216,39,72,-1),('return',307,49,83,-1),('lower_clip',188,23,78,-1)]),
 ('Rear_Crown',[110,45,745],[118,102,83],16,
  'Lower offset mound with skew crest, short upper facets, and unequal inward lower returns',[
  ('upper',-32,38,69,1),('upper',63,27,61,1),('upper',169,42,74,1),('upper',260,34,68,1),
  ('shoulder',18,61,107,1),('shoulder',87,55,96,1),('shoulder',157,69,104,1),('shoulder',241,57,105,1),('shoulder',316,65,99,1),
  ('return',-4,51,70,-1),('return',93,41,66,-1),('return',183,56,80,-1),('return',274,45,72,-1),('lower_clip',304,21,72,-1)]),
 ('Front_Short_Fold',[-59,-79,724],[109,76,63],-17,
  'Buried broad front mound; local shoulder cuts into crowns without a shelf',[
  ('upper',-12,35,48,1),('upper',86,43,52,1),('upper',188,28,46,1),('upper',276,39,53,1),
  ('shoulder',31,54,83,1),('shoulder',111,67,82,1),('shoulder',181,58,92,1),('shoulder',253,62,70,1),('shoulder',328,56,88,1),
  ('return',14,44,55,-1),('return',109,55,50,-1),('return',211,40,57,-1),('return',297,52,47,-1),('lower_clip',244,24,54,-1)]),
 ('Back_Diagonal_Ledge',[21,96,726],[129,66,58],8,
  'Short rear mound with diagonal crown facets; no broad horizontal ledge',[
  ('upper',26,31,48,1),('upper',131,41,49,1),('upper',228,36,53,1),('upper',321,27,46,1),
  ('shoulder',-5,68,111,1),('shoulder',71,57,65,1),('shoulder',150,63,98,1),('shoulder',224,54,100,1),('shoulder',287,66,66,1),
  ('return',36,50,59,-1),('return',143,38,52,-1),('return',236,55,60,-1),('return',329,43,57,-1),('lower_clip',82,22,51,-1)]),
 ('Front_Lower_Buttress',[-111,-31,662],[96,86,67],-12,
  'Raised 32 m and mostly buried: wide attachment with tapered sloping underside',[
  ('upper',-39,42,49,1),('upper',58,33,54,1),('upper',163,29,55,1),('upper',252,38,48,1),
  ('shoulder',2,58,78,1),('shoulder',75,64,75,1),('shoulder',144,53,79,1),('shoulder',230,69,81,1),('shoulder',301,60,75,1),
  ('return',-17,39,51,-1),('return',79,49,53,-1),('return',172,56,59,-1),('return',274,44,49,-1),('lower_clip',225,26,54,-1)]),
 ('Rear_Lower_Buttress',[111,55,691],[94,80,63],19,
  'Raised 26 m and buried independently; short tapered underside without a hanging foot',[
  ('upper',17,28,49,1),('upper',119,39,50,1),('upper',207,43,52,1),('upper',302,34,46,1),
  ('shoulder',-27,66,81,1),('shoulder',46,53,74,1),('shoulder',123,61,75,1),('shoulder',203,57,78,1),('shoulder',281,68,71,1),
  ('return',6,54,54,-1),('return',105,42,49,-1),('return',194,48,57,-1),('return',290,37,50,-1),('lower_clip',144,25,49,-1)]),
 ('Left_Short_Accent',[-205,-30,735],[39,41,32],23,
  'Inward buried accent leaves one small local angular fold',[
  ('upper',22,32,25,1),('upper',149,43,28,1),('upper',268,27,25,1),
  ('shoulder',-14,55,35,1),('shoulder',79,64,35,1),('shoulder',171,58,33,1),('shoulder',255,69,36,1),
  ('return',36,46,27,-1),('return',158,38,28,-1),('return',282,55,27,-1)]),
 ('Right_Short_Accent',[201,30,715],[36,40,31],-26,
  'Inward raised accent leaves only one local side/back fold',[
  ('upper',-27,41,26,1),('upper',101,29,24,1),('upper',232,36,27,1),
  ('shoulder',16,63,32,1),('shoulder',111,54,36,1),('shoulder',198,68,34,1),('shoulder',289,57,33,1),
  ('return',-8,52,27,-1),('return',120,44,28,-1),('return',247,37,26,-1)])]

def main():
 old=json.loads((P.parent/'revision-i/design58i.json').read_text())
 config=dict(candidate='58J',status='One source-only metric-plane design hypothesis; no native or visual acceptance',coordinates='Physical source-local U,V,Y metres; frozen E cameras and source basis; no whole-object fit',tolerances=old['tolerances'],metric_authoring_contract='For original transform x=c+R S q, n_local=S R.T N_metric, d_local=h. Derived once here. Rebuild reads stored local planes only.',controls=[])
 for name,center,scale,yaw,role,table in CAGES:
  theta=math.radians(yaw);R=np.array([[math.cos(theta),-math.sin(theta),0],[math.sin(theta),math.cos(theta),0],[0,0,1.]])
  local=[];authored=[]
  for kind,azimuth,inclination,support,sign in table:
   az=math.radians(azimuth);inc=math.radians(inclination)
   N=np.array([math.sin(inc)*math.cos(az),math.sin(inc)*math.sin(az),sign*math.cos(inc)])
   n=np.asarray(scale)*(R.T@N);local.append([*map(float,n),support])
   authored.append(dict(role=kind,azimuth_degrees=azimuth,inclination_from_horizontal_degrees=inclination,support_metres=support,up_sign=sign,normal_metric_UVY=N.tolist()))
  config['controls'].append(dict(id=name,role=role,center=center,scale=scale,yaw_degrees=yaw,planes=local,metric_authorship=authored))
 out=P/'design58j.json'
 if out.exists():raise RuntimeError('One authored candidate only; never overwrite design')
 out.write_text(json.dumps(config,indent=2)+'\n')
 print(json.dumps(dict(path=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),controls=len(config['controls']),planes=[len(r['planes']) for r in config['controls']],blender_started=False)))
if __name__=='__main__':main()
