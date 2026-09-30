"""Author a metre-space terrain control cage beneath the separate cliff kit.

The sparse survey points describe ridges, saddles and gullies. They are not
texture samples. The resulting cage is sculpt data for individual terrain
modules, never a camera-dependent mesh or a replacement world scene.
"""
from pathlib import Path
import sys, json, math
import numpy as np
from scipy.spatial import Delaunay
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'blender'))
import world_definition as W
F=941/(2*math.tan(math.radians(25)))
pitch=math.radians(-3.5)

def survey(u,v,h):
    x=(u-836)/F;y=(470.5-v)/F
    ray=np.array([x,math.cos(pitch)*y+math.sin(pitch),math.sin(pitch)*y-math.cos(pitch)])
    return np.array([0,145,250])+ray*((h-145)/ray[1])

# A broad continuous escarpment, with a lower saddle between its western
# buttress and main crown. It continues behind the rocks and out of view.
controls=[
    (873,936,38),(940,879,44),(1010,831,49),(1095,789,51),
    (1156,739,54),(1210,748,50),(1305,763,52),(1342,729,54),
    (1444,726,50),(1515,729,50),(1605,741,45),(1690,774,37),
    (987,933,44),(1075,908,35),(1153,898,27),(1214,887,25),
    (1273,867,29),(1322,897,35),(1383,878,26),(1429,834,29),
    (1490,893,36),(1570,913,37),(1670,935,28),
    (920,1020,30),(1030,1010,25),(1190,1045,22),
    (1330,1060,18),(1510,1040,20),(1730,1060,14),
]
points=[survey(*p).tolist() for p in controls]
# Back slopes are explicitly modeled in world coordinates. A descending
# shoulder joins the distant meadow over 80 metres, instead of a blank wall.
points += [[35,21,-160],[80,24,-155],[125,31,-145],[170,39,-145],
           [225,32,-155],[280,25,-130],[310,20,-60],
           [60,31,-70],[110,39,-80],[155,48,-80],[210,43,-90],
           [255,33,-70],[290,26,20]]
boundary=[]
for z in np.arange(-220,221,40):
    boundary += [[-10,float(W.raw_height(-10,z)),float(z)],
                 [350,float(W.raw_height(350,z)),float(z)]]
for x in np.arange(30,350,40):
    boundary += [[float(x),float(W.raw_height(x,-220)),-220],
                 [float(x),float(W.raw_height(x,220)),220]]
# Include corners explicitly; all outside vertices retain their original
# terrain elevation so neighboring terrain remains continuous.
boundary += [[x,float(W.raw_height(x,z)),z] for x,z in [(-10,220),(350,220)]]
points=np.asarray(points+boundary)
triangles=Delaunay(points[:,[0,2]]).simplices
data={'name':'Crown Escarpment foothills','units':'metres',
      'points':points.round(6).tolist(),'triangles':triangles.tolist(),
      'bounds':[-10,-220,350,220],
      'purpose':'Terrain sculpt cage: connected foot slopes, saddles and gullies beneath independent cliff prefabs'}
(ROOT/'assets/terrain_sculpt.json').write_text(json.dumps([data],indent=2))
print('FOOTHILL SCULPT CAGE',len(points),'vertices',len(triangles),'triangles')
