"""One scene load; four diagnostic layers isolate actual optical-volume rendering."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,snapshot_inputs,utc_now,write_json
def main():
    root=Path(__file__).resolve().parents[1]
    prior=root/'captures/validation_runs/lantern-lighting-28b-20260908T155820Z-3e43e974e919427cabd2e867be27facf'
    require(read_json(prior/'manifest.json')['passed'],'28b still running')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'lantern-diagnostic-28c',False,True)
        run.manifest.update(scope='Single actual scene load, four explicitly non-art debug layers of the28b volume shader. Preserve normal output too. No model/native/world rebuild.',basis_run=prior.name,expected_counts={})
        try:
            frozen=run.directory/'study-inputs';shutil.copytree(prior/'study-inputs',frozen);shutil.copy2(__file__,frozen/Path(__file__).name)
            shader_path=frozen/'lantern-optics/lantern_volume.gdshader';shader=shader_path.read_text(encoding='utf-8')
            shader=shader.replace('uniform float volume_kind=0.;','uniform float volume_kind=0.;\nuniform float debug_mode=0.;')
            shader=shader.replace('    float depth=textureLod','    float uncut_length=max(leave-enter,0.);\n    float depth=textureLod')
            shader=shader.replace('    float optical_depth=0.;','    float optical_depth=0.;float geometric_depth=0.;')
            shader=shader.replace('                vec2 uv=.5+', '                geometric_depth+=step_length*(1.-smoothstep(.70,1.,radial));\n                vec2 uv=.5+')
            shader=shader.replace('    ALPHA=clamp(1.-exp(-optical_depth),0.,.9);','''    ALPHA=clamp(1.-exp(-optical_depth),0.,.9);
    if(debug_mode>.5 && debug_mode<1.5){EMISSION=vec3(1.,.15,.02);ALPHA=.35;}
    if(debug_mode>1.5 && debug_mode<2.5){EMISSION=vec3(clamp(uncut_length*.02,0.,1.),clamp(step_length*32.*.02,0.,1.),0.);ALPHA=.8;}
    if(debug_mode>2.5 && debug_mode<3.5){EMISSION=vec3(.03,.15,1.);ALPHA=1.-exp(-geometric_depth*.03);}
    if(debug_mode>3.5){EMISSION=vec3(.1,1.,.1);ALPHA=clamp(optical_depth*3.,0.,1.);}''')
            shader_path.write_text(shader,encoding='utf-8')
            preview_path=frozen/'preview.gd';preview=preview_path.read_text(encoding='utf-8')
            anchor='\tassert(root.get_texture().get_image().save_png(output)==OK)';require(preview.count(anchor)==1,'Capture anchor changed')
            loop='''\tfor debug_mode in [1.,2.,3.,4.,0.]:
\t\tfor mesh in game.find_children("*","MeshInstance3D",true,false):
\t\t\tif mesh.material_override is ShaderMaterial and mesh.material_override.shader.code.contains("uniform float debug_mode"):
\t\t\t\tmesh.material_override.set_shader_parameter("debug_mode",debug_mode)
\t\tfor i in range(40):await process_frame
\t\tawait RenderingServer.frame_post_draw
\t\tvar target:String=output if debug_mode==0. else output.get_basename()+"-debug-"+str(int(debug_mode))+".png"
\t\tassert(root.get_texture().get_image().save_png(target)==OK)
'''
            preview=preview.replace(anchor,loop);preview_path.write_text(preview,encoding='utf-8')
            for p in frozen.rglob('*'):
                if p.is_file():run.bind(p)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            output=run.directory/'images/night-reference.png';report=Path(str(output)+'.json')
            diagnostics=[output.parent/('night-reference-debug-'+str(i)+'.png') for i in range(1,5)]
            run.stage('diagnostic-layers',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',preview_path,'--quit-after','2200','--','--label=20l','--study-dir='+str(frozen),'--view=reference-coast-near','--environment=night','--output='+str(output),'--validation-run='+run.run_id,'--study-time=0'],image=output,outputs=[report,*diagnostics])
            run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('28c OPTICAL LAYERS '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
