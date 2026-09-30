"""One-shot installation of the independently reviewed 19h lighthouse source and prefab."""
from pathlib import Path
import shutil
from validation_manifest import (ValidationRun,exclusive_lock,input_diff,read_json,require,
    sha256,snapshot_inputs,utc_now,write_json)

def main():
    root=Path(__file__).resolve().parents[1]
    candidate=root/'captures/validation_runs/lighthouse-19h-20260908T081136Z-5ae8b9c9b2f2432da9e2c4c3ab60f54f'
    review=root/'reviews/round-19h-lighthouse-independent-review.md'
    audit=root/'reviews/round-19h-lighthouse-independent-audit.json'
    require(review.is_file() and audit.is_file(),'Independent stage review required; read its decision before executing')
    source=candidate/'study-inputs'
    require(read_json(candidate/'manifest.json')['passed'] is True,'Candidate captures incomplete')
    require(sha256(source/'lighthouse.glb')=='79b5fd32ec06a3c3cf0fc948e31333c9d374fb018437f2fa630293e266382eb1','Candidate GLB changed')
    require(sha256(source/'lighthouse.blend')=='10540b562966c58df68f6bd7e5030cb0b5e991d0aceb292a318c88215876f000','Candidate source changed')
    native=root/'blender/settlement_kit/lighthouse.blend'
    require(not native.exists(),'Native lighthouse already installed; do not repeat installation')
    paths=['assets/models/lighthouse.glb','assets/collision/lighthouse.res','assets/meshes/lighthouse.res',
           'scenes/prefabs/lighthouse.tscn','assets/asset_catalog.json','assets/settlement_kit.json']
    baseline=read_json(candidate/'inputs.json')['files']
    for path in paths:
        require(sha256(root/path)==baseline['res://'+path]['sha256'],'Production baseline changed: '+path)
    prefab=(root/paths[3]).read_text()
    for old,new in [('[gd_scene load_steps=5 format=3]','[gd_scene load_steps=4 format=3]'),
            ('[ext_resource type="Material" path="res://materials/world.tres" id="2_ecwqq"]\n',''),
            ('surface_material = ExtResource("2_ecwqq")\n','')]:
        require(prefab.count(old)==1,'Unexpected prefab material contract');prefab=prefab.replace(old,new)
    entry={'name':'lighthouse','path':'assets/models/lighthouse.glb','native_source':'blender/settlement_kit/lighthouse.blend',
           'vertices':2500,'faces':1596,'parts_in_source':225,'export_mesh_nodes':24,'authoring_revision':'19h'}
    catalog=read_json(root/paths[4]);require(sum(x['name']=='lighthouse' for x in catalog)==1,'Catalog identity')
    for item in catalog:
        if item['name']=='lighthouse':item.update(entry)
    kit=read_json(root/paths[5]);require(not any(x['name']=='lighthouse' for x in kit),'Kit already installed');kit.append(entry)
    engine=root/'.tools/godot/Godot_v4.5.1-stable_win64.exe'
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'19h-native-lighthouse',False,True)
        run.manifest.update(scope='Shared lighthouse architecture only: Blender source, material-preserving prefab, full derived mesh/collision, two unchanged placements, seven local GPU views plus opening and 36 gameplay checks. Island/weather/reference completion remains unproven.',
            expected_counts={'game-test':36},candidate_run=str(candidate))
        try:
            before=snapshot_inputs(root,imported=False)
            write_json(run.directory/'preparation-inputs.json',{'run_id':run.run_id,'files':before});run.bind(run.directory/'preparation-inputs.json')
            for path in paths:
                dest=run.directory/'source-backup'/path;dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(root/path,dest);run.bind(dest)
            frozen=run.directory/'preparation';frozen.mkdir()
            for path in [Path(__file__),review,audit,source/'lighthouse.blend',source/'lighthouse.glb',source/'builder.py',source/'model-report.json',
                         root/'captures/native_lighthouse_19.gd',root/'captures/capture_native_lighthouse_19.gd']:
                dest=frozen/path.name;shutil.copy2(path,dest);run.bind(dest)
            shutil.copy2(source/'lighthouse.blend',native)
            shutil.copy2(source/'lighthouse.glb',root/paths[0])
            (root/paths[3]).write_text(prefab,encoding='utf-8',newline='\n')
            write_json(root/paths[4],catalog);write_json(root/paths[5],kit)
            marker='--validation-run='+run.run_id
            run.stage('import',[engine,'--headless','--editor','--path',root,'--import','--quit'])
            output=run.directory/'reports/derived-install.json'
            run.stage('derived-install',[engine,'--path',root,'--script',frozen/'native_lighthouse_19.gd','--quit-after','600','--','--mode=install','--output='+str(output),marker],outputs=[output])
            result=read_json(output)
            require(result['passed'] is True and result['run_id']==run.run_id and result['combined_surfaces']==24,'Derived installation report incomplete')
            changes=input_diff(before,snapshot_inputs(root,imported=False))
            allowed={'res://'+p for p in paths}|{'res://blender/settlement_kit/lighthouse.blend','res://assets/models/lighthouse.glb.import'}
            require(set(changes)<=allowed,'Unexpected production changes: '+str(set(changes)-allowed))
            require(all('res://'+p in changes for p in paths),'A required production resource did not change')
            write_json(run.directory/'preparation-changes.json',changes);run.bind(run.directory/'preparation-changes.json')
            run.inputs=snapshot_inputs(root,imported=True)
            write_json(run.directory/'inputs.json',{'run_id':run.run_id,'frozen_utc':utc_now(),'files':run.inputs})
            run.bind(run.directory/'inputs.json');run.manifest['input_count']=len(run.inputs);run.save()
            output=run.directory/'reports/native-check.json'
            run.stage('native-check',[engine,'--path',root,'--script',frozen/'native_lighthouse_19.gd','--quit-after','600','--','--mode=check','--output='+str(output),marker],outputs=[output])
            result=read_json(output)
            require(result['passed'] is True and result['run_id']==run.run_id and len(result['instances'])==2,'Native report incomplete')
            require(result['model_sha256']==sha256(source/'lighthouse.glb'),'Native model identity mismatch')
            require(result['world_sha256']==before['res://scenes/world/World.tscn']['sha256'],'World placements changed')
            for site,views in [('harbor',('front','back','gallery','context','door')),('remote',('front','door'))]:
                for view in views:
                    output=run.directory/'images'/(site+'-'+view+'.png')
                    run.stage('capture-'+site+'-'+view,[engine,'--path',root,'--script',frozen/'capture_native_lighthouse_19.gd','--','--site='+site,'--view='+view,'--output='+str(output),marker],image=output)
            output=run.directory/'images/opening.png'
            run.stage('capture-opening',[engine,'--path',root,'--','--capture','--view=opening','--output='+str(output),marker],image=output)
            run.stage('game-test',[engine,'--path',root,'--','--game-test',marker],report=root/'captures/game-validation.json')
            run.assert_inputs()
            for path,record in run.manifest['artifacts'].items():require(sha256(run.directory/path)==record['sha256'],'Changed evidence: '+path)
            run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('NATIVE LIGHTHOUSE INTEGRATION PASS '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise

if __name__=='__main__':main()
