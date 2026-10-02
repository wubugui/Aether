"""Pure Python control-flow fixtures; no bpy import or native source opening.

These test fail-closed orchestration using recorded identity data. They do not
validate Blender itself and cannot substitute for an actual saved-source read.
"""
import ast
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

P=Path(__file__).resolve().parent;ROOT=P.parents[3]

def main():
    if not __debug__:raise RuntimeError('Unoptimized Python required')
    target=P/'render_saved58h.py';out=P/'validation-flow-tests58h.json'
    assert not out.exists(),'Keep the earlier test evidence'
    tree=ast.parse(target.read_bytes())
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='validate_saved_source')
    module=ast.Module(body=[fn],type_ignores=[])
    plan=json.loads((P/'preview-plan58h.json').read_text())
    built=json.loads((ROOT/plan['inputs']['original_build_report']['path']).read_text())
    base_identity=deepcopy(built['native_identity']);base_identity['passed']=True;base_identity['checks']['no_external_data']=True
    base_external=deepcopy(built['pre_save_datablocks'])
    base_external.update(image_count=0,library_count=0,images=[],libraries=[])
    tests=[]
    cases=['valid_synthetic_post_save','nonempty_images','orphan_library_record','strong_linked_id',
        'mesh_signature_changed','group_weights_changed','control_transform_changed','embedded_text_changed',
        'field_parameters_changed','blend_parameters_changed','native_subgate_false','camera_projection_changed',
        'lighting_failure']
    for case in cases:
        identity=deepcopy(base_identity);external=deepcopy(base_external);cameras=deepcopy(built['cameras'])
        if case=='nonempty_images':external['image_count']=1
        if case=='orphan_library_record':external['library_count']=1;external['libraries']=deepcopy(built['pre_save_datablocks']['libraries'])
        if case=='strong_linked_id':external['all_strongly_linked_ids']=[dict(name='fixture',type='Mesh')]
        if case=='mesh_signature_changed':identity['mesh']['vertices_sha256']='changed'
        if case=='group_weights_changed':identity['group_sha256']='changed'
        if case=='control_transform_changed':identity['controls'][0]['location'][0]+=1
        if case=='embedded_text_changed':identity['text_sha256'][next(iter(identity['text_sha256']))]='changed'
        if case=='field_parameters_changed':identity['field_parameters']['fixture']=True
        if case=='blend_parameters_changed':identity['blend_parameters'][0]['width_m']+=1
        if case=='native_subgate_false':identity['checks']['no_modifiers']=False;identity['passed']=False
        if case=='camera_projection_changed':cameras[0]['projection'][0][0]+=1
        calls=[];writes=[]
        def inputs():calls.append('inputs');return None,None,None,None
        def native(bank):calls.append('native_identity');return identity
        def check_cameras(*args):calls.append('cameras');return cameras
        def lighting(*args):
            calls.append('lighting')
            if case=='lighting_failure':raise AssertionError('Synthetic light failure')
            return True
        namespace=dict(c=SimpleNamespace(write=lambda path,state:writes.append(deepcopy(state))),
            datablocks=SimpleNamespace(inventory=lambda:external),
            source_checks=SimpleNamespace(inputs=inputs,rebuild=SimpleNamespace(BANK_NAME='bank'),
                native_identity=native,cameras=check_cameras,light_material_identity=lighting,
                SOURCE=ROOT/plan['inputs']['source']['path']),
            bpy=SimpleNamespace(context=SimpleNamespace(scene=object()),data=SimpleNamespace(objects={'bank':object()})))
        exec(compile(module,str(target),'exec'),namespace)
        state={};error=None
        try:namespace['validate_saved_source'](state,None,built)
        except AssertionError as exc:error=str(exc)
        expected_pass=case=='valid_synthetic_post_save'
        actual_pass=error is None and state['post_save_validation']['passed']
        assert actual_pass==expected_pass,case
        assert writes and 'pre_render_datablocks' in writes[0]['post_save_validation']
        if case in ('nonempty_images','orphan_library_record','strong_linked_id'):assert calls==[],case
        if not expected_pass:assert state['post_save_validation']['passed'] is False
        tests.append(dict(case=case,expected_acceptance=expected_pass,observed_acceptance=actual_pass,
            passed=True,observed_helper_calls=calls,persisted_observation_count=len(writes),error=error))
    result=dict(status='Pure mocked validation control-flow fixtures passed; not native readback or render',passed=True,
        checked_at_utc=datetime.now(timezone.utc).isoformat(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        validator_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),tests=tests,test_count=len(tests),
        native_execution=False,world_loaded=False,visual_acceptance=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
