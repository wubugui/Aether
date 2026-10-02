#!/usr/bin/env python3
"""Pure Python math, text-parser and source-negative fixtures. Never starts Godot."""
from __future__ import annotations
import copy,gzip,json,math,random,struct,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
from scene_inputs62 import compose,numbers,f32,parse_scene,ref_uri,read_text_multimesh,IDENTITY
from run_scatter62 import source_guards,process_ok,validate_output,raw_sha,encode

CASES=[]
def require(ok,label):
    if not ok:raise RuntimeError(label)
def expect_failure(label,call):
    try:call()
    except (ValueError,RuntimeError,OverflowError,KeyError):CASES.append(label);return
    raise RuntimeError('negative case accepted: '+label)

def buffer_to_columns(buffer):
    require(len(buffer)==12 and all(math.isfinite(x)for x in buffer),'invalid buffer')
    return [buffer[0],buffer[4],buffer[8],buffer[1],buffer[5],buffer[9],buffer[2],buffer[6],buffer[10],buffer[3],buffer[7],buffer[11]]
def point(t,p):return [sum(t[c*3+r]*p[c]for c in range(3))+t[9+r]for r in range(3)]
def box_corners(lo,hi):return [[x,y,z]for x in [lo[0],hi[0]]for y in [lo[1],hi[1]]for z in [lo[2],hi[2]]]
def transformed_bound(t,lo,hi):
    points=[point(t,p)for p in box_corners(lo,hi)];return [min(p[i]for p in points)for i in range(3)],[max(p[i]for p in points)for i in range(3)]
def hits(lo,hi,b):return hi[0]>=b[0]and lo[0]<=b[1]and hi[2]>=b[2]and lo[2]<=b[3]

def main():
    require(compose(IDENTITY,IDENTITY)==IDENTITY,'identity compose');CASES.append('identity compose')
    # Deliberately nonsymmetric: catches mistaken row/column and misplaced origins.
    packed=[2,3,5,101,7,11,13,103,17,19,23,107]
    local=buffer_to_columns(packed);require(point(local,[1,2,3])==[124,171,231],'row12 swizzle');CASES.append('native row12 swizzle')
    require(point(local,[0,0,0])==[101,103,107],'origin slots');CASES.append('native origin slots3/7/11')
    require(buffer_to_columns([1,0,0,0,0,1,0,0,0,0,1,0])==IDENTITY,'identity buffer');CASES.append('identity buffer')
    rng=random.Random(62)
    for index in range(100):
        a=[f32(rng.uniform(-3,3))for _ in range(9)]+[f32(rng.uniform(-6000,6000))for _ in range(3)]
        b=[f32(rng.uniform(-3,3))for _ in range(9)]+[f32(rng.uniform(-100,100))for _ in range(3)]
        lo=[-7,-11,-5];hi=[9,13,17];combined=compose(a,b);blo,bhi=transformed_bound(combined,lo,hi)
        for p in box_corners(lo,hi):
            oracle=point(a,point(b,p))
            require(all(blo[i]-0.005<=oracle[i]<=bhi[i]+0.005 for i in range(3)),'composed corner bound')
        CASES.append('affine reflection scale shear '+str(index))
    # Root lies outside query but model's full transformed bound crosses it.
    t=IDENTITY[:];t[9:]=[-3092,10,-4000];lo,hi=transformed_bound(t,[-10,-2,-10],[10,30,10]);require(not(-3088<=t[9]<=-2000)and hits(lo,hi,[-3088,-2000,-5200,-3730]),'rootpoint false clearance');CASES.append('outside root with overlapping footprint')
    require(hits([-3090,0,-4000],[-3088,10,-3990],[-3088,-2000,-5200,-3730]),'closed boundary');CASES.append('closed boundary touching')
    require(not hits([-3090,0,-4000],[-3088.001,10,-3990],[-3088,-2000,-5200,-3730]),'outside boundary');CASES.append('outside separated boundary')
    for raw in ['Transform3D(1,2)','Transform3D(nan)','Transform3D(inf)','Transform3D(1e999)','Transform3D(0); evil()','Vector3(1,2,3)']:
        expect_failure('reject numeric '+raw,lambda raw=raw:numbers(raw,'Transform3D',12))
    expect_failure('reject float32 overflow',lambda:f32(1e100));expect_failure('reject NaN transform',lambda:compose([float('nan')]+IDENTITY[1:],IDENTITY))
    with tempfile.TemporaryDirectory()as d:
        p=Path(d)/'sample.tscn';text='[gd_scene format=3]\n[ext_resource type="ArrayMesh" path="res://mesh.res" id="mesh"]\n[sub_resource type="MultiMesh" id="mm"]\ntransform_format = 1\nuse_colors = true\nuse_custom_data = true\ninstance_count = 1\nmesh = ExtResource("mesh")\nbuffer = PackedFloat32Array(1,0,0,101,0,1,0,103,0,0,1,107,1,0.5,0.25,1,0.1,0.2,0.3,0.4)\n[node name="Root" type="Node3D"]\n[node name="Child" type="MultiMeshInstance3D" parent="."]\nmultimesh = SubResource("mm")\n'
        p.write_text(text);scene=parse_scene(p,'res://sample.tscn',{'.','Child'},{'mm'});scene['uri']='res://sample.tscn';value=read_text_multimesh('res://sample.tscn::mm',scene);require(value['stride_floats']==20 and value['buffer_float_count']==20 and value['mesh_resource']=='res://mesh.res','text stride20');CASES.append('text RGB custom20 float stride')
        for label,change in [('unknown property',{'mystery':'1'}),('wrong stride',{'instance_count':'2'}),('negative count',{'instance_count':'-1'}),('float count',{'instance_count':'1.0'}),('wrong format',{'transform_format':'0'}),('bad bool',{'use_custom_data':'1'}),('scripted resource',{'script':'ExtResource("mesh")'}),('invalid visible',{'visible_instance_count':'2'})]:
            other=copy.deepcopy(scene);other['subresources']['mm']['properties'].update(change);expect_failure('text '+label,lambda other=other:read_text_multimesh('res://sample.tscn::mm',other))
        p.write_text(text.replace('transform_format = 1','transform_format = 1\ntransform_format = 1'));expect_failure('duplicate selected property',lambda:parse_scene(p,'res://sample.tscn',{'.','Child'},{'mm'}))
        expect_failure('unknown resource reference',lambda:ref_uri('Resource("mesh")',scene))
    terminal={'status':'finished','returncode':0,'timeout_triggered':False,'external_signal':None,'wall_seconds':0.5}
    require(process_ok(terminal,[]),'clean terminal fixture');CASES.append('clean child0 terminal fixture')
    for label,delta in [('child0 launcher exception',{'status':'wrapper_exception','exception':'simulated launcher fault'}),('running child0',{'status':'running'}),('exception with finished status',{'exception':'simulated fault'}),('elapsed over60',{'wall_seconds':60.001}),('elapsed NaN',{'wall_seconds':float('nan')}),('external cancellation',{'external_signal':15}),('timeout flag',{'timeout_triggered':True}),('nonzero child',{'returncode':2}),('missing duration',{'wall_seconds':None})]:
        changed=dict(terminal,**delta);require(not process_ok(changed,[]),'accepted failed terminal '+label);CASES.append(label)
    require(not process_ok(terminal,['SCRIPT ERROR: simulated']),'accepted native log error');CASES.append('native log error fixture')
    inputs=json.loads(gzip.decompress((HERE/'prepared-inputs.json.gz').read_bytes()))
    bound={'min':[0,0,0],'max':[1,1,1]};groups=[];meshes={}
    for source in inputs['groups']:
        saved=source['saved_buffer'];t=source['world_transform_columns']
        transform={'basis_columns':[t[i:i+3]for i in [0,3,6]],'origin':t[9:],'native_variant_hex':struct.pack('<I12f',18,*t).hex()}
        item={k:saved[k]for k in ['instance_count','stride_floats','buffer_float_count','buffer_sha256','mesh_resource','use_colors','use_custom_data','transform_format']}
        item.update(path=source['path'],resource=source['resource'],saved_property_source=source['saved_property_source'],saved_data_complete=True,world_transform=transform,local_model_bounds_including_shadow=bound,saved_empty_group=saved['instance_count']==0,world_bounds_including_shadow=bound if saved['instance_count']else None,shader_deformation_envelope_proved=False,runtime_model_scene_and_collision_proved=False,unsupported_reasons=['Synthetic schema fixture, not native evidence'],instances_overlapping_query=[],query_instance_count=0,design_instance_count=0)
        groups.append(item);meshes[saved['mesh_resource']]={'base_bounds':bound,'combined_bounds_including_shadow':bound,'vertex_payload_bounds_independently_recomputed':False,'undeformed_saved_geometry_only':True}
    fixture={'status':'complete','issues':[],'expected_inputs_sha256':raw_sha(encode(inputs)),'baseline_native_intake_sha256':inputs['baseline_native_intake_sha256'],'design_box':inputs['design_box'],'query_box_with_40m':inputs['query_box_with_40m'],'saved_data_read_complete':True,'saved_affine_bound_mesh_aabbs_complete':True,'saved_group_count':775,'groups':groups,'saved_instance_count':57797,'scene_sources':inputs['scene_sources'],'world_bounds_including_shadow':bound,'mesh_resources':meshes,'material_resources':{},'query_instance_count':0,'design_instance_count':0}
    for key in ['all_occupancy_complete','shader_deformation_envelopes_proved','runtime_generated_entities_proved','road_width_proved','visual_acceptance']:fixture[key]=False
    validate_output(fixture,inputs);CASES.append('complete synthetic schema positive, no native claim')
    for key in ['expected_inputs_sha256','baseline_native_intake_sha256','design_box','query_box_with_40m','world_bounds_including_shadow','mesh_resources','material_resources']:
        broken=dict(fixture);broken.pop(key);expect_failure('native schema missing '+key,lambda broken=broken:validate_output(broken,inputs))
    for key in ['world_transform','local_model_bounds_including_shadow','world_bounds_including_shadow','unsupported_reasons','shader_deformation_envelope_proved']:
        broken=dict(fixture);broken['groups']=list(groups);broken['groups'][0]=dict(groups[0]);broken['groups'][0].pop(key)
        expect_failure('native group schema missing '+key,lambda broken=broken:validate_output(broken,inputs))
    broken=dict(fixture);broken['groups']=list(groups);broken['groups'][0]=dict(groups[0],world_transform={'basis_columns':[[1,0,0],[0,1,0],[0,0,1]],'origin':[999,0,0],'native_variant_hex':groups[0]['world_transform']['native_variant_hex']})
    expect_failure('native node transform changed',lambda:validate_output(broken,inputs))
    code=(HERE/'collect_scatter62.gd').read_text();source_guards(code);CASES.append('native source scope positive')
    for operation in ['get_instance_transform(0)','get_instance_color(0)','get_instance_custom_data(0)','node.instantiate()','node.add_child(x)','ResourceSaver.save(x)','mm.set_buffer(x)','mm.buffer = x','mm.get_aabb()']:
        expect_failure('native source rejects '+operation,lambda operation=operation:source_guards(code+'\nfunc forbidden():\n\t'+operation+'\n'))
    for token in ['mm.buffer','buffer.to_byte_array()','node_transform * local','world * local_box','mm.instance_count*stride','"native_saved_buffer_hash_mismatch"','"native_mesh_binding_mismatch"','"independent_saved_transform_mismatch"','"exact775group_count_mismatch"','"all_occupancy_complete":false','"runtime_generated_entities_proved":false','"shader_deformation_envelopes_proved":false']:
        expect_failure('missing guard '+token,lambda token=token:source_guards(code.replace(token,'REMOVED')))
    return {'status':'passed_python_only','case_count':len(CASES),'cases':CASES,'godot_invoked':False,'native_parse_passed':False,'native_collection_passed':False,'all_occupancy_complete':False}
if __name__=='__main__':print(json.dumps(main(),indent=2))
