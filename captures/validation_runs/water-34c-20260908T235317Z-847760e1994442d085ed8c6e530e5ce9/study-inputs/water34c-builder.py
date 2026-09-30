from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];O=R/'captures/water_study_34c';assert not O.exists();O.mkdir()
prior=R/'captures/validation_runs/water-34b-20260908T234145Z-bcb3451587f949d8b6faa363cf23622d/study-inputs';source=prior/'new-environment27f/open_water.gdshader';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();s=source.read_text(encoding='utf-8')
assert sha(source)=='2f1c09d17eaa641d665a34c5d95c00675d0fcf07c15278a163f028dad06e1781'
s=s.replace('uniform vec3 moon_direction=vec3(-.184,.38,-.907);','uniform vec3 moon_direction=vec3(-.184,.38,-.907);\nuniform vec3 moon_world_center=vec3(-3933.250977,3478.453369,-9791.308594);\nuniform float moon_world_radius=330.;')
start=s.index('    // Reflect the actual finite330m');end=s.index('    float broken_wave=',start)
s=s[:start]+'''    // Finite authored world sphere; actual runtime node values are bound
    // after construction. Each water point has its own incident direction.
    vec3 reflected_ray=reflect(-view_direction,wave_normal);
    vec3 to_moon=moon_world_center-world_point;
    float moon_distance=max(length(to_moon),moon_world_radius+1.);
    vec3 local_moon_direction=to_moon/moon_distance;
    float separation=acos(clamp(dot(reflected_ray,local_moon_direction),-1.,1.));
    float moon_radius=asin(clamp(moon_world_radius/moon_distance,0.,1.));
    float pixel_angle=max(.00015,.65*(length(dFdx(view_direction))+length(dFdy(view_direction))));
    float reflected=1.-smoothstep(moon_radius-pixel_angle,moon_radius+pixel_angle,separation);
    // Micro-rough reflection surrounds a smaller silver core. This is an
    // angular surface response, not a screen-space position/brightness mask.
    float rough_width=.045;
    float outside_disk=max(separation-moon_radius,0.);
    float rough_reflection=exp(-outside_disk*outside_disk/(2.*rough_width*rough_width));
    float rough_peak=(moon_radius*moon_radius)/(moon_radius*moon_radius+rough_width*rough_width);
    vec3 moon_radiance=vec3(.36,.55,.95)*rough_reflection*rough_peak+vec3(.60,.78,1.16)*reflected*.62;
'''+s[end:]
s=s.replace('vec3 reflected_night_sky=mix(vec3(.050,.090,.18),vec3(.006,.018,.050),sky_height);','''// Match the actual open_sky night gradient and halo radiance.
    float sky_altitude=clamp(sky_ray.y,0.,1.);
    vec3 reflected_night_sky=mix(vec3(.065,.14,.30),vec3(.009,.028,.085),pow(clamp(sky_altitude/.7,0.,1.),.6));
    reflected_night_sky+=vec3(.10,.16,.32)*exp(-separation*25.);''')
s=s.replace('night_color+vec3(.98,1.28,2.05)*reflected*broken_wave','night_color+moon_radiance*broken_wave')
s=s.replace('    NORMAL=normalize(NORMAL+vec3(cos(world_point.x*.031+world_time*.8)*.04,cos(world_point.z*.043-world_time*.6)*.04,0));\n','')
(O/'open_water.gdshader').write_text(s,encoding='utf-8')
adapter_source=prior/'coast_environment_27f.gd';a=adapter_source.read_text(encoding='utf-8')
a=a.replace('var emissive_surfaces:int=0','var emissive_surfaces:int=0\nvar water_reflection_bindings:Array=[]')
needle='\t\tmoon.position=Vector3(-2278,60,-1632)+MOON.normalized()*9000.';assert needle in a
a=a.replace(needle,needle+'''
\t\tfor material in material_cache.values():
\t\t\tif material is ShaderMaterial and material.shader==shader_cache.get("open_water"):
\t\t\t\tmaterial.set_shader_parameter("moon_world_center",moon.global_position)
\t\t\t\tmaterial.set_shader_parameter("moon_world_radius",330.)
\t\t\t\tvar actual:Vector3=material.get_shader_parameter("moon_world_center")
\t\t\t\tassert(actual.is_equal_approx(moon.global_position))
\t\t\t\twater_reflection_bindings.append({"moon_node":str(moon.get_path()),"center":[actual.x,actual.y,actual.z],"radius_m":material.get_shader_parameter("moon_world_radius"),"scope":"Actual world sphere bound to each water material; per-water-point incident ray in shader."})
\t\tassert(not water_reflection_bindings.is_empty())''')
a=a.replace('return {"unmapped_shader_paths":','return {"water_reflection_bindings":water_reflection_bindings,"unmapped_shader_paths":')
(O/'coast_environment_27f.gd').write_text(a,encoding='utf-8');shutil.copy2(__file__,O/'builder.py')
(O/'design-plan.json').write_text(json.dumps(dict(label='34c',source=str(source.relative_to(R)),source_sha256=sha(source),shader_sha256=sha(O/'open_water.gdshader'),adapter_source_sha256=sha(adapter_source),adapter_sha256=sha(O/'coast_environment_27f.gd'),scope='34b rework: actual instantiated finite moon bound into water, per-point incident direction/angular radius, micro-rough blue reflection around silver core, actual sky gradient. Geometry remains flat. No local emitter or cloud/island scene reflections yet. Coast33f unchanged.',production_modified=False,full_reference_accepted=False),indent=2),encoding='utf-8')
driver=(R/'tools/render_water_34b.py').read_text(encoding='utf-8').replace('34b','34c')
driver=driver.replace("prior=root/'captures/validation_runs/water-34a-20260908T233808Z-05bd651c68574ef79ba9b59ab98506bb'", "prior=root/'captures/validation_runs/water-34b-20260908T234145Z-bcb3451587f949d8b6faa363cf23622d'")
needle="   shutil.copy2(native/'open_water.gdshader',frozen/'new-environment27f/open_water.gdshader')";assert needle in driver
driver=driver.replace(needle,needle+"\n   require(sha256(frozen/'coast_environment_27f.gd')==plan['adapter_source_sha256'],'Adapter parent identity');shutil.copy2(native/'coast_environment_27f.gd',frozen/'coast_environment_27f.gd')")
needle="     require(d['headland_study']['trees']==old['headland_study']['trees'],'Named tree placement changed')";assert needle in driver
driver=driver.replace(needle,needle+"\n     if mode=='night':require(len(d['environment_study']['water_reflection_bindings'])>0,'Actual moon bindings missing')")
p=R/'tools/render_water_34c.py';assert not p.exists();p.write_text(driver,encoding='utf-8');print('34c prepared')
