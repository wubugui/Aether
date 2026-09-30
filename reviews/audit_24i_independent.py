"""Independent design audit. Reads final caps; does not import preparer/root audit."""
from pathlib import Path
import json, math, hashlib
from collections import Counter, defaultdict
import numpy as np
import shapely
from shapely.geometry import Polygon, Point, LineString

ROOT=Path(r'E:\FeiTing')
src=ROOT/'captures/village_paving_design_24i/paving.json'
d=json.loads(src.read_text()); plan=json.loads((ROOT/'captures/village_street_layout_24a/layout.json').read_text())
report={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'method':'All solid cap triangle edge-incidence and boundary graph audit; union triangle polygons by foundation top+12mm; analytical 2D segment/boundary intersections in route arc-length coordinates; midpoint classify each exact interval. No preparer or root audit imports.','scope':'Design-only JSON cap geometry. Not Blender/native/GPU/collision/visual acceptance. Grout up to 12mm excluded from design step metric.','groups':[],'failures':[]}

def parts(g):
    if hasattr(g,'geoms'):
        for p in g.geoms:yield from parts(p)
    else:yield g

def cross(a,b):return a[0]*b[1]-a[1]*b[0]

for group in d['groups']:
    polys=defaultdict(list); topology=[]; cap_area_error=0.; count=0
    for solid in group['solids']:
        v=np.array(solid['vertices_xz']); faces=solid['cap_triangles']; edges=Counter(); tri=[]
        for f in faces:
            for a,b in zip(f,f[1:]+f[:1]):edges[tuple(sorted((a,b)))]+=1
            tri.append(Polygon(v[f]))
        boundary={e for e,n in edges.items() if n==1}
        claimed={tuple(sorted(e)) for e in solid['boundary_edges']}
        degrees=Counter(x for e in boundary for x in e)
        union=shapely.union_all(tri)
        err=abs(union.area-solid['area_m2']); cap_area_error=max(cap_area_error,err)
        area=sum(p.area for p in tri)
        reasons=[]
        if boundary!=claimed:reasons.append('boundary edge mismatch')
        if any(n>2 for n in edges.values()):reasons.append('nonmanifold cap edge')
        if any(n!=2 for n in degrees.values()):reasons.append('boundary graph degree != 2')
        if not union.is_valid:reasons.append('invalid cap union')
        if abs(area-union.area)>1e-7:reasons.append('overlapping cap triangles')
        if err>1e-6:reasons.append('cap area does not equal cleaned contour area')
        if reasons:topology.append({'solid':solid['name'],'reasons':reasons,'error':err,'area_m2':solid['area_m2'],'bad_boundary_vertices':[{'id':i,'xz':v[i].tolist(),'degree':n,'incident_boundary_edges':[e for e in solid['boundary_edges'] if i in e],'extruded_vertical_edge_face_incidence':n} for i,n in degrees.items() if n!=2]})
        if solid['kind']=='foundation':polys[round(solid['top_y']+.012,6)].append(union)
        count+=1
    floors={h:shapely.union_all(p) for h,p in polys.items()}
    coverage=shapely.union_all(list(floors.values())); footprint=shapely.from_geojson(group['footprint_geojson'])
    segment_edges=[]
    for h,poly in floors.items():
        for p in parts(poly):
            if p.geom_type!='Polygon':continue
            for ring in [p.exterior]+list(p.interiors):
                vv=np.array(ring.coords)
                segment_edges.extend((a,b) for a,b in zip(vv[:-1],vv[1:]))
    ee=np.array(segment_edges); ba=ee[:,0]; delta=ee[:,1]-ba
    def height(pt,tol=1e-8):
        hs=[h for h,p in floors.items() if p.distance(Point(pt))<=tol]
        return max(hs) if hs else None
    profiles=[]
    for ri,coords in enumerate(group['routes']):
        line=LineString(coords)
        for offset in [0.,-.6,.6]:
            shifted=line.offset_curve(offset) if offset else line
            for path in parts(shifted):
                if path.geom_type!='LineString':continue
                runs=[]; cumulative=0.
                for a,b in zip(np.array(path.coords)[:-1],np.array(path.coords)[1:]):
                    dr=b-a; length=float(np.linalg.norm(dr)); den=dr[0]*delta[:,1]-dr[1]*delta[:,0]
                    q=ba-a; mask=np.abs(den)>1e-10
                    t=np.full(len(den),-1.); u=t.copy()
                    t[mask]=(q[mask,0]*delta[mask,1]-q[mask,1]*delta[mask,0])/den[mask]
                    u[mask]=(q[mask,0]*dr[1]-q[mask,1]*dr[0])/den[mask]
                    vals=sorted(set([0.,1.]+[round(float(x),11) for x in t[(t>0)&(t<1)&(u>=-1e-8)&(u<=1+1e-8)]]))
                    for t0,t1 in zip(vals,vals[1:]):
                        if (t1-t0)*length<1e-7:continue
                        mid=a+dr*((t0+t1)/2); h=height(mid)
                        start=cumulative+t0*length; end=cumulative+t1*length
                        if runs and runs[-1]['height']==h and abs(runs[-1]['end']-start)<1e-5:runs[-1]['end']=end
                        else:runs.append({'start':start,'end':end,'height':h,'example_xz':mid.tolist()})
                    cumulative+=length
                issues=[]
                for i,r in enumerate(runs):
                    if r['height'] is None:
                        if r['end']-r['start']>.003:issues.append({'kind':'uncovered route','run':r})
                        continue
                    if i and runs[i-1]['height'] is not None:
                        jump=abs(r['height']-runs[i-1]['height'])
                        if jump>.180001:issues.append({'kind':'step over 18cm','rise_m':jump,'xz':list(path.interpolate(r['start']).coords)[0]})
                    if i and i+1<len(runs) and runs[i-1]['height'] is not None and runs[i+1]['height'] is not None:
                        depth=min(runs[i-1]['height'],runs[i+1]['height'])-r['height']
                        if depth>=.14999 and r['end']-r['start']<.24:issues.append({'kind':'15cm groove under 24cm','depth_m':depth,'width_m':r['end']-r['start'],'run':r})
                row={'route_index':ri,'house':plan['groups'][0 if group['name']=='foreground' else 1]['routes'][ri]['house'],'offset_m':offset,'issues':issues,'runs':runs}
                profiles.append(row)
                if issues:report['failures'].append({'group':group['name'],**row})
    historic=[]
    points=[(-2251.58,-1750.84)] if group['name']=='foreground' else [(-2247.4,-1870.672734),(-2235.170884,-1878.4),(-2219.636357,-1859.016522)]
    for p in points:historic.append({'xz':p,'height':height(p),'nearby_height_range_10cm':[min(h for h,poly in floors.items() if poly.distance(Point(p))<.10),max(h for h,poly in floors.items() if poly.distance(Point(p))<.10)]})
    entries=[]
    for ent in group['entries']:
        h=next(h for h in plan['houses'] if h['name']==ent['house']); c,s=math.cos(h['yaw']),math.sin(h['yaw'])
        for lateral in [-.6,0,.6]:
            # Three transverse points, 20mm into the authored entrance apron.
            x=h['entry'][0]+c*lateral+s*.02; z=h['entry'][1]-s*lateral+c*.02
            actual=height((x,z)); entries.append({'house':h['name'],'lateral_m':lateral,'xz':[x,z],'expected_y':h['entry_y'],'actual_y':actual,'pass':actual is not None and abs(actual-h['entry_y'])<1e-6})
    row={'name':group['name'],'solid_count':count,'topology_failures':topology,'max_cap_area_error_m2':cap_area_error,'coverage_missing_m2':footprint.difference(coverage).area,'coverage_missing_beyond_1mm_m2':footprint.difference(coverage.buffer(.001)).area,'coverage_extra_m2':coverage.difference(footprint).area,'historic':historic,'entries':entries,'profiles':profiles}
    report['groups'].append(row)
    print(json.dumps({'group':group['name'],'solid_count':count,'topology_failures':len(topology),'missing_m2':row['coverage_missing_m2'],'failed_profiles':sum(bool(p['issues']) for p in profiles),'issues':[{'house':p['house'],'offset':p['offset_m'],'issues':p['issues']} for p in profiles if p['issues']],'entries_pass':sum(e['pass'] for e in entries),'historic':historic}),flush=True)

target=ROOT/'reviews/round-24i-village-paving-independent-design-review.json'
target.write_text(json.dumps(report,indent=2),encoding='utf-8')
