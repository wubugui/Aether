"""Five GPU views in two scene loads; C/D native geometry over retained28h optics."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json

CAMERAS='''
	var ref_position:Vector3=camera.position;var ref_rotation:Vector3=camera.rotation;var ref_fov:float=camera.fov
	var views:Array=["night-reference"] if environment_mode=="night" else ["day-reference","day-d-front","day-d-back","day-c-front"]
	for camera_name in views:
		if str(camera_name).ends_with("reference"):
			camera.position=ref_position;camera.rotation=ref_rotation;camera.fov=ref_fov
		elif camera_name=="day-d-front":
			camera.position=islands.island_d.to_global(Vector3(65,40,70));camera.look_at(islands.island_d.to_global(Vector3(0,10,0)));camera.fov=55
		elif camera_name=="day-d-back":
			camera.position=islands.island_d.to_global(Vector3(-70,35,-65));camera.look_at(islands.island_d.to_global(Vector3(0,10,0)));camera.fov=55
		else:
			camera.position=islands.island_c.to_global(Vector3(65,40,70));camera.look_at(islands.island_c.to_global(Vector3(0,10,0)));camera.fov=55
		for i in range(40):await process_frame
		await RenderingServer.frame_post_draw
		var target:String=output.get_base_dir().path_join(camera_name+".png")
		assert(root.get_texture().get_image().save_png(target)==OK)
'''

def main():
    root=Path(__file__).resolve().parents[1]
    prior=root/'captures/validation_runs/lantern-lighting-28f-20260908T162319Z-487bb5915c3e40169b6ec7339610e55e'
    baseline=root/'captures/validation_runs/lantern-lighting-28h-20260908T163354Z-e69c09f62fc547389d39adbbd0011225/images/final-beam-side.png.json'
    old=read_json(baseline);native=root/'captures/lantern_island_study_29e';gate=root/'reviews/round-29e-island-native-check.json'
    check=read_json(gate);require(check['passed'],'Saved29e source check failed')
    require(sha256(native/'island_c.blend')==check['source_sha256'] and sha256(native/'island_c.glb')==check['glb_sha256'],'Native29e identities changed')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'lantern-island-29e',False,True)
        run.manifest.update(scope='C/D29e connected terrain and original bedrock topology remodeling, retaining occupied20l pad/tree support and rebuilding terrain-fitted road on broad graded shoulders,26b mainland and28h optics. Five actual views from two scene loads; preserve original structure/tree placements and footing samples. No production/whole-world generation.',basis_run=prior.name,expected_counts={})
        try:
            frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen)
            for name in ['island_c.blend','island_c.glb']:shutil.copy2(native/name,frozen/name)
            for name in ['model-report.json','geometry-evidence.json','builder.py','terrain-plan.json']:shutil.copy2(native/name,frozen/('island-c-29e-'+name))
            for p in [Path(__file__),gate,root/'captures/lantern_lighting_28h.gd']:shutil.copy2(p,frozen/p.name)
            shutil.copy2(baseline,frozen/'baseline-28h-scene-points.json')
            path=frozen/'preview.gd';s=path.read_text(encoding='utf-8').replace('lantern_lighting_28f.gd','lantern_lighting_28h.gd')
            cut=s.index('\tfor i in range(40):await process_frame',s.index('environment_report["sampled_world_time"]'))
            start=s.index('\tvar report:={',cut);end=s.index('\tvar file:=',start)
            report=s[start:end]
            report+='\treport["view"]=camera_name\n\treport["island_geometry_revision"]="29e"\n\treport["island_c_glb_sha256"]=FileAccess.get_sha256(directory.path_join("island_c.glb"))\n'
            report+='\tvar file:=FileAccess.open(target+".json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()\n'
            s=s[:cut]+CAMERAS+'\n'.join('\t'+line for line in report.splitlines())+'\n\tprint("29e ISLAND VIEWS ",views)\n\tquit()\n'
            path.write_text(s,encoding='utf-8')
            for p in frozen.rglob('*'):
                if p.is_file():run.bind(p)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            points=[]
            for mode,names in [('night',['night-reference']),('day',['day-reference','day-d-front','day-d-back','day-c-front'])]:
                image=run.directory/'images'/(names[-1]+'.png');outputs=[]
                for name in names:
                    p=image.parent/(name+'.png');outputs.append(Path(str(p)+'.json'))
                    if p!=image:outputs.append(p)
                run.stage(mode+'-views',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',path,'--quit-after','1800','--','--label=20l','--study-dir='+str(frozen),'--view=reference-coast-near','--environment='+mode,'--output='+str(image),'--validation-run='+run.run_id,'--study-time=0'],image=image,outputs=outputs)
                for name in names:
                    d=read_json(image.parent/(name+'.png.json'))
                    require(d['run_id']==run.run_id and d['island_c_glb_sha256']==check['glb_sha256'],'Actual runtime native identity')
                    require(d['world_sha256']==old['world_sha256'],'World changed')
                    require(len(d['placements'])==len(old['placements']),'Structure/tree/scatter point count changed')
                    maximum=0.
                    for a,b in zip(d['placements'],old['placements']):
                        require(a['kind']==b['kind'] and a.get('island')==b.get('island'),'Placement sequence changed')
                        maximum=max(maximum,max(abs(x-y) for x,y in zip(a['position'],b['position'])))
                    require(maximum<.001,'A structure or tree moved: '+str(maximum))
                    require(len(d['footing_samples'])==len(old['footing_samples']),'Foundation count changed')
                    foundation_delta=0.
                    for a,b in zip(d['footing_samples'],old['footing_samples']):
                        require(a['building']==b['building'],'Foundation identity changed')
                        for p,q in zip(a['samples'],b['samples']):foundation_delta=max(foundation_delta,abs(p['gap_m']-q['gap_m']))
                    require(foundation_delta<.001,'Foundation support changed: '+str(foundation_delta))
                    points.append({'view':name,'placement_count':len(d['placements']),'maximum_position_delta_m':maximum,'foundation_gap_delta_m':foundation_delta,'island_c_glb_sha256':d['island_c_glb_sha256']})
            report=run.directory/'actual-site-preservation.json';write_json(report,{'run_id':run.run_id,'passed':True,'views':points,'scope':'Actual same-world ray-derived structure/tree positions and original9x9 footprint samples. Native29e rebuilds road heights and retains occupied building/tree support while remodeling connected terrain; this does not prove every branch/rock collision or full walking/flight clearance.'});run.bind(report)
            run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('29e ISLAND GPU READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
