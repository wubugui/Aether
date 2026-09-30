shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;
uniform sampler2D surface_original : source_color, filter_linear_mipmap, repeat_disable;
uniform sampler2D surface_occluded : source_color, filter_linear_mipmap, repeat_disable;
uniform float phase=0.0;
varying vec3 world_point;
void vertex() {world_point=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}

float region(vec2 p, vec4 box, float feather) {
    vec2 a=smoothstep(box.xy-feather,box.xy,p);
    vec2 b=1.0-smoothstep(box.zw,box.zw+feather,p);
    return a.x*a.y*b.x*b.y;
}
void fragment() {
    // Model UV coordinates are exported from Blender; they never follow the camera.
    vec2 p=UV*vec2(1672.0,941.0);
    float mask=region(p,vec4(651.0,350.0,905.0,610.0),9.0);
    mask=max(mask,region(p,vec4(17.0,680.0,217.0,878.0),12.0));
    mask=max(mask,region(p,vec4(1462.0,724.0,1637.0,900.0),12.0));
    vec3 c=mix(texture(surface_original,UV).rgb,texture(surface_occluded,UV).rgb,mask);
    float boundary=smoothstep(-.045,0.,UV.x)*(1.-smoothstep(1.,1.045,UV.x));
    boundary*=smoothstep(-.045,0.,UV.y)*(1.-smoothstep(1.,1.045,UV.y));
    float water=1.-step(.10,abs(world_point.y));
    float haze=1.-exp(-length(world_point-CAMERA_POSITION_WORLD)*.0008);
    vec3 sea=mix(vec3(.27,.53,.68),vec3(.7882,.8784,.9255),haze);
    sea+=sin(world_point.x*.017)*sin(world_point.z*.022)*.007;
    vec3 land=mix(vec3(.60,.65,.44),vec3(.7882,.8784,.9255),haze);
    vec3 continuation=mix(land,sea,water);
    if(!OUTPUT_IS_SRGB)continuation=pow(continuation,vec3(2.2));
    ALBEDO=mix(continuation,c,boundary);
}
