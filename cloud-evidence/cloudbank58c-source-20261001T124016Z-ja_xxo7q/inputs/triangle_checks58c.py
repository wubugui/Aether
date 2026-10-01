"""Actual triangle vertical support and cross sections, independent of Blender."""
import math
import numpy as np

def stations(corridor,spacing=25):
    pts=np.array(corridor['xz'],float);lens=np.linalg.norm(np.diff(pts,axis=0),axis=1);cum=np.r_[0,np.cumsum(lens)]
    distances=list(np.arange(0,cum[-1],spacing))+[float(cum[-1])];rows=[]
    for dist in distances:
        i=min(int(np.searchsorted(cum,dist,side='right')-1),len(lens)-1);t=(dist-cum[i])/lens[i];tangent=(pts[i+1]-pts[i])/lens[i];normal=np.array([-tangent[1],tangent[0]])
        for offset in [-corridor['half_width_m'],0,corridor['half_width_m']]:
            q=pts[i]+t*(pts[i+1]-pts[i])+normal*offset;rows.append(dict(distance_m=float(dist),transverse_offset_m=offset,world_xz=q.tolist()))
    return rows

def vertical_hits(tri,xz):
    # Exact barycentric intersection of eachactualtriangle with world-verticalline.
    a=tri[:,0][:,[0,2]];b=tri[:,1][:,[0,2]];c=tri[:,2][:,[0,2]];p=np.array(xz)
    den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1]);valid=abs(den)>1e-10
    wa=np.full(len(tri),np.nan);wb=wa.copy()
    wa[valid]=((b[valid,1]-c[valid,1])*(p[0]-c[valid,0])+(c[valid,0]-b[valid,0])*(p[1]-c[valid,1]))/den[valid]
    wb[valid]=((c[valid,1]-a[valid,1])*(p[0]-c[valid,0])+(a[valid,0]-c[valid,0])*(p[1]-c[valid,1]))/den[valid];wc=1-wa-wb
    ids=np.flatnonzero(valid&(wa>=-1e-8)&(wb>=-1e-8)&(wc>=-1e-8));y=wa[ids]*tri[ids,0,1]+wb[ids]*tri[ids,1,1]+wc[ids]*tri[ids,2,1]
    normal=np.cross(tri[ids,1]-tri[ids,0],tri[ids,2]-tri[ids,0]);order=np.argsort(-y);clusters=[]
    for k in order:
        yy=float(y[k]);idx=int(ids[k]);orientation='entry' if normal[k,1]>0 else 'exit'
        if yy>1500+1e-6:continue
        if clusters and abs(clusters[-1]['world_y_m']-yy)<1e-5:
            clusters[-1]['triangle_ids'].append(idx);clusters[-1]['orientations'].append(orientation)
        else:clusters.append(dict(world_y_m=yy,triangle_ids=[idx],orientations=[orientation]))
    intervals=[];opened=None;errors=[]
    for h in clusters:
        unique=set(h['orientations'])
        if len(unique)>1:
            errors.append(dict(kind='ambiguous_tangent_or_coincident_hit',hit=h));continue
        typ=next(iter(unique))
        if typ=='entry':
            if opened is not None:errors.append(dict(kind='entry_without_previous_exit',hit=h))
            opened=h
        else:
            if opened is None:errors.append(dict(kind='exit_without_entry',hit=h))
            else:
                intervals.append(dict(top_y_m=opened['world_y_m'],bottom_y_m=h['world_y_m'],thickness_m=opened['world_y_m']-h['world_y_m'],entry_triangle_ids=opened['triangle_ids'],exit_triangle_ids=h['triangle_ids']));opened=None
    if opened is not None:errors.append(dict(kind='entry_without_final_exit',hit=opened))
    return dict(hits=clusters,solid_intervals=intervals,errors=errors)

def valley_report(tri,corridors):
    rows=[]
    for corridor in corridors:
        samples=[];low,high=corridor['intended_floor_y_range_m']
        for s in stations(corridor):
            hit=vertical_hits(tri,s['world_xz']);intervals=hit['solid_intervals'];floor=intervals[0]['top_y_m'] if intervals else None
            supported=bool(intervals and intervals[0]['thickness_m']>=160)
            floor_ok=floor is not None and low<=floor<=high
            samples.append(dict(s,**hit,first_cloud_surface_y_m=floor,first_solid_interval_at_least_160m=supported,floor_in_declared_band=bool(floor_ok),passed=bool(supported and floor_ok and not hit['errors'])))
        rows.append(dict(id=corridor['id'],floor_band_y_m=[low,high],sample_count=len(samples),passing_samples=sum(s['passed'] for s in samples),passed=all(s['passed'] for s in samples),samples=samples))
    return dict(passed=all(r['passed'] for r in rows),corridors=rows,method='Every25m arc-length station plus endpoint, transverse−half/0/+half, raysdownfromworldY1500 throughactualtriangles. Complete signed entry/exit hits retained. First interval must be >=160m; first floor must be indeclaredband.',ocean_y_m=0,not_full_flight_clearance=True)

def cross_sections(tri,planes):
    rows=[]
    for p in planes:
        axis=2 if p['plane']=='world_z' else 0;value=p['value_m'];segments=[];coplanar=[]
        for tid,t in enumerate(tri):
            d=t[:,axis]-value
            if np.all(abs(d)<1e-7):coplanar.append(tid);continue
            if d.min()>0 or d.max()<0:continue
            pts=[]
            for j in range(3):
                a,b=t[j],t[(j+1)%3];da,db=d[j],d[(j+1)%3]
                if abs(da)<1e-7:pts.append(a)
                if da*db<0:pts.append(a+(b-a)*(-da/(db-da)))
            unique=[]
            for pt in pts:
                if not any(np.linalg.norm(pt-q)<1e-5 for q in unique):unique.append(pt)
            if len(unique)==2:segments.append(dict(triangle_id=tid,world_points=[q.tolist() for q in unique]))
        # Actual sectionline vertical intervals at25m coordinate spacing.
        limits=p.get('range_x_m',p.get('range_z_m'));scan=[]
        for coord in np.arange(limits[0],limits[1]+.01,25):
            xz=[float(coord),value] if axis==2 else [value,float(coord)];scan.append(dict(coordinate_m=float(coord),world_xz=xz,**vertical_hits(tri,xz)))
        rows.append(dict(plane=p,actual_triangle_segments=segments,coplanar_triangle_ids=coplanar,actual_vertical_solid_intervals=scan))
    return dict(sections=rows,method='Actualtriangle/plane segments and actualray solid intervals. No filledAABB or inferredheightfield.')
