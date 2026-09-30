"""Actual same-world coastal storm views, using independently saved Blender clouds."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json

def main():
    root=Path(__file__).resolve().parents[1]
    prior=root/'captures/validation_runs/water-34e-20260909T000818Z-086f9efe84964e12b961d88e6587cb3b'
    native=root/'captures/storm_study_35c'
    plan=read_json(native/'design-plan.json')
    require(read_json(prior/'manifest.json')['status']=='passed','Previous world run must be terminal')
    for name,h in plan['files_sha256'].items():require(sha256(native/name)==h,'35c native changed: '+name)
    old=read_json(prior/'images/day-reference.png.json')
    names=['storm-high','storm-coast-low','storm-inside','storm-edge','storm-clear','storm-flash','storm-inside-flash','storm-cloud-back']
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'storm-35c',False,True)
        print('35c RUN '+str(run.directory),flush=True)
        try:
            frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen)
            weather=frozen/'storm35c';shutil.copytree(native,weather)
            for p in native.glob('*.gdshader'):
                if (frozen/'new-environment27f'/p.name).exists():shutil.copy2(p,frozen/'new-environment27f'/p.name)
            shutil.copy2(__file__,frozen/Path(__file__).name)
            p=frozen/'preview.gd';s=p.read_text(encoding='utf-8')
            anchor='\tvar village_report:Dictionary='
            start=s.index(anchor)
            s=s[:start]+'''\tvar storm_adapter=load(directory.path_join("storm35c/storm_front_35c.gd")).new()
\tvar storm_setup:Dictionary=storm_adapter.configure(game,directory.path_join("storm35c"))
'''+s[start:]
            start=s.index('\tvar views:Array=');end=s.index('\t\tfor i in range(40):',start)
            s=s[:start]+'''\tvar views:Array=[
\t\t["storm-high",Vector3(-3000,520,-1250),Vector3(-1100,180,-3000),70.,0.],
\t\t["storm-coast-low",Vector3(-2830,170,-1550),Vector3(-900,150,-2920),60.,0.],
\t\t["storm-inside",Vector3(-3700,330,-2500),Vector3(-3300,160,-5100),70.,0.],
\t\t["storm-edge",Vector3(-2350,330,-2500),Vector3(-1950,160,-5100),70.,0.],
\t\t["storm-clear",Vector3(-1600,330,-2500),Vector3(-1200,160,-5100),70.,0.],
\t\t["storm-flash",Vector3(-3000,520,-1250),Vector3(-1100,180,-3000),70.,2.04],
\t\t["storm-inside-flash",Vector3(-3700,330,-2500),Vector3(-3300,160,-5100),70.,2.04],
\t\t["storm-cloud-back",Vector3(-6900,2000,-3300),Vector3(-2750,1100,-3600),70.,0.]]
\tfor setup in views:
\t\tvar camera_name:String=setup[0]
\t\tcamera.position=setup[1];camera.look_at(setup[2]);camera.fov=setup[3]
\t\tvar view_time:float=setup[4]
\t\tRenderingServer.global_shader_parameter_set("world_time",view_time)
\t\tenvironment_report["sampled_world_time"]=view_time
\t\tvar storm_sample:Dictionary=storm_adapter.sample(camera,view_time)
'''+s[end:]
            s=s.replace('\t\treport["emitter_reflection"]=emitter_report','\t\treport["emitter_reflection"]=emitter_report\n\t\treport["storm_setup"]=storm_setup\n\t\treport["storm_sample"]=storm_sample\n\t\treport["storm_runtime_sha256"]=FileAccess.get_sha256(directory.path_join("storm35c/storm_front_35c.gd"))')
            s=s.replace('34e WATER VIEWS','35c STORM VIEWS')
            s=s.replace('34a water material only; unchanged33f land/collision evidence inherited, no repeated paving validation.','35c spatial weather and new cloud models only; unchanged33f land/collision evidence inherited, no repeated paving validation.')
            p.write_text(s,encoding='utf-8')
            for p in frozen.rglob('*'):
                if p.is_file():run.bind(p)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            final=run.directory/'images'/(names[-1]+'.png')
            outputs=[]
            for name in names:
                p=final.parent/(name+'.png');outputs.append(Path(str(p)+'.json'))
                if p!=final:outputs.append(p)
            run.stage('storm-world-views',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','1800','--','--label=20l','--study-dir='+str(frozen),'--view=reference-coast-near','--environment=day','--output='+str(final),'--validation-run='+run.run_id,'--study-time=0'],image=final,outputs=outputs)
            views=[]
            for name in names:
                d=read_json(final.parent/(name+'.png.json'))
                require(d['run_id']==run.run_id,'Wrong run')
                require(d['world_sha256']==old['world_sha256'] and d['rightcoast_glb_sha256']==old['rightcoast_glb_sha256'] and d['placements']==old['placements'],'World or coast changed')
                require(d['headland_study']['trees']==old['headland_study']['trees'],'Named land trees changed')
                require(d['storm_runtime_sha256']==sha256(native/'storm_front_35c.gd'),'Wrong storm runtime')
                require(d['storm_setup']['legacy_cloud_meshes_adapted']>0,'Legacy cloud binding missing')
                require(len(d['storm_setup']['assets'])==12 and d['storm_setup']['rain_instances']==14000,'Missing native cloud/rain assembly')
                require(d['storm_sample']['flash']==(1 if name in ['storm-flash','storm-inside-flash'] else 0),'Flash time wrong')
                views.append(dict(view=name,camera=d['camera'],sample=d['storm_sample']))
            byname={d['view']:d for d in views}
            require(byname['storm-inside']['sample']['camera_weather']>.95,'Inside front expected')
            require(.2<byname['storm-edge']['sample']['camera_weather']<.8,'Edge expected')
            require(byname['storm-clear']['sample']['camera_weather']<.05,'Clear side expected')
            path=run.directory/'actual-storm-revision.json';write_json(path,dict(run_id=run.run_id,views=views,passed=True,visual_accepted=False,scope='Same-world discrete GPU weather/side/back/time observations. No complete flight replay or reference landform acceptance. Land support inherited.'))
            run.bind(path);run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('35c GPU READY '+str(run.directory),flush=True)
        except Exception as e:
            run.manifest.update(status='failed',passed=False,error=str(e),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
