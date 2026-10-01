"""One controlled upper-form experiment: editable lofts, preserved52f low bodies."""
import bpy,bmesh,hashlib,json,math
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent.parent
PREVIOUS=P.parent/'cloud-sea52f/variants/cloud_sea52f_variants.blend'
protected=list((P.parent/'cloud-sea52f').rglob('*'))
protected=[p for p in protected if p.is_file() and '__pycache__' not in p.parts]
protected += [ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52f/Game52f.tscn',
 ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend',ROOT/'candidates/round40-exclusive-20260930/project/project.godot']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(PREVIOUS),link=False) as (s,d):
    d.objects=[n for n in s.objects if n.startswith(('CloudSea52f_v0_','CONTROL52f_v0_'))]
lowcol=bpy.data.collections.new('Preserved52f_v0_low_bodies');bpy.context.scene.collection.children.link(lowcol)
oldctrl=bpy.data.collections.new('Preserved52f_v0_editable_controls');bpy.context.scene.collection.children.link(oldctrl)
for ob in d.objects:
    (oldctrl if ob.name.startswith('CONTROL') else lowcol).objects.link(ob)
    ob.hide_render=ob.name.startswith('CONTROL')
oldctrl.hide_viewport=True;oldctrl.hide_render=True
mat=bpy.data.objects['CloudSea52f_v0_low_saddle'].data.materials[0]
col=bpy.data.collections.new('CloudSea52g_v0_upper_forms');bpy.context.scene.collection.children.link(col)
ctrl=bpy.data.collections.new('Editable52g_v0_cross_section_cages');bpy.context.scene.collection.children.link(ctrl)

# Knots: position along long axis, lateral bend, half-width, low belly, high crown.
# One primary crown, two smaller folds and deep broad saddles. No sphere components.
profile=[
 (-1,0,0,90,90),(-.91,-.03,.40,30,167),(-.78,-.08,.75,-5,220),
 (-.64,-.12,.88,-15,285),(-.50,-.07,.92,-5,350),(-.36,.02,.85,-20,305),
 (-.22,.14,.74,0,230),(-.10,.10,.72,-10,195),(.03,-.06,.90,10,267),
 (.16,-.11,.82,25,247),(.29,-.03,.69,0,178),(.43,.11,.79,20,211),
 (.57,.17,.65,30,174),(.70,.12,.53,45,132),(.84,.08,.37,55,125),
 (.94,.03,.19,68,100),(1,0,0,82,82)
]

def interp(t,k):
    for j in range(len(profile)-1):
        if profile[j][0]<=t<=profile[j+1][0]:break
    u=(t-profile[j][0])/(profile[j+1][0]-profile[j][0])
    # Cubic smoothstep preserves every designed high/low knot without overshoot.
    q=u*u*(3-2*u)
    return profile[j][k]*(1-q)+profile[j+1][k]*q
def gauss(x,c,s):return math.exp(-.5*((x-c)/s)**2)
def cyclic_gauss(a,c,s):
    diff=(a-c+math.pi)%(2*math.pi)-math.pi
    return math.exp(-.5*(diff/s)**2)
def build(kind,cx,cy,yaw,length,width,lo,hi,budget,mode):
    verts=[];faces=[];rings=55;n=40
    # Distinct parameterization changes folds, bend and asymmetry per part.
    for j in range(1,rings):
        t=-1+2*j/rings
        bend=interp(t,1)
        if mode==1:bend=-bend+.11*math.sin((t+.25)*math.pi)
        if mode==2:bend=.12*math.sin((t+.45)*math.pi)+.05*t
        w=interp(t,2);bottom=interp(t,3);top=interp(t,4)
        if mode==1:
            top=bottom+(top-bottom)*(.91+.10*t);w*=1+.10*math.sin(t*3+1)
        elif mode==2:
            top=bottom+(top-bottom)*(.88-.12*t);w*=1+.10*math.sin(t*4-.5)
        zc=(bottom+top)/2;rz=(top-bottom)/2
        for i in range(n):
            a=2*math.pi*i/n
            # A high crown cut by real concave side gullies, with lower offset shoulders.
            gully=(.17*gauss(t,-.08,.16)*cyclic_gauss(a,1.03,.33)
                  +.16*gauss(t,.34,.14)*cyclic_gauss(a,2.19,.32)
                  +.12*gauss(t,-.60,.13)*cyclic_gauss(a,2.42,.30))
            shoulder=(.15*gauss(t,-.38,.12)*cyclic_gauss(a,.35,.38)
                     +.17*gauss(t,.06,.14)*cyclic_gauss(a,2.87,.32)
                     +.14*gauss(t,.59,.11)*cyclic_gauss(a,.60,.35))
            small_fold=(.045*math.sin(t*16+a*2+.8*mode)*gauss(a,math.pi/2,1.7))
            radial=1-gully+shoulder+small_fold
            y=bend*width+math.cos(a)*width*.5*w*radial*(1+.065*math.sin(a+mode))
            z=zc+math.sin(a)*rz*radial
            # Lower contour changes along the ridge, instead of a disk-shaped common base.
            if math.sin(a)<0:z+=12*math.sin(t*7+mode)*(-math.sin(a))**2*(1-t*t)
            verts.append((t*length*.5,y,z))
    start=len(verts);verts.append((-length*.5,0,90))
    end=len(verts);verts.append((length*.5,0,82))
    for j in range(rings-2):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n;c=(j+1)*n+(i+1)%n;d=(j+1)*n+i
            faces.append((a,d,c,b))
    for i in range(n):
        faces.append((start,(i+1)%n,i))
        faces.append((end,(rings-2)*n+i,(rings-2)*n+(i+1)%n))
    me=bpy.data.meshes.new(f'52g_{kind}_section_cage');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    # Explicit whole-part bounds; varying bottoms and side profiles are preserved.
    zmin=min(v.co.z for v in me.vertices);zmax=max(v.co.z for v in me.vertices)
    ca,sa=math.cos(math.radians(yaw)),math.sin(math.radians(yaw))
    for v in me.vertices:
        x,y,z=v.co;v.co=(cx+x*ca-y*sa,cy+x*sa+y*ca,lo+(z-zmin)/(zmax-zmin)*(hi-lo))
    cage=bpy.data.objects.new(f'CONTROL52g_v0_{kind}_loft_cage',me);ctrl.objects.link(cage)
    cage['cross_section_knots']=json.dumps(profile);cage['construction']='Closed, asymmetric section loft with broad concave gullies';cage.hide_render=True
    ob=bpy.data.objects.new(f'CloudSea52g_v0_{kind}',me.copy());col.objects.link(ob)
    bpy.context.view_layer.objects.active=ob;ob.select_set(True)
    m=ob.modifiers.new('Continuous organic section interpolation','SUBSURF');m.levels=1;m.render_levels=1
    bpy.ops.object.modifier_apply(modifier=m.name)
    tri=sum(len(f.vertices)-2 for f in ob.data.polygons)
    m=ob.modifiers.new('Facets follow irregular ridge and broad gullies','DECIMATE');m.ratio=min(1,budget/tri)
    bpy.ops.object.modifier_apply(modifier=m.name)
    ob.data.materials.append(mat);colors=ob.data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
    for f in ob.data.polygons:
        f.use_smooth=False;z=sum(ob.data.vertices[k].co.z for k in f.vertices)/len(f.vertices)
        v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
        for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
    ob['visual_status']='Unreviewed upper hierarchy prototype, not accepted cloud form'
    return ob,{'name':ob.name,'center_xy':[cx,cy],'heading':yaw,'length':length,'nominal_width':width,'low':lo,'high':hi,'mode':mode,'editable_control_cage':cage.name,'triangle_target':budget}

specs=[('main_ridge',-350,-360,12,740,460,-30,350,2200,0),
       ('offset_shoulder',350,-60,-18,435,310,10,215,1300,1),
       ('low_tail',-40,400,32,305,230,-20,120,850,2)]
new=[];report=[]
for args in specs:
    ob,r=build(*args);new.append(ob);report.append(r)
ctrl.hide_viewport=True;ctrl.hide_render=True
def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT')
    for item in objects:item.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.gltf(filepath=str(P/name),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
export('cloud_sea_52g_upper_v0.glb',new)
export('cloud_sea_52g_prototype_v0.glb',new+list(lowcol.objects))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52g_prototype.blend'))
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected};assert before==after
(P/'protected-sources52g.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2)+'\n')
(P/'layout52g.json').write_text(json.dumps({'status':'One representative upper-form prototype','parts':report,'retained_low_bodies':['CloudSea52f_v0_low_saddle','CloudSea52f_v0_low_drift'],
 'hierarchy_intent':'Dominant irregular long ridge, smaller offset shoulder and short low tail; about5:2:1 plan-area design intent',
 'construction':'Editable closed cross-section cages, genuine concave gullies, no sphere pile or brightness change',
 'unchanged_low_body_limitation':'52f lower disk appearance remains for separate later resculpt',
 'world_integration':False,'visual_acceptance':False},indent=2)+'\n')
print('52G UPPER LOFT PROTOTYPE READY; NO RENDER OR WORLD INTEGRATION')
