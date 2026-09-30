"""Same-world water-only change, real GPU main/near/translated/time views."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json
def main():
 root=Path(__file__).resolve().parents[1];prior=root/'captures/validation_runs/water-34d-20260909T000325Z-9d52dcd583c84d04a34254a8eab8e9e3';native=root/'captures/water_study_34e'
 require(read_json(prior/'manifest.json')['status']=='passed','33f GPU must finish first')
 old=read_json(prior/'images/night-reference.png.json');plan=read_json(native/'design-plan.json')
 require(sha256(native/'open_water.gdshader')==plan['shader_sha256'],'34e source identity')
 with exclusive_lock(root/'captures/.validation-pipeline.lock'):
  run=ValidationRun(root,'water-34e',False,True);print('34e RUN '+str(run.directory),flush=True)
  try:
   frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen)
   require(sha256(frozen/'new-environment27f/open_water.gdshader')==plan['source_sha256'],'Water parent identity')
   shutil.copy2(native/'open_water.gdshader',frozen/'new-environment27f/open_water.gdshader')
   require(sha256(frozen/'coast_environment_27f.gd')==plan['adapter_source_sha256'],'Adapter parent identity');shutil.copy2(native/'coast_environment_27f.gd',frozen/'coast_environment_27f.gd')
   for name in ['builder.py','design-plan.json']:shutil.copy2(native/name,frozen/('water34e-'+name))
   shutil.copy2(__file__,frozen/Path(__file__).name)
   shutil.copy2(native/'water_emitter_reflections_34e.gd',frozen/'water_emitter_reflections_34e.gd')
   p=frozen/'preview.gd';s=p.read_text(encoding='utf-8')
   s=s.replace('water_emitter_reflections_34d.gd','water_emitter_reflections_34e.gd')
   s=s.replace('34a WATER VIEWS','34e WATER VIEWS')
   # No land or collision revision: retain verified33f report as explicitly
   # inherited evidence; do not claim repeated paving samples this round.
   require((frozen/'inherited-33f-coast-runtime.json').exists(),'Inherited33f runtime report missing')
   s=s.replace('var village_report:Dictionary=village_adapter.validate()', 'var village_report:Dictionary={"scope":"34e water material only; unchanged33f land/collision evidence inherited, no repeated paving validation.","inherited_report_sha256":FileAccess.get_sha256(directory.path_join("inherited-33f-coast-runtime.json"))}')
   start=s.index('\tvar views:Array=');end=s.index('\t\tfor i in range(40):',start)
   s=s[:start]+'''\tvar views:Array=["night-reference","night-water-near","night-water-shift","night-time18"] if environment_mode=="night" else ["day-reference"]
\tfor camera_name in views:
\t\tcamera.position=ref_position;camera.rotation=ref_rotation;camera.fov=ref_fov
\t\tvar view_time:float=18. if camera_name=="night-time18" else 0.
\t\tRenderingServer.global_shader_parameter_set("world_time",view_time)
\t\tenvironment_report["sampled_world_time"]=view_time
\t\tif camera_name=="night-water-near":
\t\t\tcamera.position=Vector3(-2330,8,-1740);camera.look_at(Vector3(-2430,3,-1990));camera.fov=70
\t\telif camera_name=="night-water-shift":
\t\t\tcamera.position=ref_position+Vector3(-85,-20,-30)
'''+s[end:]
   s=s.replace('33f RIGHTCOAST VIEWS','34e WATER VIEWS');p.write_text(s,encoding='utf-8')
   for p in frozen.rglob('*'):
    if p.is_file():run.bind(p)
   run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json');results=[]
   for mode,names in [('night',['night-reference','night-water-near','night-water-shift','night-time18']),('day',['day-reference'])]:
    image=run.directory/'images'/(names[-1]+'.png');outputs=[]
    for name in names:
     p=image.parent/(name+'.png');outputs.append(Path(str(p)+'.json'))
     if p!=image:outputs.append(p)
    if mode=='night':outputs.append(image.parent/'actual-emitter-reflection.json')
    run.stage(mode+'-views',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','1800','--','--label=20l','--study-dir='+str(frozen),'--view=reference-coast-near','--environment='+mode,'--output='+str(image),'--validation-run='+run.run_id,'--study-time=0'],image=image,outputs=outputs)
    for name in names:
     d=read_json(image.parent/(name+'.png.json'));require(d['run_id']==run.run_id and d['water_shader_sha256']==plan['shader_sha256'],'Water identity')
     require(d['world_sha256']==old['world_sha256'] and d['rightcoast_glb_sha256']==old['rightcoast_glb_sha256'] and d['placements']==old['placements'],'Unchanged world/coast/placements')
     require(d['headland_study']['trees']==old['headland_study']['trees'],'Named tree placement changed')
     if mode=='night':require(len(d['environment_study']['water_reflection_bindings'])>0 and d['emitter_reflection']['count']==67 and d['emitter_reflection']['rays']==137216,'Actual emitter/moon bindings missing')
     results.append(dict(view=name,camera=d['camera'],time=d['environment_study']['sampled_world_time'],water_shader_sha256=d['water_shader_sha256'],world_and_coast_unchanged=True))
   report=run.directory/'actual-water-revision.json';write_json(report,dict(run_id=run.run_id,views=results,scope='RealGPU water-only main/near/translated/time18/night/day. 67 actual emission-source approximations with finite static collision occlusion; no full scene reflections. Land33f runtime inherited, not repeated.',passed=True));run.bind(report)
   run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('34e GPU READY '+str(run.directory),flush=True)
  except Exception as e:
   run.manifest.update(status='failed',passed=False,error=str(e),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
