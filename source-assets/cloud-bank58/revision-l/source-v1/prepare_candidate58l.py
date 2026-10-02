"""Pure finite geometry preparation; explicit --write only. Never starts Blender.
Scipy is used only here. The persisted candidate is directly usable in Blender.
"""
import sys,os
os.environ['OPENBLAS_NUM_THREADS']='1';sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry58l as g
import numpy as np
from fractions import Fraction as Q
from scipy.spatial import Delaunay, cKDTree
from scipy.interpolate import PchipInterpolator
import importlib.util,math,json,argparse,time

def exact_rim(source):
    seg=source['source_segments'];out=[];audit=[]
    for i,s in enumerate(seg):
        before=seg[i-1];a,b=[np.array(x)[[0,2]] for x in before['source_welded_edge_world_xyz_m']];c,d=[np.array(x)[[0,2]] for x in s['source_welded_edge_world_xyz_m']]
        A,B,C,D=[[Q(float(v)) for v in p] for p in (a,b,c,d)];u=[B[k]-A[k] for k in range(2)];v=[D[k]-C[k] for k in range(2)];den=u[0]*v[1]-u[1]*v[0]
        if den:
            t=((C[0]-A[0])*v[1]-(C[1]-A[1])*v[0])/den;p=[A[k]+t*u[k] for k in range(2)]
        else:
            common=[x for x in (A,B) if x in (C,D)];g.require(len(common)==1,'COLLINEAR_RIM_JOIN_WITHOUT_COMMON_SOURCE_ENDPOINT');p=common[0]
        f=np.array([float(v) for v in p]);g.require(np.linalg.norm(f-np.array(s['xz_endpoints_m'][0]))<1e-7,'SOURCE_BOUND_JOIN_IDENTITY');out.append(f);audit.append(dict(source_segment_ids=[before['id'],s['id']],exact_xz_fraction=[[v.numerator,v.denominator] for v in p],float64_xz=f.tolist(),catalog_delta_m=float(np.linalg.norm(f-np.array(s['xz_endpoints_m'][0])))))
    # Catalog is clockwise. Preserve that order in provenance, reverse for disk.
    return np.array(out)[::-1],audit

def inside(p,poly):
    p=np.asarray(p);x=p[:,0];z=p[:,1];hit=np.zeros(len(p),bool)
    for a,b in zip(poly,np.roll(poly,-1,axis=0)):
        hit^=((a[1]>z)!=(b[1]>z))&(x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1] if b[1]!=a[1] else 1)+a[0])
    return hit

def triangle_edges(tris):
    edges={}
    for i,t in enumerate(tris):
        for a,b in zip(t,np.roll(t,-1)):edges.setdefault(tuple(sorted((int(a),int(b)))),[]).append(i)
    return edges

def recover(points,tris,constraints):
    """Constrained edge recovery by convex diagonal flips; fails rather than hull fill."""
    locked=set()
    for a,b in constraints:
        target=tuple(sorted((a,b)));steps=0
        while True:
            edges=triangle_edges(tris)
            if target in edges:locked.add(target);break
            crossings=[]
            for (c,d),adj in edges.items():
                if len(adj)!=2 or len({a,b,c,d})<4:continue
                if g.orient(points[a],points[b],points[c])*g.orient(points[a],points[b],points[d])<0 and g.orient(points[c],points[d],points[a])*g.orient(points[c],points[d],points[b])<0:crossings.append(((c,d),adj))
            g.require(crossings,'UNRECOVERABLE_CONSTRAINT_NO_CROSSING')
            flipped=False
            for edge,adj in crossings:
                g.require(edge not in locked,'CONSTRAINTS_CROSS')
                c,d=edge;i,j=adj;e=next(k for k in tris[i] if k not in edge);f=next(k for k in tris[j] if k not in edge)
                if g.orient(points[e],points[f],points[c])*g.orient(points[e],points[f],points[d])>=0:continue
                # Do not flip an edge to another edge crossing the target unless
                # no resolving convex edge exists; cycling fails bounded below.
                if g.orient(points[a],points[b],points[e])*g.orient(points[a],points[b],points[f])<0:continue
                new=[[e,f,c],[f,e,d]]
                for k,t in zip((i,j),new):
                    if g.orient(*points[t])<0:t[1],t[2]=t[2],t[1]
                    tris[k]=t
                flipped=True;break
            g.require(flipped,'UNRECOVERABLE_NONCONVEX_CONSTRAINT');steps+=1;g.require(steps<10000,'EDGE_RECOVERY_BUDGET')
    return tris

def load_profiles():
    spec=importlib.util.spec_from_file_location('v2_profiles',g.HERE.parent/'design-v2/revise_design_v2.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    plan=g.read(g.HERE.parent/'design-v1/design_plan.json');definition=g.read(g.HERE.parent/'design-v2/profile-definition.json');nodes=m.resolve_nodes(definition,plan);profiles={k:m.resolve_section(k,v,nodes) for k,v in definition['sections'].items()};return m,plan,definition,nodes,profiles

def line_nearest(points,path):
    p=np.asarray(points);best=np.full(len(p),np.inf);ystar=np.zeros(len(p))
    for a,b in zip(path,path[1:]):
        d=b[[0,2]]-a[[0,2]];t=np.clip((p-a[[0,2]])@d/(d@d),0,1);dist=np.linalg.norm(p-a[[0,2]]-t[:,None]*d,axis=1);take=dist<best;best[take]=dist[take];ystar[take]=(a[1]+t*(b[1]-a[1]))[take]
    return best,ystar

def make():
    start=time.monotonic();m,plan,definition,nodes,profiles=load_profiles();rim_source=g.read(g.HERE.parent/'design-v3/external-rim.json');rim64,joins=exact_rim(rim_source)
    # Native author coordinates rounded exactly as the eventual Blender float32.
    def native_xz(p):return np.column_stack((g.f32(p[:,0]-3958)+3958,3667-g.f32(3667-p[:,1])))
    rim=native_xz(rim64);R=len(rim);points=list(rim);special={};section_ids={};constraints=[(i,(i+1)%R) for i in range(R)]
    def add(p,top=None,bottom=None,label=None):
        p=native_xz(np.array(p).reshape(1,2))[0]
        close=[j for j,q in enumerate(points) if np.linalg.norm(np.asarray(q)-p)<1e-8]
        i=close[0] if close else len(points)
        if not close:points.append(p)
        if top is not None:
            if i in special:g.require(abs(special[i]['top']-top)<1e-7 and (bottom is None or special[i].get('bottom') is None or abs(special[i]['bottom']-bottom)<1e-7),'CONFLICTING_AUTHORITY_NODE')
            special[i]=dict(top=float(top),bottom=float(bottom) if bottom is not None else special.get(i,{}).get('bottom'),label=label)
        return i
    for name,p in profiles.items():
        # Every actual PCHIP knot retained, plus 25m segments for finite approx.
        stations=np.unique(np.r_[p['stations'],p['path_s'],np.linspace(p['stations'][0],p['stations'][-1],math.ceil((p['stations'][-1]-p['stations'][0])/25)+1)])
        ids=[add(m.world_xz(p,t),p['top'](t),p['bottom'](t),name+':'+str(t)) for t in stations];section_ids[name]=dict(stations=stations.tolist(),indices=ids)
        # Float32 near-path may wobble <0.1mm. Keep authored line constraints.
        constraints.extend(zip(ids,ids[1:]))
    for name,p in nodes.items():
        if name=='A_belly':continue
        add(p[[0,2]],p[1],None,name)
    # Valley floor rails: broad supported floor instead of a knife-edge trench.
    paths=[np.array([nodes[k] for k in definition[key]]) for key in ('main_valley_nodes','branch_valley_nodes')]
    for path in paths:
        for a,b in zip(path,path[1:]):
            d=b[[0,2]]-a[[0,2]];normal=np.array([-d[1],d[0]])/np.linalg.norm(d)
            for t in np.linspace(0,1,max(2,math.ceil(np.linalg.norm(d)/50)+1)):
                p=a*(1-t)+b*t
                for off in (-52,0,52):
                    q=p[[0,2]]+normal*off
                    if inside(q[None],rim)[0] and min(np.linalg.norm(q-np.array(points),axis=1))>14:add(q,p[1]+3*(abs(off)/52),None,'valley_floor_rail')
    # Sparse irregular triangular plan sampling. Deterministic authored low
    # frequency variation; no sphere unions, random noise, roof or flat slab.
    for iz,z in enumerate(np.arange(3455,4910,48)):
        for ix,x in enumerate(np.arange(3650+(iz%2)*24,5080,48)):
            q=np.array([x+5*math.sin(iz*1.7+ix*.7),z+4*math.sin(ix*1.5)])
            if inside(q[None],rim)[0] and g.rim_distance(q[None],rim)[0]>15 and min(np.linalg.norm(q-np.array(points),axis=1))>18:add(q)
    pts=np.array(points);g.require(len(pts)<1390,'PLAN_POINT_BUDGET')
    tris=Delaunay(pts).simplices.copy();tris=recover(pts,tris,constraints);tris=tris[inside(pts[tris].mean(1),rim)]
    # Avoid all-rim zero-volume ears by insert one genuine interior point.
    ears=[i for i,t in enumerate(tris) if max(t)<R]
    new=[]
    for i,t in enumerate(tris):
        if i in ears:
            q=native_xz(pts[t].mean(0)[None])[0];j=len(pts);pts=np.vstack((pts,q));new.extend([[t[0],t[1],j],[t[1],t[2],j],[t[2],t[0],j]])
        else:new.append(t.tolist())
    tris=np.array(new,int)
    # A non-boundary chord joining two rim vertices would be shared by both
    # sheets and create a four-face pinched edge. Split every such chord with
    # a genuine interior vertex before lifting, never weld two sheets there.
    for (a,b),adj in list(triangle_edges(tris).items()):
        if a>=R or b>=R or len(adj)!=2:continue
        k=len(pts);pts=np.vstack((pts,native_xz(((pts[a]+pts[b])/2)[None])[0]));rebuilt=[]
        for t in tris:
            if a in t and b in t:
                c=next(x for x in t if x not in (a,b))
                for nt in ([a,k,c],[k,b,c]):
                    if g.orient(*pts[nt])<0:nt[1],nt[2]=nt[2],nt[1]
                    rebuilt.append(nt)
            else:rebuilt.append(t.tolist())
        tris=np.array(rebuilt,int)
    N=len(pts);d=g.rim_distance(pts,rim);u=np.clip(d/80,0,1);w=u*u*(3-2*u)
    main=np.vstack((paths[0],));dv,yv=line_nearest(pts,paths[0]);db,yb=line_nearest(pts,paths[1]);take=db<dv;dv[take]=db[take];yv[take]=yb[take]
    # Broad shared body and bent shoulder, with offset asymmetric crown fields.
    top=770+13*np.sin((pts[:,0]-3800)/310)*np.cos((pts[:,1]-4100)/230)
    for key,rx,rz,amp in [('A',265,250,235),('B',285,230,270),('C',185,310,150),('D',235,170,75)]:
        c=nodes[key][[0,2]];dx=(pts[:,0]-c[0])/rx;dz=(pts[:,1]-c[1])/rz
        q=dx*dx+dz*dz+.22*dx*dz;hill=amp*np.exp(-1.7*q);top=np.maximum(top,770+hill)
    # Main / blind branch have a broad 110m floor then rounded banks.
    valley_blend=np.clip((160-dv)/(160-55),0,1);valley_blend=valley_blend**2*(3-2*valley_blend)
    top=top*(1-valley_blend)+(yv+3*np.minimum(dv/55,1)**2)*valley_blend
    bottom=590+17*np.sin((pts[:,0]-4050)/340)*np.sin((pts[:,1]-3600)/270)
    # Interpolate profile controls laterally, exactly retaining all actual knots.
    # This soft field supplies coherent shoulders; constrained path vertices are
    # overwritten by their single authoritative top/bottom values below.
    known=np.array(list(special));kp=pts[known];tree=cKDTree(kp);dist,idx=tree.query(pts,k=4)
    for i in range(N):
        weights=1/(dist[i]**2+40**2);blend=math.exp(-(dist[i,0]/95)**2)
        ty=np.array([special[int(known[j])]['top'] for j in idx[i]]);top[i]=top[i]*(1-blend)+np.dot(weights,ty)/sum(weights)*blend
        good=np.array([special[int(known[j])]['bottom'] is not None for j in idx[i]])
        if good.any():by=np.array([special[int(known[j])]['bottom'] or 0 for j in idx[i]]);bottom[i]=bottom[i]*(1-blend)+np.dot(weights[good],by[good])/sum(weights[good])*blend
    # Explicit rim authoring independent of old rim Y. Smooth 0..80 return.
    rim_y=685+15*np.sin((pts[:,0]-3950)/260)+12*np.cos((pts[:,1]-4100)/220)
    roll=np.clip(d/45,0,1);roll=roll*roll*(3-2*roll)
    top=rim_y*(1-roll)+top*roll;bottom=rim_y*(1-roll)+bottom*roll
    for i,row in special.items():top[i]=row['top'];bottom[i]=row['bottom'] if row['bottom'] is not None else bottom[i]
    # Keep broad lower surface at least560, no automatic gate clamp. Near profile
    # exact560 knot is retained; other authored values arise from convex blends.
    crest_nodes=np.array([np.argmin(np.linalg.norm(pts-nodes[k][[0,2]],axis=1)) for k in ('A','B','C','D','V2')])
    meso_valley=np.clip((dv-85)/75,0,1);meso_valley=meso_valley**2*(3-2*meso_valley)
    relief=w*meso_valley*(.38*np.sin(pts[:,0]*2*np.pi/140)*np.sin(pts[:,1]*2*np.pi/125)+.22*np.cos((pts[:,0]+pts[:,1])*2*np.pi/160))
    relief[list(special)]=0;top+=18*relief
    top[:R]=rim_y[:R];bottom[:R]=rim_y[:R]
    V=np.vstack((np.column_stack((pts[:,0],top,pts[:,1])),np.column_stack((pts[R:,0],bottom[R:],pts[R:,1]))));V=g.native_world(V)
    bottom_ids=np.r_[np.arange(R),np.arange(N,2*N-R)];faces=np.vstack((tris[:,[0,2,1]],bottom_ids[tris]))
    controls=[]
    def control(id,default,lo,hi,center,weight,disp,semantic,exercise):
        controls.append(dict(id=id,default=default,min=lo,max=hi,position_world=center,weights=g.f32(weight).tolist(),displacements_world=np.column_stack((np.zeros(len(V)),disp,np.zeros(len(V)))).tolist(),semantic=semantic,units='m' if id!='C07_Meso_Relief' else 'amplitude m',exercise_value=exercise))
    for row,key in zip(plan['controls'][:4],'ABCD'):
        q=np.sum(((pts-nodes[key][[0,2]])/(np.array(row['plan_span_xz_m'])/2))**2,1);ww=w*np.maximum(0,1-q)**2;ww[:R]=0;support=np.r_[ww,np.zeros(N-R)]
        control(row['id'],row['default_crest_y_m'],*row['crest_y_range_m'],nodes[key].tolist(),support,support,row['shape'],row['default_crest_y_m']+5)
    ww=w*np.maximum(0,1-(dv/160)**2)**2;ww[:R]=0;support=np.r_[ww,np.zeros(N-R)]
    control('C05_Main_Valley',740,735,780,nodes['V2'].tolist(),support,support,'Shared main/blind-branch valley floor lift; V2 has one canonical vertex',745)
    width_band=np.clip((dv-55)/45,0,1)*np.clip((160-dv)/60,0,1)
    width_disp=-w*width_band*np.maximum(0,top-yv)*1.6
    width_disp[:R]=0;width_disp[crest_nodes]=0
    controls[-1]['secondary_parameters']=[dict(id='width_multiplier',default=1.,min=.9,max=1.1,exercise_value=1.05,units='dimensionless',semantic='Widen/narrow the shoulder field on fixed XZ, preserving the shared floor and blind end; no rim translation',displacements_world=np.column_stack((np.zeros(len(V)),np.r_[width_disp,np.zeros(N-R)],np.zeros(len(V)))).tolist())]
    ww=w.copy();ww[:R]=0;support=np.r_[np.zeros(N),ww[R:]]
    control('C06_Belly',585,560,615,[4380,585,4110],support,support,'Lower-volume fullness parameter, not a constant belly height; invalid states reject',586)
    support=np.r_[np.abs(relief),np.zeros(N-R)];disp=np.r_[relief,np.zeros(N-R)]
    control('C07_Meso_Relief',18,0,25,[4380,825,4110],support,disp,'Shoulder breakup only, valley85m exclusion, authoritative nodes excluded',20)
    c=dict(version=g.VERSION,stage='isolated_author_candidate',anchor_world=[3958,0,3667],scale=[1,1,1],vertices_world=V.tolist(),faces=faces.tolist(),planar_vertex_count=N,rim_count=R,planar_triangles=tris.tolist(),external_rim_authority_float64_xz=rim64.tolist(),controls=controls,section_paths=section_ids,authoritative_vertices=[dict(index=i,**row) for i,row in special.items()],named_nodes={k:dict(vertex_index=int(np.argmin(np.linalg.norm(pts-v[[0,2]],axis=1))),world_xyz=v.tolist()) for k,v in nodes.items() if k!='A_belly'},contact_acceptance=False,world_acceptance=False,global_GOAL=False,source_visual_acceptance=False)
    c['manual_edit_probe']=dict(vertex_index=next(i for i in range(R,N) if i not in special and top[i]<1000 and d[i]>100),delta_local=[0,0,.125])
    error=np.linalg.norm(rim-rim64,axis=1);c['rim_numerics']=dict(source_segments=203,exact_source_join_method='Fraction intersections of adjacent frozen source-welded projected edges; exact common source endpoint for parallel lines',maximum_catalog_join_delta_m=max(x['catalog_delta_m'] for x in joins),float32_max_corresponding_vertex_error_m=float(error.max()),float32_rms_vertex_error_m=float(np.sqrt(np.mean(error**2))),corresponding_segment_Hausdorff_upper_m=float(error.max()),pointwise_identity=False,world_contact_contract_modified=False,source_catalog_sha256=g.sha(g.HERE.parent/'design-v3/external-rim.json'))
    return c,dict(joins=joins,source_rim_float64=rim64.tolist(),native_rim_float32_world=rim.tolist()),dict(preparation_seconds=time.monotonic()-start,points=N,triangles=len(faces))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    if not args.write:print('Read-only default; --write prepares finite candidate, never native.');return
    c,r,report=make();g.write(g.CANDIDATE_PATH,c);g.write(g.HERE/'rim-source-binding.json',r);report['geometry']=g.validate_candidate(c)
    report['controls']=[]
    for row in c['controls']:
        moved=g.evaluate(c,{row['id']:row['exercise_value']});report['controls'].append(dict(id=row['id'],exercise_value=row['exercise_value'],changed_vertices=int(np.any(moved!=np.array(c['vertices_world']),1).sum())))
    
    for row in c['controls']:
        for extra in row.get('secondary_parameters',[]):
            key=row['id']+'.'+extra['id'];moved=g.evaluate(c,{key:extra['exercise_value']});report['controls'].append(dict(id=key,exercise_value=extra['exercise_value'],changed_vertices=int(np.any(moved!=np.array(c['vertices_world']),1).sum())))
    g.write(g.HERE/'candidate-preparation.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()
