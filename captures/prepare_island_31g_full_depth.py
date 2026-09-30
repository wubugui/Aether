from pathlib import Path
import bpy,bmesh,json,math
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'captures/lantern_island_study_31f/island_c.blend'))
o=bpy.data.objects['island_c grass and exposed rock terrain'];bm=bmesh.new();bm.from_mesh(o.data)
planes=[([0,0,-6],[0,0,1]),([0,0,10.7],[0,0,1])]
for deg in [58,156]:
 a=math.radians(deg);planes.append(([0,0,0],[-math.sin(a),math.cos(a),0]))
for co,no in planes:
 fs=[f for f in bm.faces if any(v.co.y>0 and -7<v.co.z<12 for v in f.verts)]
 es={e for f in fs for e in f.edges};vs={v for f in fs for v in f.verts}
 bmesh.ops.bisect_plane(bm,geom=fs+list(es)+list(vs),dist=1e-6,plane_co=co,plane_no=no,clear_inner=False,clear_outer=False)
bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.verts.index_update();bm.faces.index_update()
sel=[]
for f in bm.faces:
 p=f.calc_center_median();a=math.degrees(math.atan2(p.y,p.x))
 if 58+1e-5<a<156-1e-5 and -6+1e-5<p.z<10.7-1e-5:sel.append(f.index)
data=dict(vertices=[list(v.co) for v in bm.verts],polygons=[[v.index for v in f.verts] for f in bm.faces],materials=[f.material_index for f in bm.faces],selected_faces=sel,planes=planes)
(R/'captures/island-31g-cut-patch-full-depth.json').write_text(json.dumps(data))
print('CUT PATCH',len(bm.verts),len(bm.faces),len(sel),flush=True)
