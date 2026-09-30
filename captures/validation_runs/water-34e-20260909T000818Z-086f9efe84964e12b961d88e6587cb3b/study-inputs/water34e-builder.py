from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];O=R/'captures/water_study_34e';assert not O.exists();O.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=R/'captures/validation_runs/water-34d-20260909T000325Z-9d52dcd583c84d04a34254a8eab8e9e3/study-inputs';source=prior/'new-environment27f/open_water.gdshader';s=source.read_text(encoding='utf-8')
for a,b in [('emitter_positions[16]','emitter_positions[80]'),('emitter_dimensions[16]','emitter_dimensions[80]'),('emitter_colors[16]','emitter_colors[80]'),('i<16','i<80'),('emitter_reflection_gain=6.','emitter_reflection_gain=18.')]:
 assert a in s,a;s=s.replace(a,b)
(O/'open_water.gdshader').write_text(s,encoding='utf-8');shutil.copy2(prior/'coast_environment_27f.gd',O/'coast_environment_27f.gd')
runtime=(prior/'water_emitter_reflections_34d.gd').read_text(encoding='utf-8').replace('34d','34e')
runtime=runtime.replace('["NativeLanternLight","VillageWarmLight"]','["NativeLanternLight","VillageWarmLight","HarborWarmLight"]')
runtime=runtime.replace('lights.size()==13','lights.size()==67').replace('resize(16)','resize(80)').replace('.008 if tower else .002','.024 if tower else .006')
runtime=runtime.replace('Actual13 native emission surfaces','Actual67 native emission surfaces').replace('No full scene reflection or all harbor/window emitter coverage.','All54 existing harbor lamps plus9village lamps and4tower cores; window/other scene emission not included. Roughness broadened with explicit radiance gain18; no physical radiometric calibration.')
(O/'water_emitter_reflections_34e.gd').write_text(runtime,encoding='utf-8');shutil.copy2(__file__,O/'builder.py')
(O/'design-plan.json').write_text(json.dumps(dict(label='34e',source=str(source.relative_to(R)),source_sha256=sha(source),shader_sha256=sha(O/'open_water.gdshader'),adapter_source_sha256=sha(prior/'coast_environment_27f.gd'),adapter_sha256=sha(O/'coast_environment_27f.gd'),emitter_runtime_sha256=sha(O/'water_emitter_reflections_34e.gd'),scope='34d expansion to all54 existing harbor lamps +9village flames+4tower cores (67 actualsources). All sizes/emissions from native meshes/materials; angular roughness .024tower/.006lantern, artistic radiance gain18. Static64x32 per-source collision atlas450m extent unchanged. Moon/waves/land/clouds unchanged; no window/full-scene reflection or art acceptance.',production_modified=False,full_reference_accepted=False),indent=2),encoding='utf-8')
d=(R/'tools/render_water_34d.py').read_text(encoding='utf-8').replace('34d','34e').replace("prior=root/'captures/validation_runs/water-34c-20260908T235317Z-847760e1994442d085ed8c6e530e5ce9'", "prior=root/'captures/validation_runs/water-34d-20260909T000325Z-9d52dcd583c84d04a34254a8eab8e9e3'")
# The parent preview already calls its emitter adapter. Rebind that single
# invocation and report; do not insert or calculate another atlas.
start=d.index("   needle='\\tvar village_report:Dictionary='");end=d.index('   # No land or collision revision:',start)
d=d[:start]+'''   s=s.replace('water_emitter_reflections_34d.gd','water_emitter_reflections_34e.gd')
   s=s.replace('34a WATER VIEWS','34e WATER VIEWS')
'''+d[end:]
d=d.replace("d['emitter_reflection']['count']==13 and d['emitter_reflection']['rays']==26624", "d['emitter_reflection']['count']==67 and d['emitter_reflection']['rays']==137216")
d=d.replace('13 actual emission-source approximations','67 actual emission-source approximations')
p=R/'tools/render_water_34e.py';assert not p.exists();p.write_text(d,encoding='utf-8');print('34e prepared')
