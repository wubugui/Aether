"""Actual same-world coast revision with truthful retained paving provenance."""
from pathlib import Path
import shutil,json
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json
def main():
 root=Path(__file__).resolve().parents[1];prior=root/'captures/validation_runs/foreground-island-32f-20260908T224143Z-7598ab628ffa40f0a4f20816ba9f05e2';native=root/'captures/rightcoast_study_33e';check=read_json(native/'native-check.json');old=read_json(prior/'images/night-reference.png.json')
 require(check['passed'] and sha256(native/'mainland_headland.blend')==check['source_sha256'] and sha256(native/'mainland_headland.glb')==check['glb_sha256'],'Native identity')
 with exclusive_lock(root/'captures/.validation-pipeline.lock'):
  run=ValidationRun(root,'rightcoast-33e',False,True);print('33e RUN '+str(run.directory),flush=True)
  try:
   frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen)
   for name in ['mainland_headland.blend','mainland_headland.glb']:shutil.copy2(native/name,frozen/'headland'/name)
   for name in ['builder.py','design-plan.json','native-check.json']:shutil.copy2(native/name,frozen/('rightcoast33e-'+name))
   shutil.copy2(__file__,frozen/Path(__file__).name)
   history=frozen/'village-grading/build-report.json';grading=read_json(history)
   parent=read_json(root/'captures/rightcoast_study_33b/native-check.json');require(parent['glb_sha256']==check['immediate_source_glb_sha256'] and parent['immediate_source_glb_sha256']==grading['glb_sha256'],'Actual26b to33b to33e identity mismatch')
   revision=dict(revision='33e',retained_grading_glb_sha256=grading['glb_sha256'],parent_revision_native_check_sha256=sha256(root/'captures/rightcoast_study_33b/native-check.json'),immediate_source_glb_sha256=check['immediate_source_glb_sha256'],immediate_source_blend_sha256=check['immediate_source_blend_sha256'],glb_sha256=check['glb_sha256'],source_sha256=check['source_sha256'],retained_grading_report_sha256=sha256(history),retained_paving_design_sha256=sha256(frozen/'village-paving/paving-design.json'),scope='Retained26b graded support domains with adjacent33e sculpt. Historical report remains unchanged; this record binds the new actual mesh.')
   write_json(frozen/'rightcoast-revision.json',revision);shutil.copy2(root/'captures/rightcoast_study_33b/native-check.json',frozen/'rightcoast-parent-native-check.json')
   p=frozen/'village_paving_runtime_26b.gd';s=p.read_text(encoding='utf-8');needle='\tassert(grading.glb_sha256==FileAccess.get_sha256(folder.path_join("headland/mainland_headland.glb")))';require(needle in s,'Grading contract absent')
   s=s.replace(needle,'''\tvar revision:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("rightcoast-revision.json")))
\tassert(revision.retained_grading_glb_sha256==grading.glb_sha256)
\tassert(revision.parent_revision_native_check_sha256==FileAccess.get_sha256(folder.path_join("rightcoast-parent-native-check.json")))
\tvar parent:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("rightcoast-parent-native-check.json")))
\tassert(parent.glb_sha256==revision.immediate_source_glb_sha256 and parent.immediate_source_glb_sha256==grading.glb_sha256)
\tassert(revision.retained_grading_report_sha256==FileAccess.get_sha256(folder.path_join("village-grading/build-report.json")))
\tassert(revision.retained_paving_design_sha256==FileAccess.get_sha256(folder.path_join("village-paving/paving-design.json")))
\tassert(revision.glb_sha256==FileAccess.get_sha256(folder.path_join("headland/mainland_headland.glb")))''');p.write_text(s,encoding='utf-8')
   p=frozen/'headland_runtime_23g.gd';s=p.read_text(encoding='utf-8')
   s=s.replace('var at:=Vector3(item[0],0,item[1]);var ground:=hit(at)','var at:=Vector3(item[0],0,item[1]);var ground:=hit(at,260)')
   s=s.replace('elif ground.position.y>at.y+.1:','elif absf(ground.position.y-at.y)>.1:').replace('"raised to new terrain"','"refit to current terrain"')
   needle='\t\t\t\tif not ground.is_empty():\n';require(needle in s,'Scatter ground gate absent');s=s.replace(needle,needle+'\t\t\t\t\tground=hit(at,260)\n');p.write_text(s,encoding='utf-8')
   p=frozen/'preview.gd';s=p.read_text(encoding='utf-8');start=s.index('\tvar village_report:Dictionary=');end=s.index('\n',start)
   s=s[:start]+'\tvar village_report:Dictionary=village_adapter.validate()'+s[end:]
   s=s.replace('["day-reference","day-a-front","day-a-back","day-a-approach"]','["day-reference","day-coast-front","day-coast-bay","day-coast-back"]')
   start=s.index('\t\telif camera_name=="day-a-front":');end=s.index('\t\tfor i in range(40):',start)
   s=s[:start]+'''\t\telif camera_name=="day-coast-front":
\t\t\tcamera.position=Vector3(-2301,36,-1808);camera.look_at(Vector3(-2240,10,-1750));camera.fov=62
\t\telif camera_name=="day-coast-bay":
\t\t\tcamera.position=Vector3(-2288,40,-1930);camera.look_at(Vector3(-2224,14,-1873));camera.fov=62
\t\telse:
\t\t\tcamera.position=Vector3(-2103,110,-1710);camera.look_at(Vector3(-2200,30,-1840));camera.fov=65
'''+s[end:]
   s=s.replace('\t\treport["headland_study"]=headland_report','\t\treport["headland_study"]=headland_report\n\t\treport["rightcoast_glb_sha256"]=FileAccess.get_sha256(directory.path_join("headland/mainland_headland.glb"))')
   s=s.replace('32f FOREGROUND VIEWS','33e RIGHTCOAST VIEWS');p.write_text(s,encoding='utf-8')
   for p in frozen.rglob('*'):
    if p.is_file():run.bind(p)
   run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json');results=[]
   for mode,names in [('night',['night-reference']),('day',['day-reference','day-coast-front','day-coast-bay','day-coast-back'])]:
    image=run.directory/'images'/(names[-1]+'.png');outputs=[]
    for name in names:
     p=image.parent/(name+'.png');outputs.append(Path(str(p)+'.json'))
     if p!=image:outputs.append(p)
    run.stage(mode+'-views',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','1800','--','--label=20l','--study-dir='+str(frozen),'--view=reference-coast-near','--environment='+mode,'--output='+str(image),'--validation-run='+run.run_id,'--study-time=0'],image=image,outputs=outputs)
    for name in names:
     d=read_json(image.parent/(name+'.png.json'));require(d['run_id']==run.run_id and d['rightcoast_glb_sha256']==check['glb_sha256'],'Actual coast identity mismatch');require(d['world_sha256']==old['world_sha256'],'World changed');require(d['placements']==old['placements'],'Unchanged islands/placements moved')
     village=d['village_paving_study'];require(village['passed'],'Actual paving collision checks failed')
     houses=d['headland_study'];before=old['headland_study'];require(len(houses['trees'])==len(before['trees']),'Headland tree count changed')
     errors=[abs(x['gap_m']-y['gap_m']) for a,b in zip(houses['footings'],before['footings']) for x,y in zip(a['samples'],b['samples'])];require(len(errors)==81 and max(errors)<.002,'Existing house support changed')
     results.append(dict(view=name,house_footing_delta_m=max(errors),actual_trees=len(houses['trees']),tree_max_height_change_m=max(abs(a['position'][1]-b['position'][1]) for a,b in zip(houses['trees'],before['trees'])),paving_passed=village['passed'],paver_samples=len(village['paver_collision_samples']),islands_unchanged=True))
   report=run.directory/'actual-coast-rebuild.json';write_json(report,dict(run_id=run.run_id,views=results,scope='Same-version real GPU views, 81house probes and actual paving centroids/door interfaces, actual trees refit. No full art/all-reference acceptance.',passed=True));run.bind(report)
   run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('33e GPU READY '+str(run.directory),flush=True)
  except Exception as e:
   run.manifest.update(status='failed',passed=False,error=str(e),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
