"""Scoped native material workflow fix; current default view must stay exact."""
from pathlib import Path
import sys,shutil,json,re
root=Path('D:/test6');sys.path.insert(0,str(root/'tools'))
from validation_manifest import ValidationRun,exclusive_lock,snapshot_inputs,write_json,utc_now,require,sha256
with exclusive_lock(root/'captures/.validation-pipeline.lock'):
 run=ValidationRun(root,'12-native-material-fix',False,True)
 run.manifest['scope']='Preserve native terrain material at World startup. GPU material save/reopen/startup, unchanged default opening, current source game controls. No asset geometry, grade-material or release acceptance.'
 run.manifest['release_validation']=False
 run.manifest['expected_counts']={'game-test':36,'native-material':4}
 shutil.copy2(__file__,run.directory/'scoped-driver.py');run.bind(run.directory/'scoped-driver.py')
 try:
  run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'frozen_utc':utc_now(),'files':run.inputs});run.bind(run.directory/'inputs.json');run.manifest['input_count']=len(run.inputs);run.save()
  engine=root/'.tools/godot/Godot_v4.5.1-stable_win64.exe';marker='--validation-run='+run.run_id
  run.stage('native-material',[engine,'--path',root,'--script','tools/verify_native_terrain_material.gd'])
  match=re.findall(r'NATIVE MATERIAL REPORT (res://[^\r\n]+)',(run.directory/'native-material.log').read_text());require(len(match)==1,'Missing material report')
  report=root/match[0].removeprefix('res://');require(report.resolve().is_relative_to(root/'captures/native_material_checks'),'Unexpected report path')
  stage=run.manifest['stages'][-1];require(report.stat().st_mtime_ns>=stage['started_ns'],'Stale material report');value=json.loads(report.read_text())
  require(value.get('passed') is True and len(value.get('checks',[]))==4 and all(c.get('passed') is True for c in value['checks']),'Incomplete material checks')
  require(len({c['name'] for c in value['checks']})==4,'Duplicate material check')
  require(value['source_world_sha256']==run.inputs['res://scenes/world/World.tscn']['sha256'],'Material fixture uses another World')
  require(value['runtime_sha256']==run.inputs['res://scripts/open_world.gd']['sha256'],'Material fixture uses another runtime')
  destination=run.directory/'reports/native-material.json';destination.parent.mkdir(exist_ok=True);shutil.copy2(report,destination);stage['report']=run.bind(destination);stage['report_contract_passed']=True
  fixture=root/value['saved_fixture'].removeprefix('res://');require(fixture.resolve().is_relative_to(report.parent.resolve()),'Unexpected fixture path');shutil.copy2(fixture,run.directory/'EditedWorld.tscn');run.bind(run.directory/'EditedWorld.tscn');run.save()
  opening=run.directory/'images/opening.png';run.stage('capture-opening',[engine,'--path',root,'--','--capture','--output='+str(opening),marker],image=opening)
  baseline=root/'captures/validation_runs/10l-cliff-terrain-edit-20260905T222858Z-e09be6fff0384003802bf7994a07d749/images/opening.png'
  require(sha256(opening)==sha256(baseline),'Default rendering changed with material ownership fix')
  run.manifest['default_opening_equal_to_10l']={'passed':True,'sha256':sha256(opening),'baseline':str(baseline)};run.save()
  run.stage('game-test',[engine,'--path',root,'--','--game-test',marker],report=root/'captures/game-validation.json')
  run.assert_inputs();require(len(run.manifest['stages'])==3 and all(s['passed'] for s in run.manifest['stages']),'Incomplete native material run')
  for path,record in run.manifest['artifacts'].items():require(sha256(run.directory/path)==record['sha256'],'Changed evidence '+path)
  run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('Native material workflow fix passed. '+str(run.directory),flush=True)
 except Exception as error:
  run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
