from pathlib import Path
import shutil, json, hashlib
R=Path(__file__).resolve().parents[1]
OUT=R/'captures/storm_study_35a'
if OUT.exists():
    assert not (OUT/'design-plan.json').exists(), 'Completed preparation cannot be rerun'
    failure=R/'captures/storm_study_35a_prepare_failure1'
    assert not failure.exists(), 'Only the recorded partial preparation may be resumed once'
    shutil.copytree(OUT,failure)
    (failure/'failure.txt').write_text('First preparation stopped on missing wood_surface world-position varying. No GPU was run. Partial files retained before source-aware repair.\n')
else:
    OUT.mkdir()
P=R/'captures/validation_runs/water-34e-20260909T000818Z-086f9efe84964e12b961d88e6587cb3b/study-inputs'
for p in (P/'new-environment27f').glob('*.gdshader'):shutil.copy2(p,OUT/p.name)
if not (OUT/'cloud-assets').exists():shutil.copytree(R/'captures/storm_cloud_assets_35a',OUT/'cloud-assets')
shutil.copy2(R/'tools/storm_front_35a.gd',OUT/'storm_front_35a.gd')
shutil.copy2(__file__,OUT/'builder.py')

common='''
uniform float storm_flash=0.;
uniform vec3 storm_camera=vec3(-2350.,420.,-1300.);
float storm35_mask(vec3 p){
    float edge=-2350.+150.*sin((p.z+3500.)*.0007);
    return (1.-smoothstep(-450.,450.,p.x-edge))*(1.-smoothstep(5200.,6800.,abs(p.z+3500.)))*smoothstep(-12000.,-10000.,p.x);
}
float storm35_flash(vec3 p){
    float f=0.;
    for(int i=0;i<3;i++){
        vec3 c=vec3(-3450.-float(i)*440.,420.,-4000.-float(i)*1600.);
        f+=exp(-length((p-c)/vec3(1150.,850.,1150.))*1.6);
    }
    return f*storm_flash;
}
float storm35_air(vec3 p){
    vec3 ray=p-storm_camera;float density=0.;
    for(int i=0;i<4;i++){
        vec3 q=storm_camera+ray*((float(i)+.5)/4.);
        density+=storm35_mask(q)*(1.-smoothstep(600.,1600.,q.y));
    }
    return 1.-exp(-length(ray)*.00011*density/4.);
}
'''
(OUT/'storm_common.gdshaderinc').write_text(common,encoding='utf-8')

def insert_fragment_end(s, code):
    start=s.index('void fragment()')
    opening=s.index('{',start);depth=1;i=opening+1
    while depth:
        if s[i]=='{':depth+=1
        elif s[i]=='}':depth-=1
        i+=1
    return s[:i-1]+code+'\n'+s[i-1:]

for name in ['terrain_native','world_surface','wood_surface','cliff_surface','ship_surface']:
    p=OUT/(name+'.gdshader');s=p.read_text()
    s=s.replace('shader_type spatial;', 'shader_type spatial;\n'+common)
    position='land_position' if name=='cliff_surface' else 'world_point'
    # All source shaders are inspected before injection; ship is invisible but
    # remains a consistent material binding if the existing vehicle is shown.
    if 'varying vec3 '+position not in s:
        s=s.replace('void vertex() {','varying vec3 world_point;\nvoid vertex() {\n    world_point=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;')
        assert 'varying vec3 world_point' in s, name
    code='''
    float storm=storm35_mask(POSITION);
    float storm_air=storm35_air(POSITION);
    EMISSION*=mix(vec3(1.13,.92,.59),vec3(.16,.23,.32),storm);
    ALBEDO*=mix(vec3(1.05,.91,.67),vec3(.45,.52,.63),storm);
    EMISSION+=ALBEDO*vec3(.55,.56,.90)*storm35_flash(POSITION)*1.4;
    EMISSION=mix(EMISSION,vec3(.11,.15,.21)+vec3(.22,.21,.32)*storm35_flash(POSITION),storm_air);
    ALBEDO*=1.-storm_air;
    ROUGHNESS=mix(ROUGHNESS,.58,storm);
'''.replace('POSITION',position)
    s=insert_fragment_end(s,code)
    s=s.replace('LIGHT_COLOR*ATTENUATION','LIGHT_COLOR*ATTENUATION*(1.-.90*storm35_mask('+position+'))')
    p.write_text(s,encoding='utf-8')

p=OUT/'open_water.gdshader';s=p.read_text()
s=s.replace('shader_type spatial;','shader_type spatial;\n'+common)
s=s.replace('return swell+crest+small;','return (swell+crest+small)*(1.+storm35_mask(vec3(p.x,0.,p.y))*.75);')
s=insert_fragment_end(s,'''
    float storm=storm35_mask(world_point);
    vec3 sun_center=vec3(-2278.,420.,-1300.)+normalize(vec3(.32,.14,-.94))*13000.;
    vec3 to_sun=normalize(sun_center-world_point);
    float sun_sep=acos(clamp(dot(reflected_ray,to_sun),-1.,1.));
    float sun_reflection=exp(-sun_sep*sun_sep/.006)*(1.-storm*.96);
    float crest_level=1.-wave_normal.y;
    float whitecaps=smoothstep(.032,.105,crest_level)*storm;
    vec3 storm_water=mix(vec3(.024,.055,.085),vec3(.26,.34,.40),whitecaps*.8);
    vec3 clear_water=EMISSION*vec3(.87,.94,.78)+vec3(1.1,.68,.23)*sun_reflection;
    EMISSION=mix(clear_water,storm_water,storm);
    EMISSION+=vec3(.34,.35,.65)*storm35_flash(world_point)*(whitecaps+.18);
    EMISSION=mix(EMISSION,vec3(.11,.15,.21),storm35_air(world_point));
    ALBEDO*=1.-storm*.85;
''')
s=s.replace('LIGHT_COLOR*ATTENUATION','LIGHT_COLOR*ATTENUATION*(1.-.9*storm35_mask(world_point))')
p.write_text(s,encoding='utf-8')

(OUT/'storm_cloud.gdshader').write_text('''shader_type spatial;
render_mode unshaded,cull_disabled,fog_disabled;
varying vec3 cloud_position;
varying vec3 cloud_normal;
'''+common+'''
void vertex(){cloud_position=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;cloud_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
    vec3 n=normalize(cloud_normal);
    float underside=smoothstep(-.85,.65,n.y);
    float sunward=max(dot(n,normalize(vec3(.32,.14,-.94))),0.);
    float edge=-2350.+150.*sin((cloud_position.z+3500.)*.0007);
    float edge_light=exp(-max(edge-cloud_position.x,0.)/450.);
    vec3 dark=mix(vec3(.021,.032,.047),vec3(.11,.14,.18),underside);
    vec3 warm=mix(vec3(.20,.16,.125),vec3(.76,.53,.28),sunward*.75+underside*.25);
    vec3 c=mix(dark,warm,edge_light*.86);
    c+=vec3(.38,.36,.59)*storm35_flash(cloud_position);
    float air=1.-exp(-distance(storm_camera,cloud_position)*.000035);
    ALBEDO=mix(c,vec3(.16,.18,.22),air*.65);
}
''',encoding='utf-8')

(OUT/'storm_native.gdshader').write_text('''shader_type spatial;
render_mode diffuse_lambert,cull_disabled,ambient_light_disabled;
uniform vec4 base_color:source_color=vec4(1.);
uniform sampler2D base_texture:source_color;
uniform bool has_texture=false;
uniform bool use_vertex_color=false;
uniform float base_roughness=1.;
uniform vec3 source_emission=vec3(0.);
varying vec3 native_position;
'''+common+'''
void vertex(){native_position=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
void fragment(){
    vec3 base=base_color.rgb;
    if(has_texture)base*=texture(base_texture,UV).rgb;
    if(use_vertex_color)base*=COLOR.rgb;
    float storm=storm35_mask(native_position);
    float air=storm35_air(native_position);
    ALBEDO=base*mix(vec3(1.,.87,.59),vec3(.45,.52,.63),storm)*(1.-air);
    EMISSION=base*mix(vec3(.65,.55,.35),vec3(.05,.085,.13),storm)+source_emission;
    EMISSION+=base*vec3(.55,.56,.90)*storm35_flash(native_position)*1.4;
    EMISSION=mix(EMISSION,vec3(.11,.15,.21),air);
    ROUGHNESS=mix(base_roughness,.55,storm);
}
void light(){DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*(1.-.9*storm35_mask(native_position))*max(dot(NORMAL,LIGHT),0.)*.35/PI;}
''',encoding='utf-8')

(OUT/'storm_sky.gdshader').write_text('''shader_type sky;
'''+common+'''
void sky(){
    vec3 ray=normalize(EYEDIR);float h=clamp(ray.y,0.,1.);
    vec3 sun=normalize(vec3(.32,.14,-.94));
    float glow=exp(-acos(clamp(dot(ray,sun),-1.,1.))*3.5);
    vec3 clear=mix(vec3(.94,.59,.24),vec3(.23,.38,.54),pow(h,.60));
    clear+=vec3(.52,.28,.05)*glow;
    float distance_to_layer=clamp((850.-storm_camera.y)/max(ray.y,.06),200.,12000.);
    float cloud_coverage=storm35_mask(storm_camera+ray*distance_to_layer);
    vec3 overcast=mix(vec3(.14,.19,.25),vec3(.027,.043,.065),pow(h,.6));
    COLOR=mix(clear,overcast,cloud_coverage*.90);
}
''',encoding='utf-8')

(OUT/'storm_rain.gdshader').write_text('''shader_type spatial;
render_mode unshaded,cull_disabled,depth_draw_never;
global uniform float world_time;
varying vec3 rain_position;
'''+common+'''
void vertex(){
    vec3 p=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
    float top=storm_camera.y+450.;
    float new_y=top-mod(top-p.y+world_time*150.,900.);
    VERTEX.y+=new_y-p.y;
    rain_position=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
}
void fragment(){
    float d=distance(storm_camera,rain_position);
    float fade=smoothstep(8.,25.,d)*(1.-smoothstep(450.,720.,d));
    float under_cloud=1.-smoothstep(560.,900.,rain_position.y);
    ALBEDO=vec3(.35,.43,.54)+vec3(.35,.33,.50)*storm35_flash(rain_position);
    ALPHA=.30*storm35_mask(rain_position)*fade*under_cloud;
}
''',encoding='utf-8')

hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file()}
(OUT/'design-plan.json').write_text(json.dumps(dict(label='35a',source_run=P.parent.name,
    files_sha256=hashes,scope='New native volumetric cloud groups + finite world-space front driving material light attenuation, air, waves, rain and local lightning. Existing land unchanged and remains incomplete. Discrete camera evidence planned, not full flight.',
    production_modified=False,full_reference_accepted=False),indent=2)+'\n',encoding='utf-8')
print('35a storm shaders prepared',len(hashes))
