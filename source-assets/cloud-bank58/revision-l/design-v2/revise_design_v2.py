"""Pure offline v2 section resolver, checks and diagrams. No engine or mesh builder.
Required explicit repository and verified NPZ paths; no sibling-directory fallback.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,math,os
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import binary_fill_holes
from scipy.spatial import cKDTree

HERE=Path(__file__).resolve().parent
class Reject(ValueError): pass

def need(value, code):
    if not value: raise Reject(code)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def exact_rows_sha(x):return hashlib.sha256(np.asarray(x,dtype='<f8').tobytes()).hexdigest()

def load_inputs(definition,aether_root,survey_npz):
    definition=Path(definition).resolve();root=Path(aether_root).resolve();npz=Path(survey_npz).resolve()
    spec=json.loads(definition.read_text());ident=spec['inherits'];base=root/ident['base_directory']
    bindings={ 'design_plan.json':'design_plan_sha256','design-landmarks.json':'landmarks_sha256','evidence-bindings.json':'bindings_sha256','draw_design_schematics.py':'old_plot_script_sha256'}
    for name,key in bindings.items():need((base/name).is_file() and sha(base/name)==ident[key],'INPUT_IDENTITY:'+name)
    need(npz.is_file() and sha(npz)==ident['survey_npz_sha256'],'INPUT_IDENTITY:survey_npz')
    plan=json.loads((base/'design_plan.json').read_text());landmarks=json.loads((base/'design-landmarks.json').read_text());evidence=json.loads((base/'evidence-bindings.json').read_text())
    g=np.load(npz);xs=g['xs'];zs=g['zs'];mask=np.isfinite(g['CloudSea_1_1_top']);filled=binary_fill_holes(mask)
    need(xs.shape==(340,) and zs.shape==(360,) and mask.shape==(360,340),'GRID_SHAPE')
    need(int(np.count_nonzero(filled&~mask))==20,'GRID_INTERNAL_HOLES')
    need(not (filled[0].any() or filled[-1].any() or filled[:,0].any() or filled[:,-1].any()),'GRID_OUTER_CONTOUR_TRUNCATED')
    zz,xx=np.where(~filled);external=np.c_[xs[xx],zs[zz]]
    return {'spec':spec,'plan':plan,'landmarks':landmarks,'evidence':evidence,'grid':g,'xs':xs,'zs':zs,'mask':mask,'filled':filled,'tree':cKDTree(external),'base':base,'root':root,'npz':npz,'definition':definition}

def resolve_nodes(spec,base):
    by={c['id']:c for c in base['controls']};valley=by['C05_Main_Valley'];nodes={}
    for name,row in spec['nodes'].items():
        if 'base_control' in row:
            c=by[row['base_control']];x,z=c['world_center_xz_m'];nodes[name]=np.array([x,c['default_crest_y_m'],z],float)
        elif 'base_main_valley_index' in row:
            x,z,y=valley['path_xzy_m'][row['base_main_valley_index']];nodes[name]=np.array([x,y,z],float)
        elif 'base_branch_index' in row:
            x,z,y=valley['blind_branch_xzy_m'][row['base_branch_index']];nodes[name]=np.array([x,y,z],float)
        elif 'xz_of_node' in row:
            ref=nodes[row['xz_of_node']];nodes[name]=np.array([ref[0],row['y_m'],ref[2]],float)
        else:nodes[name]=np.array(row['world_xyz_m'],float)
        need(nodes[name].shape==(3,) and np.isfinite(nodes[name]).all(),'NODE_FINITE:'+name)
    return nodes

def resolve_section(name,row,nodes):
    scalar=lambda v:float(nodes[v['node_y']][1]) if isinstance(v,dict) else float(v)
    if row['path_kind']=='line':
        s=np.array(row['stations_m'],float);origin=nodes[row['origin_node']][[0,2]];direction=np.array(row['xz_direction'],float)
        path_s=np.array([s[0],s[-1]]);path_xz=origin+path_s[:,None]*direction
        anchors=row['anchor_stations']
    else:
        path_xz=np.array([nodes[k][[0,2]] for k in row['path_nodes']]);lengths=np.linalg.norm(np.diff(path_xz,axis=0),axis=1);path_s=np.r_[0,np.cumsum(lengths)]
        def station(v):
            if 'node' in v:return float(path_s[row['path_nodes'].index(v['node'])])
            return float(path_s[v['segment']]+lengths[v['segment']]*v['fraction'])
        s=np.array([station(v) for v in row['stations']]);anchors=[{'node':k,'station_m':float(t),**({'bottom_node':row['bottom_anchor_nodes'][k]} if k in row.get('bottom_anchor_nodes',{}) else {})} for k,t in zip(row['path_nodes'],path_s)]
    top=np.array([scalar(v) for v in row['top_y_m']]);bottom=np.array([scalar(v) for v in row['bottom_y_m']])
    need(len(s)==len(top)==len(bottom) and np.all(np.diff(s)>0),'STATION_IDENTITY:'+name)
    need(np.isfinite(top).all() and np.isfinite(bottom).all(),'PROFILE_FINITE:'+name)
    return {'id':name,'stations':s,'top_values':top,'bottom_values':bottom,'top':PchipInterpolator(s,top),'bottom':PchipInterpolator(s,bottom),'path_s':path_s,'path_xz':path_xz,'anchors':anchors,'maximum_node':row['maximum_node']}

def world_xz(p,t):
    t=np.asarray(t);return np.stack([np.interp(t,p['path_s'],p['path_xz'][:,j]) for j in range(2)],axis=-1)

def polynomial_range(pp,a,b):
    """All extrema of a piecewise cubic over [a,b], not only endpoint samples."""
    cuts=np.unique(np.r_[a,pp.x[(pp.x>a)&(pp.x<b)],b]);values=[];locations=[]
    for lo,hi in zip(cuts[:-1],cuts[1:]):
        j=min(max(np.searchsorted(pp.x,(lo+hi)/2,side='right')-1,0),len(pp.x)-2);co=pp.c[:,j];d=np.polyder(co);roots=np.roots(d) if np.any(d) else []
        pts=[lo,hi]+[float(r.real+pp.x[j]) for r in roots if abs(r.imag)<1e-10 and lo<r.real+pp.x[j]<hi]
        vals=np.asarray(pp(pts));values.extend(vals.tolist());locations.extend(pts)
    k=int(np.argmin(values));q=int(np.argmax(values));return float(values[k]),float(values[q]),float(locations[k]),float(locations[q])

def interval_audit(p,ctx):
    form=ctx['plan']['form'];gate=float(form['interior_min_vertical_thickness_m']);edge=float(form['interior_distance_from_outer_rim_m']);blo,bhi=form['target_interior_belly_y_range_m'];need(gate==120 and edge==80 and [blo,bhi]==[560,630],'ORIGINAL_GATES_CHANGED')
    # Include every interpolation/path knot. Each interval is <=1m along parameter;
    # world motion radius is evaluated from its actual linear XZ path.
    breaks=np.unique(np.r_[np.linspace(p['stations'][0],p['stations'][-1],int(math.ceil(p['stations'][-1]-p['stations'][0]))+1),p['stations'],p['path_s']])
    thick=PchipInterpolator(p['stations'],p['top_values']);thick.c=p['top'].c-p['bottom'].c
    intervals=[];violations=[];guarded_min=float('inf');guarded_bmin=float('inf');guarded_bmax=-float('inf')
    for a,b in zip(breaks[:-1],breaks[1:]):
        mid=(a+b)/2;pt=world_xz(p,mid);radius=max(np.linalg.norm(world_xz(p,a)-pt),np.linalg.norm(world_xz(p,b)-pt));d=float(ctx['tree'].query(pt)[0]);halfdiag=math.sqrt(2)*2.5
        lower=max(0,d-halfdiag-radius);upper=d+radius
        # Only intervals wholly below 80m even by the conservative upper distance
        # are exempt. Near the threshold we enforce the interior rule as well.
        guarded=bool(upper>=edge)
        tm,tx,tat,_=polynomial_range(thick,a,b);bm,bx,_,_=polynomial_range(p['bottom'],a,b)
        row={'a_m':float(a),'b_m':float(b),'external_discrete_distance_lower_m':lower,'external_center_distance_upper_m':upper,'guarded_as_interior':guarded,'thickness_min_m':tm,'thickness_min_at_m':tat,'belly_min_m':bm,'belly_max_m':bx}
        intervals.append(row)
        if guarded:
            guarded_min=min(guarded_min,tm);guarded_bmin=min(guarded_bmin,bm);guarded_bmax=max(guarded_bmax,bx)
            if tm<gate-1e-9:violations.append({'code':'INTERIOR_THICKNESS','section':p['id'],**row})
            if bm<blo-1e-9 or bx>bhi+1e-9:violations.append({'code':'INTERIOR_BELLY_RANGE','section':p['id'],**row})
    end=p['stations'][-1];pt=world_xz(p,end);dc=float(ctx['tree'].query(pt)[0]);ix=int(np.argmin(abs(ctx['xs']-pt[0])));iz=int(np.argmin(abs(ctx['zs']-pt[1])));g=ctx['grid'];names=[f'CloudSea_{x}_{z}' for x in [0,1,2] for z in [0,1,2] if (x,z)!=(1,1)]
    exempt=[]
    for row in intervals:
        if not row['guarded_as_interior']:
            if exempt and abs(exempt[-1][1]-row['a_m'])<1e-9:exempt[-1][1]=row['b_m']
            else:exempt.append([row['a_m'],row['b_m']])
    return {'section':p['id'],'edge_exempt_ranges_m':exempt,'interval_count':len(intervals),'guarded_interval_count':sum(r['guarded_as_interior'] for r in intervals),'edge_exempt_interval_count':sum(not r['guarded_as_interior'] for r in intervals),'guarded_thickness_min_m':guarded_min,'guarded_belly_range_m':[guarded_bmin,guarded_bmax],'whole_profile_thickness_min_m':polynomial_range(thick,p['stations'][0],end)[0],'endpoint':{'station_m':float(end),'world_xz_m':pt.tolist(),'top_y_m':float(p['top'](end)),'bottom_y_m':float(p['bottom'](end)),'thickness_m':float(p['top'](end)-p['bottom'](end)),'external_center_distance_m':dc,'external_cell_discrete_lower_m':max(0,dc-math.sqrt(2)*2.5),'selected_sample_covered':bool(ctx['mask'][iz,ix]),'any_eight_neighbor_sample_covered':any(np.isfinite(g[n+'_top'][iz,ix]) for n in names)},'intervals':intervals,'violations':violations}

def validate(ctx,spec=None):
    spec=spec or ctx['spec'];nodes=resolve_nodes(spec,ctx['plan']);profiles={k:resolve_section(k,v,nodes) for k,v in spec['sections'].items()};issues=[]
    # Preserve the exact 52-points authority, including A/B/C/D crest meanings.
    for i,key in enumerate('ABCD'):
        source=np.array(ctx['landmarks']['groups'][i]['rows'][0]['world_xyz_m'],float)
        if not np.array_equal(nodes[key],source):issues.append('CONTROL_LANDMARK_DRIFT:'+key)
    main=[nodes[k] for k in spec['main_valley_nodes']];branch=[nodes[k] for k in spec['branch_valley_nodes']];hub=nodes[spec['shared_junction']]
    if not np.array_equal(branch[0],hub) or not any(np.array_equal(p,hub) for p in main):issues.append('SHARED_JUNCTION_IDENTITY')
    for a in main:
        if np.array_equal(a[[0,2]],branch[0][[0,2]]) and a[1]!=branch[0][1]:issues.append('SHARED_JUNCTION_HEIGHT')
    for p in profiles.values():
        for anchor in p['anchors']:
            node=nodes[anchor['node']];t=anchor['station_m']
            if not np.allclose(world_xz(p,t),node[[0,2]],rtol=0,atol=1e-9) or abs(float(p['top'](t))-node[1])>1e-9:issues.append('PROFILE_ANCHOR_DRIFT:'+p['id']+':'+anchor['node'])
            if 'bottom_node' in anchor:
                lower=nodes[anchor['bottom_node']]
                if not np.allclose(world_xz(p,t),lower[[0,2]],rtol=0,atol=1e-9) or abs(float(p['bottom'](t))-lower[1])>1e-9:issues.append('PROFILE_BOTTOM_ANCHOR_DRIFT:'+p['id']+':'+anchor['bottom_node'])
        highest=nodes[p['maximum_node']];_,height,_,at=polynomial_range(p['top'],p['stations'][0],p['stations'][-1])
        if abs(height-highest[1])>1e-9 or not np.allclose(world_xz(p,at),highest[[0,2]],rtol=0,atol=1e-9):issues.append('PROFILE_CREST_DRIFT:'+p['id'])
    audits=[interval_audit(p,ctx) for p in profiles.values()]
    for a in audits:issues.extend(sorted({x['code']+':'+a['section'] for x in a['violations']}))
    report={'version':'v2-offline-consistency','passed':not issues,'issues':issues,'scope':spec['validation_scope'],'node_coordinates_xyz_m':{k:v.tolist() for k,v in nodes.items()},'main_valley_xyz_m':[x.tolist() for x in main],'branch_valley_xyz_m':[x.tolist() for x in branch],'resolved_control_override':{'id':'C05_Main_Valley','path_xzy_m':[x[[0,2,1]].tolist() for x in main],'blind_branch_xzy_m':[x[[0,2,1]].tolist() for x in branch],'all_other_control_fields':'inherit exact v1 base unchanged'},'section_audits':audits,'unchanged_constraints':ctx['plan']['form'],'source_definition_sha256':hashlib.sha256(canonical(spec)).hexdigest(),'original_definition_file_sha256':sha(ctx['definition']),'survey_npz_sha256':sha(ctx['npz']),'native_geometry':False,'interface_acceptance':False,'pixel_acceptance':False,'analytical_true_mesh_boundary_distance_proven':False,'internal_cells_filled_only_for_outer_edge_classification':int(np.count_nonzero(ctx['filled']&~ctx['mask'])),'roundoff_note':'1e-9 arithmetic comparison guard only; no physical 120m/80m gate change. Reported valid margins are meters, not epsilon-level passes.'}
    return report,profiles,nodes

def line_data(profiles):
    result={}
    for name,p in profiles.items():
        t=np.unique(np.r_[np.linspace(p['stations'][0],p['stations'][-1],501),p['stations']]);result[name]={'x':t.tolist(),'top':p['top'](t).tolist(),'bottom':p['bottom'](t).tolist()}
    return result

def check_plot_trace(trace,profiles):
    expected=line_data(profiles)
    need(set(trace)==set(expected),'PLOT_GROUP_DRIFT')
    for name,row in expected.items():
        for key,values in row.items():need(np.array_equal(np.array(trace[name][key]),np.array(values)),'PLOT_DATA_DRIFT:'+name+':'+key)

def check_rendered_receipt(ctx,out,record=None):
    from PIL import Image
    out=Path(out);record=record or json.loads((out/'plot-trace.json').read_text())
    need(record['definition_file_sha256']==sha(ctx['definition']),'STALE_PLOT_DEFINITION')
    _,profiles,_=validate(ctx);check_plot_trace(record['lines'],profiles)
    for im in record['images']:
        path=out/im['path'];need(path.is_file() and sha(path)==im['sha256'] and path.stat().st_size==im['bytes'],'PNG_BYTE_DRIFT:'+im['path'])
        with Image.open(path) as image:
            image.load();need(image.info.get('DesignDefinitionSHA256')==sha(ctx['definition']) and image.info.get('SectionID')==im['section'],'PNG_METADATA_DRIFT:'+im['path'])
    return True

def render(ctx,out):
    report,profiles,nodes=validate(ctx);need(report['passed'],'DESIGN_REJECTED:'+','.join(report['issues']))
    out=Path(out).resolve();need(not out.is_relative_to(ctx['root']),'OUTPUT_MUST_BE_OUTSIDE_AETHER');out.mkdir(parents=True,exist_ok=True)
    os.environ['MPLCONFIGDIR']=str(out/'runtime-cache');os.environ['XDG_CACHE_HOME']=str(out/'runtime-cache')
    import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    data=line_data(profiles);trace={};images=[]
    for name,p in profiles.items():
        row=data[name];x=np.array(row['x']);top=np.array(row['top']);bottom=np.array(row['bottom']);fig,ax=plt.subplots(figsize=(12.2,6.5),layout='constrained')
        ax.fill_between(x,bottom,top,color='#bdcfdf');lt,=ax.plot(x,top,color='#294662',lw=3);lb,=ax.plot(x,bottom,color='#516a80',lw=2);ax.scatter(p['stations'],p['top_values'],s=24,color='#294662');ax.scatter(p['stations'],p['bottom_values'],s=18,color='#516a80')
        actual={'x':lt.get_xdata().tolist(),'top':lt.get_ydata().tolist(),'bottom':lb.get_ydata().tolist()};trace[name]=actual
        section_audit=next(a for a in report['section_audits'] if a['section']==name)
        for lo,hi in section_audit['edge_exempt_ranges_m']:ax.axvspan(lo,hi,color='#e7bd82',alpha=.20,zorder=-3)
        for j,a in enumerate(p['anchors']):
            t=a['station_m'];y=float(p['top'](t));ax.annotate(f"{a['node']}: Y {y:g}",xy=(t,y),xytext=(t+(-35 if name=='near_A' else (-130 if j==len(p['anchors'])-1 else 20)),y+80+20*(j%2)),fontsize=11,arrowprops=dict(arrowstyle='->',color='#294662'))
        if name=='near_A':
            end=p['stations'][-1];ty=float(p['top'](end));by=float(p['bottom'](end));ax.annotate(f"t {end:g}: top {ty:g} / belly {by:g} / thickness {ty-by:g} m",xy=(end,(ty+by)/2),xytext=(-210,500),arrowprops=dict(arrowstyle='->'),fontsize=10)
            ax.text(-235,1100,'Tinted left-tip band: explicit outer-edge exception',fontsize=10,color='#8b632e')
            title='Corrected near-facing A section: crest anchored at t=0; thick curved belly';xlabel='t (m); world XZ = A.xz + t * inherited direction (0.7282,-0.6854)';filename='04-near-shoulder-section-v2.png'
        else:
            title='D to A to valley to B: anchors use exact node positions and path distance';xlabel='Actual XZ polyline arc distance (m); unfolded section, not a camera silhouette';filename='03-central-volume-section-v2.png'
        ax.set(title=title,xlabel=xlabel,ylabel='World Y (m)',ylim=(450,1160));ax.grid(alpha=.2)
        fig.suptitle('V2 OFFLINE DESIGN SECTION | Not native geometry or pixel evidence',fontsize=15,weight='bold')
        ax.text(.01,.015,'One machine definition drives the curves, controls and generated text; external-rim gate unchanged',transform=ax.transAxes,fontsize=9,color='#52606e')
        fig.savefig(out/filename,dpi=155,metadata={'DesignDefinitionSHA256':sha(ctx['definition']),'SectionID':name});plt.close(fig);images.append({'path':filename,'sha256':sha(out/filename),'bytes':(out/filename).stat().st_size,'section':name})
    check_plot_trace(trace,profiles)
    (out/'plot-trace.json').write_text(json.dumps({'status':'Actual Matplotlib line data, checked against the resolved authority','definition_file_sha256':sha(ctx['definition']),'lines':trace,'images':images},indent=2)+'\n')
    import gzip
    raw=canonical({'sections':{a['section']:a['intervals'] for a in report['section_audits']}})
    (out/'interval-audit.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    stored=copy.deepcopy(report)
    for a in stored['section_audits']:a.pop('intervals')
    stored['interval_storage']={'path':'interval-audit.json.gz','encoding':'gzip of canonical UTF-8 JSON','raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),'compressed_sha256':sha(out/'interval-audit.json.gz')}
    (out/'validation-report.json').write_text(json.dumps(stored,indent=2)+'\n')
    lines=['# 机器定义生成的修订剖面记录','', '仅离线设计一致性；不是实体、接缝或原生验收。','',f"权威定义 SHA256：`{sha(ctx['definition'])}`",'', '## 三项修正','']
    near=profiles['near_A'];end=near['stations'][-1];lines += [f"- A冠点：{nodes['A'].tolist()}；near t=0顶高 {float(near['top'](0)):g}m",f"- near t={end:g}：顶 {float(near['top'](end)):g}m、底 {float(near['bottom'](end)):g}m、厚 {float(near['top'](end)-near['bottom'](end)):g}m",f"- 主/支谷共同节点 V2：{nodes['V2'].tolist()}（XYZ顺序）；两条路径引用同一节点",'', '## 全段有限空间门与分段多项式极值','']
    for a in report['section_audits']:lines += [f"- {a['section']}：{a['interval_count']}个≤1m参数区间，{a['guarded_interval_count']}个按内域守门；守门区间最小厚 {a['guarded_thickness_min_m']:.6f}m，腹面范围 {a['guarded_belly_range_m']}m；明确边缘豁免范围 {a['edge_exempt_ranges_m']}"]
    lines += ['',report['scope'],'','内域分类仅依据归档5m掩码；内存填20个内部空格以识别外缘。外缘距离与多项式连续极值不是实际新三维网格证明。','', '## 位于剖面上的权威节点','']
    for p in profiles.values():
        for a in p['anchors']:lines.append(f"- {p['id']} / {a['node']}：弧距 {a['station_m']:.9f}m，XYZ={nodes[a['node']].tolist()}")
    (out/'RESOLVED_PROFILE.md').write_text('\n'.join(lines)+'\n')
    return report

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aether-root',required=True);ap.add_argument('--survey-npz',required=True);ap.add_argument('--definition',default=str(HERE/'profile-definition.json'));ap.add_argument('--render-to');args=ap.parse_args();ctx=load_inputs(args.definition,args.aether_root,args.survey_npz)
    if args.render_to:r=render(ctx,args.render_to)
    else:r,_,_=validate(ctx)
    print(json.dumps({'passed':r['passed'],'issues':r['issues'],'section_summaries':[{k:v for k,v in a.items() if k not in ('intervals','violations')} for a in r['section_audits']]},indent=2));return 0 if r['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
