"""Build only an independent editable local cloud-bank .blend and root-local GLBs.

Prepared for the parent's scheduled Blender process. Does not open Godot, run a
renderer, touch project assets, change a default, or overwrite an existing build.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

P=Path(__file__).resolve().parent;ROOT=P.parents[1]
sys.path.insert(0,str(P))
import geometry58 as G
from intake58 import native_intake, SCENE, PROJECT

ORIGIN=(3775.,700.,3575.)
MATERIAL='Cloud46 diffuse warm crown cool belly'


def source_coordinate(p):
    return (p[0]-ORIGIN[0],-(p[2]-ORIGIN[2]),p[1]-ORIGIN[1])


def world_coordinate(p):
    return (p[0]+ORIGIN[0],p[2]+ORIGIN[1],-p[1]+ORIGIN[2])


def make_poly_control(collection,role,row):
    curve=bpy.data.curves.new('EDIT58_'+row['name'],'CURVE');curve.dimensions='3D'
    spline=curve.splines.new('POLY');spline.points.add(len(row['points'])-1)
    for point,data in zip(spline.points,row['points']):
        if role in ('ridges','valleys'):p=(data[0],710+data[2],data[1])
        else:p=(data[0],data[2],data[1])
        point.co=(*source_coordinate(p),1)
    ob=bpy.data.objects.new(curve.name,curve);collection.objects.link(ob)
    ob['control_role']=role;ob['recipe_name']=row['name'];ob['point_widths_m']=[p[3] for p in row['points']]
    ob['edit_instructions']='Edit this POLY spline in native Edit Mode. Widths and heights are in Custom Properties. Rebuild using build58.py --from-controls --out a NEW revision directory.'
    if role in ('ridges','valleys'):ob['profile_power']=row['power']
    else:
        ob['half_thickness_m']=[p[4] for p in row['points']];ob['crest_heights_m']=[p[5] for p in row['points']]
        ob['original_root']=row['root'];ob['radial_sides']=row['sides']
    return ob


def read_controls():
    assert bpy.context.scene.get('cloudbank58_schema')==G.SCHEMA,'Open a native58 source before rebuilding controls'
    recipe=json.loads(bpy.data.texts['RECIPE58.json'].as_string())
    for role in ('ridges','valleys','shelves'):
        for row in recipe[role]:
            ob=bpy.data.objects['EDIT58_'+row['name']];sp=ob.data.splines[0]
            assert sp.type=='POLY' and len(ob.data.splines)==1
            widths=list(ob['point_widths_m']);assert len(widths)==len(sp.points)
            pts=[]
            for i,p in enumerate(sp.points):
                x,y,z=world_coordinate(ob.matrix_world@Vector(p.co[:3]))
                if role in ('ridges','valleys'):pts.append((x,z,y-710,widths[i]))
                else:pts.append((x,z,y,widths[i],ob['half_thickness_m'][i],ob['crest_heights_m'][i]))
            row['points']=pts
            if role in ('ridges','valleys'):row['power']=float(ob['profile_power'])
    for p in recipe['peaks']:
        ob=bpy.data.objects['EDIT58_'+p['name']];x,y,z=world_coordinate(ob.matrix_world.translation)
        p.update(center=[x,z],radii=list(ob['radii_m']),height=float(ob['height_m']))
    return recipe


def build(out,from_controls=False):
    out=out.resolve()
    assert out==P or P in out.parents,'Keep all58 outputs inside its independent source directory'
    assert not(out/'cloud_bank58.blend').exists(),'Never overwrite a completed source; choose a new revision directory'
    out.mkdir(parents=True,exist_ok=True)
    intake,_=native_intake()
    roots={r['name']:r for r in intake['roots']}
    recipe=read_controls() if from_controls else G.recipe()
    protected=[SCENE,PROJECT/'project.godot',ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend',
               ROOT/'source-assets/cloud-sea52f/variants/cloud_sea52f_variants.blend']
    protected += [ROOT/f['path'] for f in intake['source_glbs']]
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    before={str(p.relative_to(ROOT)):digest(p) for p in protected}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene['cloudbank58_schema']=G.SCHEMA
    scene['source_origin_godot_world']=ORIGIN;scene['visual_acceptance']=False
    scene['authored_scope']='One closed 2300m local bank over four native roots, plus three closed upper ribbons. No internal caps. Not a whole-world model.'
    scene.render.threads_mode='FIXED';scene.render.threads=2
    with bpy.data.libraries.load(str(ROOT/'source-assets/cloud-sea52f/variants/cloud_sea52f_variants.blend'),link=False) as (source,target):
        assert MATERIAL in source.materials;target.materials=[MATERIAL]
    material=target.materials[0]
    controls=bpy.data.collections.new('EDIT58_native_crest_valley_and_upper_controls');scene.collection.children.link(controls)
    surfaces=bpy.data.collections.new('CloudBank58_local_four_root_field');scene.collection.children.link(surfaces)
    for role in ('ridges','valleys','shelves'):
        for row in recipe[role]:make_poly_control(controls,role,row)
    for p in recipe['peaks']:
        ob=bpy.data.objects.new('EDIT58_'+p['name'],None);controls.objects.link(ob);ob.empty_display_type='CONE';ob.empty_display_size=35
        ob.location=source_coordinate((p['center'][0],710+p['height'],p['center'][1]))
        ob['radii_m']=p['radii'];ob['height_m']=p['height'];ob['control_role']='peak'
    origin=bpy.data.objects.new('World58_origin_reference',None);controls.objects.link(origin)
    origin['godot_world_xyz']=ORIGIN;origin['source_axis']='Blender x,y,z maps to Godot x,z,-y relative to origin'
    controls.hide_render=True
    meshes=G.meshes(recipe);manifest=[]
    for spec in meshes:
        data=bpy.data.meshes.new(spec['name']+'_native_mesh');data.from_pydata([source_coordinate(p) for p in spec['vertices']],[],spec['faces']);data.update()
        ob=bpy.data.objects.new(spec['name'],data);surfaces.objects.link(ob);data.materials.append(material)
        for f in data.polygons:f.use_smooth=False
        ob['kind']=spec['kind'];ob['original_root']=spec['root'];ob['world_visual_acceptance']=False
        ob['source_vertices_are_editable']=True;ob['internal_caps']=int(spec.get('internal_caps',0))
        for name,indices in spec.get('native_region_vertex_groups',{}).items():
            group=ob.vertex_groups.new(name='NATIVE_REGION_'+name);group.add(indices,1,'REPLACE')
        for role in set(spec['roles']):
            group=ob.vertex_groups.new(name='SURFACE_'+role);group.add([i for i,r in enumerate(spec['roles']) if r==role],1,'REPLACE')
        # Preserve the old native material and exact old world-height color law.
        # This is a geometry-only source: no new darker belly or lighting cheat.
        col=data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
        for face in data.polygons:
            y=sum(spec['vertices'][i][1] for i in face.vertices)/len(face.vertices)
            v=.76+.16*max(0,min(1,((y-700)+190)/460));linear=((v+.055)/1.055)**2.4
            for li in face.loop_indices:col.data[li].color=(linear,linear,linear,1)
        # Temporary export mesh is transformed into this original root's local
        # axes. It is deleted before saving the .blend, so authoring remains one
        # coherent common-world native source and controls stay understandable.
        root=roots[spec['root']];basis=Matrix(root['basis_rows']);inv=basis.inverted();pos=Vector(root['position'])
        local=[inv@(Vector(v)-pos) for v in spec['vertices']]
        export=data.copy()
        for v,p in zip(export.vertices,local):v.co=(p.x,-p.z,p.y)
        temp=bpy.data.objects.new('EXPORT58_'+spec['name'],export);scene.collection.objects.link(temp)
        bpy.ops.object.select_all(action='DESELECT');temp.select_set(True);bpy.context.view_layer.objects.active=temp
        filename=spec['name']+'.glb'
        bpy.ops.export_scene.gltf(filepath=str(out/filename),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
        bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(export)
        manifest.append(dict(name=ob.name,kind=spec['kind'],file=filename,root=spec['root'],native_root_basis_rows=root['basis_rows'],native_root_position=root['position'],
                             vertices=len(data.vertices),triangles=len(data.polygons),world_bounds=[[min(v[k] for v in spec['vertices']) for k in range(3)],[max(v[k] for v in spec['vertices']) for k in range(3)]],
                             source_origin_godot_world=ORIGIN,internal_caps=0,sha256=digest(out/filename)))
    for name,contents in [('RECIPE58.json',json.dumps(recipe,indent=2)),('geometry58.py',(P/'geometry58.py').read_text()),('build58.py',Path(__file__).read_text())]:
        txt=bpy.data.texts.new(name);txt.write(contents)
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    bpy.ops.object.select_all(action='DESELECT')
    for ob in surfaces.objects:ob.select_set(True)
    bpy.context.view_layer.objects.active=surfaces.objects[0]
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'cloud_bank58.blend'))
    after={str(p.relative_to(ROOT)):digest(p) for p in protected};assert before==after
    (out/'protected-sources58.json').write_text(json.dumps(dict(before=before,after=after,unchanged=True),indent=2)+'\n')
    (out/'construction58.json').write_text(json.dumps(dict(recipe=recipe,origin=ORIGIN,meshes=manifest,selected_native_roots=sorted(r['name'] for r in intake['roots'] if r['selected']),
        internal_coplanar_caps=0,old_resources_or_world_changed=False,rendered=False,visual_acceptance=False,
        native_readback_pending=True,external_root_contact_check_pending=True,source_blend_sha256=digest(out/'cloud_bank58.blend')),indent=2)+'\n')
    print('58 SOURCE BUILT ONLY: one local continuous lower bank + three closed upper ribbons; visual/native-readback gates pending')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=P);parser.add_argument('--from-controls',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    build(args.out,args.from_controls)
