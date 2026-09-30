"""Replace discontinuous sampled Voronoi slopes with a shared wave triangulation."""
from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1]
out=R/'captures/coast_environment_study_27e';assert not out.exists()
shutil.copytree(R/'captures/coast_environment_study_27d',out)
p=(out/'open_water.gdshader').read_text(encoding='utf-8')
start=p.index('vec3 sea_facet_normal(');end=p.index('void vertex()',start)
replacement='''// Shared jittered vertices define a continuous piecewise-planar height field.
// This supplies material normals; the existing sea geometry is still flat.
float sea_cross(vec2 a,vec2 b){return a.x*b.y-a.y*b.x;}
vec2 sea_vertex(vec2 id){
    vec2 offset=vec2(sea_hash(id),sea_hash(id+vec2(71.,19.)))-.5;
    return (id+offset*.32)*vec2(4.8,2.6);
}
bool sea_inside(vec2 p,vec2 a,vec2 b,vec2 c){
    return sea_cross(b-a,p-a)>=-.00001 && sea_cross(c-b,p-b)>=-.00001 && sea_cross(a-c,p-c)>=-.00001;
}
vec3 sea_facet_normal(vec2 p){
    vec2 wind=normalize(vec2(.83,-.56));vec2 across=vec2(-wind.y,wind.x);
    vec2 q=vec2(dot(p,wind),dot(p,across));q.y+=world_time*.55;
    vec2 cell=floor(q/vec2(4.8,2.6));
    vec2 va=vec2(0.);vec2 vb=vec2(1.,0.);vec2 vc=vec2(0.,1.);bool found=false;
    for(int y=-1;y<=1;y++){
        for(int x=-1;x<=1;x++){
            vec2 id=cell+vec2(float(x),float(y));
            vec2 a=sea_vertex(id),b=sea_vertex(id+vec2(1.,0.));
            vec2 c=sea_vertex(id+vec2(1.,1.)),d=sea_vertex(id+vec2(0.,1.));
            if(mod(id.x+id.y,2.)<1.){
                if(!found && sea_inside(q,a,b,c)){va=a;vb=b;vc=c;found=true;}
                if(!found && sea_inside(q,a,c,d)){va=a;vb=c;vc=d;found=true;}
            }else{
                if(!found && sea_inside(q,a,b,d)){va=a;vb=b;vc=d;found=true;}
                if(!found && sea_inside(q,b,c,d)){va=b;vb=c;vc=d;found=true;}
            }
        }
    }
    va.y-=world_time*.55;vb.y-=world_time*.55;vc.y-=world_time*.55;
    vec2 wa=wind*va.x+across*va.y,wb=wind*vb.x+across*vb.y,wc=wind*vc.x+across*vc.y;
    vec3 a3=vec3(wa.x,sea_height(wa),wa.y),b3=vec3(wb.x,sea_height(wb),wb.y),c3=vec3(wc.x,sea_height(wc),wc.y);
    vec3 n=normalize(cross(c3-a3,b3-a3));
    return n.y<0.?-n:n;
}
'''
p=p[:start]+replacement+p[end:]
p=p.replace('),110.);','),140.);')
(out/'open_water.gdshader').write_text(p,encoding='utf-8')
p=(R/'captures/coast_environment_27d.gd').read_text(encoding='utf-8').replace('27d','27e')
(R/'captures/coast_environment_27e.gd').write_text(p,encoding='utf-8')
p=(R/'tools/render_coast_environment_27d.py').read_text(encoding='utf-8').replace('27d','27e')
p=p.replace("sky=root/'captures/coastal_sky_assets_27e';gate=root/'reviews/round-27e-sky-native-check.json'","sky=root/'captures/coastal_sky_assets_27d';gate=root/'reviews/round-27d-sky-native-check.json'")
p=p.replace("require(check['passed'],'27e actual saved sky gate failed')","require(check['passed'],'Unchanged27d actual saved sky gate failed')")
p=p.replace("('night-reference-later','reference-coast-near','night',18),('day-cloud-back','cloud-back','day',0)","('night-reference-later','reference-coast-near','night',18)")
p=p.replace('Five affected GPU samples of27e cloud/water, including an actual cloud rear view.','Four affected GPU samples of27e shared-triangle water, retaining exact27d cloud assets.')
p=p.replace('New Blender27e cloud volumes and spatial cloud lighting/haze; irregular world-space wave normals and view-dependent moon glints over fixed26b native world assembly.','Exact saved27d cloud volumes and layout retained.27e water normals come from shared jittered triangular wave heights, with view-dependent moon glints over fixed26b native world assembly.')
(R/'tools/render_coast_environment_27e.py').write_text(p,encoding='utf-8')
shutil.copy2(__file__,out/'prepare-27e.py')
(out/'change-report-27e.json').write_text(json.dumps({'scope':'Water-only revision. Every jittered grid vertex has one common wave height; alternating shared-edge triangles derive actual plane normals. This is a coherent continuous virtual height field but does not displace the sea mesh. Exact27d native cloud geometry and fixed27c positions retained. Four affected GPU samples planned; no repeated cloud native gate or rear render needed.','water_sha256':hashlib.sha256((out/'open_water.gdshader').read_bytes()).hexdigest(),'production_modified':False},indent=2),encoding='utf-8')
print('27e shared wave triangles prepared;27d native sky reused byte for byte')
