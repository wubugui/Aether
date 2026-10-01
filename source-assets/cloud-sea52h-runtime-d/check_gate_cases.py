"""Offline counterexamples for new named-material/pixel/camera validation rules."""
from pathlib import Path
import copy,json,numpy as np
from validate52h_d_ab import material_proofs,pixel_pair,camera_proof
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
contract=json.loads((P/'temporary-world-comparison-contract.json').read_text());targets=contract['target_paths']
old=json.loads((ROOT/'cloud-evidence/cloudsea52g-cache-diagnostic-v2-front-20261001T091704Z-5rx_5cuu/images/report.json').read_text())
groups=copy.deepcopy(old['live_cloud_bindings']);labels=['1216','A0','A','D','A2']
for group,label in zip(groups,labels):
 group['reference']=label;group['all_initial_material_identities_and_values_exact']=True
 for i,row in enumerate(group['rows']):row['active_material_id']=101+i%3;row['active_material_typed_digest']='fixture-material-'+str(i%3)
cases=[]
def check(label,result):
 cases.append({'case':label,'passed':bool(result)});assert result,label
check('all five exact named sets accepted',material_proofs(groups,targets))
check('missing initialization rejected',not material_proofs(groups[1:],targets))
x=copy.deepcopy(groups);x[3]['reference']='B';check('old B phase name rejected',not material_proofs(x,targets))
x=copy.deepcopy(groups);x[3]['rows'][0]['active_material_id']=999;check('changed original active material rejected',not material_proofs(x,targets))
x=copy.deepcopy(groups);x[4]['rows'][0]['visible']=False;check('hidden part rejected',not material_proofs(x,targets))
x=copy.deepcopy(groups);x[2]['rows'][0]['path']=x[2]['rows'][1]['path'];check('duplicate cloud path rejected',not material_proofs(x,targets))
a=np.zeros((4,4,4),dtype=np.uint8);a[:,:,3]=255;b=a.copy();b[1,2,0]=1
check('one RGB channel residual detected exactly',pixel_pair(a,b,'A','A2')['rgba_exact'] is False and pixel_pair(a,b,'A','A2')['changed_channels']==1)
b=a.copy();b[1,2,3]=254;pair=pixel_pair(a,b,'A','A2');check('alpha-only residual fails all-RGBA equality',pair['rgba_exact'] is False and pair['alpha_changed_pixels']==1)
check('equal all-RGBA arrays accepted',pixel_pair(a,a.copy(),'A','A2')['rgba_exact'] is True)
rows=[{'path':path,'classification':'outside','nearest_surface_m':50,'nearest_triangle_index':1,'actual_world_triangles':1834,'actual_D_resource_bound':True,'D_closed_source_proof_applies':True,'ray_tests':[{'unique_crossings':0,'odd_parity':False} for _ in range(3)]} for path in targets]
cap={'phase':'D','target_camera_geometry':{'phase':'D','complete':True,'boundary_epsilon_m':.025,'ray_hit_dedup_m':.001,'is_ship_or_sphere_clearance_proof':False,'rows':rows,'counts':{'inside':0,'outside':10,'boundary':0,'ambiguous':0},'outside_all_ten_target_volumes':True}}
check('complete outside camera diagnosis accepted',camera_proof(cap,targets))
x=copy.deepcopy(cap);x['target_camera_geometry']['rows'][0]['nearest_surface_m']=.01;check('near-boundary outside claim rejected',not camera_proof(x,targets))
x=copy.deepcopy(cap);x['target_camera_geometry']['rows'][0]['ray_tests'][1]={'unique_crossings':1,'odd_parity':True};check('contradictory parity outside claim rejected',not camera_proof(x,targets))
x=copy.deepcopy(cap);x['target_camera_geometry']['rows'][0]['actual_D_resource_bound']=False;check('original resource masquerading as D rejected',not camera_proof(x,targets))
x=copy.deepcopy(cap);x['target_camera_geometry']['rows'][0]['classification']='inside';x['target_camera_geometry']['rows'][0]['ray_tests']=[{'unique_crossings':1,'odd_parity':True} for _ in range(3)];x['target_camera_geometry']['counts']={'inside':1,'outside':9,'boundary':0,'ambiguous':0};x['target_camera_geometry']['outside_all_ten_target_volumes']=False
check('inside diagnostic remains valid but cannot claim outside',camera_proof(x,targets))
check('inside diagnosis with false outside claim rejected',not camera_proof({**x,'target_camera_geometry':{**x['target_camera_geometry'],'outside_all_ten_target_volumes':True}},targets))
(P/'offline-gate-cases.json').write_text(json.dumps({'all_passed':True,'cases':cases,'no_engine_or_world_run':True,'fixtures_not_actual_runtime_results':True},indent=2)+'\n')
print(json.dumps({'all_passed':True,'cases':len(cases),'no_world_run':True}))
