"""Correct 37a's observed courtyard obstruction and unsupported paving.
Retain the saved carved geometry; add a connected low front gallery.
"""
from pathlib import Path
import ast,json,math,hashlib
import bpy,bmesh,numpy as np
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];OUT=R/'captures/crownreach_study_37b';OUT.mkdir(exist_ok=False)
SOURCE=R/'captures/crownreach_study_37a/castle.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
library=bpy.data.collections['Crownreach - carved stone and town roofs 37a']
material=bpy.data.materials['Pale limestone - matte palette 37a']
parts=[o for o in bpy.context.scene.objects if o.type=='MESH']
tree=ast.parse((R/'blender/create_assets.py').read_text())
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ['bl','lin','rgb','finish','box','cone','rod','mesh','roof']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<castle helpers>','exec'),globals())
def name(o,label):o.name=label;return o
changes=[]
for obj in list(parts):
    if obj.name.startswith('Courtyard paving'):
        # Preserve top and bevel, extend the submerged bottom into real ground.
        for v in obj.data.vertices:
            if v.co.z<.68:v.co.z-=1.0
        changes.append({'name':obj.name,'edit':'lower bottom vertices 1m; top unchanged'})
    if obj.name.startswith(('Courtyard house 02','Courtyard roof 02')):
        # Relocate the blocking front cottage to the actual vacant rear-left
        # bay. Apply identical transform to its separate roof/door/chimney.
        for v in obj.data.vertices:
            v.co.x=-14+(v.co.x-1.2)*.65
            v.co.y+=17.8
        changes.append({'name':obj.name,'edit':'front axis obstruction moved to rear-left bay; x width 0.65'})

# A low east-front gallery joins the hall to the courtyard, giving an inhabited
# roof layer without filling the open entry axis or the western alley.
stone='d2cbb5';light='e0d9c5';shade='b8b5a4';roofcol='aa9f8a'
name(box((8.4,-.05,2.0),(10.0,1.3,2.9),shade,.05),'East gallery embedded floor')
for x in [3.7,6.05,8.4,10.75,13.1]:
    name(box((x,1.7,3.08),(.33,3.4,.4),stone,.04),'East gallery square pier')
    name(box((x,3.24,3.08),(.6,.22,.65),light,.03),'East gallery pier capital')
name(box((8.4,3.45,3.05),(10.1,.38,.46),light,.035),'East gallery front architrave')
name(roof(8.4,2.0,10.7,3.45,3.55,4.65,roofcol),'East gallery layered roof')

# A small rear stair tower is subordinate to the original high towers and
# joins the existing keep/curtain. Its roof breaks the old bare rear box.
name(cone((-1.5,3.6,-9.6),8.2,1.65,1.52,stone,8),'Keep rear stair turret')
name(cone((-1.5,8.35,-9.6),1.45,1.85,.10,roofcol,8),'Keep rear stair turret roof')
for y in [2.7,5.1,6.6]:
    name(box((-1.5,y,-11.13),(.42,.9,.10),'74766f',.025),'Stair turret rear slit')

# Thick dormer bodies and individual gable roofs intersect the saved keep
# roof, with inset dark windows framed by actual stone.
for x in [-5.5,-2.3,.9]:
    name(box((x,9.36,-.55),(1.5,1.65,1.65),stone,.035),'Keep front dormer cheek')
    name(roof(x,-.55,1.86,1.93,10.18,10.9,roofcol),'Keep front dormer gable')
    name(box((x,9.45,.30),(.68,.90,.06),'656c6c'),'Keep dormer inset window')
    for dx in [-.4,.4]:name(box((x+dx,9.45,.38),(.12,1.05,.15),light),'Keep dormer jamb')
    name(box((x,8.94,.38),(.94,.15,.20),light),'Keep dormer sill')

# Save and export exactly the retained native parts plus these local changes.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'castle.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'castle.glb'),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
report={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'changes':changes,'instance_origin':[43.288,18.845,-282.521],'instance_scale':[1,1,1],'parts':[],'scope':'Saved 37a source revision; bottom supports and real entry axis corrected, new low gallery/dormer/stair volume. Native World occupancy still needs GPU checks.'}
for obj in parts:
    pts=[obj.matrix_world@v.co for v in obj.data.vertices]
    report['parts'].append({'name':obj.name,'vertices':len(obj.data.vertices),'polygons':len(obj.data.polygons),'bounds_blender':[list(map(min,zip(*pts))),list(map(max,zip(*pts)))]})
(OUT/'model-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(OUT/'builder.py').write_text(Path(__file__).read_text(),encoding='utf-8')
print('CROWNREACH37B SAVED',len(parts),flush=True)
