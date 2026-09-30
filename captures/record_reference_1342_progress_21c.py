from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
run=root/'captures/validation_runs/coast-environment-21c-20260908T102214Z-b866a4fcb0724d3ba6755f194b342f8b'
data=json.loads((run/'images/night-reference.png.json').read_text(encoding='utf-8'))
manifest=json.loads((run/'manifest.json').read_text(encoding='utf-8'));assert manifest['passed']
record={'reference':'ref/1342.png','reference_sha256':hashlib.sha256((root/'ref/1342.png').read_bytes()).hexdigest(),'status':'in_progress_not_accepted','scope':'Reproducible temporary scene assembly in the same existing World. These candidate assets and environment are not installed in production. No character or HUD reconstruction.','camera':data['camera'],'world_sha256':data['world_sha256'],'environment_study':data['environment_study'],'island_design':{'A':[-2350,0,-1650],'B':[-2700,0,-2200],'C':[-3050,0,-2650],'D':[-2340,0,-1810],'D_asset':'island_c','D_yaw':.55,'geography_note':'Designed candidate placement, not known geography of the original reference game.'},'original_site_checks':data['site_checks'],'frozen_run':str(run.relative_to(root)).replace('\\','/'),'frozen_preview':'study-inputs/preview.gd','native_island_candidate':'captures/lantern_islands_study_20l','native_sky_candidate':'captures/coastal_sky_assets_21b','environment_candidate':'captures/coast_environment_study_21c','outstanding':['Rock cliffs and grass margins still have repetitive terraced forms','Reference right-bank villages, piers and scene boats not built','Warm coastal light chains and true lighthouse beam missing','Moon reflection still has regular crossed wave pattern','Cloud bank composition and silhouette need further refinement','Streaming-safe continuous environment updates and other reference weather states not implemented','Full-scene visual reference acceptance and production integration incomplete']}
out=root/'reviews/reference-view-1342-progress-21c.json';assert not out.exists();out.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print(out)
p=root/'REFERENCE_SCENES.md';s=p.read_text(encoding='utf-8');s+='''

1342首个可复现候选机位已登记 `reviews/reference-view-1342-progress-21c.json`：20l四岛临时装配、21b原生Blender月球/云体、21c真实夜间填光；原始完整参考仍未通过。机位、世界SHA、环境参数、D中心原海面探针和冻结run均已记录，未集成生产。两岸村镇、木码头、场景船、暖光链、灯塔体积束光及自然岛岸/水光仍缺失或需返工。
''';p.write_text(s,encoding='utf-8')
