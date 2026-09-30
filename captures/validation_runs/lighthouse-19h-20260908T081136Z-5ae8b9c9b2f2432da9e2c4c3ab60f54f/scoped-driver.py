"""Freeze the candidate plus reference identities and capture actual native-world views."""
from pathlib import Path
import shutil, argparse, json
from validation_manifest import ValidationRun,exclusive_lock,require,snapshot_inputs,write_json,utc_now,sha256

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('label',choices=['19a','19b','19c','19d','19e','19f','19g','19h'],default='19a',nargs='?')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'lighthouse-'+args.label,False,True)
        run.manifest.update(scope='Blender lighthouse architecture at existing harbor world placement; four comparison GPU views plus door detail for 19f. No weather, full reference, production integration or gameplay acceptance.',production_modified=False,expected_counts={})
        try:
            frozen=run.directory/'study-inputs';frozen.mkdir()
            for filename in ('lighthouse.blend','lighthouse.glb','builder.py','model-report.json'):
                shutil.copy2(root/'captures'/('lighthouse_study_'+args.label)/filename,frozen/filename);run.bind(frozen/filename)
            if args.label in ('19g','19h'):
                for suffix in ('source-face-check','step-solid-check','export-inspection','footing-probe'):
                    source=root/'reviews'/('round-'+args.label+'-'+suffix+'.json')
                    evidence=json.loads(source.read_text())
                    if suffix in ('source-face-check','step-solid-check'):
                        require(evidence['passed'] and evidence['source_sha256']==sha256(frozen/'lighthouse.blend'),'Invalid native gate')
                    elif suffix=='export-inspection':
                        require(evidence['passed'] and evidence['results'][0]['glb_sha256']==sha256(frozen/'lighthouse.glb'),'Invalid exported geometry gate')
                    else:
                        require(evidence['candidate_sha256']==sha256(frozen/'lighthouse.glb'),'Footing probe belongs to another candidate')
                        require(all(s['gap_m']<=0 for i in evidence['instances'] for s in i['samples']),'Foundation base still above terrain samples')
                        if args.label=='19h':
                            require(all(len(i['tread_samples'])==15 and all(s['gap_m']>0 for s in i['tread_samples']) for i in evidence['instances']),'Tread samples still below terrain')
                    target=frozen/source.name;shutil.copy2(source,target);run.bind(target)
            for source,target in [(root/'captures/preview_lighthouse_19.gd',frozen/'preview.gd'),(Path(__file__),run.directory/'scoped-driver.py')]:
                shutil.copy2(source,target);run.bind(target)
            refs=run.directory/'reference-inputs';refs.mkdir()
            for source in sorted((root/'ref').glob('*.png')):
                shutil.copy2(source,refs/source.name);run.bind(refs/source.name)
            run.inputs=snapshot_inputs(root,imported=True)
            write_json(run.directory/'inputs.json',{'run_id':run.run_id,'frozen_utc':utc_now(),'files':run.inputs})
            run.bind(run.directory/'inputs.json');run.manifest['input_count']=len(run.inputs);run.save()
            engine=root/'.tools/godot/Godot_v4.5.1-stable_win64.exe'
            views=('front','back','gallery','context')+(('door',) if args.label in ('19f','19g','19h') else ())
            for view in views:
                output=run.directory/'images'/(view+'.png');stage='capture-'+view
                run.stage(stage,[engine,'--path',root,'--script',frozen/'preview.gd','--','--view='+view,'--output='+str(output),'--study-dir='+str(frozen),'--validation-run='+run.run_id],image=output)
                model_report=json.loads((frozen/'model-report.json').read_text())
                part_count=model_report.get('export_mesh_nodes',model_report['parts'])
                require(('meshes='+str(part_count)) in (run.directory/(stage+'.log')).read_text(encoding='utf-8',errors='replace'),'Missing candidate parts')
            run.assert_inputs()
            for path,record in run.manifest['artifacts'].items():require(sha256(run.directory/path)==record['sha256'],'Changed evidence '+path)
            run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('LIGHTHOUSE STUDY READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise

if __name__=='__main__':main()
