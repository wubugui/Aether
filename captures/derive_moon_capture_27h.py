"""Resample only the two missing-moon27f night views with an actual pixel gate."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=(R/'tools/diagnose_coast_moon_27g.py').read_text(encoding='utf-8')
p=p.replace('One unchanged27f GPU sample with longer settling and actual sky-mesh state.','Two unchanged27f night samples with an observed moon-disk readiness gate.')
p=p.replace("'coast-moon-diagnostic-27g'","'coast-moon-readiness-27h'")
p=p.replace('One unchanged27f night-reference rendering with3seconds plus240frames settling and actual sky mesh/material state. Diagnose missing moon; no visual acceptance or broad retest.','Only the two affected27f night-reference samples. Same assets and water, actual projected moon pixels required before capture; no full world or weather acceptance.')
start=p.index("            preview=preview.replace('\\tfor i in range(40)")
end=p.index("            anchor=",start)
replacement="""            readiness='''\\tfor i in range(40):await process_frame
\\tvar moon_ready:Dictionary={}
\\tfor attempt in range(40):
\\t\\tawait RenderingServer.frame_post_draw
\\t\\tmoon_ready=check_moon_pixels(camera)
\\t\\tmoon_ready["attempt"]=attempt
\\t\\tif moon_ready["ready"]:break
\\t\\tawait create_timer(.25).timeout
\\tif not moon_ready["ready"]:
\\t\\troot.get_texture().get_image().save_png(output)
\\t\\tassert(false,"Projected moon disk failed actual-pixel readiness gate")'''
            preview=preview.replace('\\tfor i in range(40):await process_frame',readiness)
            preview+='''
func check_moon_pixels(camera:Camera3D) -> Dictionary:
\\tvar moon:MeshInstance3D=game.get_node("NativeCoastalSky27f/moon/Faceted lunar sphere with sculpted basins")
\\tassert(moon.is_visible_in_tree() and not camera.is_position_behind(moon.global_position))
\\tvar center:Vector2=camera.unproject_position(moon.global_position)
\\tvar radius:float=center.distance_to(camera.unproject_position(moon.global_position+camera.global_basis.y*330.))
\\tvar frame:Image=root.get_texture().get_image();var bright:=0;var sample_count:=0
\\tfor y in range(-2,3):
\\t\\tfor x in range(-2,3):
\\t\\t\\tvar point:Vector2=center+Vector2(x,y)*radius*.16
\\t\\t\\tassert(point.x>=0. and point.y>=0. and point.x<frame.get_width() and point.y<frame.get_height())
\\t\\t\\tif frame.get_pixel(int(point.x),int(point.y)).get_luminance()>.25:bright+=1
\\t\\t\\tsample_count+=1
\\treturn {"ready":bright>=20,"samples":sample_count,"bright_samples":bright,"minimum_bright_samples":20,"luminance_threshold":.25,"center":[center.x,center.y],"radius_pixels":radius,"scope":"Fixed full-moon reference composition only; pixel evidence does not prove all material readiness."}
'''
"""
p=p[:start]+replacement+p[end:]
p=p.replace('"settling_seconds":3.,"settling_frames":240,','"initial_settling_frames":40,"pixel_readiness":moon_ready,')
start=p.index("            output=run.directory/'images/night-reference.png'")
end=p.index('            run.assert_inputs();',start)
p=p[:start]+'''            for name,sample_time in [('night-reference',0),('night-reference-later',18)]:
                output=run.directory/'images'/(name+'.png');report=Path(str(output)+'.json')
                run.stage(name,[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','1500','--','--label=20l','--study-dir='+str(frozen),'--view=reference-coast-near','--environment=night','--output='+str(output),'--validation-run='+run.run_id,'--study-time='+str(sample_time)],image=output,outputs=[report])
                d=read_json(report)
                require(d['sky_mesh_diagnostic']['pixel_readiness']['ready'],'Moon not visible in actual projected pixels')
                require(d['environment_study']['sampled_world_time']==sample_time,'World time control missing')
'''+p[end:]
p=p.replace("print('27g MOON DIAGNOSTIC '","print('27h MOON PIXEL GATE '")
(R/'tools/validate_coast_moon_27h.py').write_text(p,encoding='utf-8')
print('27h actual moon-pixel readiness sampler prepared')
