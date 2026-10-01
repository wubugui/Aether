from pathlib import Path
import re,json,numpy as np,hashlib
D=Path(__file__).resolve().parent;P=D.parent.parent/'candidates/round40-exclusive-20260930/project'
data=json.loads((D/'native-coast.json').read_text())
N='Ground_-4_-4';target=next(v for v in data['terrain'] if v['node'].endswith('/'+N));tri=np.array(target['faces']).reshape(-1,3,3)
contour=[]
for t in tri:
 for a,b in zip(t,np.roll(t,-1,axis=0)):
  if (a[1]<=0<b[1]) or (b[1]<=0<a[1]):contour.append(a+(b-a)*(-a[1]/(b[1]-a[1])))
contour=np.array(contour);c=contour[(contour[:,2]>=-3010)&(contour[:,2]<=-2760)]
coef=np.polyfit(c[:,2],c[:,0],1);res=c[:,0]-np.polyval(coef,c[:,2]);print('Contour span',c.min(axis=0),c.max(axis=0),'x(z)',coef,'RMS',np.sqrt(np.mean(res**2)),'max',np.max(np.abs(res)))
# The proposed box is an intake envelope, not a blanket editing permission.
box=[-3010,-2660,-3040,-2760]
def hit(m,box=box):
 a,b=m['min'],m['max'];return b[0]>=box[0] and a[0]<=box[1] and b[2]>=box[2] and a[2]<=box[3]
groups={}
for m in data['other_meshes']:
 if hit(m):
  k='/'.join(m['node'].split('/')[:4]);groups.setdefault(k,[]).append(m)
print('Other meshes inside box')
for k,v in groups.items():print(k,len(v),np.array([m['min'] for m in v]).min(axis=0),np.array([m['max'] for m in v]).max(axis=0))
s=(P/'scenes/candidate53d-west/Game53dWest.tscn').read_text();blocks=re.split(r'\n(?=\[(?:node|sub_resource|ext_resource) )',s);resources={}
for b in blocks:
 m=re.match(r'\[sub_resource type="([^"]+)" id="([^"]+)"',b)
 if m:resources[m[2]]=b
scat=[]
for b in blocks:
 h=b.split('\n',1)[0]
 if 'type="MultiMeshInstance3D"' not in h or 'parent="World/Vegetation"' not in h:continue
 tr=re.search(r'transform = Transform3D\(([^)]+)\)',b)
 if tr:
  tm=np.fromstring(tr[1],sep=',');origin=tm[-3:];basis=tm[:9].reshape(3,3).T
 else:origin=np.zeros(3);basis=np.eye(3)
 rid=re.search(r'multimesh = SubResource\("([^"]+)"\)',b)
 if not rid:continue
 rb=resources[rid[1]];cm=re.search(r'instance_count = (\d+)',rb)
 if not cm:continue
 count=int(cm[1]);buf=re.search(r'buffer = PackedFloat32Array\(([^)]+)\)',rb)
 if not buf:continue
 a=np.fromstring(buf[1],sep=',');stride=len(a)//count
 if stride!=12:raise ValueError((h,count,len(a),stride))
 a=a.reshape(count,stride);pos=a[:,[3,7,11]]@basis.T+origin
 idx=np.flatnonzero((pos[:,0]>=box[0])&(pos[:,0]<=box[1])&(pos[:,2]>=box[2])&(pos[:,2]<=box[3]))
 if len(idx):
  name=re.search(r'name="([^"]+)"',h)[1];kind=re.search(r'metadata/asset_kind = "([^"]+)"',b)[1]
  scat.append({'node':'World/Vegetation/'+name,'kind':kind,'group_total':count,'instances_in_box':[{'index':int(i),'position':pos[i].tolist(),'transform_buffer':a[i].tolist()} for i in idx]})
print('scatter in box',sum(len(v['instances_in_box']) for v in scat))
for v in scat:print(v['node'],v['kind'],len(v['instances_in_box']),'of',v['group_total'])
# Exact geometry buffers, not IDs/materials, bind historical47 screenshot to current53 coast.
def geom(fn):
 text=fn.read_text();bks=re.split(r'\n(?=\[(?:node|sub_resource|ext_resource) )',text);rs={};nodes={}
 for b in bks:
  m=re.match(r'\[sub_resource type="ArrayMesh" id="([^"]+)"',b)
  if m:rs[m[1]]=b
  m=re.match(r'\[node name="(Ground_[^"]+)" type="MeshInstance3D" parent="World/Terrain/',b)
  if m:nodes[m[1]]=re.search(r'mesh = (?:SubResource|ExtResource)\("([^"]+)"\)',b)[1]
 out={}
 for k in ['Ground_-4_-4','Ground_-4_-5','Ground_-5_-5','Ground_-5_-6']:
  b=rs[nodes[k]];pieces=[]
  for field in ['aabb','format','index_count','index_data','vertex_count','vertex_data']:
   pieces.append(re.search(r'^"'+field+r'": (.*)$',b,re.M)[1])
  out[k]=hashlib.sha256('\n'.join(pieces).encode()).hexdigest()
 return out
old=geom(P/'scenes/candidate47/Game47.tscn');new=geom(P/'scenes/candidate53d-west/Game53dWest.tscn');print('47->53 geometry equal', {k:old[k]==new[k] for k in old})
out={'proposed_intake_box_xmin_xmax_zmin_zmax':box,'shore_contour_fit':{'x_equals_z_times':float(coef[0]),'plus':float(coef[1]),'rms_x_deviation':float(np.sqrt(np.mean(res**2))),'max_abs_x_deviation':float(np.max(np.abs(res))),'contour_bounds':[c.min(axis=0).tolist(),c.max(axis=0).tolist()]},'other_meshes_in_box':[m for m in data['other_meshes'] if hit(m)],'scatter':scat,'geometry47_sha256':old,'geometry53_sha256':new,'geometry47_53_equal':{k:old[k]==new[k] for k in old}}
(D/'scope.json').write_text(json.dumps(out,indent=2))
