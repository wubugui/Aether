from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
specs=[
 dict(name='South short convex shoulder',center=[-11.7,-20.2],outline=[[-17,-22],[-13,-24],[-8,-23],[-5.5,-20.5],[-8,-17],[-13,-16.8],[-17.8,-19]],mid_z=[5.6,5.5,5.9,6.8,7.9,7.6,6.5],roof_z=[6.9,6.7,7,7.8,8.1,8,7.4],roof_scale=.74,bottom_z=.7),
 dict(name='Southeast short offset knuckle',center=[3.2,-14.6],outline=[[-.2,-16.8],[2.1,-18.3],[6,-17.1],[8,-14.5],[5.7,-11.2],[1.8,-11.5],[-.5,-13.6]],mid_z=[4.8,5.2,5.9,6.4,7,6.7,5.7],roof_z=[6.1,6,6.5,7.2,7.5,7.4,6.8],roof_scale=.7,bottom_z=.8)]
for s in specs:
    s['vertices']=[[x,y,s['bottom_z']] for x,y in s['outline']]+[[x,y,z] for (x,y),z in zip(s['outline'],s['mid_z'])]+[[s['center'][0]+(x-s['center'][0])*s['roof_scale'],s['center'][1]+(y-s['center'][1])*s['roof_scale'],z] for (x,y),z in zip(s['outline'],s['roof_z'])]
p=R/'captures/island-31a-convex-shoulder-plan.json';assert not p.exists();p.write_text(json.dumps(dict(scope='31a two short broad convex solids united into30k main exterior. Separate editable operand scene retained. No loose rock ring, no long diagonal ramps. Current14tree positions, road and pad support to verify.',source='captures/lantern_island_study_30k/island_c.blend',components=specs),indent=2))
s=(R/'blender/model_lantern_island_30k.py').read_text().replace('30k','31a').replace("SRC=R/'captures/lantern_island_study_30d/island_c.blend'", "SRC=R/'captures/lantern_island_study_30k/island_c.blend'")
start=s.index('input_plan=');end=s.index('# Explicit editable final triangles',start)
s=s[:start]+'''input_plan=json.loads((R/'captures/island-31a-convex-shoulder-plan.json').read_text())
authoring_scene=bpy.data.scenes.new('31a editable short rock shoulders')
specs=input_plan['components'];operands=[]
for spec in specs:
    mesh=bpy.data.meshes.new(spec['name']+' authored beveled hull')
    bm=bmesh.new()
    for v in spec['vertices']:bm.verts.new(v)
    result=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    unused=[v for v in bm.verts if not v.link_faces]
    if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
    assert bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free()
    for mat in terrain.data.materials:mesh.materials.append(mat)
    for p in mesh.polygons:p.material_index=2
    obj=bpy.data.objects.new(spec['name'],mesh);bpy.context.collection.objects.link(obj)
    copy=obj.copy();copy.data=obj.data.copy();authoring_scene.collection.objects.link(copy)
    spec['actual_operand_geometry']=sig(obj);operands.append(obj)
bpy.data.libraries.write(str(OUT/'shoulder_operands.blend'),{authoring_scene},fake_user=True)
for obj in list(authoring_scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.scenes.remove(authoring_scene)
for obj in operands:
    bpy.ops.object.select_all(action='DESELECT');terrain.select_set(True);bpy.context.view_layer.objects.active=terrain
    mod=terrain.modifiers.new(obj.name+' connected shoulder union','BOOLEAN');mod.operation='UNION';mod.solver='MANIFOLD';mod.object=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
    print('United native short convex shoulder '+obj.name,flush=True);bpy.data.objects.remove(obj,do_unlink=True)
'''+s[end:]
s=s.replace("plan.update(boolean_solver='MANIFOLD',lower_floor_clamped_to_source=False,scope=input_plan['scope'],cutbacks=cutters,top_vertex_count=None,core_boundary_map=None,retained_source='30d local-cut welded exterior',faceted_input_plan=input_plan)", "plan.update(boolean_solver='MANIFOLD',scope=input_plan['scope'],additions=specs,addition_input_plan=input_plan,retained_source='30k broad-cut exterior with current lower eastern tree group')")
s=s.replace("sites=plan['sites'],cutbacks=cutters", "sites=plan['sites'],additions=specs")
p=R/'blender/model_lantern_island_31a.py';assert not p.exists();p.write_text(s)
for a,b in [('captures/check_island_30k.py','captures/check_island_31a.py'),('tools/render_lantern_island_30k_r1.py','tools/render_lantern_island_31a.py')]:
    p=R/b;assert not p.exists();p.write_text((R/a).read_text().replace('30k','31a').replace('lantern-island-31a-r1','lantern-island-31a'))
print('31a authored short convex operands and union builder prepared')
