import bpy, bmesh, math, json, hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
ROOT=P.parent.parent
OLD=ROOT/'candidates/round40-exclusive-20260930/source-assets/cloud-sea46/cloud_sea46.blend'
PROTECTED=[OLD,ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend']
before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in PROTECTED}
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(OLD),link=False) as (src,dst):
    dst.materials=[n for n in src.materials if n.startswith('Cloud46')]
mat=dst.materials[0]
# Authored loft stations: t, lateral center, halfwidth, crown, belly.
# Values describe unequal broad crown / shoulder / taper, not a chain of spheres.
profiles=[
[(0,0,0,.40,.46),(.07,-.12,.38,.50,.36),(.16,-.26,.72,.66,.23),(.27,-.32,.92,.92,.09),(.39,-.28,1,1,0),(.51,-.12,.92,.85,.05),(.63,.12,.79,.70,.16),(.75,.28,.67,.66,.25),(.86,.32,.49,.52,.34),(.94,.25,.25,.43,.40),(1,.18,0,.40,.44)],
[(0,0,0,.40,.46),(.07,.08,.36,.51,.35),(.17,.18,.69,.83,.17),(.29,.25,.95,1,.02),(.40,.20,.88,.84,0),(.50,.05,.70,.60,.09),(.60,-.12,.83,.72,.13),(.71,-.24,.90,.89,.16),(.82,-.28,.70,.71,.25),(.93,-.20,.33,.48,.38),(1,-.12,0,.42,.44)],
[(0,-.10,0,.36,.43),(.07,-.08,.26,.44,.34),(.18,-.02,.50,.57,.22),(.30,.08,.71,.67,.12),(.43,.20,.92,.79,.02),(.56,.31,1,.96,0),(.67,.32,.95,1,.04),(.78,.22,.76,.77,.17),(.87,.07,.52,.60,.29),(.95,-.10,.23,.46,.38),(1,-.20,0,.40,.42)]
]
# x,y,heading,length,width,bottom,top. Piece centers remain local to original root.
layouts=[
 [(-365,-365,17,750,480,45,360),(340,-90,-18,660,425,135,330),(-30,345,28,570,390,-5,255)],
 [(-355,-390,24,730,465,40,350),(275,-95,-23,640,410,125,325),(-65,325,7,585,400,-15,265)],
 [(-390,-355,9,740,450,55,375),(310,-55,-29,690,440,140,335),(-20,440,34,550,370,0,275)]
]
report={'scope':'Independent CloudSea52 source only; no scene or material45/47 edits', 'visual_acceptance':False,'rendered':False,'axis_mapping':'Blender (x,y,z) -> glTF/Godot (x,z,-y); export_yup=True','anchor_y':700,'variants':[]}
def make_piece(vi,pi,row,col):
    cx,cy,heading,L,W,bottom,top=row
    prof=profiles[(vi+pi)%3]; verts=[]; faces=[]; N=16
    h=math.radians(heading); ca,sa=math.cos(h),math.sin(h)
    def place(x,y,z):return (cx+x*ca-y*sa,cy+x*sa+y*ca,z)
    verts.append(place(-L/2,prof[0][1]*W,(bottom+top)/2))
    for ri,(t,shift,w,crown,belly) in enumerate(prof[1:-1]):
        # Crown leans sideways; lower half pinches toward the spine.
        for j in range(N):
            a=2*math.pi*j/N; sn,cs=math.sin(a),math.cos(a)
            center=bottom+(top-bottom)*.43
            z=center+(top-bottom)*(crown-.43)*max(sn,0)+(top-bottom)*(.43-belly)*min(sn,0)
            width=W*.5*w*(1-.31*max(-sn,0))
            y=shift*W*.38+width*cs+W*.075*max(sn,0)*(1 if pi!=1 else -1)
            x=(t-.5)*L+L*.018*math.sin(a*2+ri*.73)*math.sin(math.pi*t)
            verts.append(place(x,y,z))
    end=len(verts);verts.append(place(L/2,prof[-1][1]*W*.38,bottom+(top-bottom)*.43))
    for j in range(N):faces.append((0,1+(j+1)%N,1+j))
    for r in range(len(prof)-3):
        for j in range(N):
            a=1+r*N+j;b=1+r*N+(j+1)%N;c=b+N;d=a+N
            if (r+j)%2:faces.extend([(a,b,d),(b,c,d)])
            else:faces.extend([(a,b,c),(a,c,d)])
    last=1+(len(prof)-3)*N
    for j in range(N):faces.append((last+j,last+(j+1)%N,end))
    name=f'CloudSea52_v{vi}_{["main_bent_crown","notched_shoulder","slant_low_ridge"][pi]}'
    me=bpy.data.meshes.new(name+'_editable_loft');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat)
    ob['construction']='Direct editable closed ring loft; no spherical lobes, no combined floor'
    ob['profile_type']=['bent ridge','double crown with notch','slant long shoulder'][(vi+pi)%3]
    ob['station_parameters']=json.dumps(prof);ob['layout_parameters']=json.dumps(row)
    colors=me.color_attributes.new('Col','FLOAT_COLOR','CORNER')
    for f in me.polygons:
        f.use_smooth=False
        # Preserve the exact old46 vertex color formula, no emission/transparency.
        z=sum(me.vertices[k].co.z for k in f.vertices)/len(f.vertices)
        v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
        for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
    return ob
for vi,rows in enumerate(layouts):
    col=bpy.data.collections.new(f'cloud_sea_52_{vi}');bpy.context.scene.collection.children.link(col)
    obs=[make_piece(vi,pi,row,col) for pi,row in enumerate(rows)]
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    bpy.ops.export_scene.gltf(filepath=str(P/f'cloud_sea_52_{vi}.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
    report['variants'].append({'variant':vi,'objects':[ob.name for ob in obs],'design_layouts':rows})
# Display one variant in source by default; collections remain editable.
for col in bpy.data.collections:
    if col.name.startswith('cloud_sea_52_'):
        col.hide_viewport=not col.name.endswith('_0');col.hide_render=not col.name.endswith('_0')
bpy.context.scene['CloudSea52_status']='Source candidate, no visual acceptance. No render or Godot run.'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52.blend'))
after={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in PROTECTED}
assert before==after
(P/'protected-sources.json').write_text(json.dumps({'before':before,'after':after,'unchanged':before==after},indent=2))
(P/'design52.json').write_text(json.dumps(report,indent=2))
print('SOURCE52_READY')
