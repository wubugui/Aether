shader_type sky;
// 38 reference rig sky: gradient + sun/moon glow + optional disc and stars.
uniform vec3 zenith=vec3(.440,.630,.837);
uniform vec3 horizon=vec3(.815,.905,.940);
uniform vec3 glow=vec3(.13,.12,.07);
uniform vec3 sun_dir=vec3(-.48,.82,.30);
uniform float disc=0.;
uniform float stars=0.;
float hash(vec3 p){p=fract(p*.3183099+.1);p*=17.;return fract(p.x*p.y*p.z*(p.x+p.y+p.z));}
void sky() {
    float altitude=clamp(EYEDIR.y,0.,1.);
    vec3 c=mix(horizon,zenith,pow(clamp(altitude/.33,0.,1.),.85));
    if(EYEDIR.y<0.) c=horizon*(.92+.08*(1.+EYEDIR.y));
    vec3 s=normalize(sun_dir);
    float d=max(dot(EYEDIR,s),0.);
    c+=glow*(pow(d,96.)+pow(d,8.)*.35+pow(d,2.)*.12);
    c+=vec3(1.,.97,.90)*disc*smoothstep(.99935,.99965,d);
    if(stars>.5){
        vec3 q=floor(EYEDIR*520.);
        float h=hash(q);
        c+=vec3(.85,.9,1.)*step(.9982,h)*smoothstep(.02,.25,EYEDIR.y)*stars;
    }
    COLOR=c;
}
