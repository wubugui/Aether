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
root=Path(__file__).resolve().parents[1];out=root/'captures/village_paving_design_24h';assert not out.exists();out.mkdir()
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
    dt=Delaunay(seed)
    region_triangles=[]
    patch_union=shapely.union_all([p['polygon'] for p in patches])
    for tri in dt.simplices:
        cut=Polygon(seed[tri]).intersection(footprint)
        if cut.is_empty or cut.area<1e-8:continue
        regions=[cut.difference(patch_union)]+[cut.intersection(patch['polygon']) for patch in patches]
        for region in regions:
            for polygon in pieces(region):
                if polygon.area<1e-8:continue
                for triangle in shapely.constrained_delaunay_triangles(polygon).geoms:
                    v=[[x,z,field(x,z)] for x,z in list(triangle.exterior.coords)[:-1]]
                    if triangle.area>1e-8:region_triangles.append(v)
    levels=[round(v,7) for v in np.arange(0,50,.15)]
    bands=defaultdict(list)
    for triangle in region_triangles:
        triangle=[[x,z,round(h,6)] for x,z,h in triangle]
        polygon=Polygon([(p[0],p[1]) for p in triangle])
        low=min(v[2] for v in triangle);high=max(v[2] for v in triangle)
        if high-low<1e-6:
            top=next((p['height'] for p in patches if abs(p['height']-high)<1e-6),min(v for v in levels if v>=high-1e-7))
            bands[round(top,7)].append(polygon);continue
        # Partition by successive upper half-planes. Every triangle remainder
        # belongs to its highest band; no uncovered region gets a minimum floor.
        remaining=polygon
        relevant=[v for v in levels if v>=low-1e-7 and v<=high+.1500001]
        for level in relevant:
            if remaining.is_empty:break
            clipped=clip(triangle,level,False)
            region=Polygon([(p[0],p[1]) for p in clipped]) if len(clipped)>=3 else Polygon()
            region=shapely.make_valid(region).intersection(remaining)
            for piece in pieces(region):
                if piece.area>1e-12:bands[level].append(piece)
            remaining=remaining.difference(region)
        assert remaining.area<1e-8,(name,'unassigned triangle floor',remaining.area)
    # Extensiveness is essential: never erode a high road edge down to the
    # group's lowest floor. Closing fills narrow depressions; union with the
    # original superlevel explicitly preserves every pre-existing high point.
    raw_bands={level:shapely.union_all(polygons,grid_size=1e-5) for level,polygons in bands.items()}
    raw_coverage=shapely.union_all(list(raw_bands.values()))
    missing=footprint.difference(raw_coverage)
    assert missing.area<.001,(name,'raw bands left a physical hole',missing.area)
    filtered={};previous=footprint;ordered=sorted(raw_bands)
    superlevels={}
    for level in ordered:
        original=shapely.union_all([poly for h,poly in raw_bands.items() if h>=level-1e-7])
        closed=original.buffer(.20,join_style=1,quad_segs=4).buffer(-.20,join_style=1,quad_segs=4)
        region=shapely.union_all([original,closed]).intersection(footprint).intersection(previous)
        assert original.difference(region).area<.001,(name,level,'closing eroded original floor')
        superlevels[level]=region;previous=region
    for i,level in enumerate(ordered):
        higher=superlevels[ordered[i+1]] if i+1<len(ordered) else Polygon()
        region=superlevels[level].difference(higher).difference(patch_union)
        filtered[level]=region
    for patch in patches:
        height=round(patch['height'],7);filtered[height]=shapely.union_all([filtered.get(height,Polygon()),patch['polygon'].intersection(footprint)])
    bands={h:pieces(poly) for h,poly in filtered.items() if not poly.is_empty and poly.area>.0001}
    grading_bands=[{'height':h,'geojson':shapely.to_geojson(shapely.union_all(polygons,grid_size=1e-5))} for h,polygons in bands.items()]
    grading_footprint=footprint.buffer(.65,join_style=1,quad_segs=4).difference(shapely.union_all(obstacles))
    solids=[];band_rows=[]
    for level,polygons in sorted(bands.items()):
        band=shapely.union_all(polygons,grid_size=1e-5)
        band_rows.append({'height':level,'area_m2':band.area,'pieces':len(pieces(band))})
        for j,polygon in enumerate(pieces(band)):
            if polygon.area<.0001:continue
            bottom=min(ground(x,z) for x,z in coords(polygon))-.28
            base=solid(polygon,level-.012,min(bottom,level-.28),'foundation',0,name+' terrace bedding %.3f %d'%(level,j))
            solids.extend(base)
        # Individually editable staggered stone pavers; lower bedding backs the narrow joints.
        angle=-20 if name=='foreground' else -10
        rotated=affinity.rotate(band,-angle,origin=hub)
        bx,bz,ex,ez=rotated.bounds
        for row in range(math.floor(bz/.55),math.ceil(ez/.55)):
            offset=.4*(row%2)
            for col in range(math.floor((bx-offset)/.8),math.ceil((ex-offset)/.8)):
                x=col*.8+offset;z=row*.55
                tile=Polygon([(x+.004,z+.004),(x+.796,z+.004),(x+.796,z+.546),(x+.004,z+.546)])
                for cut in pieces(rotated.intersection(tile)):
                    if cut.area<.022:continue
                    paver=affinity.rotate(cut,angle,origin=hub)
                    item=solid(paver,level,level-.10,'paver',1+(row+col)%4,name+' worn stair paver %.3f %d %d'%(level,row,col))
                    solids.extend(item)
    coverage=shapely.union_all([shapely.union_all(p,grid_size=1e-5) for p in bands.values()])
    difference=coverage.symmetric_difference(footprint).area
    assert difference<.015,(name,'coverage mismatch',difference)
    groups.append({'name':name,'origin':[-2180,0,-1830],'footprint_geojson':shapely.to_geojson(footprint),'footprint_area_m2':footprint.area,'planning_obstacle_clip_area_m2':overlap,'coverage_difference_m2':difference,'court_y':court_y,'court_geojson':shapely.to_geojson(court),'routes':[list(line.coords) for line in lines],'entries':[{'house':p['house'],'height':p['height'],'polygon_geojson':shapely.to_geojson(p['polygon'])} for p in entries],'levels':band_rows,'solids':solids,'grading_bands':grading_bands,'grading_footprint_geojson':shapely.to_geojson(grading_footprint),'grade_limit':grade_limit})
    print(name+' paving design '+str(len(solids))+' editable solids; area '+str(round(footprint.area,2)),flush=True)
data={'label':'24h','headland_glb_sha256':plan['headland_glb_sha256'],'source_grid_run':plan['source_run'],'groups':groups,'scope':'Prepared from actual23g GLB triangle planes with native1m route grid. Closed Blender solids and native collision/render review follow. Quantized shared level field prevents conflicting overlapping road tops at junctions; not full walk or reference acceptance.'}
(out/'paving.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
