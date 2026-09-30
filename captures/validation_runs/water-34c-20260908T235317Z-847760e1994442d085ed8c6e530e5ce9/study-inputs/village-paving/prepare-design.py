"""Prepare editable contour stair/paving solids from the actual23g GLB surface.
All roads share one surface field within each connected village footprint.
"""
from pathlib import Path
import json,struct,math,hashlib
from collections import defaultdict
import numpy as np
from scipy.spatial import Delaunay
import shapely
from shapely.geometry import Polygon,Point,LineString
from shapely import affinity
root=Path(__file__).resolve().parents[1];out=root/'captures/village_paving_design_26b';assert not out.exists();out.mkdir()
plan=json.loads((root/'captures/village_street_layout_24a/layout.json').read_text())
source=root/'captures/headland_study_23g/mainland_headland.glb'
assert hashlib.sha256(source.read_bytes()).hexdigest()==plan['headland_glb_sha256']
raw=source.read_bytes();ln=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+ln]);buf=raw[28+ln:]
def access(i):
    a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];typ={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];n={'VEC3':3,'SCALAR':1}[a['type']];sz=np.dtype(typ).itemsize
    return np.ndarray((a['count'],n),dtype=typ,buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*sz),sz)).copy()
triangles=[]
for node in doc['nodes']:
    assert not any(k in node for k in ['matrix','translation','rotation','scale'])
    if 'mesh' not in node:continue
    for primitive in doc['meshes'][node['mesh']]['primitives']:
        v=access(primitive['attributes']['POSITION']).astype(float)+np.array([-2180,0,-1830]);f=access(primitive['indices']).reshape(-1,3)
        triangles.extend(v[f])
polys=[];planes=[]
for v in triangles:
    p=Polygon(v[:,[0,2]])
    if p.area<1e-8:continue
    polys.append(p);planes.append(np.linalg.solve(np.column_stack([v[:,0],v[:,2],np.ones(3)]),v[:,1]))
tree=shapely.STRtree(polys);height_cache={}
def ground(x,z):
    key=(round(x,7),round(z,7))
    if key in height_cache:return height_cache[key]
    point=Point(x,z);values=[]
    for i in tree.query(point):
        if polys[i].buffer(1e-7).covers(point):
            a,b,c=planes[i];values.append(a*x+b*z+c)
    assert values,('No actual headland face',x,z)
    value=max(values);assert value>1.,('Paving outside shore',x,z,value);height_cache[key]=value;return value
def pieces(geometry):
    if geometry.is_empty:return []
    if geometry.geom_type=='Polygon':return [geometry]
    return [p for g in geometry.geoms for p in pieces(g)] if hasattr(geometry,'geoms') else []
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
def world(h,u,v):
    x,_,z=h['position'];c,s=math.cos(h['yaw']),math.sin(h['yaw']);return (x+c*u+s*v,z-s*u+c*v)
def rounded(points):
    line=LineString(points).simplify(.65,preserve_topology=False);p=[np.array(v) for v in line.coords];result=[p[0]]
    for a,b,c in zip(p,p[1:],p[2:]):
        la,lc=np.linalg.norm(a-b),np.linalg.norm(c-b)
        if min(la,lc)<.01:continue
        radius=min(1.1,la*.30,lc*.30);qa=b+(a-b)*radius/la;qc=b+(c-b)*radius/lc
        result.append(qa)
        for t in np.linspace(0,1,9)[1:]:result.append((1-t)**2*qa+2*t*(1-t)*b+t*t*qc)
    result.append(p[-1]);return LineString(result)
def coords(poly):return list(poly.exterior.coords)[:-1]+[p for hole in poly.interiors for p in list(hole.coords)[:-1]]
def solid(poly,top,bottom,kind,material,name):
    cleaned=shapely.set_precision(poly.simplify(.0005,preserve_topology=True),.001)
    return [component_solid(p,top,bottom,kind,material,name+' component '+str(i)) for i,p in enumerate(pieces(cleaned)) if p.area>=.0001]
def component_solid(poly,top,bottom,kind,material,name):
    vertices=[];lookup={};edges=[]
    def vertex(p):
        key=tuple(round(v,5) for v in p)
        if key not in lookup:lookup[key]=len(vertices);vertices.append(key)
        return lookup[key]
    for ring in [poly.exterior]+list(poly.interiors):
        ids=[vertex(p) for p in list(ring.coords)[:-1]]
        edges += [(a,b) for a,b in zip(ids,ids[1:]+ids[:1]) if a!=b]
    faces=[]
    for tri in shapely.constrained_delaunay_triangles(poly).geoms:
        ids=[vertex(p) for p in list(tri.exterior.coords)[:-1]]
        assert len(ids)==3;faces.append(ids)
    return {'name':name,'kind':kind,'material':material,'vertices_xz':vertices,'cap_triangles':faces,'boundary_edges':edges,'top_y':float(top),'bottom_y':float(bottom),'area_m2':poly.area}
def clip(v,level,above):
    result=[]
    for a,b in zip(v,v[1:]+v[:1]):
        ina=a[2]>=level if above else a[2]<=level
        inb=b[2]>=level if above else b[2]<=level
        if ina:result.append(a)
        if ina!=inb:
            t=(level-a[2])/(b[2]-a[2]);result.append([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),level])
    return result
groups=[]
for group in plan['groups']:
    name=group['name'];houses=[h for h in plan['houses'] if h['name'].startswith('fore_' if name=='foreground' else 'bay_')]
    lines=[rounded(route['control_points']) for route in group['routes']]
    hub=group['hub'];court=Point(hub).buffer(2.35,quad_segs=4)
    entries=[];obstacles=[]
    for h in houses:
        wx,wz,d=(3.9,5.4,6.4) if h['asset']=='keeper_house' else ((3.26,4.1,4.95) if h['asset']=='fisher_cottage' else (4.4,3.4,4.25))
        obstacles.append(Polygon([world(h,u,v) for u,v in [(-wx,-wz),(wx,-wz),(wx,wz),(-wx,wz)]]).buffer(.025,join_style=2))
        patch=Polygon([world(h,u,v) for u,v in [(-.85,d),(.85,d),(.85,d+1.15),(-.85,d+1.15)]])
        entries.append({'house':h['name'],'polygon':patch,'height':h['entry_y']})
    footprint=shapely.union_all([line.buffer(.85,cap_style=2,quad_segs=4) for line in lines]+[court]+[e['polygon'] for e in entries])
    overlap=footprint.intersection(shapely.union_all(obstacles)).area
    # Clip tiny curve-clearance corners, with the exact remaining width audited afterward.
    footprint=footprint.difference(shapely.union_all(obstacles));assert footprint.geom_type=='Polygon',('Disconnected network',name)
    court=court.intersection(footprint)
    court_y=math.ceil((max(ground(x,z) for x,z in coords(court)+[hub])+.06)/.15)*.15
    patches=[{'polygon':court,'height':court_y,'house':'shared courtyard'}]+entries
    # Euclidean Lipschitz roadbed bounds honor every entry and courtyard, while
    # allowing deliberate localized terrain cuts where the existing slope is too high.
    grade_limit=.30
    for a in patches:
        for b in patches:
            assert abs(a['height']-b['height'])<=grade_limit*a['polygon'].distance(b['polygon'])+.001,('Incompatible fixed road levels',name,a['house'],b['house'])
    def limits(x,z):
        p=Point(x,z);distances=[patch['polygon'].distance(p) for patch in patches]
        return max(patch['height']-grade_limit*d for patch,d in zip(patches,distances)),min(patch['height']+grade_limit*d for patch,d in zip(patches,distances))
    minx,minz,maxx,maxz=footprint.bounds
    seed=coords(footprint)+[p for patch in patches for p in coords(patch['polygon'])]
    for z in np.arange(math.floor(minz),maxz,1.):
        for x in np.arange(math.floor(minx),maxx,1.):
            if footprint.contains(Point(x,z)):seed.append((x,z))
    seed=np.unique(np.round(seed,7),axis=0)
    # Author a connected entry-to-courtyard stair grade rather than following
    # every dip in the old hill. The underlying editable ground is graded later.
    route_heights=[next(p['height'] for p in entries if p['house']==r['house']) for r in group['routes']]
    seed_levels=[]
    for x,z in seed:
        point=Point(x,z);lower,upper=limits(x,z);candidates=[]
        for line,entry_height in zip(lines,route_heights):
            along=line.project(point)
            t=max(0,min(1,(along-1.15)/max(.01,line.length-1.15)))
            height=entry_height+(court_y-entry_height)*t
            candidates.append(height-grade_limit*line.distance(point))
        preferred=max(min(p['height'] for p in patches),max(candidates))
        seed_levels.append(max(lower,min(upper,preferred)))
    seed_levels=np.array(seed_levels)
    def field(x,z):
        lower,upper=limits(x,z)
        cone=float(np.max(seed_levels-grade_limit*np.linalg.norm(seed-np.array([x,z]),axis=1)))
        return max(min(p['height'] for p in patches),lower,min(upper,cone))
    # Continuous laid-stone lanes replace the repeated rounded contour steps.
    # Keep the previously authored route plan, fixed door aprons and courtyard.
    from shapely.ops import polygonize
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    domain=shapely.set_precision(footprint,.001)
    lines2=[domain.boundary]+[shapely.set_precision(p['polygon'],.001).boundary for p in patches]
    for x in range(math.floor(minx),math.ceil(maxx)+1):
        q=LineString([(x,minz-1),(x,maxz+1)]).intersection(domain)
        if not q.is_empty:lines2.append(q)
    for z in range(math.floor(minz),math.ceil(maxz)+1):
        q=LineString([(minx-1,z),(maxx+1,z)]).intersection(domain)
        if not q.is_empty:lines2.append(q)
    cells=list(polygonize(shapely.union_all(lines2,grid_size=.001)))
    fv=[];ft=[];lookup={}
    def idx(p):
        key=tuple(round(v,3) for v in p)
        if key not in lookup:lookup[key]=len(fv);fv.append(key)
        return lookup[key]
    for cell in cells:
        if not domain.covers(cell.representative_point()):continue
        for tri in shapely.constrained_delaunay_triangles(cell).geoms:
            if tri.area>1e-10:ft.append([idx(p) for p in list(tri.exterior.coords)[:-1]])
    fv=np.array(fv);n=len(fv);preferred=np.array([field(x,z) for x,z in fv]);weight=np.zeros(n)
    rr=[];cc=[];values=[];rhs=[]
    def add(ids,coeff,b):
        rr.extend([len(rhs)]*len(ids));cc.extend(ids);values.extend(coeff);rhs.append(float(b))
    for ids in ft:
        v=fv[ids];inv=np.linalg.inv(v[1:]-v[0]);grad=np.column_stack([-inv.sum(axis=1),inv])
        weight[ids]+=Polygon(v).area/3
        for axis in range(2):add(ids,grad[axis],.30);add(ids,-grad[axis],.30)
    bounds=[];fixed_count=0
    for i,(x,z) in enumerate(fv):
        fixed=[p['height'] for p in patches if shapely.set_precision(p['polygon'],.001).buffer(.00001).covers(Point(x,z))]
        if fixed:
            assert max(fixed)-min(fixed)<.001;bounds.append((fixed[0],fixed[0]));fixed_count+=1
        else:bounds.append((min(p['height'] for p in patches),max(p['height'] for p in patches)))
        add([i,n+i],[1,-1],preferred[i]);add([i,n+i],[-1,-1],-preferred[i])
    matrix=coo_matrix((values,(rr,cc)),shape=(len(rhs),2*n)).tocsr()
    result=linprog(np.r_[np.zeros(n),weight],A_ub=matrix,b_ub=np.array(rhs),bounds=bounds+[(0,None)]*n,method='highs')
    assert result.success,(name,result.message)
    heights=result.x[:n];field_polys=[Polygon(fv[ids]) for ids in ft];field_tree=shapely.STRtree(field_polys)
    field_planes=[]
    for ids in ft:
        v=fv[ids]-np.array(hub);field_planes.append(np.linalg.solve(np.column_stack([v,np.ones(3)]),heights[ids]))
    def surface_y(p):
        at=Point(p);near=field_tree.query(at.buffer(.0011));inside=[j for j in near if field_polys[j].distance(at)<.0011]
        assert inside,('Lane field missing',p)
        j=min(inside,key=lambda j:field_polys[j].distance(at));return float((np.array(p)-hub)@field_planes[j][:2]+field_planes[j][2])
    def lane_solid(poly,kind,material,label):
        poly=shapely.set_precision(poly,.00001)
        points=[];top_heights=[];lookup2={};faces=[]
        def vertex(p):
            key=tuple(round(v,5) for v in p)
            if key not in lookup2:lookup2[key]=len(points);points.append(key);top_heights.append(surface_y(key)-(0.012 if kind=='foundation' else 0))
            return lookup2[key]
        # Node the complete cap network once. Separate clipped triangle soups
        # can leave T-junctions after tiny intersections round differently.
        cap_lines=[poly.boundary]
        for j in field_tree.query(poly):
            line=field_polys[j].boundary.intersection(poly)
            if not line.is_empty:cap_lines.append(line)
        for cell in polygonize(shapely.union_all(cap_lines,grid_size=.00001)):
            if not poly.buffer(.00002).covers(cell.representative_point()):continue
            for tri in shapely.constrained_delaunay_triangles(cell).geoms:
                if tri.area<1e-12:continue
                ids=[vertex(p) for p in list(tri.exterior.coords)[:-1]]
                if len(set(ids))==3:faces.append(ids)
        counts=defaultdict(int)
        for face in faces:
            for a,b in zip(face,face[1:]+face[:1]):counts[tuple(sorted((a,b)))]+=1
        assert all(count<=2 for count in counts.values()),('Nonmanifold lane cap',label)
        edges=[e for e,count in counts.items() if count==1]
        degree=defaultdict(int)
        for a,b in edges:degree[a]+=1;degree[b]+=1
        assert all(c==2 for c in degree.values()),('Pinched lane boundary',label)
        if kind=='foundation':
            bottom=min(min(top_heights),min(ground(x,z) for x,z in points))-2.8
            bottom_heights=[bottom]*len(points)
        else:bottom_heights=[h-.10 for h in top_heights]
        return {'name':label,'kind':kind,'material':material,'vertices_xz':points,'cap_triangles':faces,'boundary_edges':edges,'top_y':float(np.mean(top_heights)),'bottom_y':min(bottom_heights),'top_heights':top_heights,'bottom_heights':bottom_heights,'area_m2':poly.area}
    solids=[]
    # Editable local bedding blocks, capped by the same continuous lane field.
    for z in range(math.floor(minz/4),math.ceil(maxz/4)):
        for x in range(math.floor(minx/4),math.ceil(maxx/4)):
            tile=Polygon([(x*4,z*4),(x*4+4,z*4),(x*4+4,z*4+4),(x*4,z*4+4)])
            for i,p in enumerate(pieces(domain.intersection(tile))):
                if p.area>.002:solids.append(lane_solid(p,'foundation',0,name+' continuous buried bedding '+str((x,z,i))))
    angle=-20 if name=='foreground' else -10
    bx,bz,ex,ez=affinity.rotate(domain,-angle,origin=hub).bounds
    for row in range(math.floor(bz/.55),math.ceil(ez/.55)):
        offset=.4*(row%2)
        for col in range(math.floor((bx-offset)/.8),math.ceil((ex-offset)/.8)):
            x=col*.8+offset;z=row*.55
            tile=affinity.rotate(Polygon([(x+.004,z+.004),(x+.796,z+.004),(x+.796,z+.546),(x+.004,z+.546)]),angle,origin=hub)
            for i,p in enumerate(pieces(domain.intersection(tile))):
                if p.area>.022:solids.append(lane_solid(p,'paver',1+(row+col)%4,name+' inclined limestone '+str((row,col,i))))
    grading_faces=[{'vertices_xz':fv[ids].tolist(),'heights':heights[ids].tolist()} for ids in ft]
    groups.append({'name':name,'origin':[-2180,0,-1830],'footprint_geojson':shapely.to_geojson(domain),'grading_surface_triangles':grading_faces,'solids':solids,'fixed_patches':[{'house':p['house'],'height':p['height'],'geojson':shapely.to_geojson(p['polygon'])} for p in patches],'field_solve':{'vertices':n,'triangles':len(ft),'fixed_vertices':fixed_count,'success':True,'max_axis_slope':.30,'maximum_preferred_height_adjustment':float(np.max(abs(heights-preferred)))}})
    print(name,len(solids),'editable continuous lane solids; field',len(ft),'triangles',flush=True)
report={'label':'26b','headland_glb_sha256':plan['headland_glb_sha256'],'source_grid_run':plan['source_run'],'groups':groups,'scope':'Continuous inclined stone lanes with shared planar height field, fixed door aprons/courtyards and individually editable stones. Replaces scalloped quantized contours. Requires updated actual terrain grading, native source/export checks and GPU review before acceptance. Production unchanged.'}
(out/'paving.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
