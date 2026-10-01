"""Build an independent source B from editable closed3D fold controls only.

No rectangular heightfield, crop wall, lower cap, old mesh scaling, Godot launch,
or rendered preview. The parent's resource slot must be scheduled separately.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;A=P.parent;ROOT=A.parents[1]
sys.path[:0]=[str(P),str(A)]
import lofts58b as L
from geometry58 import signed_volume
from build58 import source_coordinate,world_coordinate,ORIGIN,MATERIAL
from intake58 import native_intake
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def object_geometry(ob):
    me=ob.data;me.calc_loop_triangles();verts=[v.co.copy() for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles]
    bm=bmesh.new();bm.from_mesh(me)
    tree=BVHTree.FromPolygons(verts,tri,all_triangles=True,epsilon=0)
    bad=[(a,b) for a,b in tree.overlap(tree) if a<b and not(set(tri[a])&set(tri[b]))]
    row=dict(name=ob.name,vertices=len(verts),triangles=len(tri),boundary=sum(e.is_boundary for e in bm.edges),nonmanifold=sum(not e.is_manifold for e in bm.edges),
             signed_volume=bm.calc_volume(signed=True),nonadjacent_self_overlap_count=len(bad),pairs=bad[:30])
    bm.free();return row


def build(out,from_controls=False):
    out=out.resolve();assert out==P or P in out.parents
    assert not(out/'cloud_bank58b.blend').exists(),'Keep completed source B immutable; use a new revision directory'
    out.mkdir(parents=True,exist_ok=True)
    freeze=json.loads((A/'revision-a-freeze.json').read_text())
    assert all(sha(ROOT/name)==r['sha256'] for name,r in freeze['files'].items()),'Frozen A changed'
    intake,_=native_intake();roots={r['name']:r for r in intake['roots']}
    protected={name:r['sha256'] for name,r in freeze['files'].items()}
    protected.update({f['path']:f['sha256'] for f in intake['source_glbs']})
    protected[intake['source_scene']]=intake['source_scene_sha256']
    selected_controls=[]
    if from_controls:
        assert bpy.context.scene.get('cloudbank58b_native3d_folds')
        # Capture native edited mesh data before factory reset; the new build is
        # authored from actual editable mesh vertices, not stale JSON controls.
        for ob in bpy.data.collections['EDIT58B_closed_3d_fold_volumes'].objects:
            if ob.type=='MESH' and not ob.get('not_a_loft_rebuild_input',False):
                selected_controls.append(dict(name=ob['fold_name'],vertices=[tuple(world_coordinate(ob.matrix_world@v.co)) for v in ob.data.vertices],faces=[tuple(f.vertices) for f in ob.data.polygons],
                                              knots=json.loads(ob['initial_knots_json']),section_count=ob['section_count'],profile=L.PROFILE))
    else:selected_controls=L.controls()
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    scene['cloudbank58b_native3d_folds']=True;scene['source_origin_godot_world']=ORIGIN;scene['visual_acceptance']=False
    scene['source_method']='Union of11 unequal closed3D native loft folds. No heightfield rectangle, underside cap, rectangular crop, spheres, or smooth modifier.'
    scene.render.threads_mode='FIXED';scene.render.threads=2
    controlcol=bpy.data.collections.new('EDIT58B_closed_3d_fold_volumes');scene.collection.children.link(controlcol)
    resultcol=bpy.data.collections.new('CloudBank58B_local_four_root_field');scene.collection.children.link(resultcol)
    upper_names=['CloudBank58_upper_west_layer','CloudBank58_upper_east_layer','CloudBank58_upper_far_veil']
    with bpy.data.libraries.load(str(A/'cloud_bank58.blend'),link=False) as (src,dst):dst.objects=upper_names
    upper=[]
    for ob in dst.objects:
        resultcol.objects.link(ob);upper.append(ob)
    material=bpy.data.materials[MATERIAL]
    control_objects=[];reports=[]
    for spec in selected_controls:
        vertices=spec['vertices'];faces=spec['faces']
        if signed_volume(vertices,faces)<0:faces=[tuple(reversed(f)) for f in faces]
        me=bpy.data.meshes.new('EDIT58B_'+spec['name']);me.from_pydata([source_coordinate(v) for v in vertices],[],faces);me.update()
        ob=bpy.data.objects.new(me.name,me);controlcol.objects.link(ob);ob.hide_render=True
        ob['fold_name']=spec['name'];ob['initial_knots_json']=json.dumps(spec['knots']);ob['section_count']=spec['section_count']
        ob['edit_instruction']='Edit native closed mesh vertices directly. Run build58b.py --from-controls --out a NEW revision directory to rebuild the union. Controls are not discarded.'
        for f in me.polygons:f.use_smooth=False
        row=object_geometry(ob);reports.append(row);control_objects.append(ob)
    (out/'native-control-input58b.json').write_text(json.dumps(dict(controls=reports,loft_specs=selected_controls,visual_acceptance=False),indent=2)+'\n')
    assert all(not(r['boundary'] or r['nonmanifold'] or r['nonadjacent_self_overlap_count']) and r['signed_volume']>0 for r in reports),'Native loft input invalid; retain report and redesign before union'
    # Join temporary copies, then one true volumetric remesh removes all interior
    # overlap faces. Native authored control bodies remain intact and editable.
    bpy.ops.object.select_all(action='DESELECT')
    for ob in control_objects:
        temp=bpy.data.objects.new('WORK58B_'+ob['fold_name'],ob.data.copy());resultcol.objects.link(temp);temp.select_set(True)
        bpy.context.view_layer.objects.active=temp
    bpy.ops.object.join();bank=bpy.context.object;bank.name='CloudBank58B_four_root_folded_volume'
    bank.data.remesh_voxel_size=26.;bank.data.use_remesh_preserve_volume=True
    bpy.ops.object.voxel_remesh()
    raw=bpy.data.objects.new('EDIT58B_continuous_union_before_facets',bank.data.copy());controlcol.objects.link(raw);raw.hide_render=True
    raw['fold_name']='continuous_union_review_mesh';raw['not_a_loft_rebuild_input']=True
    # Native quad-flow remeshing distributes restrained flat facets across the
    # entire3D surface; it does not add a smooth surface modifier or round caps.
    bpy.ops.object.quadriflow_remesh(target_faces=4800,use_mesh_symmetry=False,use_preserve_sharp=True,use_preserve_boundary=True)
    tri=bank.modifiers.new('Native restrained facets','TRIANGULATE');tri.quad_method='BEAUTY';tri.ngon_method='BEAUTY'
    bpy.ops.object.modifier_apply(modifier=tri.name)
    bank.data.materials.clear();bank.data.materials.append(material)
    for f in bank.data.polygons:f.use_smooth=False
    bank['original_root']='CloudSea_0_0';bank['kind']='continuous_lower_folded_volume';bank['internal_caps']=0;bank['visual_acceptance']=False
    for attr in list(bank.data.color_attributes):bank.data.color_attributes.remove(attr)
    col=bank.data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
    for f in bank.data.polygons:
        y=sum(world_coordinate(bank.data.vertices[i].co)[1] for i in f.vertices)/len(f.vertices)
        v=.76+.16*max(0,min(1,((y-700)+190)/460));linear=((v+.055)/1.055)**2.4
        for li in f.loop_indices:col.data[li].color=(linear,linear,linear,1)
    controlcol.hide_render=True;controlcol.hide_viewport=True
    construction=[]
    for ob in [bank]+upper:
        world=[Vector(world_coordinate(ob.matrix_world@v.co)) for v in ob.data.vertices]
        root=roots[ob['original_root']];inv=Matrix(root['basis_rows']).inverted();pos=Vector(root['position'])
        export=ob.data.copy()
        for v,p in zip(export.vertices,world):
            q=inv@(p-pos);v.co=(q.x,-q.z,q.y)
        temp=bpy.data.objects.new('EXPORT58B_'+ob.name,export);scene.collection.objects.link(temp)
        bpy.ops.object.select_all(action='DESELECT');temp.select_set(True);bpy.context.view_layer.objects.active=temp
        filename=ob.name+'.glb'
        bpy.ops.export_scene.gltf(filepath=str(out/filename),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
        bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(export)
        construction.append(dict(name=ob.name,file=filename,sha256=sha(out/filename),root=root['name'],native_root_basis_rows=root['basis_rows'],native_root_position=root['position'],
                                 kind=ob['kind'],world_bounds=[[min(p[k] for p in world) for k in range(3)],[max(p[k] for p in world) for k in range(3)]],native_geometry=object_geometry(ob)))
    for filename in ('lofts58b.py','build58b.py'):
        txt=bpy.data.texts.new(filename);txt.write((P/filename).read_text())
    bpy.ops.object.select_all(action='DESELECT');bank.select_set(True);bpy.context.view_layer.objects.active=bank
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'cloud_bank58b.blend'))
    after={name:sha(ROOT/name) for name in protected};assert after==protected
    (out/'protected-sources58b.json').write_text(json.dumps(dict(before=protected,after=after,unchanged=True),indent=2)+'\n')
    (out/'construction58b.json').write_text(json.dumps(dict(source_method=scene['source_method'],native_control_count=len(control_objects),voxel_size_m=26,quad_target=4800,
        native_controls_retained=True,rectangular_domain=False,heightfield=False,common_bottom_cap=False,coplanar_seam_caps=False,upper_A_geometry_retained_unaccepted=True,
        origin=ORIGIN,meshes=construction,source_sha256=sha(out/'cloud_bank58b.blend'),rendered=False,world_loaded=False,visual_acceptance=False,native_readback_pending=True),indent=2)+'\n')
    print('58B native loft union built; no render or world launch; fresh readback still required')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=P);parser.add_argument('--from-controls',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    build(args.out,args.from_controls)
