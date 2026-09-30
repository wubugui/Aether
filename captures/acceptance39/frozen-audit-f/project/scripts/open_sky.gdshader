shader_type sky;
void sky() {
    float altitude=clamp(EYEDIR.y,0.,1.);
    vec3 horizon=vec3(.815,.905,.940);
    vec3 zenith=vec3(.440,.630,.837);
    vec3 c=mix(horizon,zenith,pow(clamp(altitude/.33,0.,1.),.85));
    vec3 sun=normalize(vec3(-.48,.82,.30));
    float glow=pow(max(dot(EYEDIR,sun),0.),96.);
    COLOR=c+vec3(.13,.12,.07)*glow;
}
