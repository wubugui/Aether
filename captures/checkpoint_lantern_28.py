"""Record actual28 GPU/optics evidence only after root has viewed all5 images."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];label=sys.argv[1];run=R/'captures/validation_runs'/sys.argv[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
out=R/'reviews'/('round-'+label+'-root-evidence.json');assert not out.exists()
m=read(run/'manifest.json');assert m['passed'] and m['status']=='passed' and len(m['stages'])==5
for name,row in m['artifacts'].items():assert sha(run/name)==row['sha256'],name
views=[];basis=None
for name in ['night-reference','night-beam-side','night-lamp-close','night-reverse','day-reference']:
    image=run/'images'/(name+'.png');d=read(image.with_suffix('.png.json'));e=d['lantern_lighting']
    assert d['world_sha256']==sha(R/'scenes/world/World.tscn')
    assert len(e['beams'])==(0 if name=='day-reference' else 4)
    depths=np.array([b['occlusion']['axial_depths_m'] for b in e['beams']])
    if len(e['beams']):
        assert depths.shape==(4,1089)
        if basis is None:basis=depths
        assert np.max(np.abs(depths-basis))<1e-4
    views.append({'name':name,'image':str(image.relative_to(R)),'png_sha256':sha(image),'sidecar_sha256':sha(image.with_suffix('.png.json')),'camera':d['camera'],'root_directly_viewed':True,'beams':[{k:b[k] for k in ['tower','position','direction','length_m','far_radius_m','omni_energy','omni_range','spot_energy','spot_angle','spot_shadows']}|{'blocked_rays':b['occlusion']['blocked_rays'],'rays':b['occlusion']['rays'],'excluded_own_tower_bodies':b['occlusion']['excluded_own_tower_bodies']} for b in e['beams']],'lamp_material_surface_count':len(e['lamp_materials'])})
result={'run_id':m['run_id'],'terminal_passed':True,'manifest_sha256':sha(run/'manifest.json'),'binding_count':len(m['artifacts']),'all_artifact_sha256_verified':True,'views':views,'light_space_depths_consistent_between_views':True,'maximum_comparison_tolerance_m':.0001,'scope':'Actual saved5GPU images, frozen input identities, four static collision-sampled angular depth maps, lamp material/node reports.33x33 ray maps are a sampled approximation, not exact thin-object shadow contours. No geometry/contact suite repeated, no full weather/rotation/warm-water reflection proof.','visual_acceptance':False,'production_installed':False,'full_goal_status':'active'}
out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(out),'bindings':len(m['artifacts']),'views':len(views),'blocked_rays':[b['blocked_rays'] for b in views[0]['beams']]},ensure_ascii=False))
