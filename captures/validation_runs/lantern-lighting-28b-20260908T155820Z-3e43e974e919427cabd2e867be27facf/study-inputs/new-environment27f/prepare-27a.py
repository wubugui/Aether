from pathlib import Path
import shutil,hashlib,json
R=Path(__file__).resolve().parents[1];out=R/'captures/coast_environment_study_27a';assert not out.exists();out.mkdir()
old=R/'captures/coast_environment_study_21c'
for p in old.iterdir():
    if p.is_file():shutil.copy2(p,out/p.name)
shutil.copy2(__file__,out/'prepare-27a.py')
cloud='''shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;
global uniform float world_time;
uniform float study_night=0.;
uniform vec3 moon_direction=vec3(-.184,.38,-.907);
varying vec3 world_normal;
varying vec3 cloud_world;
void vertex(){
    VERTEX.x+=sin(world_time*.018)*9.;
    world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
    cloud_world=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
}
void fragment(){
    vec3 n=normalize(world_normal);
    float sky_fill=smoothstep(-1.,.72,n.y);
    float direct=max(dot(n,normalize(moon_direction)),0.);
    float transmitted=max(dot(-n,normalize(moon_direction)),0.);
    float light=clamp(.44*sky_fill+.43*direct+.13*transmitted,0.,1.);
    vec3 night=mix(vec3(.105,.165,.34),vec3(.38,.50,.86),light);
    vec3 day=mix(vec3(.70,.76,.83),vec3(.97,.95,.92),sky_fill);
    day+=(max(dot(n,normalize(vec3(-.48,.82,.30))),0.)-.4)*.035;
    // Cloud altitude uses its own sparse haze rather than sea-level dense fog.
    // This is spatial distance attenuation; geometry and normals remain real.
    float haze=1.-exp(-distance(CAMERA_POSITION_WORLD,cloud_world)*.000035);
    vec3 air=mix(vec3(.50,.64,.78),vec3(.025,.065,.18),study_night);
    ALBEDO=mix(mix(day,night,study_night),air,haze);
}
'''
(out/'cloud_surface.gdshader').write_text(cloud,encoding='utf-8')
p=(old/'open_water.gdshader').read_text()
anchor='void vertex() {'
noise='''// A continuous world-space wind field; no repeated two-sine grid mask.
float sea_hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float sea_noise(vec2 p){
    vec2 i=floor(p),f=fract(p);vec2 u=f*f*(3.-2.*f);
    return mix(mix(sea_hash(i),sea_hash(i+vec2(1.,0.)),u.x),
               mix(sea_hash(i+vec2(0.,1.)),sea_hash(i+vec2(1.,1.)),u.x),u.y);
}
float sea_height(vec2 p){
    vec2 wind=normalize(vec2(.83,-.56));
    vec2 q=vec2(dot(p,wind),dot(p,vec2(-wind.y,wind.x)));
    q.y+=world_time*.55;
    float warp=sea_noise(q*vec2(.033,.08))*2.;
    float swell=.24*sin(q.y*.34+warp);
    float crest=.42*(sea_noise(q*vec2(.072,.32)+vec2(2.3,1.7))-.5);
    float small=.13*(sea_noise(q*vec2(.21,.86)+vec2(17.2,5.6))-.5);
    return swell+crest+small;
}
'''
p=p.replace(anchor,noise+anchor,1)
start=p.index('    vec3 wave_normal=');end=p.index('    vec3 night_color=',start)
p=p[:start]+'''    float e=.18;
    float dx=(sea_height(world_point.xz+vec2(e,0.))-sea_height(world_point.xz-vec2(e,0.)))/(2.*e);
    float dz=(sea_height(world_point.xz+vec2(0.,e))-sea_height(world_point.xz-vec2(0.,e)))/(2.*e);
    vec3 wave_normal=normalize(vec3(-dx,1.,-dz));
    vec3 view_direction=normalize(INV_VIEW_MATRIX[3].xyz-world_point);
    float reflected=pow(max(dot(reflect(-view_direction,wave_normal),normalize(moon_direction)),0.),65.);
    float broken_wave=.45+.55*sea_noise(world_point.xz*vec2(.075,.18)+vec2(4.,world_time*.15));
'''+p[end:]
p=p.replace('vec3(.43,.57,.94)*reflected*broken_wave','vec3(.68,.86,1.30)*reflected*broken_wave')
(out/'open_water.gdshader').write_text(p,encoding='utf-8')
report={'label':'27a','basis':'21c environment with26b world assembly','scope':'New editable taller cloud geometry and spatial cloud transmitted-light/haze approximation; continuous irregular world-space water-wave normals and view-dependent moon reflection. Warm beams and complete weather/streaming remain pending.','changed_shaders':{n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ['cloud_surface.gdshader','open_water.gdshader']},'production_modified':False}
(out/'change-report-27a.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
a=(R/'captures/coast_environment_21c.gd').read_text().replace('NativeCoastalSky21b','NativeCoastalSky27a')
a=a.replace('Temporary actual shader, scene light and sky changes; no fullscreen tint. Streaming transitions and other weather states remain unimplemented.','27a actual cloud geometry, cloud transmission/haze and irregular world-water normals;21c lights and moon retained. No fullscreen tint. Beams, streaming transitions and other weather states remain unimplemented.')
(R/'captures/coast_environment_27a.gd').write_text(a,encoding='utf-8')
print('27a environment candidate prepared',flush=True)
