"""Native source build/read/render entry. Only the bounded wrapper may execute it."""
import argparse,sys,os,json,time,traceback,math
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import telemetry62 as telemetry
if __name__=='__main__':
    early=sys.argv[sys.argv.index('--')+1:];mode=early[early.index('--mode')+1];view=early[early.index('--view')+1]if '--view' in early else None
    telemetry.initialize(Path(early[early.index('--out')+1]),mode+('-'+view if view else ''))
import bpy
from mathutils import Vector
import numpy as np
import contract62 as c
import rebuild62
import bulk62
_EMBED_DIR=None

def text(name,value):
    # The compact BINDINGS text remains byte-identical, but loading the file avoids
    # Text.write's pathological first-line character-insertion path.
    telemetry.emit('text.begin',name=name,utf8_bytes=len(value.encode()))
    path=_EMBED_DIR/name;path.write_text(value)
    t=bpy.data.texts.load(filepath=str(path),internal=True);t.name=name
    actual=t.as_string().encode();expected=value.encode()
    fields=dict(name=t.name,is_in_memory=t.is_in_memory,filepath=t.filepath,actual_utf8_bytes=len(actual),actual_sha256=c.hashlib.sha256(actual).hexdigest(),expected_sha256=c.hashlib.sha256(expected).hexdigest())
    c.write(_EMBED_DIR/(name+'.loaded-fields.json'),fields)
    if actual!=expected:(_EMBED_DIR/(name+'.unexpected-loaded-bytes')).write_bytes(actual)
    c.require(t.name==name and t.is_in_memory and t.filepath=='' and actual==expected,'Exact internal editable text load '+name)
    telemetry.emit('text.complete',name=name,sha256=c.sha(path))

def create_object(name,collection,kind='MESH'):
    data=bpy.data.meshes.new(name+'_mesh') if kind=='MESH' else None
    ob=bpy.data.objects.new(name,data);collection.objects.link(ob);return ob

def create_source(b):
    telemetry.emit('factory_reset.begin');bpy.ops.wm.read_factory_settings(use_empty=True);telemetry.emit('factory_reset.complete')
    scene=bpy.context.scene
    for key,value in dict(source_version=c.VERSION,origin_godot_json=json.dumps(c.ORIGIN),world_integration_allowed=False,source_material_study_only=True,weather_acceptance=False,visual_acceptance=False,auto_rebuild=False).items():scene[key]=value
    control_col=bpy.data.collections.new('R62_SHARED_CONTROLS');scene.collection.children.link(control_col)
    terrain_col=bpy.data.collections.new('R62_DERIVED_FOUR_TILES');scene.collection.children.link(terrain_col)
    hidden_col=bpy.data.collections.new('R62_SHARED_EVALUATED_SURFACE');scene.collection.children.link(hidden_col)
    for m in c.MATERIALS:
        material=bpy.data.materials.new(m['name']);material.use_nodes=True;material.diffuse_color=m['color']
        bsdf=material.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=m['color'];bsdf.inputs['Roughness'].default_value=m['roughness'];bsdf.inputs['Metallic'].default_value=0
        material['scope']='Editable source material study; not world material/weather acceptance'
    text('BINDINGS62.json',json.dumps(b,separators=(',',':'),ensure_ascii=False));text('CONTRACT62.py',(c.HERE/'contract62.py').read_text());text('REBUILD62.py',(c.HERE/'rebuild62.py').read_text());text('README62.txt',(c.HERE/'SOURCE_README.txt').read_text());text('BULK62.py',(c.HERE/'bulk62.py').read_text())
    control=create_object('R62_MASTER_CONTROL',control_col)
    control.data.from_pydata(c.f32(c.local([[x['xz'][0],x['target_y'],x['xz'][1]]for x in b['controls']])).tolist(),[],b['control_faces_blender']);control.data.update()
    control.hide_render=True;control.display_type='WIRE';control['edit_contract']='Change relief vertex Z or semantic Empty Z, then explicitly run REBUILD62.py. Boundary and X/Y fixed.'
    for i,row in enumerate(b['controls'][12:],12):
        handle=create_object('R62_HANDLE_'+row['name'],control_col,'EMPTY');handle.location=control.data.vertices[i].co;handle.empty_display_type='SPHERE';handle.empty_display_size=12
        handle.lock_location=(True,True,False);handle.lock_rotation=(True,True,True);handle.lock_scale=(True,True,True);handle.hide_render=True;handle['control_index']=i;handle['last_synced_height']=float(handle.location.z)
    master=create_object('R62_MASTER_EVALUATED',hidden_col);master.hide_render=True;master.hide_viewport=True
    for tile in b['tiles']:
        ob=create_object('R62_'+tile['name'],terrain_col);ob['derived_from']='R62_MASTER_EVALUATED';ob['source_resource']=tile['source_resource'];ob['original_mapping_scope']=b['mapping_scope']
    rebuild62.rebuild(initial=True,progress=telemetry.emit)
    inspection=bpy.data.collections.new('R62_SOURCE_INSPECTION');scene.collection.children.link(inspection)
    for view in b['views']:
        data=bpy.data.cameras.new('R62_CAMERA_'+view['name']);ob=bpy.data.objects.new(data.name,data);inspection.objects.link(ob)
        eye=c.local([view['eye']])[0];target=c.local([view['target']])[0];ob.location=eye;ob.rotation_euler=(Vector(target)-Vector(eye)).to_track_quat('-Z','Y').to_euler()
        data.type='PERSP';data.sensor_fit='VERTICAL';data.sensor_height=32;data.lens=16/math.tan(math.radians(view['fov']/2));data.clip_start=.1;data.clip_end=10000
        ob['source_view_json']=json.dumps(view,sort_keys=True)
    world=bpy.data.worlds.new('R62 neutral source world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.19,.23,.29,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65;scene.world=world
    light=bpy.data.lights.new('R62 neutral key','SUN');light.energy=2.4;light.angle=math.radians(12);ob=bpy.data.objects.new(light.name,light);inspection.objects.link(ob);ob.rotation_euler=(math.radians(26),math.radians(-32),math.radians(-28))
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2
    scene.render.resolution_x=1179;scene.render.resolution_y=664;scene.render.resolution_percentage=100;scene.render.pixel_aspect_x=1;scene.render.pixel_aspect_y=1
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=False;scene.view_settings.view_transform='AgX';scene.camera=bpy.data.objects['R62_CAMERA_1131'];scene.render.use_file_extension=True
    bpy.context.view_layer.update()

def capture(b):
    terrain=[]
    for name in ['R62_MASTER_EVALUATED']+['R62_'+x for x in c.TILES]:
        ob=bpy.data.objects[name];mesh=ob.data
        telemetry.emit('capture.mesh.begin',mesh=name,vertices=len(mesh.vertices),triangles=len(mesh.polygons))
        weights=np.zeros((len(mesh.vertices),27),np.float32)
        # Nested deform membership has no flat RNA foreach API. Retain every
        # actual native membership read; never substitute recipe weights.
        for v in mesh.vertices:
            for g in v.groups:weights[v.index,g.group]=g.weight
        attrs={};schemas={}
        for name2,kind,domain in bulk62.SCHEMAS:
            att=mesh.attributes[name2];prop,dtype,components=bulk62.KINDS[kind]
            schemas[name2]=dict(data_type=att.data_type,domain=att.domain)
            attrs[name2]=bulk62.read_collection(att.data,prop,dtype,components);del att
        loop_total=bulk62.read_collection(mesh.polygons,'loop_total','<i4');loop_start=bulk62.read_collection(mesh.polygons,'loop_start','<i4')
        loop_indices=bulk62.read_collection(mesh.loops,'vertex_index','<i4')
        faces=[loop_indices[start:start+count]for start,count in zip(loop_start,loop_total)]
        terrain.append(dict(name=name,source_properties={key:ob[key]for key in ('derived_from','source_resource','original_mapping_scope')if key in ob},vertices=bulk62.read_collection(mesh.vertices,'co','<f4',3),faces=faces,material_indices=bulk62.read_collection(mesh.polygons,'material_index','<i4'),flat=[not flag for flag in bulk62.read_collection(mesh.polygons,'use_smooth','?')],material_slots=[m.name for m in mesh.materials],matrix_world=[list(x)for x in ob.matrix_world],attributes=attrs,attribute_schemas=schemas,polygon_loop_counts=loop_total,polygon_loop_starts=loop_start,loop_vertex_indices=loop_indices,group_names=[g.name for g in ob.vertex_groups],weights=weights.tolist(),polygon_normals=bulk62.read_collection(mesh.polygons,'normal','<f4',3),corner_normals=bulk62.read_collection(mesh.corner_normals,'vector','<f4',3)))
        telemetry.emit('capture.mesh.complete',mesh=name)
    handles=[]
    for row in b['controls'][12:]:
        ob=bpy.data.objects['R62_HANDLE_'+row['name']];handles.append(dict(name=row['name'],location=list(ob.location),lock_location=list(ob.lock_location),lock_rotation=list(ob.lock_rotation),lock_scale=list(ob.lock_scale)))
    mats=[]
    for spec in c.MATERIALS:
        m=bpy.data.materials[spec['name']];p=m.node_tree.nodes.get('Principled BSDF');mats.append(dict(name=m.name,use_nodes=m.use_nodes,base_color=list(p.inputs['Base Color'].default_value),roughness=p.inputs['Roughness'].default_value,metallic=p.inputs['Metallic'].default_value))
    cameras=[]
    for view in b['views']:
        ob=bpy.data.objects['R62_CAMERA_'+view['name']];cameras.append(dict(name=view['name'],matrix_world=[list(x)for x in ob.matrix_world],type=ob.data.type,sensor_fit=ob.data.sensor_fit,sensor_height=ob.data.sensor_height,lens=ob.data.lens,angle_y=ob.data.angle_y,clip_start=ob.data.clip_start,clip_end=ob.data.clip_end,declared_view=json.loads(ob['source_view_json'])))
    control=bpy.data.objects['R62_MASTER_CONTROL'];scene=bpy.context.scene
    return dict(version=c.VERSION,blender_version=list(bpy.app.version),pid=os.getpid(),cpu_affinity=sorted(os.sched_getaffinity(0)),terrain=terrain,control_matrix_world=[list(x)for x in control.matrix_world],control_vertices=[list(v.co)for v in control.data.vertices],control_faces=[list(p.vertices)for p in control.data.polygons],semantic_handles=handles,embedded_binding_sha256=c.hashlib.sha256(bpy.data.texts['BINDINGS62.json'].as_string().encode()).hexdigest(),embedded_text_names=sorted([t.name for t in bpy.data.texts],key=lambda x:c.TEXTS.index(x) if x in c.TEXTS else 999),embedded_text_internal={t.name:dict(is_in_memory=t.is_in_memory,filepath=t.filepath)for t in bpy.data.texts},embedded_text_sha256={t.name:c.hashlib.sha256(t.as_string().encode()).hexdigest()for t in bpy.data.texts},materials=mats,cameras=cameras,object_names=sorted(bpy.data.objects.keys()),mesh_names=sorted(bpy.data.meshes.keys()),scene_flags={key:scene[key]for key in ['source_version','origin_godot_json','world_integration_allowed','source_material_study_only','weather_acceptance','visual_acceptance','auto_rebuild','edited_after_frozen_build']},render_settings=dict(engine=scene.render.engine,resolution=[scene.render.resolution_x,scene.render.resolution_y],percentage=scene.render.resolution_percentage,pixel_aspect=[scene.render.pixel_aspect_x,scene.render.pixel_aspect_y],threads=scene.render.threads,samples=scene.cycles.samples,use_denoising=scene.cycles.use_denoising),external_libraries=[x.filepath for x in bpy.data.libraries],image_dependencies=[x.filepath for x in bpy.data.images if x.source=='FILE'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['build','verify','render'],required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--view',choices=['1131','1347','side','back']);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);a.out.mkdir(parents=True,exist_ok=True)
    label=a.mode+('-'+a.view if a.view else '');telemetry.emit('arguments_checked')
    global _EMBED_DIR
    _EMBED_DIR=a.out/'embedded-text-inputs';_EMBED_DIR.mkdir(exist_ok=True)
    report=dict(version=c.VERSION,mode=a.mode,pid=os.getpid(),passed=False,state='started',source_saved=False,images=0,world_loaded=False,world_integration_allowed=False,visual_acceptance=False)
    try:
        telemetry.emit('binding.read.begin');b=c.read(c.BINDING_PATH);telemetry.emit('binding.read.complete');telemetry.emit('binding.validation.begin');c.check_binding(b);telemetry.emit('binding.validation.complete')
        if a.mode=='build':c.require(not c.SOURCE.exists(),'Never overwrite source');create_source(b)
        else:
            telemetry.emit('fresh_open.begin');bpy.ops.wm.open_mainfile(filepath=str(c.SOURCE),load_ui=False,use_scripts=False);telemetry.emit('fresh_open.complete')
        telemetry.emit('capture.begin');raw=capture(b);telemetry.emit('capture.complete');rawpath=a.out/(a.mode+('-'+a.view if a.view else '')+'-raw.json');c.write(rawpath,raw);telemetry.emit('raw.persisted',sha256=c.sha(rawpath),bytes=rawpath.stat().st_size)
        report['raw_sha256']=c.sha(rawpath);report['raw_path']=str(rawpath)
        # Preserve actual raw before any validation, including failure evidence.
        c.write(a.out/(a.mode+('-'+a.view if a.view else '')+'-result.json'),report)
        telemetry.emit('validation.begin');report['validation']=c.validate_raw(raw,b);telemetry.emit('validation.complete')
        if a.mode=='build':
            telemetry.emit('save.begin');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(c.SOURCE),check_existing=True);report['source_saved']=True;telemetry.emit('save.complete',source_sha256=c.sha(c.SOURCE))
        if a.mode=='render':
            c.require(a.view is not None,'One named source view');scene=bpy.context.scene;scene.camera=bpy.data.objects['R62_CAMERA_'+a.view]
            png=a.out/('62-'+a.view+'.png');scene.render.filepath=str(png);telemetry.emit('render.begin',view=a.view);bpy.ops.render.render(write_still=True);telemetry.emit('render.complete',view=a.view);report.update(images=1,image_sha256=c.sha(png),image_path=str(png),source_geometry_study_only=True,reference_weather_acceptance=False)
        report.update(passed=True,state='completed',source_sha256=c.sha(c.SOURCE),source_bytes=c.SOURCE.stat().st_size)
    except BaseException:report.update(state='failed',error=traceback.format_exc());raise
    finally:
        telemetry.emit('native_terminal',passed=report['passed'],state=report['state']);report['native_stage_timing']=telemetry.report();report['recovery_version']=c.RECOVERY_VERSION
        c.write(a.out/(a.mode+('-'+a.view if a.view else '')+'-result.json'),report)
if __name__=='__main__':main()
