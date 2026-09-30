import sys, math
import numpy as np
sys.path.insert(0,'D:/test6/blender')
from cliff_terrace_topology import ground_at
F=941/(2*math.tan(math.radians(25)));pitch=math.radians(-3.5)
def ray(u,v):
    y=(470.5-v)/F
    return np.array([(u-836)/F, math.cos(pitch)*y+math.sin(pitch),math.sin(pitch)*y-math.cos(pitch)])
def at_height(u,v,h):
    r=ray(u,v);return np.array([0,145,250])+r*((h-145)/r[1])
def ground(u,v):
    r=ray(u,v)
    last=None
    for d in np.arange(10,600,.5):
        p=np.array([0,145,250])+r*d
        if p[1]<=ground_at(p[0],p[2]):return p
for u,v,h in [(1186,780,52),(1229,750,58),(1278,752,58),(1301,773,51),(1166,831,0),(1200,842,0),(1240,839,0),(1280,849,0),(1320,827,0),(1398,624,82),(1429,718,58),(1372,719,63)]:
    p=at_height(u,v,h) if h else ground(u,v)
    print('SURVEY',u,v,h,np.round(p,2),'GROUND',round(ground_at(p[0],p[2]),2),flush=True)
