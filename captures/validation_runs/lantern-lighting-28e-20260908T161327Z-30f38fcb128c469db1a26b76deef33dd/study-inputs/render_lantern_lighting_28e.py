"""Five actual GPU views of world-space lantern optics over the existing27f study."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json
def main():
    root=Path(__file__).resolve().parents[1]
    prior=root/'captures/validation_runs/coast-environment-27f-20260908T152526Z-f1543e06af9f4533a1689edaf5dc0add'
    require(read_json(prior/'manifest.json')['passed'],'27f basis incomplete')
    native=root/'captures/lantern_volume_assets_28a';gate=root/'reviews/round-28a-lantern-native-check.json'
    check=read_json(gate);require(check['passed'],'Saved Blender volume gate failed')
    for row in check['assets']:
        for ext,key in [('blend','source_sha256'),('glb','glb_sha256')]:require(sha256(native/(row['asset']+'.'+ext))==row[key],'Optical asset identity changed')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'lantern-lighting-28e',False,True)
        run.manifest.update(scope='28e fixes unshaded final color routing to ALBEDO; records and requires one actual bound mesh for each beam and halo. Retains explicit scene depth clipping with hardware depth disabled. Exact28a editable Blender control volumes and four fixed beams, warmer lamp glass/core, native spotlight/omni receivers and sampled static light-space occlusion. Existing27f sky/water and26b geometry retained. No production, rotating-beam, warm-water-reflection or full-reference acceptance.',basis_run=prior.name,expected_counts={})
        try:
            frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen)
            optics=frozen/'lantern-optics';shutil.copytree(native,optics)
            shutil.copy2(root/'captures/lantern_volume_28e.gdshader',optics/'lantern_volume.gdshader');shutil.copy2(gate,optics/gate.name)
            for source in [Path(__file__),root/'captures/lantern_lighting_28e.gd']:shutil.copy2(source,frozen/source.name)
            preview=(frozen/'preview.gd').read_text(encoding='utf-8')
            anchor='\t\t_:assert(false)';require(preview.count(anchor)==1,'View anchor changed')
            preview=preview.replace(anchor,'\t\t"lamp-close":camera.position=region.get_node("Lighthouse_island_a").global_position+Vector3(9,23,13);camera.look_at(region.get_node("Lighthouse_island_a").global_position+Vector3(0,19.60,0));camera.fov=45\n\t\t"beam-side":camera.position=region.get_node("Lighthouse_island_a").global_position+Vector3(460,144.6,-170);camera.look_at(region.get_node("Lighthouse_island_a").global_position+Vector3(120,19.6,-220));camera.fov=70\n'+anchor)
            anchor='\tvar village_report:Dictionary={';require(preview.count(anchor)==1,'Optical configure anchor changed')
            preview=preview.replace(anchor,'\tvar lantern_adapter=load(directory.path_join("lantern_lighting_28e.gd")).new()\n\tvar lantern_report:Dictionary=lantern_adapter.configure(game,region,directory.path_join("lantern-optics"),environment_mode=="night")\n'+anchor)
            preview=preview.replace('\treport["site_checks"]=site_checks','\treport["lantern_lighting"]=lantern_report\n\treport["site_checks"]=site_checks')
            (frozen/'preview.gd').write_text(preview,encoding='utf-8')
            for p in frozen.rglob('*'):
                if p.is_file():run.bind(p)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            for name,view,mode in [('night-reference','reference-coast-near','night'),('night-beam-side','beam-side','night'),('night-lamp-close','lamp-close','night'),('night-reverse','island-back','night'),('day-reference','reference-coast-near','day')]:
                output=run.directory/'images'/(name+'.png');report=Path(str(output)+'.json')
                run.stage(name,[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','1200','--','--label=20l','--study-dir='+str(frozen),'--view='+view,'--environment='+mode,'--output='+str(output),'--validation-run='+run.run_id,'--study-time=0'],image=output,outputs=[report])
                d=read_json(report);e=d['lantern_lighting']
                require(d['run_id']==run.run_id and d['world_sha256']==run.inputs['res://scenes/world/World.tscn']['sha256'],'World identity changed')
                require(e['night']==(mode=='night') and len(e['beams'])==(4 if mode=='night' else 0),'Actual beam count/mode failed')
                if mode=='night':
                    require(len(e['lamp_materials'])>=12,'Actual lamp materials missing')
                    require(all(b['occlusion']['rays']==1089 and b['occlusion']['excluded_own_tower_bodies']>=1 for b in e['beams']),'Light-space scene rays incomplete')
            run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('LANTERN LIGHTING28e READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
