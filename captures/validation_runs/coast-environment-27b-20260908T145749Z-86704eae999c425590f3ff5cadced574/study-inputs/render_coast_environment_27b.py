"""Three affected GPU views of27b cloud/water over the fixed26b scene assembly."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json

def main():
    root=Path(__file__).resolve().parents[1]
    prior=root/'captures/validation_runs/village-paving-26b-20260908T143321Z-441bad8ec7bd4024b195dca93cc8bd82'
    require(read_json(prior/'manifest.json')['passed'],'26b basis is not terminal passed')
    sky=root/'captures/coastal_sky_assets_27b';gate=root/'reviews/round-27b-sky-native-check.json'
    check=read_json(gate);require(check['passed'],'27b actual saved sky gate failed')
    for row in check['assets']:
        for ext,key in [('blend','source_sha256'),('glb','glb_sha256')]:require(sha256(sky/(row['asset']+'.'+ext))==row[key],'Sky native/export identity changed')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'coast-environment-27b',False,True)
        run.manifest.update(scope='New Blender27b cloud volumes and spatial cloud lighting/haze; irregular world-space wave normals and view-dependent moon glints over fixed26b native world assembly. Night reference/reverse and day reference. No lighthouse beams, full weather/streaming or whole-reference acceptance.',basis_run=prior.name,expected_counts={})
        try:
            frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen)
            env=frozen/'new-environment27b';shutil.copytree(root/'captures/coast_environment_study_27b',env)
            shutil.copytree(sky,env/'sky-assets');shutil.copy2(gate,env/'sky-assets'/gate.name)
            for p in [Path(__file__),root/'captures/coast_environment_27b.gd',root/'reviews/round-26b-root-evidence.json']:shutil.copy2(p,frozen/p.name)
            preview=(frozen/'preview.gd').read_text(encoding='utf-8')
            require(preview.count('coast_environment_21c.gd')==1,'Environment adapter anchor changed')
            preview=preview.replace('coast_environment_21c.gd','coast_environment_27b.gd').replace('directory.path_join("environment")','directory.path_join("new-environment27b")')
            require(preview.count('var village_report:Dictionary=village_adapter.validate()')==1,'Unchanged paving probe anchor changed')
            preview=preview.replace('var village_report:Dictionary=village_adapter.validate()','var village_report:Dictionary={"unchanged_geometry_basis":"26b","evidence":"round-26b-root-evidence.json","scope":"Roads and ground are byte-identical26b assets; already checked collisions are not resampled for this cloud/water-only edit."}')
            (frozen/'preview.gd').write_text(preview,encoding='utf-8')
            for p in frozen.rglob('*'):
                if p.is_file():run.bind(p)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            for name,view,mode in [('night-reference','reference-coast-near','night'),('night-reverse','island-back','night'),('day-reference','reference-coast-near','day')]:
                output=run.directory/'images'/(name+'.png');report=Path(str(output)+'.json')
                run.stage(name,[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','900','--','--label=20l','--study-dir='+str(frozen),'--view='+view,'--environment='+mode,'--output='+str(output),'--validation-run='+run.run_id],image=output,outputs=[report])
                d=read_json(report);e=d['environment_study']
                require(d['run_id']==run.run_id and d['world_sha256']==run.inputs['res://scenes/world/World.tscn']['sha256'],'Scene identity mismatch')
                require(e['night']==(mode=='night') and len(e['native_sky_assets'])==(8 if mode=='night' else 7),'Actual sky/mode missing')
                require(len(e['material_bindings'])>=5 and (mode!='night' or e['ambient_source']==2),'Environment bindings missing')
            run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('COAST ENVIRONMENT27b READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
