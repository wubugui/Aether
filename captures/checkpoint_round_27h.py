"""Checkpoint27 local progress with the moon-observation correction preserved."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
h=R/'captures/validation_runs/coast-moon-readiness-27h-20260908T153333Z-8b7579b40e2d437a8b1142c3bfdb7403'
g=R/'captures/validation_runs/coast-moon-diagnostic-27g-20260908T153017Z-e0efc52dc9094edc9316da694d642a7f'
f=R/'captures/validation_runs/coast-environment-27f-20260908T152526Z-f1543e06af9f4533a1689edaf5dc0add'
review=read(R/'reviews/round-27h-cloud-water-independent-review.json')
assert all(v['moon_visible_in_saved_png'] for v in review['views'])
assert not review['pixel_readiness_vs_saved_png_conflict']
correction=read(R/'reviews/round-27h-moon-observation-correction.json');assert correction['all_moon_regions_identical']
manifests=[]
for run in [g,h]:
    m=read(run/'manifest.json');assert m['passed'] and m['status']=='passed'
    for name,row in m['artifacts'].items():assert sha(run/name)==row['sha256'],name
    manifests.append({'run_id':m['run_id'],'binding_count':len(m['artifacts']),'all_artifact_sha256_verified':True,'manifest_sha256':sha(run/'manifest.json')})
views=[]
for name in ['night-reference','night-reference-later']:
    p=h/'images'/(name+'.png');d=read(p.with_suffix('.png.json'))
    assert sha(p)==sha(f/'images'/p.name)
    moon=d['sky_mesh_diagnostic']['pixel_readiness'];assert moon['ready'] and moon['bright_samples']==25 and moon['attempt']==0
    im=np.asarray(Image.open(p).convert('RGB'));region=im[120:212,1080:1170]
    assert hashlib.sha256(region.tobytes()).hexdigest()=='a641b1483067ab29f855f3b7773b09e71386c6ae590d97184d220488df1676d6'
    views.append({'image':str(p.relative_to(R)),'png_sha256':sha(p),'exactly_same_as_27f':True,'moon_region_verified_against_saved_png':True,'readiness':moon,'root_directly_viewed':True})
evidence={'scope':'Completed27g/h extra diagnostics and explicit correction of the mistaken missing-moon observation. No engine defect or rendering repair proven.27h PNGs equal27f exactly. Prior27f covers day/reverse;27d covers actual new-cloud rear view.','runs':manifests,'views':views,'correction':'reviews/round-27h-moon-observation-correction.json','independent_review':'reviews/round-27h-cloud-water-independent-review.md','full_reference_accepted':False,'production_installed':False,'goal_status':'active'}
out=R/'reviews/round-27h-root-evidence.json';assert not out.exists();out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
old=R/'reviews/round-27f-moon-missing-input-diagnostic.json';data=read(old)
data['withdrawn_original_scope']=data['scope'];data['scope']='Historical comparison of matching27e/27f moon inputs. The motivating missing-moon observation was incorrect; saved moon pixels are identical. No moon rendering regression is established.'
data['superseded_by']='reviews/round-27h-moon-observation-correction.json';old.write_text(json.dumps(data,indent=2),encoding='utf-8')
d=read(h/'images/night-reference.png.json')
registry={'reference':'ref/1342.png','reference_sha256':sha(R/'ref/1342.png'),'status':'in_progress_not_accepted','scope':'Same continuous original World; temporary scene candidates only. No character or HUD reconstruction.','camera':d['camera'],'world_sha256':d['world_sha256'],'environment_study':d['environment_study'],'current_candidate':{'native_clouds':'captures/coastal_sky_assets_27d','cloud_placement':'captures/coast_environment_study_27c/cloud-layout-27c.json','water_shader':'captures/coast_environment_study_27f/open_water.gdshader','geometry_basis':'reviews/reference-view-1342-progress-26b.json','four_view_run':str(f.relative_to(R)),'two_night_pixel_gate_run':str(h.relative_to(R)),'night_pngs_equal_27f':True,'production_installed':False},'evidence':['reviews/round-27d-root-evidence.json','reviews/round-27f-root-evidence.json','reviews/round-27h-root-evidence.json','reviews/round-27d-cloud-water-independent-review.md','reviews/round-27e-cloud-water-independent-review.md','reviews/round-27h-cloud-water-independent-review.md'],'retained_local_progress':['Round-shoulder editable cloud volumes and visible rear/underside replace pointed27c peaks','Actual world/view/time-dependent water normal study; not physical sea displacement or finished art'],'remaining_reference_failures':['Cloud banks still too similarly spaced/layered; broad flat undersides and older World puff clouds remain','Regular dense horizontal moon glints and repeated bright clumps remain','Warm lighthouse beams and local warm reflections missing','Broad bare shoreline and regular island skirts need detailed Blender rockwork','Working waterfront context and all other reference scenes/weather/flight/streaming/production acceptance unfinished'],'moon_observation_correction':'reviews/round-27h-moon-observation-correction.json','next_visual_priority':'Continue cloud layering/water shape and warm lighthouse beams, then authored main rock coast and all remaining20reference scenes. Do not repeat missing-moon diagnostics; that claim was an observation error.'}
out=R/'reviews/reference-view-1342-progress-27h.json';assert not out.exists();out.write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
notice='''**最新27d云体＋27f水面完成实际GPU及独立限定审查，整体美术仍打回。** 27d三组Blender云/12可编辑体块保留圆肩与真实底面方向；27c尖峰、27d大水斑、27e大三角和27f重复横纹均有失败证据。27d五视图含新云后下方观察，27f四视图含0/18秒，27h仅补两夜图并与27f PNG逐字节相同；全部原生/引擎进程已结束。**先前“月球缺失/等待恢复”是根与初版独立的观察错误，已撤回：27e/f/g/h共7张月区像素完全一致，月球一直存在。** 不再追查这个错误命题。接续 `reviews/round-27-worklog.md`、`reviews/round-27h-moon-observation-correction.json`、修订后的 `reviews/round-27h-cloud-water-independent-review.md` 和 `reviews/reference-view-1342-progress-27h.json`。继续云层/水光/灯塔暖束光、主岩岸和完整20参考范围；27d/e/h均无整图接受。生产仍17e/18c/19h，26b街巷/岸体未改也未重跑。会话Goal已实际读回全部20参考及原图范围，保持active。'''
for path in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
    p=R/path;text=p.read_text(encoding='utf-8');split=text.index('\n')+1
    assert notice not in text;p.write_text(text[:split]+'\n'+notice+'\n'+text[split:],encoding='utf-8')
for path in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
    p=R/path;text=p.read_text(encoding='utf-8');assert notice not in text;p.write_text(text+'\n\n'+notice+'\n',encoding='utf-8')
print(json.dumps({'diagnostic_manifests':manifests,'checkpoint':'reviews/reference-view-1342-progress-27h.json','full_goal':'active'},ensure_ascii=False))
