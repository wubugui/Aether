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
    old=read_json(baseline);native=root/'captures/lantern_island_study_30e';gate=root/'reviews/round-30e-island-native-check.json'
    check=read_json(gate);require(check['passed'],'Saved30e source check failed')
    require(sha256(native/'island_c.blend')==check['source_sha256'] and sha256(native/'island_c.glb')==check['glb_sha256'],'Native30e identities changed')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'lantern-island-30e',False,True)
        run.manifest.update(scope='C/D30e faceted transition cuts in directly located southern/eastern visible main slope. Protected masks removed before native tools; complete path,17rocks and D placement retained. Actual new collision mesh grounding. Unaffected A/B, reefs, mainland and production remain. Fixed reference camera and five GPU views.',basis_run=prior.name,expected_counts={})
        try:
            frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen)
            for name in ['island_c.blend','island_c.glb']:shutil.copy2(native/name,frozen/name)
            for name in ['model-report.json','geometry-evidence.json','builder.py','proportion-plan.json']:shutil.copy2(native/name,frozen/('island-c-30e-'+name))
            for p in [Path(__file__),gate,root/'captures/lantern_lighting_28h.gd']:shutil.copy2(p,frozen/p.name)
            shutil.copy2(baseline,frozen/'baseline-28h-scene-points.json')
            path=frozen/'preview.gd';s=path.read_text(encoding='utf-8').replace('lantern_lighting_28f.gd','lantern_lighting_28h.gd')
            s=s.replace('var proposed:=Vector3(-2340,0,-1810)','var proposed:=Vector3(-2372,0,-1812)').replace('model("island_c",proposed,.55)','model("island_c",proposed,2.0)').replace('"yaw":.55','"yaw":2.0')
            needle='\tvar at:Vector3=islands[island_name].to_global(offset)'
            replacement='\tif island_name in ["island_c","island_d"]:\n\t\toffset=Vector3(1.5,0,.8) if kind=="lighthouse" else offset*.72\n'+needle
            require(needle in s,'Building placement insertion missing');s=s.replace(needle,replacement)
            s=s.replace('else (.7 if island_name=="island_b" else .5)','else (.7 if island_name=="island_b" else .36)')
            cut=s.index('\tfor i in range(40):await process_frame',s.index('environment_report["sampled_world_time"]'))
            start=s.index('\tvar report:={',cut);end=s.index('\tvar file:=',start)
            report=s[start:end]
            report+='\treport["view"]=camera_name\n\treport["island_geometry_revision"]="30e"\n\treport["island_c_glb_sha256"]=FileAccess.get_sha256(directory.path_join("island_c.glb"))\n'
            report+='\tvar file:=FileAccess.open(target+".json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()\n'
            s=s[:cut]+CAMERAS+'\n'.join('\t'+line for line in report.splitlines())+'\n\tprint("30e ISLAND VIEWS ",views)\n\tquit()\n'
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
                    def affected(p):return p.get('island') in ['island_c','island_d'] or p['kind']=='island_c'
                    unchanged=[p for p in d['placements'] if not affected(p)];before=[p for p in old['placements'] if not affected(p)]
                    require(len(unchanged)==len(before),'Unchanged site count changed');maximum=0.
                    for a,b in zip(unchanged,before):
                        require(a['kind']==b['kind'] and a.get('island')==b.get('island'),'Unchanged placement identity changed')
                        maximum=max(maximum,max(abs(x-y) for x,y in zip(a['position'],b['position'])))
                    require(maximum<.001,'Unchanged region moved')
                    buildings=[p for p in d['placements'] if p.get('island') in ['island_c','island_d'] and p['kind'] in ['lighthouse','keeper_house']]
                    require(len(buildings)==4,'Expected two full-size tower and two keeper sites')
                    old_footing={p['building']:p for p in old['footing_samples']};rebuilt=[];unaffected_foundation_delta=0.
                    for f in d['footing_samples']:
                        center=f['samples'][4]['position'];matches=[p for p in buildings if abs(p['position'][0]-center[0])+abs(p['position'][2]-center[2])<.02]
                        if matches:
                            require(len(matches)==1,'Ambiguous rebuilt building');b=matches[0];expected=-.5 if b['kind']=='lighthouse' else -.65*.7
                            gaps=[p['gap_m'] for p in f['samples']];require(all(g is not None and abs(g-expected)<.10 for g in gaps),'New building support outside expected foundation embed: '+str(gaps))
                            require(abs(b['scale']-(1. if b['kind']=='lighthouse' else .7))<1e-6,'Native building scale changed')
                            rebuilt.append({'building':f['building'],'island':b['island'],'kind':b['kind'],'position':b['position'],'scale':b['scale'],'sample_gaps_m':gaps})
                        else:
                            base=old_footing[f['building']]
                            for p,q in zip(f['samples'],base['samples']):unaffected_foundation_delta=max(unaffected_foundation_delta,abs(p['gap_m']-q['gap_m']))
                    require(len(rebuilt)==4 and unaffected_foundation_delta<.001,'Rebuilt/unaffected foundations invalid')
                    points.append({'view':name,'placement_count':len(d['placements']),'unchanged_placement_count':len(unchanged),'unchanged_maximum_position_delta_m':maximum,'unaffected_foundation_delta_m':unaffected_foundation_delta,'rebuilt_buildings':rebuilt,'affected_placements':[p for p in d['placements'] if affected(p)],'island_c_glb_sha256':d['island_c_glb_sha256']})
            report=run.directory/'actual-site-rebuild.json';write_json(report,{'run_id':run.run_id,'passed':True,'views':points,'design':{'land_blender_scale':[.72,.72,.65],'d_position':[-2372,0,-1812],'d_yaw':2.0,'tower_offset':[1.5,0,.8],'native_building_scales':[1.,.7]},'scope':'Actual same-world re-grounded native buildings and trees. Four rebuilt building3x3 foundation samples, unaffected regions compared with28h. No all-surface contact, full walking/flight or visual acceptance claim.'});run.bind(report)
            run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('30e ISLAND GPU READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
