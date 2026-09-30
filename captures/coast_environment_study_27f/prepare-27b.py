from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1];out=R/'captures/coast_environment_study_27b';assert not out.exists();shutil.copytree(R/'captures/coast_environment_study_27a',out)
p=(out/'open_water.gdshader').read_text()
p=p.replace('float swell=.24*sin(q.y*.34+warp);','float swell=.68*(sea_noise(q*vec2(.034,.11)+vec2(9.2,3.6))-.5);')
anchor='void vertex() {'
facet='''vec3 sea_facet_normal(vec2 p){
    vec2 wind=normalize(vec2(.83,-.56));vec2 across=vec2(-wind.y,wind.x);
    vec2 q=vec2(dot(p,wind),dot(p,across));q.y+=world_time*.55;
    vec2 cell_size=vec2(10.5,3.6);vec2 g=q/cell_size;
    vec2 id=floor(g);float best=1e10;vec2 chosen=vec2(0.);
    // Irregular world-space wave facets, with normals sampled from one shared
    // continuous height field. The observer does not define their positions.
    for(int y=-1;y<=1;y++){
        for(int x=-1;x<=1;x++){
            vec2 key=id+vec2(float(x),float(y));
            vec2 site=key+vec2(.1+.8*sea_hash(key),.1+.8*sea_hash(key+vec2(71.,19.)));
            float d=dot(g-site,g-site);
            if(d<best){best=d;chosen=site;}
        }
    }
    vec2 site_q=chosen*cell_size;site_q.y-=world_time*.55;
    vec2 at=wind*site_q.x+across*site_q.y;
    float e=.24;
    float dx=(sea_height(at+vec2(e,0.))-sea_height(at-vec2(e,0.)))/(2.*e);
    float dz=(sea_height(at+vec2(0.,e))-sea_height(at-vec2(0.,e)))/(2.*e);
    return normalize(vec3(-dx,1.,-dz));
}
'''
p=p.replace(anchor,facet+anchor,1)
start=p.index('    float e=.18;');end=p.index('    vec3 view_direction=',start)
p=p[:start]+'    vec3 wave_normal=sea_facet_normal(world_point.xz);\n'+p[end:]
p=p.replace('),65.);','),90.);')
(out/'open_water.gdshader').write_text(p,encoding='utf-8');shutil.copy2(__file__,out/'prepare-27b.py')
(out/'change-report-27b.json').write_text(json.dumps({'label':'27b','scope':'Replace27a scanline-like smooth highlights with irregular world-space wave facets sampling a common continuous height field; new native curved cloud lobes. No screen-fixed reflection or claim of complete weather.','water_sha256':hashlib.sha256((out/'open_water.gdshader').read_bytes()).hexdigest(),'production_modified':False},indent=2),encoding='utf-8')
a=(R/'captures/coast_environment_27a.gd').read_text().replace('27a','27b');(R/'captures/coast_environment_27b.gd').write_text(a,encoding='utf-8')
driver=(R/'tools/render_coast_environment_27a.py').read_text().replace('27a','27b');(R/'tools/render_coast_environment_27b.py').write_text(driver,encoding='utf-8')
print('27b environment candidate prepared')
