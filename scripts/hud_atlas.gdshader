shader_type canvas_item;
uniform float heading=0.0;
uniform float fuel=0.62;
uniform float shield=0.71;
uniform float health=0.74;
float box(vec2 p,vec4 r) {return step(r.x,p.x)*step(r.y,p.y)*step(p.x,r.z)*step(p.y,r.w);}
float disk(vec2 p,vec2 c,float r) {return 1.0-smoothstep(r-.6,r+.4,length(p-c));}
float hexagon(vec2 p,vec2 c,float r) {
    vec2 q=abs(p-c);
    return 1.0-smoothstep(r*.8660254-.5,r*.8660254+.5,max(q.x,.5*q.x+.8660254*q.y));
}
float badge(vec2 p,float y) {
    float a=disk(p,vec2(61.,y),31.8);
    a=max(a,box(p,vec4(29.,y-15.,34.,y+17.)));
    a=max(a,box(p,vec4(58.,y-35.,64.,y+35.)));
    float b=box(p,vec4(86.,y-8.,328.,y+17.));
    vec2 q=p-vec2(327.,y+4.);
    b=max(b,step(0.,q.x)*step(q.x+abs(q.y)*.87,11.5));
    return max(a,b);
}
void fragment() {
    vec2 p=UV*vec2(1672.,941.);
    float mask=max(badge(p,64.),max(badge(p,133.),badge(p,202.)));
    mask=max(mask,box(p,vec4(551.,69.,1122.,76.)));
    mask=max(mask,box(p,vec4(551.,57.,569.,87.)));
    mask=max(mask,box(p,vec4(1103.,57.,1124.,88.)));
    mask=max(mask,box(p,vec4(822.,57.,846.,88.)));
    mask=max(mask,box(p,vec4(818.,96.,850.,115.)));
    for(int i=0;i<17;i++) {
        float x=674.+float(i)*19.5;
        mask=max(mask,box(p,vec4(x-1.5,65.,x+2.,79.)));
    }
    mask=max(mask,disk(p,vec2(1555.,125.),89.));
    for(int i=0;i<4;i++) {
        float t=float(i)*1.5707963;
        vec2 c=vec2(1555.,125.)+vec2(cos(t),sin(t))*90.;
        mask=max(mask,disk(p,c,9.5));
    }
    mask=max(mask,box(p,vec4(1544.,18.,1566.,44.)));
    mask=max(mask,hexagon(p,vec2(104.,732.),43.5));
    mask=max(mask,hexagon(p,vec2(72.,829.),44.5));
    mask=max(mask,hexagon(p,vec2(172.,829.),44.5));
    mask=max(mask,disk(p,vec2(1550.,811.),80.));
    vec2 uv=UV;
    vec2 c=p.y<400.?vec2(1555.,125.):vec2(1550.,811.);
    float radius=p.y<400.?33.:52.;
    if(length(p-c)<radius) {
        float a=heading;
        uv=(c+mat2(vec2(cos(a),-sin(a)),vec2(sin(a),cos(a)))*(p-c))/vec2(1672.,941.);
    }
    vec4 sampled=texture(TEXTURE,uv);
    if(p.x>540.&&p.x<1140.&&p.y<125.)
        mask*=1.-smoothstep(.035,.10,sampled.b-sampled.r);
    for(int i=0;i<3;i++) {
        float cy=64.+float(i)*69.;
        float value=i==0?fuel:(i==1?shield:health);
        float initial=i==0?.62:(i==1?.71:.74);
        if(abs(value-initial)>.002&&box(p,vec4(93.,cy-3.,325.,cy+14.))>.5) {
            sampled.rgb=vec3(.31,.41,.46);
            if((p.x-93.)/232.<value&&mod(p.x-93.,28.6)<26.)
                sampled.rgb=i==0?vec3(.80,.55,.27):(i==1?vec3(.60,.67,.52):vec3(.74,.40,.39));
        }
    }
    COLOR=vec4(sampled.rgb,sampled.a*mask);
}
