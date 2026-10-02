"""Fresh strict H post-save validation and one fixed preview, never a rebuild.

Original failure/source remain immutable. No cleanup, ignore flag, resave,
reframing, pixel edits or claim that the old build succeeded.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import traceback
import bpy

P=Path(__file__).resolve().parent
H=P.parent
ROOT=P.parents[3]

def verified_imports():
    global c,source_checks,datablocks
    frozen=json.loads((P/'preview-preparation-freeze58h.json').read_text())
    for rows in (frozen['files'],frozen['protected_files']):
        for name,row in rows.items():
            path=ROOT/name
            assert path.is_file() and path.stat().st_size==row['bytes'], 'Frozen input missing/size changed: '+name
            digest=hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
            assert digest.hexdigest()==row['sha256'],'Transitive frozen input changed: '+name
    sys.path.insert(0,str(H.parent/'revision-d/native-01'))
    import common58d as c
    source_checks=c.load_pure(H/'source58h.py')
    datablocks=c.load_pure(H.parent/'revision-g/inspection-01/inspect58g.py')


def prerequisites():
    plan=json.loads((P/'preview-plan58h.json').read_text())
    for item in plan['inputs'].values():
        path=ROOT/item['path']
        assert path.is_file() and path.stat().st_size==item['bytes'] and c.sha(path)==item['sha256']
    built=json.loads((ROOT/plan['inputs']['original_build_report']['path']).read_text())
    wrapper=json.loads((ROOT/plan['inputs']['original_wrapper']['path']).read_text())
    assert built['passed'] is False and built['native_identity']['passed'] is False
    assert built['native_identity']['checks']['no_external_data'] is False
    assert all(v is True for k,v in built['native_identity']['checks'].items() if k!='no_external_data')
    assert built['geometry']['passed'] and built['material_and_lighting_unchanged']
    assert all(row['passed'] for row in built['cameras'])
    prior=built['pre_save_datablocks']
    assert prior['image_count']==0 and prior['library_count']==1 and prior['all_strongly_linked_ids']==[]
    library=prior['libraries'][0]
    assert library['name']=='B_staggered_crowns.blend' and library['users']==1
    assert library['direct_id_references']==[] and library['linked_datablock_count']==0
    assert wrapper['passed'] is False and wrapper['actual_wrapper_exit_code']==1
    assert len(wrapper['commands'])==1 and wrapper['commands'][0]['actual_child_exit_code']==1 and wrapper['images']==[]
    assert wrapper['protected_unchanged'] and wrapper['prepared_inputs_unchanged']
    expected=plan['inputs']['source']['sha256']
    assert built['source_sha256']==wrapper['source']['sha256']==expected
    assert built['source_bytes']==wrapper['source']['bytes']==plan['inputs']['source']['bytes']==156243
    return plan,built


def validate_saved_source(state,proof,built):
    """Record each real fresh-open observation before any corresponding gate."""
    validation=dict(stage='Independent post-save full identity validation, not a repaired build result',passed=False,
        original_build_passed=False,original_build_external_data_gate=False,
        original_pre_save_datablocks=built['pre_save_datablocks'],
        original_failure_attribution='Recorded image_count=0, library_count=1; no strongly linked ID. Strict Library-count gate failed.',
        source_saved=False,cleared_or_removed_datablocks=False,world_loaded=False,
        final_geometry_pass=False,visual_acceptance=False)
    state['post_save_validation']=validation
    external=datablocks.inventory()
    validation['pre_render_datablocks']=external
    validation['loaded_subgates']=dict(images_empty=external['image_count']==0,
        libraries_empty=external['library_count']==0,no_strong_library_links=external['all_strongly_linked_ids']==[])
    validation['loaded_failing_subgates']=[k for k,v in validation['loaded_subgates'].items() if not v]
    c.write(proof,state)
    # No cleanup or exception for orphan/provenance Library records.
    assert all(validation['loaded_subgates'].values()),'Strict fresh-open image/Library/strong-link gate failed; no render'
    assert external['no_external_dependency_identified_in_images_libraries_scope']
    frame,settings,config,reference=source_checks.inputs()
    scene=bpy.context.scene;bank=bpy.data.objects[source_checks.rebuild.BANK_NAME]
    identity=source_checks.native_identity(bank)
    keys=('mesh','group_sha256','controls','text_sha256','field_parameters','blend_parameters')
    comparisons={key:identity[key]==built['native_identity'][key] for key in keys}
    validation.update(native_identity=identity,original_recorded_identity_comparisons=comparisons)
    c.write(proof,state)
    assert identity['passed'] and all(identity['checks'].values()) and all(comparisons.values()),'Full saved H native identity mismatch'
    assert identity['mesh']['vertices']==802 and identity['mesh']['triangles']==1600
    original_true_checks={key:value for key,value in built['native_identity']['checks'].items() if key!='no_external_data'}
    assert all(value is True and identity['checks'][key] is True for key,value in original_true_checks.items())
    cameras=source_checks.cameras(scene,bank,frame,settings,reference)
    validation['cameras']=cameras;c.write(proof,state)
    assert cameras==built['cameras'] and all(row['passed'] for row in cameras),'Exact original two-camera proof changed'
    assert next(row for row in cameras if row['name']=='shared-side-back')['minimum_margin']>=.07
    lighting=source_checks.light_material_identity(scene,bank,settings)
    validation['material_and_lighting_unchanged']=lighting
    assert source_checks.SOURCE.stat().st_size<=200000
    validation['passed']=True;c.write(proof,state)


def main():
    if not __debug__:raise RuntimeError('Optimized Python would disable strict gates; refusing execution')
    parser=argparse.ArgumentParser();parser.add_argument('--view',choices=['1216-source-front','shared-side-back'],required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    assert args.out.is_dir() and bpy.app.version[:3]==(4,5,14)
    proof=args.out/(args.view+'-proof.json');image=args.out/('58H-'+args.view+'.png')
    assert not proof.exists() and not image.exists(),'Preserve prior output; no in-place preview retry'
    verified_imports()
    plan,built=prerequisites();source=ROOT/plan['inputs']['source']['path'];before=c.sha(source)
    assert before==plan['inputs']['source']['sha256']
    state=dict(state='running',passed=False,pid=os.getpid(),view=args.view,source_sha256_before=before,
        source_saved=False,rebuilt=False,cleared_or_removed_datablocks=False,original_build_passed=False,
        world_loaded=False,pixels_edited=False,final_geometry_pass=False,visual_acceptance=False)
    c.write(proof,state)
    try:
        state['factory_startup_inventory']=datablocks.inventory();c.write(proof,state)
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
        assert Path(bpy.data.filepath).resolve()==source.resolve()
        validate_saved_source(state,proof,built)
        scene=bpy.context.scene;camera=bpy.data.objects['VIEW58H_'+args.view]
        c.camera_resolution(scene,camera)
        expected=(836,471) if args.view=='1216-source-front' else (836,586)
        assert (scene.render.resolution_x,scene.render.resolution_y)==expected and scene.render.resolution_percentage==100
        assert scene.cycles.samples==8 and not scene.cycles.use_denoising and scene.render.threads==2
        assert not scene.use_nodes and scene.view_settings.view_transform=='Standard'
        scene.render.use_compositing=False;scene.render.use_sequencer=False
        scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
        scene.render.image_settings.color_depth='8';scene.render.filepath=str(image)
        state['renderer']=dict(engine=scene.render.engine,device=scene.cycles.device,threads=scene.render.threads,
            samples=scene.cycles.samples,denoising=False,compositing=False,sequencer=False,resolution=list(expected))
        c.write(proof,state)
        bpy.ops.render.render(write_still=True)
        assert image.exists() and c.sha(source)==before
        state['post_render_datablocks']=datablocks.inventory()
        state['post_render_datablocks_note']='Runtime render-result images are recorded after rendering; not saved to source and not used to rewrite the pre-render gate.'
        state.update(image_sha256=c.sha(image),image_bytes=image.stat().st_size,passed=True)
    except BaseException:
        state['error']=traceback.format_exc();raise
    finally:
        state.update(state='completed',source_sha256_after=c.sha(source),source_unchanged=c.sha(source)==before)
        state['passed']=bool(state['passed'] and state['source_unchanged'])
        c.write(proof,state);print(json.dumps(state,indent=2),flush=True)
    assert state['passed'],'Saved-source preview failed; preserve source and real evidence'


if __name__=='__main__':main()
