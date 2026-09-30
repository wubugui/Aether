"""Sculpt an entire mountain landform into independently exported terrain tiles.

Peaks, ridge junctions, cirques and valley mouths use a sparse control cage.
Only fixed 3D metre-space geometry is written to the game. Godot still owns
the individual terrain instances, their colliders and all landscape props.
"""
from pathlib import Path
import json,math,sys
import numpy as np
from scipy.spatial import Delaunay
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'blender'))
import world_definition as W
F=941/(2*math.tan(math.radians(25)));pitch=math.radians(-3.5)
def at_depth(u,v,z):
    x=(u-836)/F;y=(470.5-v)/F
    ray=np.array([x,math.cos(pitch)*y+math.sin(pitch),math.sin(pitch)*y-math.cos(pitch)])
    return np.array([0,145,250])+ray*((z-250)/ray[2])

# Main summits and their descending ridge chains. Depth is authored for each
# ridge so that the front folds are real lower, nearer mountain volumes.
controls=[
    (1235,307,-2900),(1145,325,-2730),
    (1214,328,-2810),(1201,348,-2660),(1178,360,-2470),
    (1165,389,-2100),(1140,409,-1810),(1110,438,-1490),
    (1080,466,-1200),(1050,478,-1120),
    (1254,338,-2800),(1265,363,-2550),(1296,381,-2410),
    (1310,412,-1920),(1347,429,-1650),(1375,452,-1400),
    (1416,474,-1130),(1450,482,-1110),
    (1172,340,-2740),(1120,353,-2600),(1102,380,-2330),
    (1060,407,-1990),(1020,435,-1630),(983,448,-1500),
    (1153,365,-2540),(1138,386,-2290),(1118,399,-2050),
    (1087,423,-1800),(1054,447,-1460),
    (1229,359,-2500),(1210,382,-2220),(1193,410,-1880),
    (1163,438,-1460),(1144,469,-1160),
    (1254,386,-2250),(1239,418,-1830),(1200,443,-1500),
    (1232,469,-1190),(1272,480,-1120),
    (1325,361,-2920),(1343,389,-2540),(1374,405,-2340),
    (1410,429,-2050),(1459,450,-1750),(1504,469,-1500),
    (1538,494,-1120),
    # Front foothills and valley mouths give the mass its broad lower skirt.
    (1010,488,-1080),(1060,497,-1000),(1105,489,-1030),
    (1120,512,-940),(1160,511,-970),(1210,519,-890),
    (1270,526,-900),(1320,512,-990),(1390,521,-920),
    (1470,519,-990),(1552,517,-1010),
]
points=[at_depth(*p).tolist() for p in controls]
points += [[930,250,-3220],[1240,315,-3240],[1460,235,-3170],
           [1000,150,-3470],[1320,190,-3490],[1650,125,-3380]]
x0,z0,x1,z1=80,-3900,2420,-690
for z in np.arange(z0,z1+1,160):
    points += [[x0,float(W.raw_height(x0,z)),float(z)],
               [x1,float(W.raw_height(x1,z)),float(z)]]
for x in np.arange(x0,x1+1,130):
    points += [[float(x),float(W.raw_height(x,z0)),z0],
               [float(x),float(W.raw_height(x,z1)),z1]]
points += [[x,float(W.raw_height(x,z)),z] for x,z in [(x0,z1),(x1,z1)]]
points=np.unique(np.round(points,6),axis=0)
triangles=Delaunay(points[:,[0,2]]).simplices
path=ROOT/'assets/terrain_sculpt.json'
existing=json.loads(path.read_text()) if path.exists() else []
existing=[s for s in existing if s['name']!='Frostpeak alpine range']
existing.append({'name':'Frostpeak alpine range','units':'metres',
    'points':points.tolist(),'triangles':triangles.tolist(),
    'bounds':[x0,z0,x1,z1],
    'purpose':'Mountain ridges, cirques and descending front/back slopes in independently assembled terrain modules'})
path.write_text(json.dumps(existing,indent=2))
print('ALPINE SCULPT CAGE',len(points),'vertices',len(triangles),'triangles')
