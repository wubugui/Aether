from pathlib import Path
import json,os
D=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(D/'plot-config')
os.environ['XDG_CACHE_HOME']=str(D/'cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection
from matplotlib.patches import Rectangle

d=json.loads((D/'intake.json').read_text())
raw=json.loads((D.parent/'coast-boundary-readonly-20261001/native-coast.json').read_text())
t=np.array(next(m['faces'] for m in raw['terrain'] if m['node'].endswith('/Ground_-5_-5'))).reshape(-1,3,3)
fig,(a,b)=plt.subplots(1,2,figsize=(13.5,6.5),dpi=160)
c=PolyCollection(t[:,:,[0,2]],array=t[:,:,1].mean(1),cmap='terrain',clim=(-8,90),edgecolors='none')
a.add_collection(c)
a.add_collection(LineCollection([np.array(s['points'])[:,[0,2]] for s in d['shore_segments']],color='#00d5ff',linewidth=1.5))
x0,x1,z0,z1=d['survey_box_xmin_xmax_zmin_zmax']
a.add_patch(Rectangle((x0,z0),x1-x0,z1-z0,fill=False,color='#ce215b',linewidth=1.8,label='Survey box only'))
for kind,color,marker in [('pine','#102c12','^'),('rock','#27232b','o')]:
    ps=np.array([r['world_position'] for g in d['scatter']['groups'] if g['kind']==kind for r in g['instances']])
    a.scatter(ps[:,0],ps[:,2],s=18,c=color,marker=marker,label=f'{kind}: {len(ps)} roots')
a.plot(-3282.93,-3612.21,'x',color='red',markersize=8,label='Recorded1131 ray')
colors=plt.cm.viridis(np.linspace(.05,.9,len(d['cross_sections'])))
for cs,color in zip(d['cross_sections'],colors):
    a.plot([x0,x1],[cs['z'],cs['z']],color=color,lw=.7,alpha=.65)
    x=np.array([p['x'] for p in cs['samples']]);y=np.array([p['mesh']['y'] for p in cs['samples']])
    shore=np.interp(cs['z'],[z0,z1],np.polyval(d['shore_fit']['x_equals_a_z_plus_b'],[z0,z1]))
    b.plot(x-shore,y,color=color,label=f'Z={int(cs["z"])}')
a.set(xlim=(-3480,-3060),ylim=(-3380,-3810),xlabel='World X (m)',ylabel='World Z (m)',title='Saved native57 intake: current shore and roots')
a.axvline(-3072,color='black',ls='--',lw=1,label='Frozen east tile edge')
a.axhline(-3840,color='black',ls='--',lw=1)
a.set_aspect('equal');a.legend(fontsize=7,loc='lower left')
b.axhline(0,color='#00b2d4',lw=1);b.axvline(0,color='#555555',ls='--',lw=.7)
b.set(xlim=(-70,160),ylim=(-10,90),xlabel='X offset from fitted waterline (m; + inland)',ylabel='Native terrain height (m)',title='Current sections: abrupt high north, lower south')
b.grid(alpha=.2);b.legend(fontsize=8)
fig.colorbar(c,ax=a,label='Saved terrain Y (m)',fraction=.045)
fig.suptitle('Read-only numerical survey; no proposed deformation or engine render',fontsize=11)
fig.tight_layout();fig.savefig(D/'intake-map.png')
