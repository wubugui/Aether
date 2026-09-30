shader_type sky;
void sky() {
    float a=-0.06108652;
    float vy=cos(a)*EYEDIR.y+sin(a)*EYEDIR.z;
    float vz=-sin(a)*EYEDIR.y+cos(a)*EYEDIR.z;
    float y=clamp((0.5-vy/max(0.05,-vz)/0.9326153)*941.0,0.0,941.0);
    vec3 c=mix(vec3(115.,161.,210.),vec3(126.,173.,217.),clamp(y/100.,0.,1.));
    c=mix(c,vec3(144.,190.,223.),clamp((y-100.)/100.,0.,1.));
    c=mix(c,vec3(173.,209.,231.),clamp((y-200.)/100.,0.,1.));
    c=mix(c,vec3(201.,224.,236.),clamp((y-300.)/90.,0.,1.));
    COLOR=c/255.0;
}
