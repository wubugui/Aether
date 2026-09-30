# Appended to the standalone Blender authoring helpers by derive_harbor_paths_22d.py.
import sys
args=sys.argv[sys.argv.index('--')+1:]
survey_path=Path(args[args.index('--survey')+1])
survey=json.loads(survey_path.read_text(encoding='utf-8'))
assert len(survey['paths'])==4
shutil.copy2(survey_path,OUT/'ground-survey.json')
stone_colors=[(.150,.139,.112),(.162,.149,.121),(.141,.133,.110),(.173,.158,.129)]
path_stones=[mat('Harbor worn limestone '+str(i),color) for i,color in enumerate(stone_colors)]
bedding=mat('Harbor buried rubble masonry',(.095,.087,.066))
curbstone=mat('Harbor dressed edge stone',(.165,.150,.119))
route_reports=[]

def smooth(a,b,x):
    t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)

def local(godot,entry):return (godot[0]-entry[0],-(godot[2]-entry[2]),godot[1])

def line_at(row,ratio):
    center=row['center'];tx,_,tz=row['tangent'];width=row['width_m']
    return [center[0]-tz*width*ratio,0,center[2]+tx*width*ratio]

def section(a,b,ratio0,ratio1,entry,inset=0.):
    # Ratio in each cross section preserves exact width and continuous curved boundaries.
    points=[line_at(a,ratio0),line_at(b,ratio0),line_at(b,ratio1),line_at(a,ratio1)]
    if inset:
        center=[sum(p[i] for p in points)/4 for i in range(3)]
        points=[[p[i]+(center[i]-p[i])*inset for i in range(3)] for p in points]
    return [local(p,entry) for p in points]

def block(name,quad,top,bottom,material,bevel=False):
    tops=[top]*4 if isinstance(top,(int,float)) else top
    bottoms=[bottom]*4 if isinstance(bottom,(int,float)) else bottom
    low=[(p[0],p[1],h) for p,h in zip(quad,bottoms)]
    if not bevel:
        return loft(name,[low,[(p[0],p[1],h) for p,h in zip(quad,tops)]],material)
    # A small physical arris bevel catches light while leaving a thick closed stone.
    cx=sum(p[0] for p in quad)/4;cy=sum(p[1] for p in quad)/4
    high=[]
    for p,h in zip(quad,tops):
        dx,dy=cx-p[0],cy-p[1];distance=math.hypot(dx,dy)
        high.append((p[0]+dx/distance*.010,p[1]+dy/distance*.010,h))
    return loft(name,[low,[(p[0],p[1],h-.012) for p,h in zip(quad,tops)],high],material)

for path in survey['paths']:
    reset();index=path['pier_index'];rows=path['rows'];entry=path['entry'];length=path['length_m'];count=len(rows)-1
    start_height=path['deck_y'];end_height=path['house_low_step_top_y']
    # Terrain envelopes include all five transverse samples at BOTH ends of each stone.
    lower=[max(s['position'][1] for r in rows[i:i+2] for s in r['samples'])+.045 for i in range(count)]
    # Raised landing constraints act on groups; height propagation limits the real step between groups.
    groups=[];i=0
    while i<count:
        distance=rows[i]['distance_m'];phase=distance%7.2
        size=3 if i>4 and distance<length-5. and phase<.40 else 1
        size=min(size,count-i);groups.append(list(range(i,i+size)));i+=size
    heights=[]
    for group in groups:
        top=max(lower[i] for i in group)
        # Gradual lifted approach to the existing front doorstep, rather than a terminal high riser.
        top=max(top,end_height-.12*max(0.,length-rows[group[-1]+1]['distance_m']))
        heights.append(max(start_height,top))
    heights[0]=start_height;heights[-1]=end_height
    for j in reversed(range(len(groups)-1)):heights[j]=max(heights[j],heights[j+1]-.18)
    for j in range(1,len(groups)):heights[j]=max(heights[j],heights[j-1]-.18)
    failures=[]
    if abs(heights[0]-start_height)>1e-7:failures.append(['start height',heights[0],start_height])
    if abs(heights[-1]-end_height)>1e-7:failures.append(['end height',heights[-1],end_height])
    cell_heights=[0.]*count
    for group,h in zip(groups,heights):
        for i in group:
            cell_heights[i]=h
            if h<lower[i]-1e-7:failures.append(['terrain envelope',i,h,lower[i]])
    if any(abs(a-b)>.180001 for a,b in zip(heights,heights[1:])):failures.append(['riser bound'])
    (OUT/('path_%d-profile-precheck.json'%index)).write_text(json.dumps({'failures':failures,'groups':groups,'heights':heights,'lower':lower},indent=2),encoding='utf-8')
    if failures:raise RuntimeError('Coupled stair/terrain/endpoint constraints fail: '+str(failures[:10]))
    cells=[];footings=[];curbs=[]
    for i,h in enumerate(cell_heights):
        a,b=rows[i:i+2];quad=section(a,b,-.5,.5,entry)
        low0=min(s['position'][1] for s in a['samples'])-.24
        low1=min(s['position'][1] for s in b['samples'])-.24
        block('Buried stone foundation %03d'%i,quad,h-.16,[low0,low1,low1,low0],bedding)
        # Separate editable tread stones and small visible joints backed by the real masonry base.
        width=(a['width_m']+b['width_m'])/2
        curb_ratio=.16/width
        ratios=[-.5+curb_ratio,(-.5+curb_ratio)/3,(.5-curb_ratio)/3,.5-curb_ratio]
        for k in range(3):
            q=section(a,b,ratios[k]+.003/width,ratios[k+1]-.003/width,entry,inset=.004)
            block('Worn tread %03d stone %d'%(i,k),q,h,h-.16,path_stones[(i*3+k)%4],True)
        curb_h0=.12*smooth(.4,1.8,a['distance_m'])*(1-smooth(length-2.2,length-.2,a['distance_m']))
        curb_h1=.12*smooth(.4,1.8,b['distance_m'])*(1-smooth(length-2.2,length-.2,b['distance_m']))
        for side in [-1,1]:
            r0,r1=(-.5,-.5+curb_ratio) if side<0 else (.5-curb_ratio,.5)
            q=section(a,b,r0,r1,entry)
            block('Dressed stair edge %03d side %s'%(i,side),q,[h+curb_h0,h+curb_h1,h+curb_h1,h+curb_h0],h-.16,curbstone)
        center=[(a['center'][j]+b['center'][j])/2 for j in range(3)];center[1]=h
        min_clearance=h-max(s['position'][1] for r in [a,b] for s in r['samples'])
        cells.append({'index':i,'distance_range_m':[a['distance_m'],b['distance_m']],'top_y':h,'center':center,'top_ground_min_sample_clearance_m':min_clearance,'start_width':a['width_m'],'end_width':b['width_m'],'row_start':a,'row_end':b,'walk_clear_width_min_m':min(a['width_m'],b['width_m'])-.32})
        for row,low in [(a,low0),(b,low1)]:
            for sample in row['samples']:
                at=sample['position'];footings.append({'position':[at[0],low,at[2]],'expected_gap_m':low-at[1]})
    name='harbor_stair_%d'%index
    freeze(name,'Actual surveyed thick stone stair approach in original World, independent editable treads, curved foundations and landings. Endpoints align to pier and existing2m doorstep. Not full collision, reference or production acceptance.')
    route_reports.append({'asset':name,'origin':entry,'house_position':path['house_position'],'house_yaw':path['house_yaw'],'end':path['end'],'length_m':length,'start_top_y':cell_heights[0],'end_top_y':cell_heights[-1],'max_riser_m':max(abs(a-b) for a,b in zip(cell_heights,cell_heights[1:])),'landing_groups':[g for g in groups if len(g)>1],'cells':cells,'footing_samples':footings,'scope':'Footing samples compare the modeled base bottom with original-ground measurements. All five lanes at row boundaries only; independent runtime rays still required.'})
(OUT/'model-report.json').write_text(json.dumps({'label':'22d','assets':reports,'routes':route_reports,'source_survey_run':survey['run_id'],'world_sha256':survey['world_sha256'],'scope':'Four real editable Blender stone approaches. Temporary candidates; no full reference, entire world, production or walk acceptance.'},indent=2),encoding='utf-8')
print('HARBOR STONE APPROACHES BUILT '+str(sum(a['parts'] for a in reports)),flush=True)
