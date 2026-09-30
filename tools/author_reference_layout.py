"""Sparse art-direction landmarks -> fixed metre-space terrain controls.

This authoring tool does not read the screenshot or generate photographic
textures. The saved result is ordinary editable world geography, independent
of the runtime camera. All land extends around and behind the opening view.
"""
from pathlib import Path
import json, math
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
F=941/(2*math.tan(math.radians(25)))
ANGLE=math.radians(-3.5)
def ray(u,v):
    x=(u-836)/F;y=(470.5-v)/F
    return np.array([x,math.cos(ANGLE)*y+math.sin(ANGLE),math.sin(ANGLE)*y-math.cos(ANGLE)])
def height_point(u,v,height):
    d=ray(u,v);p=np.array([0,145,250])+d*((height-145)/d[1])
    return [round(float(a),3) for a in p]
def depth_point(u,v,z):
    d=ray(u,v);p=np.array([0,145,250])+d*((z-250)/d[2])
    return [round(float(a),3) for a in p]

# Entire mainland western boundary, continuing far beyond the opening view.
shore=[(0,644),(150,657),(282,671),(376,669),(446,679),(436,697),
       (417,709),(405,720),(429,739),(415,758),(470,779),(536,795),
       (592,806),(602,824),(649,839),(670,860),(650,881),(596,898),
       (545,920),(451,941)]
coast=[[-14000,-8500],[-5000,-4200],[-1500,-1900],[-800,-1200]]
for u,v in shore:
    x,y,z=height_point(u,v,0);coast.append([z,x])
coast += [[250,-240],[1100,-700],[3400,-2000],[8000,-3100],[15000,-4400]]
coast.sort()

def river(points):
    positions=[];widths=[];banks=[[],[]]
    for i,(u,v,half_width) in enumerate(points):
        x,y,z=height_point(u,v,0)
        positions.append([x,z])
        a=np.array(points[max(0,i-1)][:2]);b=np.array(points[min(len(points)-1,i+1)][:2])
        tangent=b-a;normal=np.array([-tangent[1],tangent[0]],float);normal/=np.linalg.norm(normal)
        for side,sign in enumerate([-1,1]):
            uu,vv=np.array([u,v])+normal*half_width*sign
            bx,_,bz=height_point(uu,vv,0);banks[side].append([bx,bz])
        widths.append(round(np.linalg.norm(np.array(banks[0][-1])-banks[1][-1])*.5,3))
    return {'points':positions,'widths':widths,'banks':banks}
rivers=[river([(0,613,22),(180,642,15),(334,653,11),(439,639,15),
               (549,616,20),(674,581,22),(760,576,23),(867,598,18),
               (970,603,22),(1100,583,18),(1226,551,19),(1390,531,20),(1672,524,24)]),
        river([(917,603,16),(1048,621,12),(1152,639,10),(1240,668,7),(1350,671,4)])]
# Explicit banks of the wide connected lake. Each bank is a separate world
# curve: the bay is not a constant-width canal, and has no westward canal
# through the mesa. The values are sparse editable survey-style controls.
far_bank=[(326,673),(396,647),(463,627),(503,611),(570,606),(602,592),
          (581,582),(620,575),(637,561),(690,561),(692,550),(713,547),
          (741,547),(756,558),(780,563),(821,566),(850,561),(878,566),
          (908,574),(945,576),(989,569),(1034,568),(1070,565),(1125,559),
          (1175,559),(1190,550),(1180,542),(1222,536),(1270,529),
          (1340,526),(1405,520),(1470,520),(1530,515),(1720,514)]
near_bank=[(385,678),(426,688),(410,705),(430,709),(447,699),(459,687),
           (491,680),(525,667),(545,654),(588,647),(625,643),(662,636),
           (693,631),(720,622),(743,612),(772,614),(800,609),(821,614),
           (852,609),(875,602),(895,609),(929,610),(939,628),(971,633),
           (1011,635),(1048,642),(1080,635),(1120,640),(1175,652),
           (1168,643),(1138,630),(1110,626),(1083,617),(1130,611),
           (1140,603),(1180,602),(1200,593),(1230,579),(1270,576),
           (1300,580),(1357,583),(1390,570),(1420,555),(1460,546),
           (1510,547),(1560,544),(1598,529),(1720,527)]
def bank_world(points):
    return [[height_point(u,v,0)[i] for i in (0,2)] for u,v in points]
rivers[0]['banks']=[bank_world(far_bank),bank_world(near_bank)]
rivers[1]=river([(1135,635,4),(1190,650,4),(1220,672,4),(1265,678,3),(1308,685,2),(1350,674,2)])

# Peaks are absolute height targets with full radial mass, not skyline cards.
# u, v, summit height, basal radius, flat summit fraction, ridge irregularity.
marks=[(1235,307,460,490,0,.11),(1145,325,390,360,0,.13),
       (1280,360,330,350,0,.13),(1184,365,340,290,0,.16),
       (1090,405,195,350,0,.12),(1350,388,250,330,0,.13),
       (1450,421,175,330,0,.15),(985,452,100,270,0,.10),
       (1180,451,145,220,.06,.15),(1530,446,130,280,0,.10),
       (1640,486,85,210,.05,.08),
       (167,544,56,88,.60,.06),(199,562,45,75,.37,.06),
       (439,581,37,43,.05,.12),(203,474,39,55,.14,.12),
       (306,438,39,85,0,.13),
       (1398,624,82,66,.23,.08),(1600,682,62,59,.36,.10),
       (1242,697,65,52,.22,.15),(1432,772,47,40,.42,.13),
       (1252,819,46,34,.36,.15),(1080,897,30,36,.30,.12),
       (282,899,11,15,.08,.12),(566,648,37,47,.05,.12),
       (487,686,30,31,0,.12),(710,628,25,44,0,.09)]
peaks=[]
for u,v,h,r,flat,ridges in marks:
    x,y,z=height_point(u,v,h)
    peaks.append([x,z,h,r,flat,ridges])
# Distant ridges are depth-constrained. Inverting a nearly horizontal ray
# against an arbitrary height can place a ridge behind the camera.
for i,z in enumerate([-2900,-2730,-2870,-3000,-2000,-2650,-2300,-1800,-2150,-2600,-850]):
    u,v,_,r,flat,ridges=marks[i]
    x,y,z=depth_point(u,v,z)
    peaks[i]=[x,z,y,r,flat,ridges]
assert all(p[1]<250 for p in peaks[:26]), 'Opening landmarks must be in front of the camera'
peaks += [[2670,1200,560,780,0,.1],[3310,1590,410,680,0,.12],
          [-1220,2490,380,630,0,.15],[-1650,2870,500,610,0,.12],
          [3020,-5390,740,820,0,.1],[-2770,-4440,440,670,0,.12],
          [-3450,-5080,610,730,0,.1],[-2920,-5680,460,680,0,.1],
          [4300,-2530,430,760,0,.1]]
for p in peaks[26:]:
    if p[1]<250 and abs(p[0]/(250-p[1]))<1.45:
        p[0]=round(math.copysign((250-p[1])*1.65,p[0]),3)
for u,v,z,r in [(1210,344,-2700,190),(1268,339,-3100,180),(1296,382,-2750,200),
                (1338,371,-2800,230),(1378,408,-2700,240),(1112,363,-2450,205),
                (1080,389,-2300,180),(1157,401,-2200,180),(1200,410,-2200,200)]:
    x,h,z=depth_point(u,v,z);peaks.append([x,z,h,r,0,.18])
for u,v,h,r in [(60,526,32,75),(290,521,28,80),(506,554,34,60),(644,501,30,90),
                (948,479,37,110),(1032,503,30,65),(1445,585,30,46),(1520,531,49,73),
                (1570,585,31,65),(1600,491,49,90),(580,480,45,95),(910,530,29,60),
                (353,482,24,66),(733,468,39,100),(868,454,47,100),(525,460,41,100),
                (996,755,32,38),(981,801,27,36),(763,848,20,28),(626,928,16,26)]:
    x,y,z=height_point(u,v,h);peaks.append([x,z,h,r,.06,.15])

clouds=[]
# Each cloud is a real modeled volume. These are its world-space placement
# constraints; its front/back/underside geometry exists independently.
for u,v,z,scale in [(1090,174,-2000,3.0),(805,280,-1800,2.6),
                    (388,344,-1800,1.85),(30,304,-1500,2.9),
                    (1238,202,-2050,1.10),(648,320,-2400,.74)]:
    clouds.append([*depth_point(u,v,z),scale])

result={'revision':2,'coast':coast,'rivers':rivers,'peaks':peaks,'clouds':clouds,
        'castle_ground_position':height_point(917,645,19),
        'authoring_note':'Sparse manually specified reference landmarks converted once to fixed world coordinates. No screenshot file is read or used as a world texture.'}
(ROOT/'blender/art_layout.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('Authored layout:',len(peaks),'complete peaks;',len(coast),'coast controls;',len(rivers),'rivers')
