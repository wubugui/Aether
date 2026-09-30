"""Bounded map/camera intake from savedWorld and11 mountain GLBs, no renderer."""
from pathlib import Path
import json,re,struct,hashlib,math
import numpy as np
R=Path(__file__).resolve().parents[1]
RUN=R/'captures/validation_runs/water-34e-20260909T000818Z-086f9efe84964e12b961d88e6587cb3b'
F=RUN/'study-inputs'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def txt(p):return p.read_text(encoding='utf-8-sig')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
exec(txt(R/'reviews/round-32b-asset-footprint-decoder.py'),globals())
def godot_tri(path):
    b=asset_world_triangles(path);return b[:,:,[0,2,1]]*np.array([1,1,-1])
worldtext=txt(R/'scenes/world/World.tscn');run=read(RUN/'images/night-reference.png.json')
frozen_inputs=read(RUN/'inputs.json')['files']
layout=read(R/'assets/world_layout.json')
coast=np.array(layout['coast'],float) # [z,x] per world_math.gd, not [x,z].
def coast_x(z):return float(np.interp(z,coast[:,0],coast[:,1]))
node_sections=re.findall(r'\[node name="([^"]+)" parent="Mountains"[^\]]*\]([^\[]*)',worldtext)
mountains=[]
for name,body in node_sections:
    transform=[float(x) for x in re.search(r'transform = Transform3D\(([^)]+)\)',body)[1].split(',')]
    basis=np.array(transform[:9]).reshape(3,3,order='F');at=np.array(transform[9:12])
    path=R/'assets/models'/(name+'.glb');tri=godot_tri(path)@basis.T+at
    verts=tri.reshape(-1,3);top=verts[np.argmax(verts[:,1])]
    mountains.append({'name':name,'saved_origin':at.tolist(),'actual_glb_path':str(path),'sha256':sha(path),
      'matches34e_frozen_asset':sha(path)==frozen_inputs['res://assets/models/'+name+'.glb']['sha256'],
      'triangle_count':len(tri),'world_bounds':[verts.min(axis=0).tolist(),verts.max(axis=0).tolist()],
      'highest_vertex_world':top.tolist(),'metadata_coast_x_at_peak_z':coast_x(top[2]),
      'inland_x_gap_to_metadata_coast_m':float(top[0]-coast_x(top[2]))})
head=godot_tri(F/'headland/mainland_headland.glb')+np.array([-2180,0,-1830])
headv=head.reshape(-1,3)
headland={'sha256':sha(F/'headland/mainland_headland.glb'),'runtime_sha_matches':sha(F/'headland/mainland_headland.glb')==run['rightcoast_glb_sha256'],
 'actual_world_bounds':[headv.min(axis=0).tolist(),headv.max(axis=0).tolist()],
 'max_height_vertex':headv[np.argmax(headv[:,1])].tolist()}
def height_at(tri,x,z):
    v=tri[:,:, [0,2]];a=v[:,1]-v[:,0];b=v[:,2]-v[:,0];q=np.array([x,z])-v[:,0]
    det=a[:,0]*b[:,1]-a[:,1]*b[:,0];valid=np.abs(det)>1e-10
    inv=np.zeros_like(det);inv[valid]=1/det[valid]
    u=(q[:,0]*b[:,1]-q[:,1]*b[:,0])*inv;w=(a[:,0]*q[:,1]-a[:,1]*q[:,0])*inv
    good=valid&(u>=-1e-7)&(w>=-1e-7)&(u+w<=1+1e-7)
    heights=tri[:,0,1]+u*(tri[:,1,1]-tri[:,0,1])+w*(tri[:,2,1]-tri[:,0,1])
    return float(heights[good].max()) if good.any() else None
tiles={};transects=[]
for z in [-1800.,-2400.,-3000.]:
  for dx in [-100.,0.,100.]:
    x=coast_x(z)+dx;cell=(math.floor(x/768),math.floor(z/768));name='Ground_'+str(cell[0])+'_'+str(cell[1])
    if name not in tiles:
      path=R/'assets/terrain'/(name+'.glb')
      body=re.search(r'\[node name="'+name+r'" parent="Terrain"[^\]]*\]([^\[]*)',worldtext)[1]
      tr=np.array([float(v) for v in re.search(r'Transform3D\(([^)]+)\)',body)[1].split(',')])
      triangles=godot_tri(path)@tr[:9].reshape(3,3,order='F').T+tr[9:12]
      tiles[name]={'tri':triangles,'source':str(path),'sha256':sha(path),'matches34e_frozen_asset':sha(path)==frozen_inputs['res://assets/terrain/'+name+'.glb']['sha256']}
    base=height_at(tiles[name]['tri'],x,z);local=height_at(head,x,z)
    transects.append({'world_xz':[x,z],'offset_from_metadata_coast_x_m':dx,'saved_base_tile':name,'actual_base_height_m':base,'actual_34e_headland_height_m':local,
      'bounded_upper_height_m':max(v for v in [base,local] if v is not None),
      'scope':'Exact vertical barycentric hit of selected saved base tile and localheadland only; no all-world props/islands census.'})

candidates=[
 {'name':'1125_local_high','reference':'1125','position':[-2390,330,-1390],'look_at':[-2590,60,-2430],'fov_vertical_degrees':70,
  'purpose':'Keep1342 archipelago and34e headland continuity from higher offshore camera; sea left/local land right.',
  'remaining':'Mountains group is far inland/right or behind this northward framing; does not supply1125 prominent right-hand alpine island hierarchy.'},
 {'name':'1125_existing_mountains_wide','reference':'1125','position':[-3000,520,-1250],'look_at':[-1100,180,-3000],'fov_vertical_degrees':70,
  'purpose':'Turn northeast across existing coast to put actual alpine group in right half and retain sea on left.',
  'remaining':'Turns inland across broad low land instead of a close mountain coast; current mountain-to-coast separation and island/channel pattern remain different.'},
 {'name':'1341_local_alongshore','reference':'1341','position':[-2440,145,-1510],'look_at':[-2760,100,-2690],'fov_vertical_degrees':60,
  'purpose':'Lower offshore along-coast view preserving34e lamps/shore with sea left and coastal slopes right.',
  'remaining':'Actual right shore is tens of metres high with village pads; cannot substitute for1341 high jagged snowy mass immediately above shoreline.'},
 {'name':'1341_existing_mountains_oblique','reference':'1341','position':[-2830,170,-1550],'look_at':[-900,150,-2920],'fov_vertical_degrees':60,
  'purpose':'Oblique northeast view intentionally includes actual mountain kit as distant right-hand silhouettes.',
  'remaining':'Broad intervening inland belt remains; lower camera may hide distant low foothills. No actual image or collision visibility test performed.'}
]
aspect=1672/941
def project(points,camera):
    pos=np.array(camera['position'],float);f=np.array(camera['look_at'],float)-pos;f/=np.linalg.norm(f)
    right=np.cross(f,np.array([0,1,0],float));right/=np.linalg.norm(right);up=np.cross(right,f)
    delta=np.array(points)-pos;depth=delta@f
    tangent=math.tan(math.radians(camera['fov_vertical_degrees'])/2)
    uv=np.column_stack([.5+(delta@right)/(2*depth*tangent*aspect),.5-(delta@up)/(2*depth*tangent)])
    return depth,uv
coast_samples=[{'world':[coast_x(z),0,z],'source':'world_layout coast metadata, before local33f extension/terrain sculpt'} for z in [-1200,-1500,-1800,-2100,-2400,-2700,-3000,-3600,-4200]]
for c in candidates:
    delta=np.array(c['look_at'])-np.array(c['position']);unit=delta/np.linalg.norm(delta)
    c['godot_rotation_radians_pitch_yaw_roll']=[float(math.asin(unit[1])),float(math.atan2(-unit[0],-unit[2])),0]
    c['offset_from_1342_camera_m']=(np.array(c['position'])-np.array(run['camera']['position'])).tolist()
    c['metadata_coast_x_at_camera_z']=coast_x(c['position'][2]);c['camera_x_minus_metadata_coast_x']=c['position'][0]-coast_x(c['position'][2])
    depths,uv=project([m['highest_vertex_world'] for m in mountains],c)
    c['mountain_peak_projection']=[{'name':m['name'],'forward_depth_m':float(depth),'uv':q.tolist(),'within_frustum':bool(depth>0 and np.all(q>=0) and np.all(q<=1))} for m,depth,q in zip(mountains,depths,uv)]
    depths,uv=project([x['world'] for x in coast_samples],c)
    c['metadata_coast_projection']=[{'world':x['world'],'forward_depth_m':float(dep),'uv':q.tolist()} for x,dep,q in zip(coast_samples,depths,uv)]
    anchors=[{'name':x['tower'].split('/')[-1],'world':x['position']} for x in run['lantern_lighting']['beams']]
    anchors.append({'name':'actual_34e_headland_highest_vertex','world':headland['max_height_vertex']})
    depths,uv=project([x['world'] for x in anchors],c)
    c['local_actual_anchor_projection']=[{'name':a['name'],'world':a['world'],'forward_depth_m':float(dep),'uv':q.tolist(),'within_frustum':bool(dep>0 and np.all(q>=0) and np.all(q<=1))} for a,dep,q in zip(anchors,depths,uv)]
    c['unverified']='Camera collision clearance, rendered visibility/occlusion, cloud volume clearance, near-clipping, fog and actual artistic framing are not GPU-tested.'

report={'scope':'Bounded same-world camera/map study; direct reference viewing and savedWorld11mountain/localheadland actualGLB bounds. No cloud edits, GPU or terrain generator.',
 'references_directly_viewed':['ref/1125.png','ref/1341.png'],'reference_image_dimensions':[1672,941],
 'reference_reading':{'1125':'High aerial composition: dark storm/ocean left, clear warm right, receding central transition, varied steep islands/mountains and channels on right. Character/airship excluded from scene scope.',
 '1341':'Lower along-coast composition: open water left, stepped rocky and forested foreground right, continuous jagged snowy highlands at right distance under low storm ceiling. Character/airship excluded.'},
 'source_identity':{'actual_world_sha':sha(R/'scenes/world/World.tscn'),'runtime_world_sha':run['world_sha256'],'world_matches_frozen_run':sha(R/'scenes/world/World.tscn')==run['world_sha256'],
  'world_layout_sha':sha(R/'assets/world_layout.json'),'world_layout_role':'Read compact coast/peaks fields only; coastline metadata is evidence of design direction, not actual shoreline intersection guarantee.',
  'local_headland':headland,'world_layout_matches34e_frozen':sha(R/'assets/world_layout.json')==frozen_inputs['res://assets/world_layout.json']['sha256']},
 'baseline_camera':run['camera'],'coordinate_convention':'Godot world XYZ; Y up, oceanY0. Coast metadata records are [z,x]. West of metadata x(z) is sea in base world_math; local appended headland/islands can override.',
 'coast_samples':coast_samples,'bounded_saved_terrain_transects':transects,
 'selected_terrain_sources':[{k:v for k,v in tile.items() if k!='tri'} for tile in tiles.values()],
 'actual_saved_mountains':mountains,'candidate_cameras':candidates,
 'limitations':['Candidates are authored suggestions, not recovered positions of reference images.',
  'Reference mountainous island chain and immediate snowy shoreline are not proven in34e. Camera/weather alone cannot remove measured broad inland gap.',
  'Projection lists are pinhole geometry at reference aspect only; inside-frustum does not prove visibility behind land, clouds or fog.',
  'Local34e headland shape and base coast metadata are different layers; headland actualGLB bounds retained separately, no unsupported exact shore-line claim.',
  'No camera path/flight/whole-world terrain surface check performed.'],
 'full_reference_accepted':False,'all_reference_goal_complete':False}
(R/'reviews/35-storm-world-camera-intake.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'world_identity':report['source_identity']['world_matches_frozen_run'],'headland_bounds':headland['actual_world_bounds'],
 'mountain_count':len(mountains),'mountains':[{k:m[k] for k in ['name','highest_vertex_world','inland_x_gap_to_metadata_coast_m']} for m in mountains],
 'candidates':[{'name':c['name'],'mountain_peaks_in_frame':[x['name'] for x in c['mountain_peak_projection'] if x['within_frustum']],'coast_offset':c['camera_x_minus_metadata_coast_x']} for c in candidates]},indent=2))
