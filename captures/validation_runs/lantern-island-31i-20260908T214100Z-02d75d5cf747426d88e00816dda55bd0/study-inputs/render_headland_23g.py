from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json
def main():
    root=Path(__file__).resolve().parents[1]
    prior=root/'captures/validation_runs/harbor-assembly-22g-20260908T112011Z-00f0a7b4c813446e842b280476463e21'
    gate=root/'reviews/round-23g-headland-native-check.json';require(read_json(gate)['passed'],'Native headland gate failed')
    shore_gate=root/'reviews/round-23g-shore-source-comparison.json'
    require(read_json(shore_gate)['shore_constraint_passed'] and read_json(shore_gate)['shore_max_error']<.001,'Shore design constraint failed')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'headland-assembly-23g',False,True)
        run.manifest.update(scope='Actual GPU views of new closed mainland headland and nine village houses in existing22g coast. No production or whole-reference acceptance.',expected_counts={})
        try:
            frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen)
            source=root/'captures/headland_study_23g';shutil.copytree(source,frozen/'headland')
            for item in read_json(gate)['assets']:
                require(sha256(source/(item['asset']+'.blend'))==item['source_sha256'] and sha256(source/(item['asset']+'.glb'))==item['glb_sha256'],'Native identity changed')
            for p in [root/'captures/headland_runtime_23g.gd',Path(__file__),gate,shore_gate]:shutil.copy2(p,frozen/p.name)
            preview=(frozen/'preview.gd').read_text(encoding='utf-8')
            anchor='\tvar adapter=load(directory.path_join("coast_environment_21c.gd")).new()'
            require(preview.count(anchor)==1,'Environment insertion changed')
            preview=preview.replace(anchor,'\tvar headland_adapter=load(directory.path_join("headland_runtime_23g.gd")).new()\n\theadland_adapter.configure(game,directory,environment_mode=="night",camera,view)\n\tawait physics_frame;await physics_frame;await physics_frame\n\tvar headland_report:Dictionary=headland_adapter.finish()\n'+anchor)
            preview=preview.replace('\t\tharbor_report','\t\tharbor_report')
            preview=preview.replace('\tharbor_report["stone_paths"]["runtime_checks"]=harbor_adapter.path_adapter.validate()','')
            preview=preview.replace('\tharbor_report["boat_ground_samples"]=harbor_adapter.path_adapter.validate_boats(harbor_adapter.root)','')
            preview=preview.replace('\t\t_:assert(false)','\t\t"headland-front","headland-back","headland-bay","headland-seam":pass\n\t\t_:assert(false)')
            preview=preview.replace('report["harbor_study"]=harbor_report','report["harbor_study"]=harbor_report\n\treport["headland_study"]=headland_report')
            (frozen/'preview.gd').write_text(preview,encoding='utf-8')
            for p in frozen.rglob('*'):
                if p.is_file():run.bind(p)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            for name,view,mode in [('night-reference','reference-coast-near','night'),('day-front','headland-front','day'),('day-back','headland-back','day'),('day-bay','headland-bay','day'),('day-seam','headland-seam','day')]:
                output=run.directory/'images'/(name+'.png');report=Path(str(output)+'.json')
                run.stage(name,[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','900','--','--label=20l','--study-dir='+str(frozen),'--view='+view,'--environment='+mode,'--output='+str(output),'--validation-run='+run.run_id],image=output,outputs=[report])
                data=read_json(report);require(data['run_id']==run.run_id and data['world_sha256']==run.inputs['res://scenes/world/World.tscn']['sha256'],'Source identity mismatch')
                head=data['headland_study'];require(len(head['assets'])==10 and len(head['footings'])==9 and len(head['lights'])==9,'Missing headland contents')
                require(all(p['gap_m']<=.005 and p['gap_m']>=-.8 for h in head['footings'] for p in h['samples']),'Headland foundation sample failure')
            run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('HEADLAND STUDY READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
