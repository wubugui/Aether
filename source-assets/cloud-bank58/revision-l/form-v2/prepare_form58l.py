"""One deterministic crown/shoulder art revision, top-Y only; no engine import."""
import os,sys
os.environ['OPENBLAS_NUM_THREADS']='1';sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry58l as g
import numpy as np,json,copy,argparse
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'source-v1'
# Explicit authored lobe centers/radii/heights, not random world regeneration.
# First four inherit the four control centers and crest heights. Small lobes are
# subordinate shoulder blocks, not new controls or disconnected objects.
LOBES=[
 ('A',4140,3910,185,180,1005),('B',4330,4480,195,180,1040),
 ('C',4750,4300,185,230,925),('D',4470,3690,210,145,845),
 ('A_near_shoulder',4020,3900,130,150,895),
 ('A_oblique_shoulder',4250,3835,145,120,910),
 ('A_foreground_shoulder',3840,3950,175,175,860),
 ('B_valley_shoulder',4245,4345,140,140,902),
 ('B_side_shoulder',4460,4460,135,155,927),
 ('B_back_shoulder',4310,4600,165,125,912),
 ('C_low_shoulder',4620,4310,145,180,857),
 ('D_near_shoulder',4360,3680,145,115,820)]
def smoothstep(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
def valley_distance(xz,c):
 paths=[['V0','V1','V2','V3','V4'],['V2','VB1','VB2']];d=np.full(len(xz),np.inf)
 for names in paths:
  for ka,kb in zip(names,names[1:]):
   a=np.array(c['named_nodes'][ka]['world_xyz'])[[0,2]];b=np.array(c['named_nodes'][kb]['world_xyz'])[[0,2]];u=b-a;t=np.clip((xz-a)@u/(u@u),0,1);d=np.minimum(d,np.linalg.norm(xz-a-t[:,None]*u,axis=1))
 return d

def make():
 c=g.read(OLD/'candidate.json');b=g.read(OLD/'bindings.json');prior=copy.deepcopy(c);v=np.array(c['vertices_world']);n=c['planar_vertex_count'];r=c['rim_count'];xz=v[:n][:,[0,2]]
 rim=np.array(c['external_rim_authority_float64_xz']);d=g.rim_distance(xz,rim);dv=valley_distance(xz,c)
 # Rounded upper ellipsoid sections interlock at different sizes. Smooth max
 # only blends a 16m band between adjacent authored blocks, so no ridge seam
 # is mistaken for a cut or flat strip; all faces remain flat-shaded.
 target=768+8*np.sin((xz[:,0]-4000)/260)*np.cos((xz[:,1]-4100)/230)
 for name,x,z,rx,rz,crest in LOBES:
  q=((xz[:,0]-x)/rx)**2+((xz[:,1]-z)/rz)**2
  cap=768+(crest-768)*np.sqrt(np.maximum(0,1-q))
  h=np.maximum(16-np.abs(target-cap),0)/16
  target=np.maximum(target,cap)+h*h*4
 # Preserve the same true outer boundary. Quarter-sine top return spreads the
 # former 45m roll over 75m, still strictly inside the UNCHANGED 80m core gate.
 rim_y=685+15*np.sin((xz[:,0]-3950)/260)+12*np.cos((xz[:,1]-4100)/220)
 roll=np.sin(np.minimum(d/75,1)*np.pi/2)
 target=rim_y+(target-rim_y)*roll
 # Wide floor vertices within55m are EXACTLY unchanged; 55..110m joins shoulders.
 influence=smoothstep((dv-55)/55)
 top=v[:n,1]*(1-influence)+target*influence
 # Retain original low-amplitude C07 shoulder field, same control semantics.
 relief=np.array(c['controls'][6]['displacements_world'])[:n,1]
 top+=18*relief*influence
 top[:r]=v[:r,1]
 for row in c['named_nodes'].values():top[row['vertex_index']]=row['world_xyz'][1]
 v[:n,1]=top;v=g.native_world(v);c['vertices_world']=v.tolist();c['version']=g.VERSION
 for row in c['authoritative_vertices']:row['top']=float(v[row['index'],1])
 for row in b['baseline_authority']:
  row['historical_v2_top_world']=row['top_world'];row['top_world']=[row['top_world'][0],float(v[row['vertex_index'],1]),row['top_world'][2]]
 fixed=np.flatnonzero(dv<=55).tolist()
 scope=dict(parent_candidate_sha256=g.sha(OLD/'candidate.json'),parent_bindings_sha256=g.sha(OLD/'bindings.json'),old_top_PCHIP_identity=False,old_bottom_PCHIP_identity=True,maximum_top_displacement_m=120,topology_unchanged=True,all_XZ_unchanged=True,complete_nonconvex_rim_unchanged=True,belly_unchanged=True,main_crowns_and_valley_nodes_unchanged=True,core80m_rule_unchanged=True,top_return_m=75,old_top_return_m=45)
 c['form_v2']=scope
 b['version']=g.VERSION;b['form_v2']={**scope,'prior_vertices_world':prior['vertices_world'],'prior_faces_sha256':g.hashlib.sha256(json.dumps(prior['faces'],separators=(',',':')).encode()).hexdigest(),'preserved_valley_vertices':fixed,'explicit_design_change':'Intermediate top PCHIP knots no longer fixed; their new top heights are bound here. Bottom knots, all named nodes, XZ, rim, controls and original core-volume gate remain unchanged.'}
 return c,b

def report(c,b):
 v=np.array(c['vertices_world']);old=np.array(b['form_v2']['prior_vertices_world']);d=v[:,1]-old[:,1];n=c['planar_vertex_count'];tri=np.array(c['planar_triangles'])
 rows=[]
 for row in b['baseline_authority']:rows.append(dict(section=row['section'],vertex_index=row['vertex_index'],old_y=row['historical_v2_top_world'][1],new_y=row['top_world'][1],delta_y=row['top_world'][1]-row['historical_v2_top_world'][1]))
 # Descriptive distribution only, not an invented visual acceptance score.
 def face_stats(points):
  p=points[:n][tri];normal=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);normal/=np.linalg.norm(normal,axis=1)[:,None];angle=np.degrees(np.arccos(np.abs(normal[:,1])))
  return {'slope_degrees_percentiles':np.percentile(angle,[0,25,50,75,90,99,100]).tolist(),'top_triangles_over_70_degrees':int((angle>70).sum())}
 return dict(scope=c['form_v2'],authored_lobes=LOBES,changed_top_vertices=int(np.count_nonzero(d)),unchanged_total_vertices=int(np.count_nonzero(d==0)),maximum_abs_displacement_m=float(abs(d).max()),minimum_delta_m=float(d.min()),maximum_delta_m=float(d.max()),rms_delta_all_top_m=float(np.sqrt(np.mean(d[:n]**2))),per_vertex_changed_y=[{'index':int(i),'old_y':float(old[i,1]),'new_y':float(v[i,1]),'delta_y':float(d[i])} for i in np.flatnonzero(d)],changed_profile_authorities=rows,old_face_descriptors=face_stats(old),new_face_descriptors=face_stats(v),visual_acceptance=False,native_executed=False)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args()
 if not a.write:print('No-op. Explicit --write builds this one pure form candidate; no engine.');return
 c,b=make();g.write(HERE/'candidate.json',c);g.write(HERE/'bindings.json',b);r=report(c,b);g.write(HERE/'FORM_CHANGE_REPORT.json',r)
 r['geometry']=g.validate_candidate(c);r['controls']=[]
 for row in c['controls']:
  moved=g.evaluate(c,{row['id']:row['exercise_value']});r['controls'].append(dict(id=row['id'],changed_vertices=int(np.any(moved!=np.array(c['vertices_world']),axis=1).sum())))
 moved=g.evaluate(c,{'C05_Main_Valley.width_multiplier':1.05});r['controls'].append(dict(id='C05_Main_Valley.width_multiplier',changed_vertices=int(np.any(moved!=np.array(c['vertices_world']),axis=1).sum())))
 g.write(HERE/'GEOMETRY_RESULT.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('per_vertex_changed_y','changed_profile_authorities')},indent=2))
if __name__=='__main__':main()
