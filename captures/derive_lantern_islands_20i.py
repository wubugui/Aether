"""Rework coastal fracture planes, rock/grass shoulders and terrain-conforming paths."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lantern_islands_20i.py';assert not target.exists()
text=(root/'blender/model_lantern_islands_20h.py').read_text()
text=text[:text.index('# All landforms are retained')]
text=text.replace('lantern_islands_study_20h','lantern_islands_study_20i')
text=text.replace("soil=mat('Coast grass soil edge',(.061,.066,.032))","soil=mat('Coast grass soil edge',(.061,.066,.032))\npathmat=mat('Coast weathered stone footpath',(.145,.127,.089))")
old='    def ungraded(x,y):'
new='''    shoulders=([(-52,-38,20,9,6),(43,-32,18,10,8),(52,31,19,12,6),(-37,32,15,10,4)] if variant==0 else
               ([(-40,-31,18,10,5),(30,32,15,13,6),(36,-20,12,8,4)] if variant==1 else
                [(-27,-24,13,10,4),(23,-9,11,9,4),(-12,38,12,9,3)]))
    def ridge_value(x,y):
        a,b=x/sx,y/sy
        return sum(h*math.exp(-2.2*(((a-cx)/wx)**2+((b-cy)/wy)**2)) for cx,cy,wx,wy,h in shoulders)
    def ungraded(x,y):'''
assert text.count(old)==1;text=text.replace(old,new)
text=text.replace('a,b=x/sx,y/sy\n        if variant==0:','a,b=x/sx,y/sy\n        added=ridge_value(x,y)\n        if variant==0:')
text=text.replace('return max(3.1,plateau+','return added+max(3.1,plateau+').replace('return max(3.4,plateau+','return added+max(3.4,plateau+').replace('return max(2.8,plateau+','return added+max(2.8,plateau+')
text=text.replace("cap=mesh(name+' sculpted grass terrain',top+lower,capfaces,grass);cap.data.materials.append(soil)","cap=mesh(name+' grass and exposed rock terrain',top+lower,capfaces,grass);cap.data.materials.append(soil);cap.data.materials.append(rockface)")
old='''    for i,p in enumerate(cap.data.polygons):
        if i>=len(triangles):p.material_index=1'''
new='''    for i,p in enumerate(cap.data.polygons):
        if i>=len(triangles):p.material_index=1
        else:
            a,b=p.center.x/sx,p.center.y/sy
            exposure=min(((a-cx)/wx)**2+((b-cy)/wy)**2 for cx,cy,wx,wy,h in shoulders)
            # Material boundaries follow actual raised rock shoulders and steep faces.
            if exposure<.70 or p.normal.z<.72:p.material_index=2'''
assert text.count(old)==1;text=text.replace(old,new)
text=text.replace('for level in range(3):','for level in range(4):')
old='''            else:point=(x*(1+k)/2,y*(1+k)/2,height(boundary[i][0],boundary[i][1])*.48)'''
new='''            else:
                before=Vector(coast[(i-1)%count]);after=Vector(coast[(i+1)%count])
                direction=after-before;outward=Vector((direction.y,-direction.x)).normalized()
                t=.34 if level==2 else .76
                shift=([-.6,2.8,-1.7,.8,3.2,-1.1,.4][(i+variant)%7] if level==2 else [1.8,-1.2,2.6,-.7,.3,-2.1,1.1][(i+variant*2)%7])*sx
                p=Vector((x,y)).lerp(Vector(boundary[i]),t)+outward*shift
                h=height(boundary[i][0],boundary[i][1])
                fraction=(.28+.095*math.sin(i*.85+variant)) if level==2 else (.69+.095*math.sin(i*.65+1.2+variant))
                point=(p.x,p.y,max(1.7,h*fraction))'''
assert text.count(old)==1;text=text.replace(old,new)
text=text.replace('index[source]=3*count+i','index[source]=4*count+i')
text=text.replace('if level<2 else index[j]','if level<3 else index[j]').replace('if level<2 else index[i]','if level<3 else index[i]')
text=text.replace('tuple(3*count+i for i in tri)','tuple(4*count+i for i in tri)')
start=text.index("    freeze(name,'Distinct concave")
text=text[:start]+'''    # The route surface is clipped against the existing terrain triangles, so it
    # follows their actual planes rather than an approximate analytic height.
    routes=([
        [(-22,-9),(-21,-12),(-15,-12),(-9,-9),(0,-7),(6,0),(6,6),(1.0,9.0)],
        [(18.15,-11.63),(13,-14),(7,-12),(0,-7)],
        [(-21,-12),(-33,-18),(-44,-25),(-59,-34),(-69,-37)]] if variant==0 else
       ([ [(-14.57,-8.34),(-9,-11),(-2,-10),(5,-5),(7,0),(4.815,3.347)],
          [(-9,-11),(-19,-18),(-30,-27),(-41,-30)] ] if variant==1 else
        [ [(-12.7,-18.64),(-7,-20),(0,-15),(6,-9),(9,-2),(8,3),(5.4,3.36)] ]))
    ribbons=[];width=1.7 if variant==0 else 1.35
    for route in routes:
        left=[];right=[]
        for i,point in enumerate(route):
            prior=Vector(route[max(0,i-1)]);following=Vector(route[min(len(route)-1,i+1)])
            tangent=(following-prior).normalized();normal=Vector((-tangent.y,tangent.x))
            left.append(Vector(point)+normal*width/2);right.append(Vector(point)-normal*width/2)
        ribbon=left+list(reversed(right))
        assert all(inside(p.x,p.y,boundary) for p in ribbon),'Path route crosses island boundary'
        ribbons.append(ribbon)
    pathcoords=[Vector(p) for p in verts2]
    constraints=list(edge_counts)
    loops=[]
    for ribbon in ribbons:
        ids=list(range(len(pathcoords),len(pathcoords)+len(ribbon)));pathcoords+=ribbon;loops.append(ids)
    pv,pe,pt,_,_,_=delaunay_2d_cdt(pathcoords,constraints,loops,1,.00001)
    selected=[]
    for tri in pt:
        center=sum((pv[i] for i in tri),Vector((0,0)))/len(tri)
        if any(inside(center.x,center.y,ribbon) for ribbon in ribbons):selected.append(tri)
    def surface_at(p):
        for tri in triangles:
            a,b,c=[Vector(top[i]) for i in tri]
            det=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y)
            if abs(det)<1e-12:continue
            u=((b.y-c.y)*(p.x-c.x)+(c.x-b.x)*(p.y-c.y))/det
            v=((c.y-a.y)*(p.x-c.x)+(a.x-c.x)*(p.y-c.y))/det;w=1-u-v
            if min(u,v,w)>-1e-4:return u*a.z+v*b.z+w*c.z
        raise RuntimeError('Path point outside actual terrain '+str(p))
    used=sorted(set(i for tri in selected for i in tri));lookup={i:j for j,i in enumerate(used)}
    pathverts=[(pv[i].x,pv[i].y,surface_at(pv[i])+.045) for i in used];pn=len(pathverts)
    pathfaces=[tuple(lookup[i] for i in tri) for tri in selected]
    pathcounts={}
    for tri in pathfaces:
        for i in range(3):
            edge=tuple(sorted((tri[i],tri[(i+1)%3])));pathcounts[edge]=pathcounts.get(edge,0)+1
    pathfaces+=[tuple(i+pn for i in reversed(tri)) for tri in list(pathfaces)]
    pathfaces+=[(a,b,b+pn,a+pn) for (a,b),nuse in pathcounts.items() if nuse==1]
    pathverts+=[(x,y,z-.35) for x,y,z in list(pathverts)]
    mesh(name+' terrain fitted keeper paths',pathverts,pathfaces,pathmat)
    bpy.context.scene['path_scope']='Detailed solid footpath surface on actual triangulated terrain; landing, treads and full walking validation incomplete.'
    bpy.context.scene['path_routes_blender_xy']=json.dumps(routes)
    freeze(name,'Inclined and offset cliff fracture bands, raised exposed rock shoulders and actual terrain-fitted keeper routes. Visual/site acceptance pending.')

island('island_a',1.,1.,24.,0)
island('island_b',.75,.66,18.,1)
island('island_c',.56,.54,14.,2)
prior=ROOT/'captures/lantern_islands_study_20h'
for record in json.loads((prior/'model-report.json').read_text())['assets']:
    if record['name'].startswith('island_'):continue
    for extension in ['.blend','.glb']:shutil.copy2(prior/(record['name']+extension),OUT/(record['name']+extension))
    reports.append(record)
report={'label':'20i','production_modified':False,'reference_images':['1126','1342','1218'],'assets':reports,'scope':'Three locally remodeled islands with terrain-fitted paths; accepted keeper house and three reef models retained from20h. No world regeneration or scene acceptance.'}
(OUT/'model-report.json').write_text(json.dumps(report,indent=2))
print('LANTERN COAST KIT BUILT '+json.dumps({'assets':len(reports),'parts':sum(r['parts'] for r in reports),'all_native_solids_passed':all(r['native_closed_solid_check_passed'] for r in reports)}),flush=True)
'''
target.write_text(text);print(target)
