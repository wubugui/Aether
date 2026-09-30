"""Same-world32e A foreground study, preserving the actual31i assembled surroundings."""
from pathlib import Path
import shutil,json
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json
def main():
 root=Path(__file__).resolve().parents[1];prior=root/'captures/validation_runs/lantern-island-31i-20260908T214100Z-02d75d5cf747426d88e00816dda55bd0'
 native=root/'captures/foreground_island_study_32e';check=read_json(native/'native-check.json');plan=read_json(native/'design-plan.json');old=read_json(prior/'images/night-reference.png.json')
 require(check['passed'] and sha256(native/'island_a.blend')==check['source_sha256'] and sha256(native/'island_a.glb')==check['glb_sha256'],'32e native identity or site gate failed')
 with exclusive_lock(root/'captures/.validation-pipeline.lock'):
  run=ValidationRun(root,'foreground-island-32e',False,True);run.manifest.update(scope=plan['scope'],basis_run=prior.name,expected_counts={})
  print('32e RUN '+str(run.directory),flush=True)
  try:
   frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen)
   for name in ['island_a.blend','island_a.glb']:shutil.copy2(native/name,frozen/name)
   for name in ['builder.py','design-plan.json','native-check.json']:shutil.copy2(native/name,frozen/('foreground-32e-'+name))
   shutil.copy2(__file__,frozen/Path(__file__).name)
   p=frozen/'preview.gd';s=p.read_text(encoding='utf-8')
   require('Vector3(-22,0,2)' in s and 'Vector3(19,0,6)' in s,'Source house positions absent')
   s=s.replace('Vector3(-22,0,2)','Vector3(-23,0,-3)').replace('Vector3(19,0,6)','Vector3(-8,0,-19)')
   s=s.replace('Vector3(-23,0,-3))','Vector3(-23,0,-3),PI/2)')
   needle='\t\tfor item in active_tree_locations:';require(needle in s,'Tree selection absent')
   trees=[[x,-y,scale] for x,y,scale in plan['trees_blender_xy_scale']]
   s=s.replace(needle,'\t\tif island_name=="island_a":active_tree_locations='+json.dumps(trees)+'\n'+needle)
   s=s.replace('["day-reference","day-d-front","day-d-back","day-c-front"]','["day-reference","day-a-front","day-a-back","day-a-approach"]')
   start=s.index('\t\telif camera_name=="day-d-front":');end=s.index('\t\tfor i in range(40):',start)
   s=s[:start]+'''\t\telif camera_name=="day-a-front":
\t\t\tcamera.position=islands.island_a.to_global(Vector3(95,65,95));camera.look_at(islands.island_a.to_global(Vector3(-12,16,0)));camera.fov=55
\t\telif camera_name=="day-a-back":
\t\t\tcamera.position=islands.island_a.to_global(Vector3(-95,60,-95));camera.look_at(islands.island_a.to_global(Vector3(-12,16,0)));camera.fov=55
\t\telse:
\t\t\tcamera.position=islands.island_a.to_global(Vector3(48,18,20));camera.look_at(islands.island_a.to_global(Vector3(-10,20,-4)));camera.fov=65
'''+s[end:]
   s=s.replace('report["island_geometry_revision"]="31i"','report["island_geometry_revision"]="32e-A_with_31i-CD"\n\t\treport["island_a_glb_sha256"]=FileAccess.get_sha256(directory.path_join("island_a.glb"))')
   s=s.replace('31i ISLAND VIEWS','32e FOREGROUND VIEWS');p.write_text(s,encoding='utf-8')
   for p in frozen.rglob('*'):
    if p.is_file():run.bind(p)
   run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
   results=[]
   def affected(p):return p.get('island')=='island_a' or p['kind']=='island_a'
   for mode,names in [('night',['night-reference']),('day',['day-reference','day-a-front','day-a-back','day-a-approach'])]:
    image=run.directory/'images'/(names[-1]+'.png');outputs=[]
    for name in names:
     p=image.parent/(name+'.png');outputs.append(Path(str(p)+'.json'))
     if p!=image:outputs.append(p)
    run.stage(mode+'-views',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','1800','--','--label=20l','--study-dir='+str(frozen),'--view=reference-coast-near','--environment='+mode,'--output='+str(image),'--validation-run='+run.run_id,'--study-time=0'],image=image,outputs=outputs)
    for name in names:
     d=read_json(image.parent/(name+'.png.json'));require(d['run_id']==run.run_id and d['island_a_glb_sha256']==check['glb_sha256'],'Actual A model identity mismatch');require(d['world_sha256']==old['world_sha256'],'World changed')
     before=[p for p in old['placements'] if not affected(p)];after=[p for p in d['placements'] if not affected(p)];require(len(before)==len(after),'Unaffected placement count changed')
     maximum=0
     for a,b in zip(before,after):
      require(a['kind']==b['kind'] and a.get('island')==b.get('island'),'Unchanged placement identity mismatch');maximum=max(maximum,max(abs(x-y) for x,y in zip(a['position'],b['position'])))
     require(maximum<.001,'Other regions unexpectedly moved')
     actual=[p for p in d['placements'] if affected(p)];atrees=[p for p in actual if p['kind']=='existing_native_pine']
     buildings=[p for p in actual if p['kind'] in ['lighthouse','keeper_house']];require(len(buildings)==3,'Expected tower and two houses')
     footings=[]
     for site in d['footing_samples']:
      center=site['samples'][4]['position'];matches=[p for p in buildings if abs(p['position'][0]-center[0])+abs(p['position'][2]-center[2])<.02]
      if not matches:continue
      require(len(matches)==1,'Ambiguous building');b=matches[0];expected=-.5 if b['kind']=='lighthouse' else -.65*b['scale'];gaps=[p['gap_m'] for p in site['samples']]
      require(all(g is not None and abs(g-expected)<.1 for g in gaps),'Building support failed: '+str(gaps));footings.append(dict(kind=b['kind'],position=b['position'],scale=b['scale'],gaps=gaps))
     require(len(footings)==3,'Missing actual footing evidence')
     tree_placement_check=dict(expected=trees,actual=atrees,all_expected_present=len(atrees)==len(trees))
     results.append(dict(view=name,unaffected_placement_count=len(after),unaffected_position_delta_m=maximum,affected_placements=actual,footings=footings,tree_placement_check=tree_placement_check))
   report=run.directory/'actual-site-rebuild.json';write_json(report,dict(run_id=run.run_id,views=results,scope='Actual same-version GPU views and limited runtime support samples; no all-reference, full walking or art acceptance.',passed=all(r['tree_placement_check']['all_expected_present'] for r in results)));run.bind(report)
   require(all(r['tree_placement_check']['all_expected_present'] for r in results),'Authored A trees were filtered; inspect actual site report and retain failure')
   run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('32e FOREGROUND GPU READY '+str(run.directory),flush=True)
  except Exception as e:
   run.manifest.update(status='failed',passed=False,error=str(e),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
