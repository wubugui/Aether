"""Blender constrained terrain layout for two near-right coastal village clusters.
Screen anchors and landforms are authored proposals, not recovered original geography.
This file only lays out the 2D terrain vertices; native original heights are surveyed next.
"""
from pathlib import Path
import bpy,json,math,shutil
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'captures/headland_layout_23c'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'layout-builder.py')
ORIGIN=(-2180.,-1830.)
# West shore runs north-to-south, with a real inlet between the two promontories.
shore=[(-2070,-1648,8),(-2120,-1660,12),(-2180,-1680,18),(-2235,-1708,16),
       (-2260,-1726,7),(-2274,-1750,5),(-2270,-1776,6),(-2255,-1793,9),
       (-2234,-1810,5),(-2205,-1825,2.5),(-2210,-1844,3),(-2238,-1854,3),
       (-2254,-1870,4),(-2257,-1890,5),(-2241,-1906,9),(-2218,-1920,12),
       (-2228,-1940,6),(-2225,-1960,3),(-2248,-1980,5),(-2265,-2000,10),(-2255,-2020,14),(-2255,-2050,2)]
# These return edges overlap existing mainland. Their final heights use actual original rays.
seam=[(-2220,-2050),(-2180,-2050),(-2140,-2050),(-2100,-2050),(-2060,-2050),(-2020,-2050),(-1990,-2050),
      (-1990,-1985),(-1990,-1920),(-1990,-1855),(-1990,-1790),(-1990,-1725),(-1990,-1660),(-2010,-1640),(-2030,-1648)]
outline=[{'position':[x,z],'height':h,'role':'shore'} for x,z,h in shore]+[{'position':[x,z],'height':None,'role':'mainland_seam'} for x,z in seam]
houses=[
    {'name':'fore_fisher','position':[-2261,9.,-1754],'yaw':-1.10,'asset':'fisher_cottage'},
    {'name':'fore_workshop','position':[-2245,10.8,-1747],'yaw':-1.40,'asset':'quay_workshop'},
    {'name':'fore_keeper','position':[-2246,12.5,-1766],'yaw':-.75,'asset':'keeper_house'},
    {'name':'fore_upper','position':[-2229,14.5,-1761],'yaw':-1.45,'asset':'keeper_house'},
    {'name':'fore_back_cottage','position':[-2227,15.5,-1739],'yaw':-1.15,'asset':'fisher_cottage'},
    {'name':'bay_fisher','position':[-2241,6.5,-1871],'yaw':-1.40,'asset':'fisher_cottage'},
    {'name':'bay_keeper','position':[-2230,8.5,-1885],'yaw':-1.70,'asset':'keeper_house'},
    {'name':'bay_upper','position':[-2217,10.5,-1875],'yaw':-1.10,'asset':'keeper_house'},
    {'name':'bay_workshop','position':[-2213,8.5,-1856],'yaw':-1.40,'asset':'quay_workshop'}]
# Pads include the actual porch approach. Heights are design levels; geometry is built after source-ground survey.
for h in houses:
    h['pad_half_size']=[4.4,7.5] if h['asset']=='keeper_house' else ([3.65,5.9] if h['asset']=='fisher_cottage' else [4.8,5.5])
def inside(x,z):
    polygon=[p['position'] for p in outline];result=False;j=len(polygon)-1
    for i,(xi,zi) in enumerate(polygon):
        xj,zj=polygon[j]
        if (zi>z)!=(zj>z) and x<(xj-xi)*(z-zi)/(zj-zi)+xi:result=not result
        j=i
    return result
boundary=[]
for a,b in zip(outline,outline[1:]+outline[:1]):
    pa,pb=Vector(a['position']),Vector(b['position']);steps=math.ceil((pb-pa).length/12.)
    for j in range(steps):
        t=j/steps;p=pa.lerp(pb,t)
        height=a['height']*(1-t)+b['height']*t if a['height'] is not None and b['height'] is not None else None
        boundary.append({'position':[p.x,p.y],'height':height,'role':'shore' if height is not None else 'mainland_seam'})
coords=[Vector((p['position'][0]-ORIGIN[0],p['position'][1]-ORIGIN[1])) for p in boundary]
edges=[];count=len(coords)
for i in range(count):edges.append((i,(i+1)%count))
for row in range(51):
    z=-2070+row*9.
    for col in range(49):
        x=-2400+(col+.5*(row%2))*9.
        if inside(x,z):coords.append(Vector((x-ORIGIN[0],z-ORIGIN[1])))
for h in houses:
    x,_,z=h['position'];co,si=math.cos(h['yaw']),math.sin(h['yaw']);wx,wz=h['pad_half_size'];start=len(coords)
    for u,v in [(-wx,-wz),(wx,-wz),(wx,wz),(-wx,wz)]:
        px,pz=x+co*u+si*v,z-si*u+co*v;assert inside(px,pz),(h['name'],px,pz)
        coords.append(Vector((px-ORIGIN[0],pz-ORIGIN[1])))
    for i in range(4):edges.append((start+i,start+(i+1)%4))
    coords.append(Vector((x-ORIGIN[0],z-ORIGIN[1])))
verts,cdt_edges,triangles,original,_,_=delaunay_2d_cdt(coords,edges,[list(range(count))],1,.00001)
assert triangles and all(len(t)==3 for t in triangles)
points=[[p.x+ORIGIN[0],0.,p.y+ORIGIN[1]] for p in verts]
edge_counts={}
for triangle in triangles:
    for a,b in zip(triangle,triangle[1:]+triangle[:1]):
        edge=tuple(sorted((a,b)));edge_counts[edge]=edge_counts.get(edge,0)+1
border=[list(e) for e,c in edge_counts.items() if c==1]
layout={'label':'23c','origin':[ORIGIN[0],0.,ORIGIN[1]],'source_reference_survey':'headland-survey-23a-20260908T113519Z-7922a8f6625742ba82e2e52c9933f6be','outline':outline,'boundary':boundary,'houses':houses,'vertices':points,'triangles':[list(t) for t in triangles],'border_edges':border,'scope':'Blender constrained terrain layout for a solid mainland extension with real inlet. All top design levels remain proposals; original terrain for every vertex must be queried before volume generation.'}
(OUT/'layout.json').write_text(json.dumps(layout,indent=2),encoding='utf-8')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mesh=bpy.data.meshes.new('Authored coastal terrain layout only');mesh.from_pydata([(p.x,-p.y,0) for p in verts],[],triangles);mesh.update()
obj=bpy.data.objects.new('Layout, not final terrain',mesh);bpy.context.collection.objects.link(obj)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'layout.blend'))
print('HEADLAND LAYOUT '+str(len(verts))+' points '+str(len(triangles))+' triangles',flush=True)
