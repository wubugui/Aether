shader_type spatial;
render_mode unshaded,fog_disabled;
uniform vec3 moon_color=vec3(.7,.8,1.);
void fragment(){ALBEDO=moon_color;}
