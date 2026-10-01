"""Native continuous density crown; replaces C's dominant planar shell entirely."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Euler,Vector
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
old_dirs=['cloud-sea52e','cloud-sea52f','cloud-sea52g','cloud-sea52h','cloud-sea52h-revision-b-plan','cloud-sea52h-revision-b','cloud-sea52h-revision-c']
protected=[p for folder in old_dirs for p in (P.parent/folder).rglob('*') if p.is_file()]
protected += [ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52f/Game52f.tscn',ROOT/'candidates/round40-exclusive-20260930/project/project.godot',ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={str(p):sha(p) for p in protected}
assert not(P/'cloud_sea52h_d.blend').exists(),'Use an independent revision instead of overwriting a built source'
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
with bpy.data.libraries.load(str(P.parent/'cloud-sea52f/variants/cloud_sea52f_variants.blend'),link=False) as (s,d):d.materials=['Cloud46 diffuse warm crown cool belly']
mat=d.materials[0]
ctrl=bpy.data.collections.new('Editable52hD_native_density_and_continuous_skin');scene.collection.children.link(ctrl)
finalcol=bpy.data.collections.new('CloudSea52hD_single_main');scene.collection.children.link(finalcol)
# Isolated isosurface dimensions specify intended mass hierarchy, not the final
# combined bounds. Positive compact density fields merge continuously in 3D.
spec=[
 ('main_wide_curved_volume',[-475,-365,155],[445,385,310],[7,-6,-11],2.0),
 ('medium_rear_broad_connection',[-255,-235,132],[280,245,245],[-9,13,31],1.8),
 ('small_front_low_connection',[-223,-450,101],[220,190,155],[11,-7,-26],1.7),
 ('main_front_left_short_rise',[-570,-505,175],[170,150,165],[-12,19,-36],1.5),
 ('main_offset_upper_crown',[-510,-355,302],[145,165,105],[17,-8,23],1.5),
 ('main_front_oblique_shoulder',[-360,-485,210],[155,115,140],[-22,14,51],1.4),
 ('main_rear_short_fold',[-440,-204,208],[155,140,130],[13,23,-58],1.45),
 ('medium_outer_unequal_shoulder',[-120,-212,170],[135,145,125],[-17,-12,68],1.4),
 ('small_outer_low_fold',[-145,-485,95],[95,130,90],[21,-14,-43],1.3),
]
mb=bpy.data.metaballs.new('52hD_editable_continuous_density');mb.resolution=9;mb.render_resolution=9;mb.threshold=.6
density=bpy.data.objects.new('CONTROL52hD_density',mb);ctrl.objects.link(density);mb.materials.append(mat);density.hide_render=True
rows=[]
for index,(role,center,dims,rot,stiffness) in enumerate(spec):
 e=mb.elements.new();e.type='ELLIPSOID';e.co=center;e.radius=100;e.stiffness=stiffness;e.use_negative=False;e.rotation=Euler([math.radians(x) for x in rot],'XYZ').to_quaternion()
 fraction=math.sqrt(1-(mb.threshold/stiffness)**(1/3))
 e.size_x,e.size_y,e.size_z=[n/(2*e.radius*fraction) for n in dims]
 density['element_%02d'%index]=role
 rows.append({'element_index':index,'role':role,'center_blender_m':center,'isolated_isosurface_dimensions_m':dims,'rotation_xyz_degrees':rot,'stiffness':stiffness,'radius':100,'size_xyz':[e.size_x,e.size_y,e.size_z],'positive_only':True})
density['edit_instruction']='Edit the nine native Metaball elements independently in Edit mode. Element role labels are stored on this object. The connected density skin replaces all C planar hull faces; no C mesh is used.'
# Evaluate a temporary copy with a distinct family name, avoiding interaction
# with the editable original's evaluation family.
work=bpy.data.objects.new('DWorkingSkin',mb.copy());finalcol.objects.link(work)
bpy.ops.object.select_all(action='DESELECT');work.select_set(True);bpy.context.view_layer.objects.active=work
bpy.ops.object.convert(target='MESH');work=bpy.context.object;work.name='CloudSea52hD_v0_main_crown'
lo=Vector([min(v.co[k] for v in work.data.vertices) for k in range(3)]);hi=Vector([max(v.co[k] for v in work.data.vertices) for k in range(3)])
# Keep a representative crown at the previous overall horizontal scale. This
# one uniform normalization preserves every direction and size ratio.
uniform=696.0/(hi.x-lo.x);center=(hi+lo)*.5;target=Vector((-362,-340.4,170))
for v in work.data.vertices:v.co=(v.co-center)*uniform+target
density.scale=(uniform,)*3;density.location=target-center*uniform
continuous=bpy.data.objects.new('CONTROL52hD_continuous_density_skin',work.data.copy());ctrl.objects.link(continuous);continuous.hide_render=True
bpy.ops.object.quadriflow_remesh(target_faces=1000,use_mesh_symmetry=False,use_preserve_sharp=False,use_preserve_boundary=True)
m=work.modifiers.new('Restrained isotropic facets on curved volume','TRIANGULATE');m.quad_method='BEAUTY';m.ngon_method='BEAUTY';bpy.ops.object.modifier_apply(modifier=m.name)
work.data.materials.clear();work.data.materials.append(mat)
for attr in list(work.data.color_attributes):work.data.color_attributes.remove(attr)
colors=work.data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
for f in work.data.polygons:
 f.use_smooth=False;f.material_index=0;z=sum(work.data.vertices[i].co.z for i in f.vertices)/len(f.vertices);v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
 for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
work['construction']='One continuous native nine-element positive density skin; no old planar shell, explicit intersecting boolean seams, negative pits, bevel or random noise';work['visual_acceptance']=False
ctrl.hide_viewport=True;ctrl.hide_render=True
bpy.ops.object.select_all(action='DESELECT');work.select_set(True);bpy.context.view_layer.objects.active=work
bpy.ops.export_scene.gltf(filepath=str(P/'cloud_sea_52h_d_main_v0.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52h_d.blend'))
after={str(p):sha(p) for p in protected};assert before==after
(P/'protected-sources52h-d.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2)+'\n')
(P/'construction52h-d.json').write_text(json.dumps({'native_density_elements':rows,'density_threshold':mb.threshold,'density_resolution_m':9,'uniform_normalization':uniform,'raw_bounds':[list(lo),list(hi)],'raw_center':list(center),'normalized_center':list(target),'editable_meta_object':density.name,'continuous_control_mesh':continuous.name,'native_quad_target':1000,'old_C_planes_used':False,'boolean_seams':False,'bevel':False,'negative_cutters':False,'random_noise':False,'global_smooth_modifier':False,'material':mat.name,'vertex_color_formula':'v=.76+.16*clamp((z+190)/460,0,1); linear=((v+.055)/1.055)**2.4','rendered':False,'world_modified':False,'visual_acceptance':False},indent=2)+'\n')
print('52H D: NATIVE NINE-ELEMENT DENSITY CROWN BUILT; NO RENDER/WORLD')
