"""Author a local, reversible day/night material study on the actual coastal world."""
from pathlib import Path
import json,hashlib,shutil
root=Path(__file__).resolve().parents[1]
out=root/'captures/coast_environment_study_21a';assert not out.exists();out.mkdir()
shutil.copy2(__file__,out/'builder.py')
origins={}
for name in ['world_surface','terrain_native','cliff_surface','ship_surface','wood_surface']:
    source=root/'scripts'/(name+'.gdshader');text=source.read_text();origins[name]=hashlib.sha256(source.read_bytes()).hexdigest()
    text=text.replace('shader_type spatial;','shader_type spatial;\nuniform vec3 study_fill=vec3(1.);\nuniform vec3 study_haze=vec3(.40,.53,.65);')
    text=text.replace('EMISSION=ALBEDO*.72','EMISSION=ALBEDO*study_fill*.72').replace('EMISSION=ALBEDO*.82','EMISSION=ALBEDO*study_fill*.82').replace('EMISSION=ALBEDO*.93','EMISSION=ALBEDO*study_fill*.93')
    text=text.replace('vec3(.40,.53,.65)*haze','study_haze*haze')
    if name=='wood_surface':text=text.replace('unshaded, cull_disabled, fog_disabled','unshaded, cull_disabled').replace('ALBEDO=OUTPUT_IS_SRGB?c:pow(c,vec3(2.2));','ALBEDO=(OUTPUT_IS_SRGB?c:pow(c,vec3(2.2)))*study_fill;')
    (out/(name+'.gdshader')).write_text(text)
(out/'cloud_surface.gdshader').write_text('''shader_type spatial;
render_mode unshaded,cull_disabled;
global uniform float world_time;
uniform float study_night=0.;
uniform vec3 moon_direction=vec3(-.184,.38,-.907);
varying vec3 world_normal;
void vertex(){VERTEX.x+=sin(world_time*.018)*9.;world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
    vec3 n=normalize(world_normal);
    float sky_fill=smoothstep(-.70,.65,n.y);
    vec3 day=mix(vec3(.83,.800,.807),vec3(.98,.950,.930),sky_fill);
    day+=(max(dot(n,normalize(vec3(-.48,.82,.30))),0.)-.4)*.022;
    float moonlight=max(dot(n,normalize(moon_direction)),0.);
    vec3 night=mix(vec3(.024,.036,.082),vec3(.105,.155,.34),sky_fill*.55+moonlight*.45);
    ALBEDO=mix(day,night,study_night);
}
''')
(out/'open_sky.gdshader').write_text('''shader_type sky;
uniform float study_night=0.;
uniform vec3 moon_direction=vec3(-.184,.38,-.907);
float hash21(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
void sky(){
    vec3 ray=normalize(EYEDIR);float altitude=clamp(ray.y,0.,1.);
    vec3 day=mix(vec3(.815,.905,.940),vec3(.440,.630,.837),pow(clamp(altitude/.33,0.,1.),.85));
    day+=vec3(.13,.12,.07)*pow(max(dot(ray,normalize(vec3(-.48,.82,.30))),0.),96.);
    vec3 night=mix(vec3(.035,.085,.20),vec3(.003,.010,.039),pow(clamp(altitude/.7,0.,1.),.6));
    vec3 moon=normalize(moon_direction);float angle=acos(clamp(dot(ray,moon),-1.,1.));
    float disk=1.-smoothstep(.036,.038,angle);
    vec2 sphere=vec2(atan(ray.z,ray.x)/6.2831853+.5,asin(ray.y)/3.14159265+.5);
    vec2 grid=sphere*vec2(650.,325.);vec2 cell=floor(grid);float seed=hash21(cell);
    vec2 offset=vec2(hash21(cell+23.7),hash21(cell-14.8));
    float star=(1.-smoothstep(.015,.055+.035*seed,length(fract(grid)-offset)))*step(.73,seed)*smoothstep(0.,.16,ray.y);
    night+=vec3(.72,.80,1.)*star;
    night+=vec3(.10,.16,.32)*exp(-angle*25.);
    float facets=.76+.24*hash21(floor(sphere*vec2(2200.,1100.)));
    night=mix(night,vec3(.70,.79,1.)*facets,disk);
    COLOR=mix(day,night,study_night);
}
''')
source=root/'scripts/open_water.gdshader';text=source.read_text();origins['open_water']=hashlib.sha256(source.read_bytes()).hexdigest()
text=text.replace('shader_type spatial;','shader_type spatial;\nuniform float study_night=0.;\nuniform vec3 moon_direction=vec3(-.184,.38,-.907);')
text=text.replace('    EMISSION=ALBEDO*.82;','''    vec3 day_emission=ALBEDO*.82;
    // The moon reflection is computed from the actual surface position,
    // wave normal and view ray. It moves with the observer in the same world.
    vec3 wave_normal=normalize(vec3(cos(world_point.x*.17+world_point.z*.07+world_time*.7)*.105+sin(world_point.z*.39-world_time)*.045,1.,cos(world_point.z*.23-world_time*.85)*.115));
    vec3 view_direction=normalize(INV_VIEW_MATRIX[3].xyz-world_point);
    float reflected=pow(max(dot(reflect(-view_direction,wave_normal),normalize(moon_direction)),0.),180.);
    float broken_wave=.38+.62*smoothstep(-.2,.75,sin(world_point.x*.85+world_point.z*1.5+world_time));
    vec3 night_color=mix(vec3(.003,.011,.036),vec3(.010,.026,.070),ripple*.3+.5);
    night_color=mix(night_color,vec3(.065,.095,.15),foam*.6);
    EMISSION=mix(day_emission,night_color+vec3(.43,.57,.94)*reflected*broken_wave,study_night);
    ALBEDO=mix(ALBEDO,vec3(.006,.016,.043),study_night);
    NORMAL=mix(NORMAL,normalize((VIEW_MATRIX*vec4(wave_normal,0.)).xyz),study_night);''')
(out/'open_water.gdshader').write_text(text)
(out/'source-identities.json').write_text(json.dumps({'scope':'Temporary actual-world material and lighting study; no production edits. No image textures or fullscreen filters. Not full weather implementation.','original_shader_sha256':origins},indent=2))
print(out)
