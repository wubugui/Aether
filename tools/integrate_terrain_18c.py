"""Install the reviewed ground material without recoloring other world assets."""
from pathlib import Path
import shutil
from validation_manifest import (ValidationRun,exclusive_lock,input_diff,read_json,require,
    sha256,snapshot_inputs,utc_now,write_json)

def replace_once(text,old,new):
    require(text.count(old)==1,'Unexpected source fragment: '+old[:90])
    return text.replace(old,new)

def main():
    root=Path(__file__).resolve().parents[1]
    candidate=root/'captures/validation_runs/terrain-18c-20260908T055452Z-686b396248a042c1900b69a901eb18a3'
    baseline=root/'captures/validation_runs/17e-native-integration-20260908T060301Z-07dc7a9c264c45aab408ab67177a7dfd'
    review=root/'reviews/round-18c-independent-review.md'
    require(read_json(candidate/'manifest.json')['passed'] is True and review.is_file(),'Missing reviewed candidate')
    require(read_json(baseline/'manifest.json')['passed'] is True,'17e baseline incomplete')
    frozen=read_json(baseline/'inputs.json')['files']
    shader=candidate/'study-inputs/terrain.gdshader'
    require(sha256(shader)=='f98fc817bb6c217870144daff7d53a0ecb1da96e29e6b2315a24301aea858384','Candidate shader changed')
    shader_out=root/'scripts/terrain_native.gdshader';material=root/'materials/terrain.tres'
    require(not shader_out.exists() and not material.exists(),'Terrain material already installed')
    tiles=sorted((root/'scenes/terrain').glob('Ground_*.tscn'))
    require(len(tiles)==208,'Expected 208 native ground scenes')
    runtime=root/'scripts/open_world.gd';test=root/'tools/verify_native_terrain_material.gd'
    existing=tiles+[runtime,test]
    for path in existing:
        require(sha256(path)==frozen['res://'+path.relative_to(root).as_posix()]['sha256'],'Source changed: '+str(path))
    updates={}
    for tile in tiles:
        updates[tile]=replace_once(tile.read_text(), 'path="res://materials/world.tres"', 'path="res://materials/terrain.tres"')
    text=replace_once(runtime.read_text(),'const WORLD_MATERIAL = preload("res://materials/world.tres")',
        'const WORLD_MATERIAL = preload("res://materials/world.tres")\nconst TERRAIN_MATERIAL = preload("res://materials/terrain.tres")')
    prefix,body=text.split('func apply_chunk_data(',1)
    body=replace_once(body,'node.material_override = WORLD_MATERIAL','node.material_override = TERRAIN_MATERIAL')
    updates[runtime]=prefix+'func apply_chunk_data('+body
    text=test.read_text()
    text=replace_once(text,'\tvar authored:=StandardMaterial3D.new()',
        '\tvar expected_default:String=fixture.get_node("Terrain/Ground_0_-1").surface_material.resource_path\n\tvar authored:=StandardMaterial3D.new()')
    text=replace_once(text,'normal.surface_material.resource_path=="res://materials/world.tres"',
        'normal.surface_material.resource_path==expected_default')
    text=replace_once(text,'\tvar passed:=checks.all(func(item):return item.passed)',
        '''\tvar defaults_ok:=true
\tfor native_tile in reopened.get_node("Terrain").get_children():
\t\tif native_tile==tile:continue
\t\tdefaults_ok=defaults_ok and native_tile.surface_material.resource_path==expected_default and reopened.first_mesh(native_tile).material_override==native_tile.surface_material
\tchecks.append({"name":"All other native ground tiles retain their selected default material","passed":defaults_ok})
\tvar generated:MeshInstance3D=reopened.apply_chunk_data(Vector2i(200,200),reopened.generate_chunk_data(Vector2i(200,200)))
\tchecks.append({"name":"Generated terrain uses the same native ground material","passed":generated.material_override.resource_path==expected_default})
\tvar rock:MultiMeshInstance3D=reopened.get_node("Vegetation/rock_0_-1")
\tchecks.append({"name":"Non-terrain scatter keeps the separate world material","passed":rock.material_override.resource_path=="res://materials/world.tres"})
\tvar passed:=checks.all(func(item):return item.passed)''')
    text=replace_once(text,'\tmesh=null;stored=null;tile=null;normal=null;',
        '\tvar run_id:="";var requested_output:=""\n\tfor arg in OS.get_cmdline_user_args():\n\t\tif arg.begins_with("--validation-run="):run_id=arg.trim_prefix("--validation-run=")\n\t\tif arg.begins_with("--output="):requested_output=arg.trim_prefix("--output=")\n\treport.run_id=run_id;report.default_material=expected_default;report.native_tiles=208\n\tgenerated=null;rock=null\n\tmesh=null;stored=null;tile=null;normal=null;')
    text=replace_once(text,'\tfor check in checks:print(',
        '\tif not requested_output.is_empty():\n\t\tvar copy:=FileAccess.open(requested_output,FileAccess.WRITE);copy.store_string(JSON.stringify(report,"\\t"));copy.close()\n\tfor check in checks:print(')
    updates[test]=text
    engine=root/'.tools/godot/Godot_v4.5.1-stable_win64.exe'
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'18c-native-material',False,True)
        run.manifest.update(scope='Separate native terrain material on 208 authored tiles and generated terrain; persistence, four GPU views, gameplay and four-direction streaming. No mesh changes or complete visual acceptance.',
            expected_counts={'native-material':7,'game-test':36,'stream-test':4},candidate_run=str(candidate),baseline_run=str(baseline))
        try:
            before=snapshot_inputs(root,imported=False)
            write_json(run.directory/'preparation-inputs.json',{'files':before});run.bind(run.directory/'preparation-inputs.json')
            for path in existing:
                dest=run.directory/'source-backup'/path.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(path,dest);run.bind(dest)
            for path in [Path(__file__),review,shader]:
                dest=run.directory/'preparation'/path.name;dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(path,dest);run.bind(dest)
            shutil.copy2(shader,shader_out)
            material.write_text('[gd_resource type="ShaderMaterial" load_steps=2 format=3]\n[ext_resource type="Shader" path="res://scripts/terrain_native.gdshader" id="1"]\n[resource]\nshader = ExtResource("1")\n')
            for path,value in updates.items():path.write_text(value,encoding='utf-8',newline='\n')
            run.stage('import',[engine,'--headless','--editor','--path',root,'--import','--quit'])
            changes=input_diff(before,snapshot_inputs(root,imported=False))
            write_json(run.directory/'preparation-changes.json',changes);run.bind(run.directory/'preparation-changes.json')
            run.inputs=snapshot_inputs(root,imported=True)
            write_json(run.directory/'inputs.json',{'run_id':run.run_id,'frozen_utc':utc_now(),'files':run.inputs})
            run.bind(run.directory/'inputs.json');run.manifest['input_count']=len(run.inputs);run.save()
            marker='--validation-run='+run.run_id
            for view in ('opening','cliff-side','cliff-back','reverse'):
                output=run.directory/'images'/(view+'.png')
                run.stage('capture-'+view,[engine,'--path',root,'--','--capture','--view='+view,'--output='+str(output),marker],image=output)
            output=run.directory/'reports/native-material.json'
            run.stage('native-material',[engine,'--path',root,'--script','tools/verify_native_terrain_material.gd','--',marker,'--output='+str(output)],outputs=[output])
            result=read_json(output)
            require(result['passed'] is True and len(result['checks'])==7 and all(c['passed'] for c in result['checks']),'Native material checks incomplete')
            require(result['run_id']==run.run_id and result['default_material']=='res://materials/terrain.tres','Wrong material test identity')
            for field,path in [('source_world_sha256','scenes/world/World.tscn'),('runtime_sha256','scripts/open_world.gd')]:
                require(result[field]==run.inputs['res://'+path]['sha256'],'Material test source mismatch')
            run.manifest['stages'][-1].update(report_contract_passed=True,report='reports/native-material.json')
            run.save()
            for name,sink in [('game-test','game-validation.json'),('stream-test','stream-flight-validation.json')]:
                run.stage(name,[engine,'--path',root,'--','--'+name,marker],report=root/'captures'/sink)
            run.assert_inputs()
            require(len(run.manifest['stages'])==8 and all(s['passed'] for s in run.manifest['stages']),'Integration incomplete')
            for path,record in run.manifest['artifacts'].items():require(sha256(run.directory/path)==record['sha256'],'Evidence changed')
            run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('NATIVE TERRAIN MATERIAL PASS '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise

if __name__=='__main__':main()
