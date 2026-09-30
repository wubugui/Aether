"""One unchanged27f GPU sample with longer settling and actual sky-mesh state."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,snapshot_inputs,utc_now,write_json
def main():
    root=Path(__file__).resolve().parents[1]
    prior=root/'captures/validation_runs/coast-environment-27f-20260908T152526Z-f1543e06af9f4533a1689edaf5dc0add'
    require(read_json(prior/'manifest.json')['passed'],'27f run incomplete')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'coast-moon-diagnostic-27g',False,True)
        run.manifest.update(scope='One unchanged27f night-reference rendering with3seconds plus240frames settling and actual sky mesh/material state. Diagnose missing moon; no visual acceptance or broad retest.',basis_run=prior.name,expected_counts={})
        try:
            frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen)
            shutil.copy2(__file__,frozen/Path(__file__).name)
            preview=(frozen/'preview.gd').read_text(encoding='utf-8')
            require(preview.count('\tfor i in range(40):await process_frame')==1,'Settling anchor changed')
            preview=preview.replace('\tfor i in range(40):await process_frame','\tawait create_timer(3.).timeout\n\tfor i in range(240):await process_frame')
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
\treport["sky_mesh_diagnostic"]={"camera_far":camera.far,"camera_cull_mask":camera.cull_mask,"settling_seconds":3.,"settling_frames":240,"meshes":sky_diagnostics}
'''
            require(preview.count(anchor)==1,'Diagnostic anchor changed')
            preview=preview.replace(anchor,injection+anchor)
            (frozen/'preview.gd').write_text(preview,encoding='utf-8')
            for p in frozen.rglob('*'):
                if p.is_file():run.bind(p)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            output=run.directory/'images/night-reference.png';report=Path(str(output)+'.json')
            run.stage('night-reference',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','1500','--','--label=20l','--study-dir='+str(frozen),'--view=reference-coast-near','--environment=night','--output='+str(output),'--validation-run='+run.run_id,'--study-time=0'],image=output,outputs=[report])
            run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('27g MOON DIAGNOSTIC '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
