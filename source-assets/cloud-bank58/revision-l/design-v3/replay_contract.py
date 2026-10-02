"""Read-only design-v3 geometry witnesses. No candidate, native or file writer.
Uses frozen build-v1 projection boundary ONLY, not its survey/analyze pipeline.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, math, sys
sys.dont_write_bytecode = True
import numpy as np
from scipy.ndimage import label, distance_transform_edt
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
L='source-assets/cloud-bank58/revision-l/'
NAMES=['CloudSea_1_1','CloudSea_0_1','CloudSea_1_0','CloudSea_1_2','CloudSea_2_1']
class Rejected(ValueError): pass
def need(value,code):
    if not value: raise Rejected(code)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def check_dependencies():
    rows=json.loads((HERE/'dependencies.json').read_text())['files']
    for r in rows:
        p=ROOT/r['path'];need(p.is_file() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'DEPENDENCY:'+r['path'])
    return len(rows)
def distance(point,segments):
    a=np.asarray(segments)[:,0];d=np.asarray(segments)[:,1]-a;den=np.sum(d*d,axis=1)
    t=np.clip(np.divide(np.sum((np.asarray(point)-a)*d,axis=1),den,out=np.zeros(len(d)),where=den>0),0,1)
    return np.linalg.norm(a+t[:,None]*d-point,axis=1)
def mesh_edges(t):
    v,ii=np.unique(t.reshape(-1,3),axis=0,return_inverse=True);f=ii.reshape(-1,3)
    e=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);eu,ei=np.unique(np.sort(e,axis=1),axis=0,return_inverse=True)
    return v,f,e,eu,ei

def ordered_ring(segments):
    # Preserve exact source segment payloads; order only. Small endpoint residual
    # is reported, never repaired by moving the historical curve.
    todo=set(range(len(segments)));i=0;points=[segments[i,0]];order=[];signs=[];start=segments[i,0];current=start
    while todo:
        choices=[]
        for j in todo:
            for flip in [False,True]:
                a,b=segments[j][::-1] if flip else segments[j]
                choices.append((float(np.linalg.norm(a-current)),j,flip,a,b))
        d,j,flip,a,b=min(choices,key=lambda x:(x[0],x[1],x[2]));need(d<1e-4,'RING_JOIN')
        order.append(j);signs.append(flip);points.append(b);todo.remove(j);current=b
    need(np.linalg.norm(current-start)<1e-4,'RING_CLOSE')
    return order,signs,np.array(points)

def full_hits(t,p):
    q=t[:,:,[0,2]];M=np.transpose(q[:,1:]-q[:,0:1],(0,2,1));det=np.linalg.det(M);good=abs(det)>1e-10
    uv=np.full((len(t),2),np.nan);uv[good]=np.linalg.solve(M[good],(p-q[:,0])[good,:,None])[:,:,0]
    ids=np.flatnonzero(good&(uv[:,0]>=-1e-10)&(uv[:,1]>=-1e-10)&(uv.sum(1)<=1+1e-10))
    y=t[ids,0,1]+np.sum(uv[ids]*(t[ids,1:,1]-t[ids,0:1,1]),axis=1);order=np.argsort(y)
    return ids[order],y[order],uv[ids[order]]
def edge_segments(t):
    q=t[:,:,[0,2]];return np.concatenate([q[:,[0,1]],q[:,[1,2]],q[:,[2,0]]])
def local_witness(t,n,p):
    # All projected edges are examined, including non-hit triangles. Thus an
    # open disk smaller than this clearance cannot acquire a hidden extra hit.
    clearance=min(float(distance(p,edge_segments(t)).min()),float(distance(p,edge_segments(n)).min()))
    need(clearance>1e-8,'WITNESS_ON_PROJECTED_EDGE')
    half=clearance/4 # corners are clearance*sqrt(2)/4 away, well inside disk
    corners=np.array([p+[x*half,z*half] for x,z in [(-1,-1),(-1,1),(1,1),(1,-1)]])
    rows={}
    for key,tri in [('old_selected',t),('neighbor',n)]:
        ids,ys,uv=full_hits(tri,p);need(len(ids)==2,'WITNESS_NOT_SINGLE_INTERVAL')
        vals=[]
        for q in corners:
            ii,vv,_=full_hits(tri,q);need(np.array_equal(ii,ids),'LOCAL_HIT_IDENTITY');vals.append(vv)
        vals=np.array(vals)
        rows[key]={'center_triangle_ids':ids.tolist(),'center_interval_y_m':ys.tolist(),'center_barycentric':np.c_[1-uv.sum(1),uv].tolist(),'corner_intervals_y_m':vals.tolist(),'lower_range_y_m':[float(vals[:,0].min()),float(vals[:,0].max())],'upper_range_y_m':[float(vals[:,1].min()),float(vals[:,1].max())]}
    lo=625.;hi=max(lo+120,rows['neighbor']['upper_range_y_m'][1])
    need(hi<=1057.0673217773438,'LOCAL_ENVELOPE_HEIGHT')
    old_margin=min(min(x[1],y[1])-max(x[0],y[0]) for x,y in zip(rows['old_selected']['corner_intervals_y_m'],rows['neighbor']['corner_intervals_y_m']))
    overlap=min(min(hi,y[1])-max(lo,y[0]) for y in rows['neighbor']['corner_intervals_y_m'])
    need(old_margin>0 and overlap>0,'LOCAL_NO_VOLUME_OVERLAP')
    return {'center_xz_m':p.tolist(),'halfwidth_m':half,'all_projected_edge_clearance_m':clearance,'corners_xz_m':corners.tolist(),'source_intervals':rows,'old_min_overlap_m':old_margin,'existential_constant_interval_y_m':[lo,hi],'existential_interval_min_overlap_m':overlap,'area_m2':float(4*half*half),'claim':'Local affine-neighbor square certificate only. This legal interval is an existence witness, not an authored candidate, control recipe, contact gate or future global proof.'}

def compute():
    count=check_dependencies();old=load(ROOT/(L+'build-v1/interface-feasibility.py'),'frozen_interface_v1')
    clouds=old.decode();t=clouds[NAMES[0]]['triangles']
    seg,labels,loops,candidates,source=old.projection_boundary(t,mesh_edges(t))
    outer=max(loops,key=lambda r:r['absolute_area_m2'])['component'];idx=np.flatnonzero(labels==outer)
    need(len(idx)==203 and len(seg)==210,'OLD_BOUNDARY_IDENTITY')
    outerseg=seg[idx];order,flips,ring=ordered_ring(outerseg);records=[]
    for number,(j,flip) in enumerate(zip(order,flips)):
        k=idx[j];s=seg[k][::-1] if flip else seg[k];edge=source[k];a=edge[0,[0,2]];d=edge[1,[0,2]]-a
        u=((s-a)@d)/(d@d)
        records.append({'id':f'outer-{number:03d}','old_boundary_segment_index':int(k),'xz_endpoints_m':s.tolist(),'source_welded_edge_world_xyz_m':edge.tolist(),'source_edge_parameters':u.tolist(),'lock':'XZ only; source Y is provenance and is explicitly not locked'})
    joins=[np.linalg.norm(np.array(records[i]['xz_endpoints_m'][1])-records[(i+1)%len(records)]['xz_endpoints_m'][0]) for i in range(len(records))]
    boundary={'schema':'cloudbank-l-external-rim-v3','source_segments':records,'maximum_endpoint_join_residual_m':float(max(joins)),'external_loop':next(x for x in loops if x['component']==outer),'released_internal_hole_loops':[x for x in loops if x['component']!=outer],'candidate_silhouette_edges':candidates,'source_algorithm':'Bound build-v1 projection_boundary, float64 clipped true triangle projection boundary; no 5m raster/convex hull/filled AABB'}
    g=np.load(ROOT/'cloud-evidence/cloudbank-next-footprint-checkpoint-20261002/survey-grids.npz');base=np.isfinite(g['CloudSea_1_1_top']);witnesses=[]
    for name in NAMES[1:]:
        mask=base&np.isfinite(g[name+'_top']);labs,num=label(mask)
        for comp in range(1,num+1):
            m=labs==comp;d=distance_transform_edt(m);z,x=np.unravel_index(np.argmax(d),d.shape);p=np.array([g['xs'][x],g['zs'][z]])
            w=local_witness(t,clouds[name]['triangles'],p);w.update(neighbor=name,archived_component=comp,archived_component_samples=int(m.sum()),selection='Maximum distance-transform interior of existing overlap component; ties first array order. No new survey.')
            witnesses.append(w)
    old_report=json.loads((ROOT/(L+'build-v1/interface-feasibility.json')).read_text())
    p=np.array(old_report['contradiction_witness']['midpoint_world_xyz_m'])[[0,2]]
    w=local_witness(t,clouds['CloudSea_1_2']['triangles'],p);w.update(neighbor='CloudSea_1_2',role='Original 530 x 4706 contradiction neighborhood; new lower-surface identity explicitly released')
    witnesses.append(w)
    # Reuse the two exact definitions; new bounded question is true-external-rim
    # compatibility, not a rerun of the old survey or old 52 landmark rays.
    v2=load(ROOT/(L+'design-v2/revise_design_v2.py'),'frozen_profiles_v2');spec=json.loads((ROOT/(L+'design-v2/profile-definition.json')).read_text());plan=json.loads((ROOT/(L+'design-v1/design_plan.json')).read_text());nodes=v2.resolve_nodes(spec,plan)
    profile_rows=[]
    for name,definition in spec['sections'].items():
        pr=v2.resolve_section(name,definition,nodes);a,b=pr['stations'][[0,-1]];cuts=np.unique(np.r_[np.linspace(a,b,int(math.ceil(b-a))+1),pr['stations'],pr['path_s']]);bad=[];guarded=0;exempt=0;min_thick=float('inf');belly_min=float('inf');belly_max=-float('inf')
        from scipy.interpolate import PchipInterpolator
        thick=PchipInterpolator(pr['stations'],pr['top_values']);thick.c=pr['top'].c-pr['bottom'].c
        for a,b in zip(cuts[:-1],cuts[1:]):
            mid=(a+b)/2;p=v2.world_xz(pr,mid);radius=max(np.linalg.norm(v2.world_xz(pr,a)-p),np.linalg.norm(v2.world_xz(pr,b)-p));d=float(distance(p,outerseg).min());tm=v2.polynomial_range(thick,a,b)[0];bm,bx,*_=v2.polynomial_range(pr['bottom'],a,b)
            if d+radius<80:exempt+=1
            else:
                guarded+=1;min_thick=min(min_thick,tm);belly_min=min(belly_min,bm);belly_max=max(belly_max,bx)
                if tm<120-1e-9 or bm<560-1e-9 or bx>630+1e-9:bad.append({'a':float(a),'b':float(b),'distance_bounds':[max(0,d-radius),d+radius],'thickness_min':tm,'belly_range':[bm,bx]})
        profile_rows.append({'section':name,'intervals':len(cuts)-1,'guarded':guarded,'exempt':exempt,'guarded_thickness_min_m':min_thick,'guarded_belly_range_m':[belly_min,belly_max],'violations':bad})
    result={'schema':'cloudbank-l-contact-evidence-v3','verified_dependencies':count,'clouds':{name:{k:v for k,v in row.items() if k in ['path','root_transform','mesh_id','vertex_data_sha256','index_data_sha256','world_bounds']} for name,row in clouds.items()},'boundary_canonical_sha256':hashlib.sha256(canonical(boundary)).hexdigest(),'finite_local_witnesses':witnesses,'profile_true_rim_checks':profile_rows,'nodes':{k:v.tolist() for k,v in nodes.items()},'limits':['No candidate mesh or geometry acceptance','Local squares certify an existential interval compatible with each frozen neighbor, not eventual global contact','True boundary reproduced with inherited finite float64 thresholds, not directed-rounding proof','Source rays at eight centers and corners only; no survey or 52-landmark rerun'],'engine_started':False,'candidate_created':False,'contact_acceptance':False,'visual_acceptance':False}
    return boundary,result

def compare(a,b,path='root'):
    if isinstance(a,dict):
        need(isinstance(b,dict) and set(a)==set(b),'KEYS:'+path)
        for k in a:compare(a[k],b[k],path+'/'+k)
    elif isinstance(a,list):
        need(isinstance(b,list) and len(a)==len(b),'LENGTH:'+path)
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
    elif isinstance(a,float):need(isinstance(b,(int,float)) and math.isfinite(b) and abs(a-b)<=1e-8,'NUMBER:'+path)
    else:need(a==b,'VALUE:'+path)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--emit',choices=['boundary','evidence']);ap.add_argument('--verify',action='store_true');args=ap.parse_args();b,e=compute()
    if args.verify:
        compare(b,json.loads((HERE/'external-rim.json').read_text()));compare(e,json.loads((HERE/'contact-evidence.json').read_text()));print(json.dumps({'verified':True,'boundary_segments':len(b['source_segments']),'local_squares':len(e['finite_local_witnesses']),'profiles':e['profile_true_rim_checks'],'candidate_created':False,'contact_acceptance':False},indent=2))
    else:print(json.dumps(b if args.emit=='boundary' else e,indent=2,allow_nan=False))
if __name__=='__main__':main()
