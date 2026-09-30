"""One GPU scene: core shadow A/B, then beam-only intensity, three fixed cameras."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,snapshot_inputs,utc_now,write_json

LOOP='''
	var ref_position:Vector3=camera.position;var ref_rotation:Vector3=camera.rotation;var ref_fov:float=camera.fov
	var core_nodes:Array=[];var optical_meshes:Array=[]
	for mesh in region.find_children("*","MeshInstance3D",true,false):
		if mesh.mesh.get_surface_count()==1:
			var mat:Material=mesh.get_active_material(0)
			if mat is StandardMaterial3D and mat.resource_name=="Lamp core":core_nodes.append(mesh)
		if mesh.material_override is ShaderMaterial and mesh.material_override.shader.code.contains("uniform float beam_length"):
			if float(mesh.material_override.get_shader_parameter("volume_kind"))<.5:optical_meshes.append(mesh)
	assert(core_nodes.size()==4 and optical_meshes.size()==4)
	var comparisons:Array=[]
	for variant in ["baseline","core-transmits","beam-boost"]:
		if variant=="core-transmits":
			for mesh in core_nodes:mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if variant=="beam-boost":
			for mesh in optical_meshes:mesh.material_override.set_shader_parameter("light_energy",1.3)
		for camera_name in ["reference","lamp-close","beam-side"]:
			var tower:Node3D=region.get_node("Lighthouse_island_a")
			if camera_name=="reference":camera.position=ref_position;camera.rotation=ref_rotation;camera.fov=ref_fov
			elif camera_name=="lamp-close":camera.position=tower.global_position+Vector3(9,23,13);camera.look_at(tower.global_position+Vector3(0,19.60,0));camera.fov=45
			else:camera.position=tower.global_position+Vector3(460,144.6,-170);camera.look_at(tower.global_position+Vector3(120,19.60,-220));camera.fov=70
			for i in range(40):await process_frame
			await RenderingServer.frame_post_draw
			var target:String=output.get_base_dir().path_join(camera_name+"-"+variant+".png")
			assert(root.get_texture().get_image().save_png(target)==OK)
			var cores:Array=[];var beam_states:Array=[]
			for mesh in core_nodes:
				var native_lamp:Node3D=mesh.get_parent().get_parent().get_node("NativeLanternLight")
				cores.append({"mesh":str(mesh.get_path()),"cast_shadow":mesh.cast_shadow,"bounds_contains_light_origin":mesh.get_aabb().has_point(mesh.to_local(native_lamp.global_position))})
			for mesh in optical_meshes:beam_states.append({"mesh":str(mesh.get_path()),"energy":mesh.material_override.get_shader_parameter("light_energy")})
			var comparison:Dictionary={"run_id":identity,"image":target,"variant":variant,"camera_name":camera_name,"camera":{"position":[camera.position.x,camera.position.y,camera.position.z],"rotation":[camera.rotation.x,camera.rotation.y,camera.rotation.z],"fov":camera.fov},"core_nodes":cores,"beam_states":beam_states,"world_sha256":FileAccess.get_sha256("res://scenes/world/World.tscn"),"scope":"Single loaded actual world. Baseline28f; core-transmits changes only four luminous-core shadow casters; beam-boost additionally doubles unshaded beam energy .65 to1.3. Native lights, opaque frame/roof, transparent glass and density geometry stay unchanged."}
			comparisons.append(comparison)
			var capture_report:=FileAccess.open(target+".json",FileAccess.WRITE);capture_report.store_string(JSON.stringify(comparison,"  "));capture_report.close()
	assert(root.get_texture().get_image().save_png(output)==OK)
'''

def main():
    root=Path(__file__).resolve().parents[1]
    prior=root/'captures/validation_runs/lantern-lighting-28f-20260908T162319Z-487bb5915c3e40169b6ec7339610e55e'
    require(read_json(prior/'manifest.json')['passed'],'28f basis incomplete')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'lantern-receiver-28g',False,True)
        run.manifest.update(scope='One real GPU scene load; nine fixed-camera A/B/C images isolate source-core shadow blocking from beam intensity. No production or geometry rebuild.',basis_run=prior.name,expected_counts={})
        try:
            frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen);shutil.copy2(__file__,frozen/Path(__file__).name)
            p=frozen/'preview.gd';s=p.read_text(encoding='utf-8');anchor='\tassert(root.get_texture().get_image().save_png(output)==OK)'
            require(s.count(anchor)==1,'Capture anchor changed');s=s.replace(anchor,LOOP)
            s=s.replace('report["lantern_lighting"]=lantern_report','report["lantern_lighting"]=lantern_report\n\treport["optical_comparisons"]=comparisons\n\treport["view"]= "beam-side-final-boost"')
            p.write_text(s,encoding='utf-8')
            for p in frozen.rglob('*'):
                if p.is_file():run.bind(p)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            output=run.directory/'images/final-beam-side.png';report=Path(str(output)+'.json')
            outputs=[report]
            for variant in ['baseline','core-transmits','beam-boost']:
                for view in ['reference','lamp-close','beam-side']:
                    im=output.parent/(view+'-'+variant+'.png');outputs.extend([im,Path(str(im)+'.json')])
            run.stage('receiver-comparison',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','2200','--','--label=20l','--study-dir='+str(frozen),'--view=reference-coast-near','--environment=night','--output='+str(output),'--validation-run='+run.run_id,'--study-time=0'],image=output,outputs=outputs)
            for variant in ['baseline','core-transmits','beam-boost']:
                for view in ['reference','lamp-close','beam-side']:
                    d=read_json(output.parent/(view+'-'+variant+'.png.json'))
                    require(d['run_id']==run.run_id and len(d['core_nodes'])==4 and len(d['beam_states'])==4,'Actual comparison identity/count')
                    require(all(c['bounds_contains_light_origin'] and c['cast_shadow']==(1 if variant=='baseline' else 0) for c in d['core_nodes']),'Core light enclosure/shadow state not actual')
                    require(all(abs(b['energy']-(1.3 if variant=='beam-boost' else .65))<1e-5 for b in d['beam_states']),'Actual beam energy')
            run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('28g RECEIVER COMPARISON '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
