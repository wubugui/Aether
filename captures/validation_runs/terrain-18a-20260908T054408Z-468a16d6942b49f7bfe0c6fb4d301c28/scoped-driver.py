"""Capture frozen world-coordinate terrain materials on the current native game."""
from pathlib import Path
import argparse
import shutil
from validation_manifest import (
    ValidationRun, exclusive_lock, require, sha256, snapshot_inputs, utc_now, write_json,
)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('label',choices=['18a'])
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'terrain-'+args.label,False,True)
        run.manifest.update(scope='Temporary world-coordinate grass pigment study on native terrain and generated terrain; three raw GPU views. No geometry, source material, gameplay or release acceptance.',
                            production_modified=False,expected_counts={})
        frozen=run.directory/'study-inputs';frozen.mkdir()
        try:
            for source,target in [(root/'captures'/('terrain_grade_'+args.label+'.gdshader'),frozen/'terrain.gdshader'),
                                  (root/'captures/preview_terrain_18.gd',frozen/'preview.gd'),
                                  (Path(__file__),run.directory/'scoped-driver.py')]:
                shutil.copy2(source,target);run.bind(target)
            run.inputs=snapshot_inputs(root,imported=True)
            write_json(run.directory/'inputs.json',{'run_id':run.run_id,'frozen_utc':utc_now(),'files':run.inputs})
            run.bind(run.directory/'inputs.json');run.manifest['input_count']=len(run.inputs);run.save()
            engine=root/'.tools/godot/Godot_v4.5.1-stable_win64.exe'
            for view in ('opening','cliff-side','reverse'):
                output=run.directory/'images'/(view+'.png')
                stage='capture-'+view
                run.stage(stage,[engine,'--path',root,'--script',frozen/'preview.gd','--','--capture',
                    '--view='+view,'--output='+str(output),'--study-dir='+str(frozen),'--validation-run='+run.run_id],image=output)
                require('TERRAIN STUDY MATERIAL APPLIED 208 native tiles' in (run.directory/(stage+'.log')).read_text(encoding='utf-8',errors='replace'),
                        'Study did not positively apply to all native terrain')
            run.assert_inputs()
            require(len(run.manifest['stages'])==3 and all(s['passed'] for s in run.manifest['stages']),'Incomplete study capture')
            for path,record in run.manifest['artifacts'].items():
                require(sha256(run.directory/path)==record['sha256'],'Evidence changed: '+path)
            run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('TERRAIN STUDY READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise

if __name__=='__main__':main()
