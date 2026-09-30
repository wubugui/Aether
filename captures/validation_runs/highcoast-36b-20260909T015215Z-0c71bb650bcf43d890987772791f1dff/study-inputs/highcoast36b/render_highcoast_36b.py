"""Real native high-coast revision in the existing continuous world."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json

def main():
    root=Path(__file__).resolve().parents[1]
    prior=root/'captures/validation_runs/storm-35c-20260909T004220Z-c4392024b9a4475faaff26f81d9cbcab'
    native=root/'captures/highcoast_study_36b';plan=read_json(native/'model-report.json')
    old=read_json(prior/'images/storm-high.png.json')
    require(read_json(prior/'manifest.json')['status']=='passed','Weather parent incomplete')
    require((root/'reviews/36-highcoast-occupancy-intake.md').exists(),'Actual occupancy intake missing')
    for row in plan['native_tiles']:
        for ext in ['blend','glb']:require(sha256(native/(row['name']+'.'+ext))==row[ext+'_sha256'],'Native tile changed')
    names=['alongshore-high','alongshore-low','storm-high','storm-coast-low','estuary-high','shore-low','highcoast-back','south-seam','river-mouth','flight-start','flight-middle','flight-end']
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'highcoast-36b',False,True);print('36b RUN '+str(run.directory),flush=True)
        run.manifest['scope']='Local14 saved-native terrain tiles/collisions, affected actual scatter, same-world12GPU frames including continuous camera traverse. Not reference acceptance.'
        run.manifest['expected_counts']={'native_tiles':14,'fixed_views':9,'flight_frames_captured':3,'flight_steps':65}
        try:
            frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen)
            local=frozen/'highcoast36b';shutil.copytree(native,local)
            shutil.copy2(root/'tools/highcoast_runtime_36b.gd',local/'highcoast_runtime_36b.gd')
            for name in ['36-highcoast-occupancy-intake.md','36-highcoast-occupancy-intake.json','36-terrain-savedmesh-intake.json']:
                shutil.copy2(root/'reviews'/name,local/name)
            shutil.copy2(__file__,local/Path(__file__).name)
            for extra in ['save_highcoast_candidate_36b.gd','candidate_game_36b.gd']:
                shutil.copy2(root/'tools'/extra,local/extra)
            p=frozen/'preview.gd';s=p.read_text(encoding='utf-8')
            anchor='\tgame.get_node("Airship").set_physics_process(false)'
            require(s.count(anchor)==1,'Unexpected preview assembly entry')
            s=s.replace(anchor,anchor+'''\n\tvar highcoast_adapter=load(directory.path_join("highcoast36b/highcoast_runtime_36b.gd")).new()
\tvar highcoast_report:Dictionary=await highcoast_adapter.configure(game,directory.path_join("highcoast36b"),output.get_base_dir())''')
            start=s.index('\tvar views:Array=');end=s.index('\t\tfor i in range(40):',start)
            s=s[:start]+'''\tvar candidate_saver=load(directory.path_join("highcoast36b/save_highcoast_candidate_36b.gd")).new()
\tvar candidate_report:Dictionary=candidate_saver.save_candidate(game,directory.path_join("highcoast36b"),output.get_base_dir())
\tvar views:Array=[
\t\t["alongshore-high",Vector3(-2250,250,-1870),Vector3(-3040,120,-3580),65.,0.],
\t\t["alongshore-low",Vector3(-2400,100,-2310),Vector3(-3300,90,-3990),65.,2.05],
\t\t["storm-high",Vector3(-3000,520,-1250),Vector3(-1100,180,-3000),70.,0.],
\t\t["storm-coast-low",Vector3(-2830,170,-1550),Vector3(-900,150,-2920),60.,0.],
\t\t["estuary-high",Vector3(-3100,250,-2780),Vector3(-2260,75,-3230),70.,0.],
\t\t["shore-low",Vector3(-3190,85,-3040),Vector3(-2640,85,-3520),70.,0.],
\t\t["highcoast-back",Vector3(-1260,520,-3930),Vector3(-2650,140,-3200),70.,0.],
\t\t["south-seam",Vector3(-1810,350,-2150),Vector3(-2070,110,-2780),70.,0.],
\t\t["river-mouth",Vector3(-3120,18,-3190),Vector3(-2630,10,-3160),70.,0.]]
\tvar flight_samples:Array=[]
\tfor step in range(65):
\t\tvar t:float=float(step)/64.
\t\tvar p:Vector3=Vector3(-3100,0,-3190).lerp(Vector3(-1390,0,-3210),t)
\t\tvar actual_height:float=game.get_node("World").terrain_height(p)
\t\tvar direction:=Vector3(1710,0,-20).normalized()
\t\tvar ahead_max:float=actual_height
\t\tfor advance in range(0,241,20):ahead_max=maxf(ahead_max,game.get_node("World").terrain_height(p+direction*float(advance)))
\t\tp.y=ahead_max+65.;camera.position=p;camera.look_at(p+direction*180.+Vector3(0,-15,0));camera.fov=70.
\t\tRenderingServer.global_shader_parameter_set("world_time",t*4.)
\t\tstorm_adapter.sample(camera,t*4.)
\t\tfor i in range(2):await process_frame
\t\tawait RenderingServer.frame_post_draw
\t\tflight_samples.append({"step":step,"position":[p.x,p.y,p.z],"actual_mesh_height":actual_height,"clearance":p.y-actual_height,"ahead_240m_max_mesh_height":ahead_max})
\t\tif step in [0,32,64]:
\t\t\tvar flight_name:String="flight-start" if step==0 else ("flight-middle" if step==32 else "flight-end")
\t\t\tvar target:String=output.get_base_dir().path_join(flight_name+".png")
\t\t\tassert(root.get_texture().get_image().save_png(target)==OK)
\t\t\tvar meta:Dictionary={"run_id":identity,"view":flight_name,"camera":{"position":[p.x,p.y,p.z],"rotation":[camera.rotation.x,camera.rotation.y,camera.rotation.z],"fov":camera.fov},"world_sha256":FileAccess.get_sha256("res://scenes/world/World.tscn"),"highcoast_revision":highcoast_report,"production_modified":false,"scope":"Actual continuous camera traverse following 240m forward terrain envelope, not vehicle input or collision-body replay."}
\t\t\tvar handle:=FileAccess.open(target+".json",FileAccess.WRITE);handle.store_string(JSON.stringify(meta,"  "));handle.close()
\tvar flight_file:=FileAccess.open(output.get_base_dir().path_join("flight-traverse.json"),FileAccess.WRITE);flight_file.store_string(JSON.stringify({"run_id":identity,"samples":flight_samples,"scope":"65 actual rendered camera positions, two process frames per step, new 240m forward mesh envelope+65m. Not gameplay control testing."},"  "));flight_file.close()
\tfor setup in views:
\t\tvar camera_name:String=setup[0]
\t\tcamera.position=setup[1];camera.look_at(setup[2]);camera.fov=setup[3]
\t\tvar view_time:float=setup[4]
\t\tRenderingServer.global_shader_parameter_set("world_time",view_time)
\t\tenvironment_report["sampled_world_time"]=view_time
\t\tvar storm_sample:Dictionary=storm_adapter.sample(camera,view_time)
'''+s[end:]
            s=s.replace('\t\treport["storm_setup"]=storm_setup','\t\treport["storm_setup"]=storm_setup\n\t\treport["highcoast_revision"]=highcoast_report')
            s=s.replace('35c STORM VIEWS','36b HIGHCOAST VIEWS')
            p.write_text(s,encoding='utf-8')
            for p in frozen.rglob('*'):
                if p.is_file():run.bind(p)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            final=run.directory/'images/river-mouth.png';outputs=[final.parent/'highcoast-runtime.json',final.parent/'flight-traverse.json',final.parent/'candidate-scenes.json']
            for name in names:
                p=final.parent/(name+'.png');outputs.append(Path(str(p)+'.json'))
                if p!=final:outputs.append(p)
            run.stage('highcoast-world-views',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','2200','--','--label=20l','--study-dir='+str(frozen),'--view=reference-coast-near','--environment=day','--output='+str(final),'--validation-run='+run.run_id,'--study-time=0'],image=final,outputs=outputs)
            actual=read_json(final.parent/'highcoast-runtime.json')
            require(len(actual['tiles'])==14 and not actual['unresolved'] and not actual['support_failures'],'Actual terrain/scatter assembly failed')
            require(actual['scatter_total_preserved']==54800,'Saved scatter count changed')
            for p in (final.parent/'native-scenes').rglob('*'):
                if p.is_file():run.bind(p)
            for name in names:
                d=read_json(final.parent/(name+'.png.json'));require(d['run_id']==run.run_id,'Wrong run')
                require(d['world_sha256']==old['world_sha256'],'Original world changed')
                require(d['highcoast_revision']['report_sha256']==sha256(final.parent/'highcoast-runtime.json'),'Terrain/scatter report binding wrong')
                if not name.startswith('flight'):
                    require(d['rightcoast_glb_sha256']==old['rightcoast_glb_sha256'] and d['placements']==old['placements'],'Existing coast/island assembly changed')
                    require(d['headland_study']['trees']==old['headland_study']['trees'],'Named33f trees changed')
            flight=read_json(final.parent/'flight-traverse.json');require(len(flight['samples'])==65,'Incomplete traverse')
            require(all(p['clearance']>=64.999 for p in flight['samples']),'Camera ground clearance changed')
            report=run.directory/'actual-highcoast-revision.json';write_json(report,dict(run_id=run.run_id,tile_count=14,scatter_changes=len(actual['scatter_changes']),axis_support_max_error_m=actual['max_axis_support_error_m'],flight_samples=65,candidate_scenes=read_json(final.parent/'candidate-scenes.json'),views=names,passed=True,visual_accepted=False,scope='Native models/collision/saved scatter resources plus same-world camera evidence; not production installed or full reference accepted.'))
            run.bind(report);run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('36b GPU READY '+str(run.directory),flush=True)
        except Exception as e:
            run.manifest.update(status='failed',passed=False,error=str(e),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
