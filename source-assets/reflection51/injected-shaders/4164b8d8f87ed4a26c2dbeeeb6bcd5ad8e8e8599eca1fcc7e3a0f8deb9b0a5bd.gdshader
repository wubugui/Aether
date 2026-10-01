shader_type spatial;
/* LAKE51_GLOBAL_BEGIN */
varying float lake51_reflection_world_y;
uniform bool lake51_reflection_clip_enabled = true;
uniform float lake51_reflection_plane_y = 0.0;
/* LAKE51_GLOBAL_END */

uniform vec3 scene_fill=vec3(1.);
uniform vec3 scene_haze=vec3(.76,.80,.78);
uniform vec3 scene_sun_direction=vec3(-.48,.82,.30);

render_mode diffuse_lambert, specular_disabled, cull_disabled;
varying vec3 world_point;
varying vec3 terrain_normal;
varying flat float meadow_moisture;

vec3 linear_to_srgb(vec3 c) {
    return mix(c*12.92,1.055*pow(max(c,vec3(0)),vec3(1./2.4))-.055,step(vec3(.0031308),c));
}
vec3 srgb_to_linear(vec3 c) {
    return mix(c/12.92,pow((c+.055)/1.055,vec3(2.4)),step(vec3(.04045),c));
}
float hash21(vec2 p) {
    return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);
}
float land_noise(vec2 p) {
    vec2 i=floor(p), f=fract(p);
    f=f*f*(3.-2.*f);
    return mix(mix(hash21(i),hash21(i+vec2(1,0)),f.x),
               mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),f.x),f.y);
}
void vertex() {
    world_point=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
    terrain_normal=normalize(mat3(MODEL_MATRIX)*NORMAL);
    float broad=land_noise(world_point.xz/128.+vec2(11.8,-3.6));
    float middle=land_noise(world_point.xz/45.+vec2(-7.3,18.2));
    // Flat interpolation keeps a single biome sample over each actual mesh
    // triangle, taken from its provoking vertex. This is not a centroid
    // bake, additional geometry, or a screen-aligned color mask.
    meadow_moisture=smoothstep(.28,.70,broad*.74+middle*.26);

/* LAKE51_VERTEX_BEGIN */
    lake51_reflection_world_y = (MODEL_MATRIX * vec4(VERTEX, 1.0)).y;
/* LAKE51_VERTEX_END */
}
void fragment() {
/* LAKE51_FRAGMENT_BEGIN */
    if (lake51_reflection_clip_enabled && (CAMERA_VISIBLE_LAYERS & 524288u) != 0u && lake51_reflection_world_y < lake51_reflection_plane_y) { discard; }
/* LAKE51_FRAGMENT_END */

    vec3 original=linear_to_srgb(COLOR.rgb);
    float grass=smoothstep(.055,.12,min(original.r,original.g)-original.b)
        *smoothstep(3.2,7.,world_point.y);
    vec3 n=normalize(terrain_normal);
    float sheltered=(1.-max(0.,dot(n,normalize(scene_sun_direction))));
    float moisture=clamp(meadow_moisture*.83+sheltered*.20,0.,1.);
    vec3 dry=vec3(.73,.745,.46);
    vec3 meadow=vec3(.46,.565,.345);
    vec3 pigment=mix(dry,meadow,moisture);
    float original_light=clamp(dot(original,vec3(.2126,.7152,.0722))/.69,.78,1.20);
    pigment*=mix(1.,original_light,.70);
    pigment*=.89+.11*max(0.,dot(n,normalize(scene_sun_direction)));
    pigment=mix(original,pigment,grass*.72);
    ALBEDO=mix(srgb_to_linear(pigment),pigment,.30);
    ROUGHNESS=1.;
    float distance_to_camera=distance(INV_VIEW_MATRIX[3].xyz,world_point);
    float low_air=1.-smoothstep(70.,250.,world_point.y);
    float haze=(1.-exp(-max(distance_to_camera-650.,0.)*.00038))*low_air;
    EMISSION=ALBEDO*.72*(1.-haze)+scene_haze*haze;
    ALBEDO*=1.-haze;

ALBEDO*=mix(vec3(1.),scene_fill,.35);
EMISSION*=scene_fill;
}
void light() {
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.)*.32/PI;
}
