"""Editable terrain-fitted harbor stone stairs and curved landings.
All geometry is local to each asset. Does not regenerate or overwrite the world.
"""
from pathlib import Path
import bpy,bmesh,math,json,shutil,hashlib
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'captures/headland_study_23e'
if OUT.exists():raise RuntimeError('Frozen study already exists')
OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
parts=[];reports=[]

def mat(name,rgb,metal=0,rough=.8):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    return m

rock=mat('Coast blue grey bedrock',(.043,.056,.066))
rockface=mat('Coast exposed fracture',(.070,.077,.080))
rockdark=mat('Coast tidal dark stone',(.028,.039,.046),rough=.62)
grass=mat('Coast short olive grass',(.050,.086,.018))
soil=mat('Coast grass soil edge',(.061,.066,.032))
plaster=mat('Keeper lime plaster',(.36,.32,.235))
stone=mat('Keeper sandstone foundations',(.195,.184,.158))
wood=mat('Keeper weathered oak',(.18,.10,.052))
roof=mat('Keeper terracotta tile',(.26,.105,.067))
roofedge=mat('Keeper darker roof seams',(.16,.064,.043))
metal=mat('Keeper dark forged bronze',(.135,.105,.072),metal=.35)
glass=mat('Keeper window glass',(.047,.073,.078),rough=.22)
dark=mat('Keeper chimney darkness',(.016,.019,.021))

def reset():
    global parts
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);parts=[]

def mesh(name,vertices,faces,material):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    data.materials.append(material);parts.append(obj)
    return obj

def box(name,center,size,material,rotation=0):
    x,y,z=size;cx,cy,cz=center
    verts=[(a*x/2,b*y/2,c*z/2) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    co,si=math.cos(rotation),math.sin(rotation)
    verts=[(cx+co*x-si*y,cy+si*x+co*y,cz+z) for x,y,z in verts]
    return mesh(name,verts,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],material)

def beam(name,a,b,width,depth,material):
    a,b=Vector(a),Vector(b);axis=(b-a).normalized()
    u=axis.cross(Vector((0,0,1)))
    if u.length<.01:u=axis.cross(Vector((0,1,0)))
    u.normalize();v=axis.cross(u).normalized()
    verts=[p+u*x*width/2+v*y*depth/2 for p in [a,b] for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    return mesh(name,verts,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],material)

def loft(name,rings,material):
    n=len(rings[0]);assert all(len(r)==n for r in rings)
    verts=[p for ring in rings for p in ring]
    faces=[tuple(reversed(range(n)))]
    for j in range(len(rings)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
    return mesh(name,verts,faces,material)

def freeze(name,scope):
    # Normalize and inspect the actual source mesh before its editable save.
    defects=[];volumes={}
    for obj in parts:
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
        if any(not e.is_manifold for e in bm.edges):defects.append([obj.name,'open/nonmanifold edge'])
        if any(f.calc_area()<1e-9 for f in bm.faces):defects.append([obj.name,'zero area'])
        volume=bm.calc_volume(signed=True);volumes[obj.name]=volume
        if volume<=0:defects.append([obj.name,'nonpositive signed volume'])
        bm.to_mesh(obj.data);bm.free();obj.data.update()
        obj['authoring_role']='Independent editable coastal scene component'
    report={'name':name,'scope':scope,'parts':len(parts),'vertices':sum(len(o.data.vertices) for o in parts),
            'polygons':sum(len(o.data.polygons) for o in parts),'native_closed_solid_check_passed':not defects,
            'defects':defects,'component_volumes_m3':volumes}
    bpy.context.scene['reference_images']='ref/1135.png;ref/1342.png'
    bpy.context.scene['scope']=scope
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))
    # Batch only the export copy by material, preserving all native components above.
    groups={}
    for o in parts:groups.setdefault(o.data.materials[0].name,[]).append(o)
    for material,objects in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        if len(objects)>1:bpy.ops.object.join()
        bpy.context.object.name=name+'_'+material
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
    report['export_mesh_nodes']=len(groups)
    report['source_sha256']=hashlib.sha256((OUT/(name+'.blend')).read_bytes()).hexdigest()
    report['glb_sha256']=hashlib.sha256((OUT/(name+'.glb')).read_bytes()).hexdigest()
    reports.append(report)
    if defects:raise RuntimeError('Native geometry rejected: '+str(defects))



layout_path=ROOT/'captures/headland_layout_23c/layout.json'
survey_path=ROOT/'captures/validation_runs/headland-vertices-23c-20260908T115702Z-aa6c2cb83361436081ef9228520432f4/survey/vertex-survey.json'
layout=json.loads(layout_path.read_text());survey=json.loads(survey_path.read_text())
assert survey['layout_sha256']==hashlib.sha256(layout_path.read_bytes()).hexdigest()
assert all(s['bed_y'] is not None for s in survey['samples'])
for source in [layout_path,survey_path]:shutil.copy2(source,OUT/source.name)
origin=layout['origin'];points=layout['vertices'];boundary=layout['boundary']
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
def segment(x,z,a,b):
    ax,az=a['position'];bx,bz=b['position'];dx,dz=bx-ax,bz-az
    t=max(0,min(1,((x-ax)*dx+(z-az)*dz)/(dx*dx+dz*dz)))
    return math.hypot(x-ax-t*dx,z-az-t*dz),t
def distances(x,z):
    coast=[];seams=[]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):
        d,t=segment(x,z,a,b)
        if a['height'] is not None and b['height'] is not None:
            coast.append((d,a['height']*(1-t)+b['height']*t))
        else:seams.append(d)
    d,h=min(coast)
    weights=[(1/max(.02,dd)**3,yy) for dd,yy in coast]
    continuous=sum(w*y for w,y in weights)/sum(w for w,y in weights)
    return d,continuous,min(seams)
def pad_distance(x,z,house):
    hx,_,hz=house['position'];c,s=math.cos(house['yaw']),math.sin(house['yaw'])
    u=c*(x-hx)-s*(z-hz);v=s*(x-hx)+c*(z-hz);wx,wz=house['pad_half_size']
    return math.hypot(max(0,abs(u)-wx),max(0,abs(v)-wz))
heights=[];ground=[]
for index,(x,_,z) in enumerate(points):
    sample=survey['samples'][index];assert sample['index']==index
    assert abs(sample['position'][0]-x)<.0001 and abs(sample['position'][2]-z)<.0001
    old=sample['position'][1];d,h,seam=distances(x,z)
    ridge=max(21*math.exp(-((x+2173)**2+(z+1760)**2)/11000),18*math.exp(-((x+2170)**2+(z+1885)**2)/7000))
    authored=h+min(12,d*.16)
    authored=authored*(1-smooth(d/90))+max(authored,ridge)*smooth(d/90)
    # Asymmetric authored rock ridges, separate from the shoreline interpolation.
    spines=[(-2177,-1720,40,48,34,-.35),(-2180,-1780,48,50,53,-.22),(-2142,-1820,34,60,44,.40),(-2180,-1890,40,48,57,.18),(-2210,-1962,31,34,58,-.2)]
    ridge_height=authored
    for rx,rz,peak,wx,wz,angle in spines:
        co,si=math.cos(angle),math.sin(angle);u=co*(x-rx)-si*(z-rz);v=si*(x-rx)+co*(z-rz)
        radius=max(abs(u)/wx,abs(v)/wz)
        ridge_height=max(ridge_height,authored+(peak-authored)*max(0,1-radius)**1.35)
    target=max(old+.05,ridge_height)
    nearest=sorted((pad_distance(x,z,house),house['position'][1]) for house in layout['houses'])
    if nearest[0][0]<.0001:target=nearest[0][1]
    elif nearest[0][0]<14:
        weights=[(max(0,1-dd/14)**2,yy) for dd,yy in nearest if dd<14]
        pad=sum(w*y for w,y in weights)/sum(w for w,y in weights)
        strength=1-smooth(nearest[0][0]/14);target=target*(1-strength)+pad*strength
    # Boundary blends below actual mainland; no visible perimeter riser is authored there.
    height=(old-.20)*(1-smooth(seam/24))+target*smooth(seam/24)
    heights.append(height);ground.append(old)
reset();n=len(points)
verts=[(p[0]-origin[0],-(p[2]-origin[2]),y) for p,y in zip(points,heights)]
verts += [(p[0]-origin[0],-(p[2]-origin[2]),min(-10.,survey['samples'][i]['bed_y']-2)) for i,p in enumerate(points)]
faces=[];tags=[]
for tri in layout['triangles']:
    faces.append(tuple(tri));tags.append('top')
    faces.append(tuple(i+n for i in reversed(tri)));tags.append('bottom')
for a,b in layout['border_edges']:
    pa,pb=Vector(verts[a]),Vector(verts[b]);center=(pa+pb)*.5
    x,z=center.x+origin[0],-center.y+origin[2];distance,_,seam=distances(x,z)
    if distance<.02 and seam>2:
        if (a+b)%2:faces.extend([(a,b,b+n),(a,b+n,a+n)])
        else:faces.extend([(a,b,a+n),(b,b+n,a+n)])
        tags.extend(['cliff','cliff'])
    else:faces.append((a,b,b+n,a+n));tags.append('buried_seam')
terrain=mesh('Mainland headland continuous bedrock and grass terraces',verts,faces,rock)
for material in [rockface,rockdark,grass,soil]:terrain.data.materials.append(material)
terrain.data.update()
for polygon,tag in zip(terrain.data.polygons,tags):
    center=polygon.center;d,_,_=distances(center.x+origin[0],-center.y+origin[2])
    normal=polygon.normal;slope=math.degrees(math.acos(min(1,abs(normal.z))))
    if tag=='top':polygon.material_index=3 if slope<27 and d>5 else (4 if slope<34 and d>12 else (1 if center.x*.18+center.y*.08>0 else 0))
    elif tag=='cliff':polygon.material_index=2 if center.z<-.5 else (1 if normal.x>.25 else 0)
    else:polygon.material_index=2
terrain['world_origin']=origin;terrain['survey_run']=survey['run_id'];terrain['role']='Closed local mainland extension with pad constraints, surveyed buried bottom and real inlet'
pad_report=[]
for house in layout['houses']:
    indices=[i for i,(x,_,z) in enumerate(points) if pad_distance(x,z,house)<.0001]
    errors=[abs(heights[i]-house['position'][1]) for i in indices]
    assert indices and max(errors)<.001,(house['name'],max(errors))
    pad_report.append({'house':house['name'],'vertices':indices,'max_height_error':max(errors)})
# Closed asymmetrical rock masses; designed below nearby house pads, not loose visual triangles.
rock_specs=[(-2272,-1742,10,9,4.2,-.25),(-2273,-1765,9,12,4.6,.3),(-2260,-1787,12,7,5.8,-.4),(-2240,-1806,11,7,3.4,.2),(-2204,-1828,7,10,2.,-.3),(-2224,-1849,10,7,2.4,.4),(-2250,-1864,8,9,3.,.5),(-2255,-1885,8,12,3.7,-.2),(-2238,-1907,10,8,6.2,.4),(-2226,-1940,8,9,4.3,.2),(-2260,-1990,8,12,5.3,-.3)]
rock_records=[]
for number,(x,z,wx,wz,top,angle) in enumerate(rock_specs):
    # Hand-shaped eight-vertex shoulder with tilted crown and an uneven seaward nose.
    local=[(-.92,-.6,-10),(.77,-.83,-10),(1.,.72,-10),(-.68,.96,-10),(-.62,-.47,top-.8),(.48,-.7,top+.6),(.66,.39,top-.2),(-.40,.58,top+1.2),(-1.13,.05,top-2.8)]
    co,si=math.cos(angle),math.sin(angle);vertices=[]
    for u,v,y in local:
        px=x+co*u*wx+si*v*wz;pz=z-si*u*wx+co*v*wz
        vertices.append((px-origin[0],-(pz-origin[2]),y))
    bm=bmesh.new()
    for p in vertices:bm.verts.new(p)
    bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    bm.verts.ensure_lookup_table();bm.verts.index_update()
    obj=mesh('Broad tidal buttress '+str(number),[tuple(v.co) for v in bm.verts],[tuple(v.index for v in f.verts) for f in bm.faces],rock);bm.free()
    obj.data.materials.append(rockface);obj.data.materials.append(rockdark)
    for polygon in obj.data.polygons:polygon.material_index=2 if polygon.center.z<-.6 else (1 if polygon.normal.x>.35 else 0)
    rock_records.append({'name':obj.name,'center':[x,0,z],'crown_y_max':top+1.2,'base_y':-10})
(OUT/'rock-buttresses.json').write_text(json.dumps(rock_records,indent=2))
freeze('mainland_headland','Closed editable local rock headland, nine constrained village terraces and actual original-ground mainland blend; no scene or route acceptance.')
(OUT/'terrain-design.json').write_text(json.dumps({'origin':origin,'heights':heights,'original_ground':ground,'pads':pad_report,'source_run':survey['run_id'],'limits':'Vertex and planar pad checks only; actual source reopen, collision, original terrain joins and visual fidelity remain to inspect.'},indent=2))

def wall(name,origin,tangent,normal,length,height,openings):
    origin,tangent,normal=Vector(origin),Vector(tangent),Vector(normal)
    xs=sorted(set([-length/2,length/2]+[v for a,b,c,d,kind in openings for v in [a,b]]))
    zs=sorted(set([.5,height]+[v for a,b,c,d,kind in openings for v in [c,d]]))
    filled={}
    for i in range(len(xs)-1):
        for j in range(len(zs)-1):
            u,z=(xs[i]+xs[i+1])/2,(zs[j]+zs[j+1])/2
            filled[i,j]=not any(a<u<b and c<z<d for a,b,c,d,kind in openings)
    verts=[];faces=[];lookup={}
    def vertex(u,z,depth):
        p=origin+tangent*u+normal*depth+Vector((0,0,z));key=tuple(round(v,6) for v in p)
        if key not in lookup:lookup[key]=len(verts);verts.append(p)
        return lookup[key]
    for (i,j),present in filled.items():
        if not present:continue
        a,b=xs[i:i+2];c,d=zs[j:j+2]
        front=[vertex(u,z,.22) for u,z in [(a,c),(b,c),(b,d),(a,d)]]
        back=[vertex(u,z,-.22) for u,z in [(a,c),(b,c),(b,d),(a,d)]]
        faces.extend([tuple(front),tuple(reversed(back))])
        for edge,neighbor in enumerate([(i,j-1),(i+1,j),(i,j+1),(i-1,j)]):
            if not filled.get(neighbor,False):faces.append((front[edge],back[edge],back[(edge+1)%4],front[(edge+1)%4]))
    mesh(name+' solid cut masonry',verts,faces,plaster)
    for k,(a,b,c,d,kind) in enumerate(openings):
        def p(u,z,depth=.25):return origin+tangent*u+normal*depth+Vector((0,0,z))
        border=.10
        for label,u1,z1,u2,z2 in [('sill',a-border,c,b+border,c),('lintel',a-border,d,b+border,d),('left',a,c,a,d),('right',b,c,b,d)]:
            beam(name+' '+kind+' '+str(k)+' '+label,p(u1,z1),p(u2,z2),.16,.18,wood)
        if kind=='window':
            pane=[p(u,z,depth) for depth in [.025,.06] for u,z in [(a,c),(b,c),(b,d),(a,d)]]
            mesh(name+' window glazing '+str(k),pane,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],glass)
            beam(name+' window vertical mullion '+str(k),p((a+b)/2,c,.28),p((a+b)/2,d,.28),.06,.08,wood)
            beam(name+' window crossbar '+str(k),p(a,(c+d)/2,.28),p(b,(c+d)/2,.28),.06,.08,wood)
            beam(name+' stone sill '+str(k),p(a-.18,c-.13,.25),p(b+.18,c-.13,.25),.30,.20,stone)
        else:
            for q in range(6):
                u=a+(b-a)*(q+.5)/6
                beam(name+' door oak board '+str(q),p(u,c,.04),p(u,d,.04),(b-a)/6-.012,.10,wood)
            for z in [c+.45,d-.45]:beam(name+' door hinge strap',p(a+.1,z,.14),p(b-.1,z,.14),.06,.055,metal)
            beam(name+' door handle',p(b-.25,c+1.0,.22),p(b-.25,c+1.25,.22),.04,.05,metal)


# Distinct native houses, real openings, deep eaves and individual thick roof shingles.
for name,width,depth,eave,ridge in [('fisher_cottage',5.5,7.6,3.3,5.65),('quay_workshop',8.2,6.2,3.5,5.25)]:
    reset();workshop=name=='quay_workshop';half=width/2;front=-depth/2
    box(name+' rubble footing',(0,0,-.15),(width+.6,depth+.6,1.),stone)
    box(name+' oak raised floor',(0,0,.42),(width,depth,.26),wood)
    door=1.35 if workshop else .7
    opening=[(-door,door,.5,2.9 if workshop else 2.6,'door')]
    if workshop:opening += [(-3.55,-2.35,1.4,2.75,'window'),(2.35,3.55,1.4,2.75,'window')]
    else:opening += [(1.3,2.3,1.35,2.6,'window'),(-2.3,-1.3,1.35,2.6,'window')]
    wall(name+' front',(0,front,0),(1,0,0),(0,-1,0),width,eave,opening)
    wall(name+' rear',(0,-front,0),(-1,0,0),(0,1,0),width,eave,[(-1.6,-.4,1.4,2.65,'window'),(.4,1.6,1.4,2.65,'window')])
    for side in [-1,1]:
        wall(name+' side '+str(side),(side*half,0,0),(0,side,0),(side,0,0),depth,eave,[(-2.3,-1.1,1.4,2.6,'window'),(1.1,2.3,1.4,2.6,'window')])
    for y in [front,-front]:
        loft(name+' masonry gable',[[(-half,y-.22,eave),(half,y-.22,eave),(0,y-.22,ridge-.13)],[(-half,y+.22,eave),(half,y+.22,eave),(0,y+.22,ridge-.13)]],plaster)
        beam(name+' verge',(-half-.3,y,eave-.03),(0,y,ridge),.15,.17,wood)
        beam(name+' verge',(0,y,ridge),(half+.3,y,eave-.03),.15,.17,wood)
    covering=roof if workshop else mat('Fisher muted russet shingles',(.19,.085,.055))
    span=half+.38;length=depth+.85;rows=6;pitch=.73
    for side in [-1,1]:
        for row in range(rows):
            a,b=row/rows,min(1,(row+1)/rows+.009);bias=(rows-row)*.018
            x0,x1=side*span*a,side*span*b;z0,z1=ridge-(ridge-eave)*a+bias,ridge-(ridge-eave)*b+bias
            for col in range(-1,math.ceil(length/pitch)+1):
                offset=.365 if row%2 else 0;ya=max(-length/2,-length/2+col*pitch+offset+.006);yb=min(length/2,-length/2+(col+1)*pitch+offset-.006)
                if yb-ya<.1:continue
                loft(name+' separate thick roof tile', [[(x0,ya,z0-.09),(x1,ya,z1-.09),(x1,yb,z1-.09),(x0,yb,z0-.09)],[(x0,ya,z0),(x1,ya,z1),(x1,yb,z1),(x0,yb,z0)]],covering)
        beam(name+' eaves fascia',(side*span,-length/2,eave),(side*span,length/2,eave),.18,.20,wood)
    for i in range(math.ceil(length/.8)):
        ya=-length/2+i*.8;yb=min(length/2,ya+.79)
        cross=[(-.16,ridge+.10),(.16,ridge+.10),(.15,ridge+.2),(0,ridge+.31),(-.15,ridge+.2)]
        loft(name+' ridge coping', [[(x,ya,z) for x,z in cross],[(x,yb,z) for x,z in cross]],covering)
    for x in [-half,half]:
        for y in [front,-front]:
            for i in range(5):box(name+' corner masonry quoin',(x,y,.8+i*.5),(.48,.48,.28),stone)
    for i,(distance,height) in enumerate([(1.15,.18),(.62,.35)]):box(name+' entry step '+str(i),(0,front-distance/2,height/2),(door*2+.3,distance,height),stone)
    canopy_width=3.25 if workshop else 2.5
    for x in [-canopy_width/2+.12,canopy_width/2-.12]:
        beam(name+' porch post',(x,front-1.28,0),(x,front-1.28,2.8),.16,.16,wood)
        beam(name+' canopy brace',(x,front-1.28,2.2),(x,front-.7,3.0),.12,.13,wood)
    loft(name+' thick canopy',[[(-canopy_width/2,front-1.42,2.8),(canopy_width/2,front-1.42,2.8),(canopy_width/2,front-.05,3.25),(-canopy_width/2,front-.05,3.25)],[(-canopy_width/2,front-1.42,2.95),(canopy_width/2,front-1.42,2.95),(canopy_width/2,front-.05,3.40),(-canopy_width/2,front-.05,3.40)]],covering)
    if workshop:
        for x in [-3.,3.]:
            box('Workshop front shutter',(x,front-.30,2.08),(1.13,.09,1.29),wood)
            for j in range(4):box('Workshop shutter board',(x-.44+j*.29,front-.37,2.08),(.25,.06,1.20),wood)
        beam('Workshop lifting beam',(0,front+.5,3.20),(0,front-1.55,3.20),.24,.24,wood)
    else:
        box('Fisher chimney masonry',(1.4,1.5,5.1),(.74,.80,2.1),stone)
        box('Fisher chimney cap',(1.4,1.5,6.22),(.94,1.,.16),stone)
        box('Fisher recessed chimney opening',(1.4,1.5,6.31),(.51,.55,.04),dark)
        # External racks are solid wood joinery, with separate crossed drying rails.
        for y in [-1.5,1.5]:beam('Fisher side rack post',(-half-.45,y,.0),(-half-.45,y,2.3),.12,.12,wood)
        for z in [.65,1.35,2.10]:beam('Fisher drying rail',(-half-.45,-1.5,z),(-half-.45,1.5,z),.09,.10,wood)
    freeze(name,'Independent editable '+name+' with real cut openings, thick separate roofing, entrance joinery, foundation and distinguishing fishing/workshop details; no furnished interior or scene acceptance.')
(OUT/'model-report.json').write_text(json.dumps({'label':'23e','production_modified':False,'assets':reports,'layout_sha256':survey['layout_sha256'],'survey_run':survey['run_id']},indent=2))
print('HEADLAND KIT BUILT '+str(len(reports))+' ASSETS',flush=True)
