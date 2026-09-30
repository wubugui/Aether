"""Two unchanged27f night samples with an observed moon-disk readiness gate."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,snapshot_inputs,utc_now,write_json
def main():
    root=Path(__file__).resolve().parents[1]
    prior=root/'captures/validation_runs/coast-environment-27f-20260908T152526Z-f1543e06af9f4533a1689edaf5dc0add'
    require(read_json(prior/'manifest.json')['passed'],'27f run incomplete')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'coast-moon-readiness-27h',False,True)
        run.manifest.update(scope='Only the two affected27f night-reference samples. Same assets and water, actual projected moon pixels required before capture; no full world or weather acceptance.',basis_run=prior.name,expected_counts={})
        try:
            frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen)
            shutil.copy2(__file__,frozen/Path(__file__).name)
            preview=(frozen/'preview.gd').read_text(encoding='utf-8')
            require(preview.count('\tfor i in range(40):await process_frame')==1,'Settling anchor changed')
            readiness='''\tfor i in range(40):await process_frame
\tvar moon_ready:Dictionary={}
\tfor attempt in range(40):
\t\tawait RenderingServer.frame_post_draw
\t\tmoon_ready=check_moon_pixels(camera)
\t\tmoon_ready["attempt"]=attempt
\t\tif moon_ready["ready"]:break
\t\tawait create_timer(.25).timeout
\tif not moon_ready["ready"]:
\t\troot.get_texture().get_image().save_png(output)
\t\tassert(false,"Projected moon disk failed actual-pixel readiness gate")'''
            preview=preview.replace('\tfor i in range(40):await process_frame',readiness)
            preview+='''
func check_moon_pixels(camera:Camera3D) -> Dictionary:
\tvar moon:MeshInstance3D=game.get_node("NativeCoastalSky27f/moon/Faceted lunar sphere with sculpted basins")
\tassert(moon.is_visible_in_tree() and not camera.is_position_behind(moon.global_position))
\tvar center:Vector2=camera.unproject_position(moon.global_position)
\tvar radius:float=center.distance_to(camera.unproject_position(moon.global_position+camera.global_basis.y*330.))
\tvar frame:Image=root.get_texture().get_image();var bright:=0;var sample_count:=0
\tfor y in range(-2,3):
\t\tfor x in range(-2,3):
\t\t\tvar point:Vector2=center+Vector2(x,y)*radius*.16
\t\t\tassert(point.x>=0. and point.y>=0. and point.x<frame.get_width() and point.y<frame.get_height())
\t\t\tif frame.get_pixel(int(point.x),int(point.y)).get_luminance()>.25:bright+=1
\t\t\tsample_count+=1
\treturn {"ready":bright>=20,"samples":sample_count,"bright_samples":bright,"minimum_bright_samples":20,"luminance_threshold":.25,"center":[center.x,center.y],"radius_pixels":radius,"scope":"Fixed full-moon reference composition only; pixel evidence does not prove all material readiness."}
'''
            anchor='\treport["site_checks"]=site_checks'
            injection='''\tvar sky_diagnostics:Array=[]
\tfor sky_mesh in game.get_node("NativeCoastalSky27f").find_children("*","MeshInstance3D",true,false):
\t\tvar surfaces:Array=[]
\t\tfor index in range(sky_mesh.mesh.get_surface_count()):
\t\t\tvar active:Material=sky_mesh.get_active_material(index)
\t\t\tsurfaces.append({"type":active.get_class(),"shader_code":active.shader.code if active is ShaderMaterial else "","moon_color":str(active.get_shader_parameter("moon_color")) if active is ShaderMaterial and active.shader.code.contains("moon_color") else ""})
\t\tvar pos:Vector3=sky_mesh.global_position
\t\tvar screen:Vector2=camera.unproject_position(pos)
\t\tsky_diagnostics.append({"path":str(sky_mesh.get_path()),"visible":sky_mesh.is_visible_in_tree(),"position":[pos.x,pos.y,pos.z],"aabb":str(sky_mesh.get_aabb()),"scale":str(sky_mesh.global_basis.get_scale()),"layers":sky_mesh.layers,"range_end":sky_mesh.visibility_range_end,"screen_center":[screen.x,screen.y],"behind_camera":camera.is_position_behind(pos),"surfaces":surfaces})
\treport["sky_mesh_diagnostic"]={"camera_far":camera.far,"camera_cull_mask":camera.cull_mask,"initial_settling_frames":40,"pixel_readiness":moon_ready,"meshes":sky_diagnostics}
'''
            require(preview.count(anchor)==1,'Diagnostic anchor changed')
            preview=preview.replace(anchor,injection+anchor)
            (frozen/'preview.gd').write_text(preview,encoding='utf-8')
            for p in frozen.rglob('*'):
                if p.is_file():run.bind(p)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            for name,sample_time in [('night-reference',0),('night-reference-later',18)]:
                output=run.directory/'images'/(name+'.png');report=Path(str(output)+'.json')
                run.stage(name,[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','1500','--','--label=20l','--study-dir='+str(frozen),'--view=reference-coast-near','--environment=night','--output='+str(output),'--validation-run='+run.run_id,'--study-time='+str(sample_time)],image=output,outputs=[report])
                d=read_json(report)
                require(d['sky_mesh_diagnostic']['pixel_readiness']['ready'],'Moon not visible in actual projected pixels')
                require(d['environment_study']['sampled_world_time']==sample_time,'World time control missing')
            run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('27h MOON PIXEL GATE '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
