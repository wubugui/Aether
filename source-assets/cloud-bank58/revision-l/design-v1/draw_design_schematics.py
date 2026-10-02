"""Creates only annotated 2-D mathematical design diagrams from frozen survey grids.
No mesh, .blend, Godot data, or repository file is written or altered.
"""
from pathlib import Path
import os,json,hashlib
P=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(P/'mpl-cache')
os.environ['XDG_CACHE_HOME']=str(P/'diagram-cache')
import numpy as np
import scipy.ndimage as ndi
from scipy.interpolate import PchipInterpolator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,PathPatch
from matplotlib.path import Path as MPath
from matplotlib.colors import ListedColormap
D=json.loads((P/'design_plan.json').read_text()); G=np.load(P/'survey-grids.npz');xs,zs=G['xs'],G['zs'];M=np.isfinite(G['CloudSea_1_1_top']);X,Z=np.meshgrid(xs,zs)
colors=['#ecb45b','#f28b72','#62c5c0','#96bdf5']
plt.rcParams.update({'font.size':11,'axes.titlesize':14,'axes.labelsize':11,'savefig.facecolor':'#f7f8fc'})
fig,ax=plt.subplots(figsize=(13.8,11.2),layout='constrained');ax.set_facecolor('#edf1f7')
N=np.zeros(M.shape,bool)
for c in D['contact_collars']:N|=np.isfinite(G[c['neighbor']+'_top'])
ax.imshow(np.where(M,np.where(N,2,1),0),origin='lower',extent=[3500,5200,3300,5100],cmap=ListedColormap(['#edf1f7','#d9e3ed','#91bdb5']),vmin=0,vmax=2)
ax.contour(xs,zs,M,levels=[.5],colors=['#263d55'],linewidths=2.4)
for k,c in enumerate(D['controls'][:4]):
 cx,cz=c['world_center_xz_m'];sx,sz=c['plan_span_xz_m'];ang=np.linspace(0,2*np.pi,13)[:-1]
 # Asymmetric 2-D influence outlines only. These are not source geometry or spheres.
 wobble=np.array([1,.92,1.04,.88,1.02,.91,1,.84,1.06,.90,.96,1.02])
 xx=cx+.5*sx*np.cos(ang)*wobble;zz=cz+.5*sz*np.sin(ang)*np.roll(wobble,3)
 for scale,alpha in [(1,.30),(.68,.23),(.36,.35)]:
  poly=np.stack([cx+(xx-cx)*scale,cz+(zz-cz)*scale],axis=1);ax.add_patch(Polygon(poly,facecolor=colors[k],edgecolor=colors[k],alpha=alpha,linewidth=2))
 ax.scatter([cx],[cz],c='#263d55',s=22);letter='ABCD'[k]
 ax.text(cx,cz+15,f'{letter}\ncrest Y {c["default_crest_y_m"]}',ha='center',va='bottom',weight='bold',fontsize=12,color='#142b47')
val=np.array(D['controls'][4]['path_xzy_m']);ax.plot(val[:,0],val[:,1],color='#294675',lw=20,alpha=.25,solid_capstyle='round');ax.plot(val[:,0],val[:,1],color='#294675',lw=3,solid_capstyle='round')
bra=np.array(D['controls'][4]['blind_branch_xzy_m']);ax.plot(bra[:,0],bra[:,1],color='#294675',lw=12,alpha=.25,solid_capstyle='round');ax.plot(bra[:,0],bra[:,1],color='#294675',lw=2,ls='--');ax.scatter(bra[-1,0],bra[-1,1],s=70,marker='x',color='#294675')
ax.annotate('Main hooked trough\nY 735-780; closed floor',xy=(4350,4110),xytext=(4370,4190),ha='center',fontsize=11,color='#243e65',arrowprops=dict(arrowstyle='->',color='#243e65'))
ax.annotate('Blind branch rises\nto a broad shoulder',xy=(4510,3820),xytext=(4700,3600),ha='center',fontsize=10,color='#243e65',arrowprops=dict(arrowstyle='->',color='#243e65'))
for c,xy,tx in [(D['contact_collars'][0],(3750,4450),(3570,4690)),(D['contact_collars'][1],(4510,3570),(4930,3390)),(D['contact_collars'][2],(4340,4780),(4650,4975)),(D['contact_collars'][3],(4950,4350),(5180,4700))]:
 ax.annotate(c['neighbor'].replace('CloudSea_','')+' overlap candidate\nplanned locked collar',xy=xy,xytext=tx,ha='center',fontsize=10,color='#27655d',arrowprops=dict(arrowstyle='->',color='#27655d'))
ax.annotate('Keep this real inlet;\ndo not fill the AABB',xy=(3910,4150),xytext=(3580,4250),ha='center',fontsize=10,color='#9b4a35',arrowprops=dict(arrowstyle='->',color='#9b4a35'))
# Planned central cut path, used in the separate section diagram.
line=np.array([[4470,3690],[4140,3910],[4180,4170],[4330,4480],[4390,4610]])
ax.plot(line[:,0],line[:,1],color='#54465e',ls=':',lw=1.5);ax.text(4530,3650,'S',color='#54465e',weight='bold');ax.text(4420,4610,"S'",color='#54465e',weight='bold')
ax.scatter([3958],[3667],marker='+',s=120,c='#151b29');ax.text(3920,3550,'Original trial anchor\n(3958, 0, 3667)\nnew geometry; scale 1',ha='right',fontsize=10,color='#293849')
ax.set(xlim=(3480,5270),ylim=(3300,5100),xlabel='World X (m)',ylabel='World Z (m)');ax.set_aspect('equal');ax.grid(alpha=.18)
fig.suptitle('PROPOSED PLAN: one full, asymmetric cloud bank\nMathematical design diagram, NOT a game render or a built asset',fontsize=17,weight='bold')
ax.set_title('Dark outline / green projected overlap = archived 5 m survey; 3D contact unproved\nColored crown regions / valley / heights = design assumptions',fontsize=12)
fig.savefig(P/'02-proposed-bank-plan.png',dpi=160);plt.close(fig)

fig,axs=plt.subplots(2,1,figsize=(13,9),layout='constrained',gridspec_kw={'height_ratios':[1.2,1]})
# No sampled future surface is saved: section ordinates are an editorial form specification.
s=np.array([0,120,240,340,397,460,520,590,660,740,820,910,1004,1080,1147])
y=np.array([845,880,965,998,1005,955,860,780,755,810,915,1000,1040,955,835])
b=np.array([610,595,580,565,570,575,585,590,595,580,570,575,585,610,650]);t=np.linspace(0,s[-1],500);yt=PchipInterpolator(s,y)(t);yb=PchipInterpolator(s,b)(t)
a=axs[0];a.fill_between(t,yb,yt,color='#b7c9dd');a.plot(t,yt,color='#253f5f',lw=3);a.plot(t,yb,color='#48627d',lw=2);a.scatter(s,y,c='#253f5f',s=15);a.annotate('A: broad crown\nY 1005',xy=(397,1005),xytext=(320,1080),arrowprops=dict(arrowstyle='->'));a.annotate('B: offset taller crown\nY 1040',xy=(1004,1040),xytext=(880,1080),arrowprops=dict(arrowstyle='->'));a.annotate('Wide valley floor\nY 755; belly still continuous',xy=(660,755),xytext=(650,930),ha='center',arrowprops=dict(arrowstyle='->'));a.annotate('Belly Y 560-630\nnot an extruded plate',xy=(520,585),xytext=(170,530),arrowprops=dict(arrowstyle='->'))
a.annotate('',xy=(675,757),xytext=(675,594),arrowprops=dict(arrowstyle='<->',color='#a85a3b'));a.text(690,665,'~160 m\nlocal thickness',color='#9a563a',fontsize=10)
a.annotate('D: front shoulder Y 845\n~235 m to lower belly',xy=(0,845),xytext=(15,1030),arrowprops=dict(arrowstyle='->'));a.set(title="PROPOSED section S-S': D / A / valley / B (unfolded path; not a camera silhouette)",xlabel='Distance along planned crown-valley-crown section (m)',ylabel='World Y (m)',xlim=(-25,1175),ylim=(500,1140));a.grid(alpha=.2)
# Distinct wider return section prevents all mass appearing as one row of identical peaks.
u=np.array([0,90,190,285,390,485,570,670,760,835]);v=np.array([740,815,910,925,875,835,770,750,720,690]);w=np.array([675,645,610,590,575,580,595,615,640,670]);q=np.linspace(0,835,400)
a=axs[1];a.fill_between(q,PchipInterpolator(u,w)(q),PchipInterpolator(u,v)(q),color='#b7d9d6');a.plot(q,PchipInterpolator(u,v)(q),color='#27635f',lw=3);a.plot(q,PchipInterpolator(u,w)(q),color='#42746b',lw=2);a.scatter(u,v,c='#27635f',s=15);a.annotate('C: long, lower return\nY 925',xy=(285,925),xytext=(170,1000),arrowprops=dict(arrowstyle='->'));a.annotate('Three-dimensional shoulder roll\nseveral broad geometric normal directions',xy=(485,835),xytext=(450,1015),ha='center',arrowprops=dict(arrowstyle='->'));a.annotate('Transition to proposed interface collar\nexact 3D contact remains unproved',xy=(775,710),xytext=(595,585),ha='center',arrowprops=dict(arrowstyle='->'));a.set(title='PROPOSED side-return section: intentionally different rhythm and thickness',xlabel='Local section distance (m; schematic)',ylabel='World Y (m)',xlim=(-20,860),ylim=(500,1080));a.grid(alpha=.2)
fig.suptitle('PROPOSED VOLUME SECTIONS | Not native geometry, not a visual acceptance result',fontsize=16,weight='bold');fig.savefig(P/'03-proposed-volume-sections.png',dpi=160);plt.close(fig)
# A local cut along the horizontal direction of the exact inherited near camera.
# These are proposed profile ordinates, not sampled future geometry.
fig,ax=plt.subplots(figsize=(12,6.2),layout='constrained')
s=np.array([-240,-190,-125,-60,0,70,150,225]);top=np.array([730,820,940,1005,990,940,850,780]);bottom=np.array([680,620,580,560,570,595,630,700]);u=np.linspace(-240,225,500)
ax.fill_between(u,PchipInterpolator(s,bottom)(u),PchipInterpolator(s,top)(u),color='#c2ccdf');ax.plot(u,PchipInterpolator(s,top)(u),lw=3,color='#2c456b');ax.plot(u,PchipInterpolator(s,bottom)(u),lw=2,color='#566a82');ax.scatter(s,top,c='#2c456b',s=24);ax.scatter(s,bottom,c='#566a82',s=20)
ax.annotate('Actual near view approaches from this side\nMultiple broad shoulder turns, not a vertical wall',xy=(-180,838),xytext=(-225,1090),arrowprops=dict(arrowstyle='->'),fontsize=11)
ax.annotate('A crest Y 1005\nfinite broad cap',xy=(-60,1005),xytext=(40,1080),arrowprops=dict(arrowstyle='->'))
ax.annotate('Continuous rounded belly\nY 560-630 in the interior',xy=(-15,565),xytext=(-190,495),arrowprops=dict(arrowstyle='->'))
ax.annotate('Far shoulder wraps downward\nwithout a flat horizontal tray',xy=(145,855),xytext=(30,680),arrowprops=dict(arrowstyle='->'))
ax.annotate('',xy=(-95,980),xytext=(-95,570),arrowprops=dict(arrowstyle='<->',color='#aa6741'));ax.text(-82,765,'~410 m\nbody thickness',fontsize=10,color='#985c3a')
ax.set(xlim=(-260,245),ylim=(460,1170),xlabel='Distance along near horizontal look direction (m)\nworld XZ = (4140,3910) + t * (0.7282,-0.6854), rounded for illustration',ylabel='World Y (m)',title='PROPOSED near-facing A section | Explicitly a mathematical sketch, not native geometry')
ax.grid(alpha=.2);fig.suptitle('Thickness and turning surfaces under the original near-camera direction',fontsize=16,weight='bold');fig.savefig(P/'04-proposed-near-shoulder-section.png',dpi=160);plt.close(fig)
print('Wrote only proposed 02/03/04 design diagrams')
