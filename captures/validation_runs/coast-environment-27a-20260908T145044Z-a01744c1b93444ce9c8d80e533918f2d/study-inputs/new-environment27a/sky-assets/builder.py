"""Editable low-poly celestial sphere and three volumetric coastal cloud banks."""
import bpy,bmesh,math,json,hashlib,shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'captures/coastal_sky_assets_27a'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py');reports=[]
def reset():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1)
    m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=1.
    return m
def save(name):
    rows=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        assert all(e.is_manifold for e in bm.edges) and all(f.calc_area()>1e-8 for f in bm.faces)
        vol=bm.calc_volume(signed=True);assert vol>0
        bm.to_mesh(o.data);rows.append({'part':o.name,'verts':len(bm.verts),'faces':len(bm.faces),'volume':vol});bm.free()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))
    bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')),export_format='GLB',export_yup=True,export_animations=False)
    reports.append({'asset':name,'parts':rows,'source_sha256':hashlib.sha256((OUT/(name+'.blend')).read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256((OUT/(name+'.glb')).read_bytes()).hexdigest()})
# Keep the reviewed moon bytes; this iteration authors cloud volumes only.
prior=ROOT/'captures/coastal_sky_assets_21b'
moon_record=next(a for a in json.loads((prior/'model-report.json').read_text())['assets'] if a['asset']=='moon')
for ext in ['blend','glb']:shutil.copy2(prior/('moon.'+ext),OUT/('moon.'+ext))
reports.append(moon_record)

def lobe(name,center,size,turn):
    cx,cy,cz=center;rx,ry,h=size;h*=1.35;co,si=math.cos(turn),math.sin(turn);points=[]
    footprint=[(-.92,-.45),(-.36,-.89),(.33,-.95),(.89,-.48),(1.,.24),(.39,.86),(-.30,.93),(-.98,.30)]
    for layer in range(2):
        for i,(x,y) in enumerate(footprint):
            scale=1. if layer==0 else .86
            u,v=x*rx*scale,y*ry*scale
            z=cz+(-h*(.10+.075*math.sin(i*1.7+turn)) if layer==0 else h*(.34+.12*math.sin(i*1.7+turn)))
            points.append((cx+co*u-si*v,cy+si*u+co*v,z))
    for x,y,z in [(-.27,.03,.86),(.19,.13,1.),(.36,-.20,.69),(-.12,-.35,.62),(-.31,-.16,-.35),(.26,.19,-.29),(.02,-.30,-.24)]:
        points.append((cx+co*x*rx-si*y*ry,cy+si*x*rx+co*y*ry,cz+z*h))
    bm=bmesh.new()
    for p in points:bm.verts.new(p)
    result=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    unused=[v for v in bm.verts if not v.link_faces]
    if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
    data=bpy.data.meshes.new(name);bm.to_mesh(data);bm.free()
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o)
    o.data.materials.append(material('Cloud silver vapor',(.75,.81,.91)))
clouds=[
    [((-62,0,0),(66,28,16),.08),((-5,4,2),(57,33,37),-.12),((52,-2,-1),(70,29,18),.13)],
    [((-105,0,0),(65,29,17),.1),((-52,4,2),(62,36,29),-.2),((10,0,3),(63,40,48),.1),((68,-5,0),(65,30,28),.2),((111,3,-2),(45,24,12),-.3)],
    [((-65,0,0),(58,29,14),-.1),((-14,-4,2),(60,38,38),.12),((44,5,4),(48,32,30),-.16),((80,-3,-1),(44,25,13),.1)]]
for index,lobes in enumerate(clouds):
    reset()
    for k,(center,size,turn) in enumerate(lobes):lobe('Cloud bank %s joined vapor lobe %02d'%(index,k),center,size,turn)
    save('cloud_bank_'+str(index))
(OUT/'model-report.json').write_text(json.dumps({'scope':'New editable cloud volumes have taller lobes and beveled asymmetric undersides, removing the single flat underside silhouette. Original21b moon bytes retained. Saved editable closed-solid Blender celestial/cloud models. Cloud lobes overlap as volumetric vapor forms. No camera planes or image textures. Visual acceptance pending.','assets':reports},indent=2))
print('COASTAL SKY ASSETS BUILT',len(reports),flush=True)
