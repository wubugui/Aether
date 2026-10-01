"""Actual savedunion sectionsegments; diagnostic only, not appearancepreview."""
import json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/feiting58c-matplotlib')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
P=Path(__file__).resolve().parent;R=P.parent/'recovery-01';data=json.loads((R/'actual-sections58c.json').read_text());fig,axes=plt.subplots(3,1,figsize=(13,10))
for ax,row in zip(axes,data['sections']):
 plane=row['plane'];axis=0 if plane['plane']=='world_z' else 2
 seg=[[(q[axis],q[1]) for q in r['world_points']] for r in row['actual_triangle_segments']]
 ax.add_collection(LineCollection(seg,colors='#426575',linewidths=1.2));ax.autoscale();ax.axhline(0,color='#67858f',lw=.8,ls='--');ax.set_ylim(0,1150)
 ax.set_title(f"{plane['id']}: {plane['plane']}={plane['value_m']}m — actual triangle intersections",fontsize=10);ax.set_xlabel('World X (m)' if axis==0 else'World Z (m)');ax.set_ylabel('World Y (m)');ax.grid(alpha=.18)
fig.suptitle('C failed genus2 union: actual three-plane cross sections\nUnfilled curves only; no inferred solid, no repaired mesh, no visual acceptance',fontsize=12);fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(P/'actual-sections58c.png',dpi=125);plt.close(fig)
