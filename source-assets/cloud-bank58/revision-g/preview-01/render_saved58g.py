"""New post-save validation + one preview of an unchanged G source.

Does not call the old render()/build(), forge a successful build report, rebuild,
save the .blend, modify old evidence, reframe cameras or postprocess pixels.
"""
import argparse
import json
import hashlib
import os
from pathlib import Path
import sys
import traceback
import bpy

P=Path(__file__).resolve().parent
G=P.parent
ROOT=P.parents[3]
def verified_imports():
    global c,source_checks,datablocks
    frozen=json.loads((P/'preview-preparation-freeze58g.json').read_text())
    for rows in (frozen['files'],frozen['protected_files']):
        for name,row in rows.items():
            path=ROOT/name
            assert path.is_file() and path.stat().st_size==row['bytes']
            digest=hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
            assert digest.hexdigest()==row['sha256'],'Transitive frozen input changed: '+name
    sys.path.insert(0,str(G.parent/'revision-d/native-01'))
    import common58d as c
    source_checks=c.load_pure(G/'source58g.py')
    datablocks=c.load_pure(G/'inspection-01/inspect58g.py')


def prerequisites():
    plan=json.loads((P/'preview-plan58g.json').read_text())
    for item in plan['inputs'].values():
        path=ROOT/item['path'];assert path.is_file() and path.stat().st_size==item['bytes'] and c.sha(path)==item['sha256']
    built=json.loads((ROOT/plan['inputs']['original_build_report']['path']).read_text())
    readback=json.loads((ROOT/plan['inputs']['readback_report']['path']).read_text())
    wrapper=json.loads((ROOT/plan['inputs']['readback_wrapper']['path']).read_text())
    assert built['passed'] is False and built['native_identity']['passed'] is False
    assert built['native_identity']['checks']['no_external_data'] is False
    assert readback['passed'] and readback['source_unchanged'] and readback['source_mesh_matches_original_build'] and readback['controls_match_original_build']
    assert readback['loaded_subgates']==dict(images_empty=True,libraries_empty=True)
    assert not readback['loaded_inventory']['all_strongly_linked_ids']
    assert wrapper['passed'] and wrapper['actual_wrapper_exit_code']==0 and wrapper['child']['actual_exit_code']==0
    expected=plan['inputs']['source']['sha256']
    assert built['source_sha256']==readback['source_sha256_before']==readback['source_sha256_after']==expected
    assert wrapper['source_sha256_before']==wrapper['source_sha256_after']==expected
    return plan,built,readback


def validate_saved_source(plan,built):
    frame,settings,config,reference=source_checks.inputs()
    scene=bpy.context.scene;bank=bpy.data.objects[source_checks.rebuild.BANK_NAME]
    identity=source_checks.native_identity(bank)
    comparisons={key:identity[key]==built['native_identity'][key] for key in ('mesh','group_sha256','controls','text_sha256')}
    assert identity['passed'] and all(identity['checks'].values()) and all(comparisons.values()),'Full saved-source native identity mismatch'
    original_true_checks={key:value for key,value in built['native_identity']['checks'].items() if key!='no_external_data'}
    assert all(value is True and identity['checks'][key] is True for key,value in original_true_checks.items())
    cameras=source_checks.cameras(scene,bank,frame,settings,reference)
    assert cameras==built['cameras'] and all(row['passed'] for row in cameras),'Exact original two-camera proof changed'
    assert next(row for row in cameras if row['name']=='shared-side-back')['minimum_margin']>=.07
    lighting=source_checks.light_material_identity(scene,bank,settings)
    external=datablocks.inventory()
    assert external['image_count']==0 and external['library_count']==0
    assert external['all_strongly_linked_ids']==[] and external['no_external_dependency_identified_in_images_libraries_scope']
    assert source_checks.SOURCE.stat().st_size<=200000
    return dict(stage='Independent post-save full identity validation, not a repaired build result',passed=True,
                native_identity=identity,original_recorded_identity_comparisons=comparisons,cameras=cameras,
                material_and_lighting_unchanged=lighting,pre_render_datablocks=external,
                original_build_passed=built['passed'],original_build_external_data_gate=built['native_identity']['checks']['no_external_data'],
                original_build_separate_trigger_still_unknown=True,source_saved=False,world_loaded=False,
                final_geometry_pass=False,visual_acceptance=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--view',choices=['1216-source-front','shared-side-back'],required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    assert args.out.is_dir() and bpy.app.version[:3]==(4,5,14)
    proof=args.out/(args.view+'-proof.json');image=args.out/('58G-'+args.view+'.png')
    assert not proof.exists() and not image.exists(),'Preserve prior output; no in-place preview retry'
    verified_imports()
    plan,built,readback=prerequisites();source=ROOT/plan['inputs']['source']['path'];before=c.sha(source)
    assert before==plan['inputs']['source']['sha256']
    state=dict(state='running',passed=False,pid=os.getpid(),view=args.view,source_sha256_before=before,
                source_saved=False,rebuilt=False,original_build_passed=False,world_loaded=False,
                pixels_edited=False,final_geometry_pass=False,visual_acceptance=False)
    c.write(proof,state)
    try:
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
        assert Path(bpy.data.filepath).resolve()==source.resolve()
        state['post_save_validation']=validate_saved_source(plan,built);c.write(proof,state)
        scene=bpy.context.scene;camera=bpy.data.objects['VIEW58G_'+args.view]
        c.camera_resolution(scene,camera)
        assert scene.cycles.samples==8 and not scene.cycles.use_denoising and scene.render.threads==2
        assert not scene.use_nodes and scene.view_settings.view_transform=='Standard'
        scene.render.use_compositing=False;scene.render.use_sequencer=False
        scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
        scene.render.image_settings.color_depth='8';scene.render.filepath=str(image)
        state['renderer']=dict(engine=scene.render.engine,device=scene.cycles.device,threads=scene.render.threads,
                               samples=scene.cycles.samples,denoising=False,compositing=False,sequencer=False)
        c.write(proof,state)
        bpy.ops.render.render(write_still=True)
        assert image.exists() and c.sha(source)==before
        state['post_render_datablocks']=datablocks.inventory()
        state['post_render_datablocks_note']='Runtime render-result images are recorded after rendering; they are not saved to the unchanged source and do not rewrite the pre-render gate.'
        state.update(image_sha256=c.sha(image),image_bytes=image.stat().st_size,passed=True)
    except BaseException:
        state['error']=traceback.format_exc();raise
    finally:
        state.update(state='completed',source_sha256_after=c.sha(source),source_unchanged=c.sha(source)==before)
        state['passed']=bool(state['passed'] and state['source_unchanged'])
        c.write(proof,state);print(json.dumps(state,indent=2),flush=True)
    assert state['passed'],'Saved-source preview failed; preserve unchanged source and real evidence'


if __name__=='__main__':main()
