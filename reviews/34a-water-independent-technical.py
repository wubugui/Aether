"""Bounded read-only shader/source/runtime review. No engine or Blender launch."""
from pathlib import Path
import hashlib,json,math,re
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'captures/validation_runs/water-34a-20260908T233808Z-05bd651c68574ef79ba9b59ab98506bb'
NATIVE=ROOT/'captures/water_study_34a'
PRIOR=ROOT/'captures/validation_runs/rightcoast-33f-20260908T233517Z-9aac3867c5f340208c238c9e2b83fc1e'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(NATIVE/'design-plan.json'); manifest=read(RUN/'manifest.json')
s=(NATIVE/'open_water.gdshader').read_text(encoding='utf-8-sig')
old=(ROOT/plan['source']).read_text(encoding='utf-8-sig')
def block(text,start,end):return text[text.index(start):text.index(end,text.index(start))]
depth_same=block(s,'    float scene_depth=','    ALBEDO=')==block(old,'    float scene_depth=','    ALBEDO=')
vertex_same=block(s,'void vertex()', 'void fragment()')==block(old,'void vertex()', 'void fragment()')

# Float32 CPU mirror checks a bounded coordinate/time domain, not GPU sin bit identity.
F=np.float32
cellsize=np.array([6.5,4.5],dtype=F)
wind=np.array([.83,-.56],dtype=F);wind/=np.linalg.norm(wind)
across=np.array([-wind[1],wind[0]],dtype=F)
def hash2(p):
    x=np.sin(p[...,0]*F(127.1)+p[...,1]*F(311.7))*F(43758.5453)
    return x-np.floor(x)
def vertex(ids):
    offsets=np.stack([hash2(ids),hash2(ids+np.array([71.,19.],dtype=F))],axis=-1)-F(.5)
    return (ids+offsets*F(.45))*cellsize
def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]
def inside(q,a,b,c):
    return (cross(b-a,q-a)>=F(-.00001))&(cross(c-b,q-b)>=F(-.00001))&(cross(a-c,q-c)>=F(-.00001))
def noise(p):
    i=np.floor(p); f=p-i;u=f*f*(F(3)-F(2)*f)
    x0=hash2(i)*(1-u[...,0])+hash2(i+np.array([1,0],dtype=F))*u[...,0]
    x1=hash2(i+np.array([0,1],dtype=F))*(1-u[...,0])+hash2(i+np.array([1,1],dtype=F))*u[...,0]
    return x0*(1-u[...,1])+x1*u[...,1]
def height(q):
    return F(.95)*(noise(q*np.array([.028,.055],dtype=F)+np.array([9.2,3.6],dtype=F))-.5)+F(.48)*(noise(q*np.array([.065,.12],dtype=F)+np.array([2.3,1.7],dtype=F))-.5)+F(.09)*(noise(q*np.array([.14,.24],dtype=F)+np.array([17.2,5.6],dtype=F))-.5)
rng=np.random.default_rng(3401)
world=rng.uniform([-3300,-2600],[-1700,-1300],size=(8192,2)).astype(F)
sample=[]; min_det=math.inf; max_hits=0; facet_normals=[]
for time in [0.,18.]:
    q=np.stack([world@wind,world@across],axis=-1);q[:,1]+=F(time*.55)
    ids0=np.floor(q/cellsize);hits=np.zeros(len(q),dtype=int)
    chosen=np.zeros((len(q),3,2),dtype=F)
    for y in range(-1,2):
      for x in range(-1,2):
        ids=ids0+np.array([x,y],dtype=F)
        a=vertex(ids);b=vertex(ids+np.array([1,0],dtype=F))
        c=vertex(ids+np.array([1,1],dtype=F));d=vertex(ids+np.array([0,1],dtype=F))
        even=np.mod(ids[:,0]+ids[:,1],F(2))<1
        for A,B,C,mask in [(a,b,c,even),(a,c,d,even),(a,b,d,~even),(b,c,d,~even)]:
            det=cross(B-A,C-A);min_det=min(min_det,float(det.min()))
            hit=inside(q,A,B,C)&mask
            take=hit&(hits==0)
            chosen[take]=np.stack([A,B,C],axis=1)[take]
            hits+=hit
    # Height field at advected vertices equals noise in q-space in exact arithmetic.
    h=height(chosen)
    uv=chosen.copy();uv[:,:,1]-=F(time*.55)
    wp=uv[:,:,0,None]*wind+uv[:,:,1,None]*across
    p3=np.stack([wp[:,:,0],h,wp[:,:,1]],axis=-1)
    n=np.cross(p3[:,2]-p3[:,0],p3[:,1]-p3[:,0]);n/=np.linalg.norm(n,axis=-1)[:,None]
    n=np.where(n[:,1,None]<0,-n,n)
    facet_normals.append(n)
    max_hits=max(max_hits,int(hits.max()))
    sample.append({'world_time':time,'points':len(q),'not_found':int(np.sum(hits==0)),
                   'multiple_hits_at_epsilon':int(np.sum(hits>1)),
                   'all_normals_finite':bool(np.isfinite(n).all()),
                   'min_up_component':float(n[:,1].min())})

oldreport=read(PRIOR/'images/night-reference.png.json')
revision=read(RUN/'actual-water-revision.json')
views=[]; bindings=[]
for r in revision['views']:
    name=r['view'];p=RUN/'images'/(name+'.png.json');d=read(p)
    expected_time=18. if name=='night-time18' else 0.
    checks={'same_run':d['run_id']==manifest['run_id'],'shader_identity':d['water_shader_sha256']==sha(NATIVE/'open_water.gdshader'),
      'camera_equals_revision':d['camera']==r['camera'],'expected_time':d['environment_study']['sampled_world_time']==expected_time,
      'world_sha_unchanged':d['world_sha256']==oldreport['world_sha256'],
      'rightcoast_glb_unchanged':d['rightcoast_glb_sha256']==oldreport['rightcoast_glb_sha256'],
      'placements_unchanged':d['placements']==oldreport['placements'],
      'named_headland_trees_unchanged':d['headland_study']['trees']==oldreport['headland_study']['trees']}
    views.append({'view':name,'camera':d['camera'],'world_time':expected_time,'checks':checks})
    for f in [p,RUN/'images'/(name+'.png')]:
        key=f.relative_to(RUN).as_posix()
        bindings.append({'path':key,'sha256':sha(f),'matches_manifest':sha(f)==manifest['artifacts'][key]['sha256']})
for key in ['study-inputs/new-environment27f/open_water.gdshader','study-inputs/water34a-builder.py','study-inputs/water34a-design-plan.json','study-inputs/render_water_34a.py']:
    bindings.append({'path':key,'sha256':sha(RUN/key),'matches_manifest':sha(RUN/key)==manifest['artifacts'][key]['sha256']})
logs={name: (RUN/name).stat().st_size for name in ['night-views-error.log','day-views-error.log']}
checks={'source_parent_sha':sha(ROOT/plan['source'])==plan['source_sha256'],
 'source_shader_sha':sha(NATIVE/'open_water.gdshader')==plan['shader_sha256'],
 'frozen_shader_matches_source':sha(RUN/'study-inputs/new-environment27f/open_water.gdshader')==sha(NATIVE/'open_water.gdshader'),
 'depth_color_foam_block_unchanged':depth_same,'vertex_block_unchanged':vertex_same,
 'run_terminal_passed':manifest['status']=='passed' and manifest['passed'],
 'stage_exit_codes_zero':all(x['exit_code']==0 for x in manifest['stages']),
 'bounded_cpu_found_all':all(x['not_found']==0 and x['all_normals_finite'] for x in sample),
 'bounded_cell_orientation_positive':min_det>0,
 'runtime_record_checks':all(all(x['checks'].values()) for x in views),
 'fourteen_selected_bindings_match':all(x['matches_manifest'] for x in bindings)}
report={'scope':'Independent bounded water shader technical review; no engine launch, image art assessment, or repeated land support scan.',
 'source':str(NATIVE/'open_water.gdshader'),'shader_sha256':sha(NATIVE/'open_water.gdshader'),
 'parent_shader_sha256':plan['source_sha256'],'checks':checks,'technical_checks_passed':all(checks.values()),
 'cells':{'previous_cell_m':[3.2,1.1],'current_cell_m':[6.5,4.5],'previous_jitter_fraction':.32,'current_jitter_fraction':.45,
  'cell_area_m2':29.25,'max_vertex_offset_from_grid_m':[1.4625,1.0125],
  'shared_vertex_height_continuity':'C0 by shared integer id and shared sea_height at reconstructed world coordinates; piecewise constant facet normals intentionally discontinuous.',
  'orientation_bound_exact_arithmetic_twice_area_m2':(.55*.55-.45*.45)*6.5*4.5,
  'bounded_float32_min_twice_area_m2':min_det,'cpu_samples':sample,
  'sample_world_xz_bounds':[[-3300,-2600],[-1700,-1300]],'seed':3401,
  'cpu_limit':'NumPy float32 mirror is not a bit-identical GLSL sin implementation or an exhaustive GPU pixel coverage test.',
  'fallback':'No found=false diagnostic in shader; if a numerical lookup miss occurs it uses the default origin triangle. No miss in this bounded CPU sample.'},
 'filter':{'formula':'p=1/(1/180+1.5*(dot(dFdx(R),dFdx(R))+dot(dFdy(R),dFdy(R))))',
  'finite_unit_ray_variance_bound':[0,8],'power_bound':[1/(1/180+12),180],
  'peak_at_zero_variance':1,'nonnegative_finite_under_unit_ray_assumptions':True,
  'energy':'p/180 approximately compensates peak for broadening; normalized cosine-lobe energy uses p+1, so this is not exact energy conservation.',
  'coverage_limit':'Post-branch derivatives measure sampled reflected-ray changes. Facet interiors only see their current facet; no multi-facet prefilter or temporal coverage guarantee.',
  'performance':'Up to 18 triangle inclusion candidates and three noise-height evaluations per fragment; no independent GPU timing collected.'},
 'shore_depth':{'preserved_from_parent':depth_same,'renderer_observed':'OpenGL 3.3 Compatibility; project selects gl_compatibility',
  'method':'Actual depth texture -> inverse projection [-1,1] NDC -> world position -> nonnegative difference in Y; original color/foam retained.',
  'limit':'Scene depth is a visible camera-ray hit, not a vertical same-XZ seabed query; shoreline appearance is still screen-space, especially at oblique views and occlusion.'},
 'limitations':[
  'No vertex displacement: flat geometry, unchanged silhouette, collision and geometric wave/shore intersection.',
  'Moon lobe and sky colors are analytic. No cloud/object/shore scene reflection or local-light specular reflection is implemented.',
  'Custom light() still computes LIGHT_COLOR*ATTENUATION Lambert diffuse, including applicable local lights. No local-light reflection is different from no local illumination.',
  'Earlier sinusoidal NORMAL assignment is overwritten by the final world-to-view facet NORMAL and does not contribute to the output.',
  'ROUGHNESS/SPECULAR values do not add a custom SPECULAR_LIGHT contribution; current custom light() only adds DIFFUSE_LIGHT.',
  'Bounded technical checks and terminal run identity do not establish artistic fidelity or flicker-free animation.'],
 'runtime':{'run_id':manifest['run_id'],'status':manifest['status'],'completed_utc':manifest.get('completed_utc'),
 'stages':[{'name':x['name'],'exit_code':x['exit_code']} for x in manifest['stages']],
 'error_log_bytes':logs,'views':views,'selected_bindings':bindings,
 'land_validation':'Exact runtime record comparison only; prior full geometry/footing validation inherited, not repeated.'},
 'full_reference_accepted':False,'all_reference_goal_complete':False}
(ROOT/'reviews/34a-water-independent-technical.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'passed':report['technical_checks_passed'],'checks':checks,'cpu':sample,'min_twice_area':min_det},indent=2))
