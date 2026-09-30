"""Editable, closed cloud volumes for a world-space coastal weather front."""
import bpy, bmesh, math, json, hashlib, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'captures/storm_cloud_assets_35a'
assert not OUT.exists()
OUT.mkdir()
shutil.copy2(__file__, OUT / 'builder.py')
records = []

def material():
    m = bpy.data.materials.new('Storm vapor: broad coherent facets')
    m.diffuse_color = (.32, .37, .43, 1)
    m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = m.diffuse_color
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1
    return m

def lobe(name, center, length, width, roof, belly, phase, turn=0):
    # Cross-sections along the bank, with separate upper and lower envelopes.
    # End caps taper to narrow rings, not sharp radial spikes or convex hulls.
    sections = [(-1,.045),(-.91,.36),(-.73,.69),(-.48,.91),(-.19,1.),
                (.12,.98),(.40,.87),(.66,.70),(.87,.39),(1,.045)]
    count = 16
    vertices = []
    for j, (t, spread) in enumerate(sections):
        bend = .13 * math.sin(t * 2.3 + phase)
        ridge = 1 + .10 * math.sin(j * 1.08 + phase)
        for k in range(count):
            a = 2 * math.pi * k / count + .035 * math.sin(j * 1.2 + phase)
            longitudinal = t * length * .5
            lateral = width * (math.cos(a) * spread * .5 + bend)
            vertical = (roof if math.sin(a) > 0 else belly) * math.sin(a) * spread * ridge
            vertical += roof * .10 * math.sin(t * 2.8 + phase)
            gx = center[0] + math.cos(turn) * longitudinal - math.sin(turn) * lateral
            gz = center[2] + math.sin(turn) * longitudinal + math.cos(turn) * lateral
            gy = center[1] + vertical
            vertices.append((gx, -gz, gy))  # Godot Y-up -> Blender Z-up
    faces = [tuple(reversed(range(count)))]
    for j in range(len(sections)-1):
        for k in range(count):
            a=j*count+k; b=j*count+(k+1)%count
            c=(j+1)*count+(k+1)%count; d=(j+1)*count+k
            if (j+k)%2: faces.extend([(a,b,d),(b,c,d)])
            else: faces.extend([(a,b,c),(a,c,d)])
    faces.append(tuple((len(sections)-1)*count+k for k in range(count)))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj=bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(material())
    obj['construction']='Authored loft rings; separate roof and underside; overlapping vapor volumes'
    return obj

def save(name):
    rows=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        assert all(e.is_manifold for e in bm.edges), obj.name
        assert min(f.calc_area() for f in bm.faces)>1e-5, obj.name
        assert bm.calc_volume(signed=True)>0, obj.name
        bm.to_mesh(obj.data)
        rows.append(dict(name=obj.name, vertices=len(bm.verts), faces=len(bm.faces),
                         signed_volume_m3=bm.calc_volume(signed=True)))
        bm.free()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))
    bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')), export_format='GLB', export_yup=True, export_animations=False)
    records.append(dict(asset=name, parts=rows,
                        blend_sha256=hashlib.sha256((OUT/(name+'.blend')).read_bytes()).hexdigest(),
                        glb_sha256=hashlib.sha256((OUT/(name+'.glb')).read_bytes()).hexdigest()))

def reset():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

reset()
# The shelf is long along local Z; its eastern lip is lower and irregular.
for i, (z,y,length,width,roof,belly,turn) in enumerate([
    (-560,30,790,540,215,130,.08),(-120,65,920,610,270,155,-.06),
    (390,0,850,590,220,120,.11),(820,50,690,500,185,145,-.08)]):
    lobe(f'Front shelf main shoulder {i:02}', (-150+35*math.sin(i),y,z), length,width,roof,belly,i*.8,math.pi/2+turn)
for i, (x,y,z,length,width) in enumerate([(100,-75,-430,520,270),(130,-85,70,600,300),(110,-95,570,470,260)]):
    lobe(f'Front shelf lower rolled lip {i:02}', (x,y,z),length,width,110,95,.7+i,math.pi/2+.10*i)
save('storm_front_shelf')

reset()
for i,(x,y,z,length,width,roof,belly,turn) in enumerate([
    (-330,75,-470,1250,730,340,180,.08),(-360,180,260,1400,950,430,220,-.12),
    (-900,140,-160,1550,1050,390,180,.21),(-1180,275,740,1330,900,490,170,-.17),
    (-700,100,1150,1200,710,280,180,.12),(-1650,230,-650,1480,1050,460,220,.05)]):
    lobe(f'Storm rear layered anvil {i:02}',(x,y,z),length,width,roof,belly,i*.55,math.pi/2+turn)
save('storm_rear_anvil')

reset()
for i,(x,y,z,length,width,roof,belly) in enumerate([
    (0,0,-440,680,460,110,170),(40,-85,40,810,460,135,215),
    (-90,-40,550,700,510,130,190),(120,-160,320,410,260,85,145)]):
    lobe(f'Low rain scud descending fold {i:02}',(x,y,z),length,width,roof,belly,1.2+i*.7,math.pi/2+.10*math.sin(i))
save('storm_rain_scud')

(OUT/'model-report.json').write_text(json.dumps(dict(
    scope='35a new native storm volumes; broad front shelf, rear anvils and hanging scud. No image planes. Overlapping closed vapor parts are deliberate. Visual acceptance pending.',
    coordinates='Authoring accepts Godot xyz metres, saves Blender x,-z,y. GLB export restores Godot Y-up.',
    assets=records, production_modified=False, visual_accepted=False), indent=2)+'\n',encoding='utf-8')
print('35a STORM CLOUD ASSETS READY', len(records),flush=True)
