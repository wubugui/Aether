"""Engineering diagrams only. No reference-image compositing, engine or native renders."""
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/north62-mpl-config')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/north62-chart-cache')
import json,math,collections
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle
D=Path(__file__).resolve().parent;R=D.parents[2]
p=json.loads((D/'candidate-plan.json').read_text());v=json.loads((D/'candidate-vertex-y.json').read_text());s=json.loads((D/'instance-support-plan.json').read_text());raw=json.loads((R/'cloud-evidence/coast-boundary-readonly-20261001/native-coast.json').read_text());src={t['node'].split('/')[-1]:np.array(t['faces']).reshape(-1,3,3)for t in raw['terrain']};tri=[];slopes=[];areas=[];links=collections.defaultdict(list)
for row in v['tiles']:
    m={tuple(q['before_xyz']):q['candidate_y']for q in row['vertex_y_overrides']}
    for old in src[row['tile']]:
        new=old.copy()
        for j,q in enumerate(old):new[j,1]=m.get(tuple(q),q[1])
        if np.array_equal(old,new):continue
        i=len(tri);tri.append(new);n=np.cross(new[1]-new[0],new[2]-new[0]);slopes.append(math.degrees(math.atan2(math.hypot(n[0],n[2]),abs(n[1]))));areas.append(float(np.linalg.norm(n)/2))
        for j in range(3):links[tuple(sorted((tuple(new[j,[0,2]]),tuple(new[(j+1)%3,[0,2]]))))].append(i)
adj=collections.defaultdict(set)
for ids in links.values():
    for i in ids:adj[i].update(ids)
seen=set();comps=[]
for i in range(len(tri)):
    if i in seen:continue
    todo=[i];component=[]
    while todo:
        x=todo.pop()
        if x in seen:continue
        seen.add(x);component.append(x);todo.extend(adj[x]-seen)
    comps.append(len(component))
metrics={'status':'offline_proposal_geometry_only','connected_modified_triangle_components':sorted(comps,reverse=True),'max_triangle_slope_degrees':max(slopes),'triangles_over_80_degrees':sum(v>80 for v in slopes),'surface_area_fraction_over_80_degrees':sum(a for a,s in zip(areas,slopes)if s>80)/sum(areas),'visual_pass':False,'style_risk':'Remaining steep short facets must be inspected in the native side/back source views; no artistic pass from slope statistics.'}
(D/'GEOMETRY_DIAGNOSTIC.json').write_text(json.dumps(metrics,indent=2)+'\n')
fig,axs=plt.subplots(1,2,figsize=(15,9),gridspec_kw={'width_ratios':[.95,1.1]})
ax=axs[0];verts=[t[:,[0,2]]for t in tri];pc=PolyCollection(verts,array=np.array([t[:,1].mean()for t in tri]),cmap='terrain',edgecolors='none');ax.add_collection(pc);fig.colorbar(pc,ax=ax,shrink=.6,label='Candidate surface world Y (m)')
poly=np.array(p['polygon_xz']+[p['polygon_xz'][0]]);ax.plot(poly[:,0],poly[:,1],color='black',lw=1.5)
for row in s['rows']:
    t=row['original_world_transform_columns'];hit=bool(row['intersected_changed_triangles']);ax.scatter(t[9],t[11],s=4 if hit else 1,c='#922b21'if hit else '#3b454c',alpha=.6)
for x in [-3072,-2304]:ax.axvline(x,color='gray',ls='--',lw=.7)
for z in [-5376,-4608,-3840]:ax.axhline(z,color='gray',ls='--',lw=.7)
c=p['cloud_spatial_guard']['actual_aabb'];ax.add_patch(Rectangle((c['min'][0]-40,c['min'][2]-40),c['max'][0]-c['min'][0]+80,c['max'][2]-c['min'][2]+80,fill=False,ec='magenta',lw=1.5))
for control in p['controls']:
    if control['name']not in ['main_peak','rear_crown','south_middle_shoulder']:continue
    x,z=control['xz'];ax.scatter(x,z,c='red',s=28);ax.text(x+15,z,f"{control['name']}\n{control['target_y']} m",fontsize=8)
ax.set_xlim(-3088,-2000);ax.set_ylim(-5200,-3730);ax.set_aspect('equal');ax.set_title('Local terrain proposal and full-footprint hits\n167 need seating; 509 query instances stay exact');ax.set_xlabel('World X (m)');ax.set_ylabel('World Z (m)')
# Two fixed-camera projection silhouettes, no atmospheric/rendering substitution.
ax=axs[1]
for ref,color in [('1131','#315e87'),('1347','#a65928')]:
    vv=p['projected_controls'];xs=[];ys=[]
    for name in ['rear_crown','northwest_saddle','main_peak','northeast_arete','cloud_east_saddle','southeast_shoulder','south_middle_shoulder','west_spur','west_rock_shoulder','rear_crown']:
        uv=vv[name][ref]['uv'];xs.append(uv[0]);ys.append(uv[1])
    ax.plot(xs,ys,'o-',color=color,label=f'{ref}, original fixed camera',ms=4)
    peak=vv['main_peak'][ref]['uv'];ax.annotate(f'{ref} main peak\ncloud-AABB line-of-sight risk',peak,xytext=(peak[0]-.13,peak[1]-.09),arrowprops={'arrowstyle':'->','color':color},color=color,fontsize=9)
ax.set_xlim(.5,.97);ax.set_ylim(.51,.0);ax.set_aspect(664/1179);ax.grid(alpha=.2);ax.set_xlabel('Normalized native screen X');ax.set_ylabel('Normalized native screen Y');ax.set_title('Control-point projection only\nNo cloud/weather/image occlusion proof');ax.legend(loc='lower left')
fig.suptitle('NORTH RIDGE 62 / SOURCE-ONLY DESIGN STUDY / NOT A GODOT OR BLENDER RENDER',fontsize=12)
fig.tight_layout();fig.savefig(D/'engineering-design.png',dpi=130);print(json.dumps(metrics,sort_keys=True))
