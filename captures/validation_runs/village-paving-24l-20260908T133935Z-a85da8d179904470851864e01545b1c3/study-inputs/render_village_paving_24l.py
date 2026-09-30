from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json
def main():
    root=Path(__file__).resolve().parents[1]
    prior=root/'captures/validation_runs/headland-assembly-23g-20260908T121755Z-4ca247af11bb4af2a7bba06fe2383718'
    source=root/'captures/village_paving_study_24j';gate=root/'reviews/round-24j-village-paving-native-check.json';require(read_json(gate)['passed'],'Paving native gate failed')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'village-paving-24l',False,True);run.manifest.update(scope='Shared native Blender courtyard/paving/contour stairs linking9 houses over24l locally graded actual terrain with original World collision retained. FiveGPU views, limited actual collision and door interface probes. Temporary, no whole reference or production acceptance.',expected_counts={})
        try:
            frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen);shutil.copytree(source,frozen/'village-paving')
            grading=root/'captures/village_grading_study_24l';grading_gate=root/'reviews/round-24l-village-grading-native-check.json'
            graded=read_json(grading/'build-report.json');gcheck=read_json(grading_gate)
            require(graded['passed'] and gcheck['passed'],'Graded headland native gate failed')
            require(sha256(grading/'mainland_headland.blend')==gcheck['source_sha256'] and sha256(grading/'mainland_headland.glb')==gcheck['glb_sha256'],'Graded source identity mismatch')
            shutil.copytree(grading,frozen/'village-grading');shutil.copy2(grading_gate,frozen/grading_gate.name)
            original=frozen/'headland'/'original-23g';original.mkdir()
            for filename in ['mainland_headland.blend','mainland_headland.glb','model-report.json']:shutil.copy2(frozen/'headland'/filename,original/filename)
            for filename in ['mainland_headland.blend','mainland_headland.glb']:shutil.copy2(grading/filename,frozen/'headland'/filename)
            manifest=read_json(frozen/'headland'/'model-report.json')
            for i,asset in enumerate(manifest['assets']):
                if asset['name']=='mainland_headland':
                    manifest['assets'][i]={'name':'mainland_headland','scope':graded['scope'],'parts':len(gcheck['parts']),'vertices':sum(p['vertices'] for p in gcheck['parts']),'polygons':sum(p['polygons'] for p in gcheck['parts']),'source_sha256':gcheck['source_sha256'],'glb_sha256':gcheck['glb_sha256'],'native_closed_solid_check_passed':True,'defects':[],'source_23g_glb_sha256':graded['source_glb_sha256']}
            manifest['label']='23g houses with24l locally graded headland';write_json(frozen/'headland'/'model-report.json',manifest)
            for item in read_json(gate)['assets']:require(sha256(source/(item['asset']+'.blend'))==item['source_sha256'] and sha256(source/(item['asset']+'.glb'))==item['glb_sha256'],'Paving source identity mismatch')
            for p in [root/'captures/village_paving_runtime_24l.gd',Path(__file__),gate]:shutil.copy2(p,frozen/p.name)
            preview=(frozen/'preview.gd').read_text(encoding='utf-8');anchor='\tvar adapter=load(directory.path_join("coast_environment_21c.gd")).new()';require(preview.count(anchor)==1,'Injection anchor changed')
            preview=preview.replace(anchor,'\tvar village_adapter=load(directory.path_join("village_paving_runtime_24l.gd")).new()\n\tvillage_adapter.configure(game,directory,camera,view)\n'+anchor)
            preview=preview.replace('\tfor i in range(40):await process_frame','\tvar village_report:Dictionary=village_adapter.validate()\n\tfor i in range(40):await process_frame')
            preview=preview.replace('\t\t_:assert(false)','\t\t"village-foreground","village-bay","village-door","village-upper":pass\n\t\t_:assert(false)')
            preview=preview.replace('report["headland_study"]=headland_report','report["headland_study"]=headland_report\n\treport["village_paving_study"]=village_report')
            (frozen/'preview.gd').write_text(preview,encoding='utf-8')
            for p in frozen.rglob('*'):
                if p.is_file():run.bind(p)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            for name,view,mode in [('day-foreground','village-foreground','day'),('day-bay','village-bay','day'),('door-junction','village-door','day'),('upper-street','village-upper','day'),('night-reference','reference-coast-near','night')]:
                output=run.directory/'images'/(name+'.png');report=Path(str(output)+'.json')
                run.stage(name,[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','900','--','--label=20l','--study-dir='+str(frozen),'--view='+view,'--environment='+mode,'--output='+str(output),'--validation-run='+run.run_id],image=output,outputs=[report])
                data=read_json(report);village=data['village_paving_study'];require(data['run_id']==run.run_id and data['world_sha256']==run.inputs['res://scenes/world/World.tscn']['sha256'],'Source identity mismatch')
                require(len(village['assets'])==2 and len(village['door_interfaces'])==9,'Missing paving records');require(village['passed'],'Paving collision or door samples failed: '+str(village['failures'][:8]))
                require(all(p['bottom_ground_gap_m']<.01 for p in village['foundation_samples']),'Paving foundation gap')
            run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('VILLAGE PAVING READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
