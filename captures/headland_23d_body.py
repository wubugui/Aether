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
    d,h=min(coast);return d,h,min(seams)
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
    target=max(old+.05,authored)
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
        outward=Vector((pb.y-pa.y,-(pb.x-pa.x),0)).normalized()
        # Choose away from triangle interior, independent of boundary edge ordering.
        owner=next(t for t in layout['triangles'] if a in t and b in t)
        inner=Vector(verts[next(i for i in owner if i not in [a,b])])
        if outward.dot(inner-center)>0:outward=-outward
        toe=(Vector(verts[a+n])+Vector(verts[b+n]))*.5
        split=center.lerp(toe,.37+.11*math.sin((a+b)*1.29))+outward*min(2.8,(pa-pb).length*.18)
        mid=len(verts);verts.append(tuple(split))
        faces.extend([(a,b,mid),(b,b+n,mid),(b+n,a+n,mid),(a+n,a,mid)]);tags.extend(['cliff']*4)
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
freeze('mainland_headland','Closed editable local rock headland, nine constrained village terraces and actual original-ground mainland blend; no scene or route acceptance.')
(OUT/'terrain-design.json').write_text(json.dumps({'origin':origin,'heights':heights,'original_ground':ground,'pads':pad_report,'source_run':survey['run_id'],'limits':'Vertex and planar pad checks only; actual source reopen, collision, original terrain joins and visual fidelity remain to inspect.'},indent=2))
