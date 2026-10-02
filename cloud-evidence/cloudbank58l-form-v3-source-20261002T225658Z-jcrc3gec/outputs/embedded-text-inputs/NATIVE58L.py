"""Inert source adapter; bounded run58l alone admits a native process.

No old build-v1 helper is imported or called. Explicit EDIT58L rebuild has no
handler, driver, auto-run, save, export or render side effect.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,resource,sys,time,traceback
from array import array
from pathlib import Path
from types import SimpleNamespace
sys.dont_write_bytecode=True
if '_EMBEDDED_SUPPORT' in globals(): s=SimpleNamespace(**_EMBEDDED_SUPPORT)
else:
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    import native_support58l as s
_TELEMETRY=None
_START=time.monotonic()

def geometry():
    if '_EMBEDDED_GEOMETRY' in globals():return SimpleNamespace(**_EMBEDDED_GEOMETRY)
    import geometry58l
    return geometry58l

def write(path,value,exclusive=False):
    with Path(path).open('xb' if exclusive else 'wb') as f:f.write(s.json_bytes(value));f.flush();os.fsync(f.fileno())

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def emit(stage,**details):
    u=resource.getrusage(resource.RUSAGE_SELF)
    row=dict(stage=stage,pid=os.getpid(),elapsed_seconds=time.monotonic()-_START,user_seconds=u.ru_utime,system_seconds=u.ru_stime,peak_rss_kib=u.ru_maxrss,**details)
    print('L58_SOURCE_STAGE '+json.dumps(row,allow_nan=False),flush=True)
    if _TELEMETRY:
        out,label=_TELEMETRY
        with (out/(label+'-events.jsonl')).open('ab') as f:f.write(s.json_bytes(row));f.flush();os.fsync(f.fileno())
        p=out/(label+'-progress.json');tmp=p.with_suffix('.json.tmp');write(tmp,row);tmp.replace(p)
    return row

def read_collection(items,key,kind='f',width=1):
    a=array(kind,[0])*(len(items)*width);items.foreach_get(key,a);a=a.tolist()
    return a if width==1 else [a[i:i+width] for i in range(0,len(a),width)]

def write_collection(items,key,values,kind='f',width=1):
    a=values if width==1 else [v for row in values for v in row]
    s.require(len(a)==len(items)*width,'RNA write size');items.foreach_set(key,array(kind,a))

def rebuild_from_controls():
    """Explicit transactional calculation; rejected values never write mesh/attrs."""
    import bpy
    c=json.loads(bpy.data.texts['CANDIDATE58L.json'].as_string());g=geometry()
    mesh=bpy.data.objects[s.MASTER].data
    s.require([list(f.vertices) for f in mesh.polygons]==c['faces'],'Topology edits need a new author candidate')
    current=read_collection(mesh.vertices,'co','f',3)
    base=read_collection(mesh.attributes[s.BASE].data,'vector','f',3)
    last=read_collection(mesh.attributes[s.LAST].data,'vector','f',3)
    handles=[bpy.data.objects[s.CONTROL_PREFIX+r['id']] for r in c['controls']]
    vals=[float(h['value']) for h in handles]
    secondary={r['id']+'.'+p['id']:float(h[p['id']]) for r,h in zip(c['controls'],handles) for p in r.get('secondary_parameters',[])}
    all_values=dict(zip([r['id'] for r in c['controls']],vals));all_values.update(secondary)
    authored,points=s.edit(c,current,base,last,vals,secondary)
    # These checks precede all writes; no range clamp or failed-state fallback.
    verdict=g.validate_evaluated(c,[s.world(p) for p in points],all_values)
    write_collection(mesh.attributes[s.BASE].data,'vector',authored,'f',3)
    write_collection(mesh.attributes[s.LAST].data,'vector',points,'f',3)
    write_collection(mesh.vertices,'co',points,'f',3);mesh.update()
    for h,v,r in zip(handles,vals,c['controls']):
        h['last_applied_value']=v
        for p in r.get('secondary_parameters',[]):h['last_applied_'+p['id']]=float(h[p['id']])
    baseline=[s.local(p) for p in c['vertices_world']]
    bpy.context.scene['edited_after_frozen_build']=(points!=baseline or authored!=baseline)
    bpy.context.view_layer.update()
    return dict(passed=True,geometry=verdict,source_saved=False,rendered=False,exported=False)

def internal_text(name,data,directory,original_filepath=None):
    import bpy
    path=directory/name
    with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    t=bpy.data.texts.load(filepath=str(path),internal=True);t.name=name;t.use_module=False
    if original_filepath:t['original_filepath']=str(original_filepath)
    actual=t.as_string().encode();write(directory/(name+'.readback.json'),dict(name=t.name,is_in_memory=t.is_in_memory,filepath=t.filepath,bytes=len(actual),sha256=s.digest(actual),expected_sha256=s.digest(data)))
    if actual!=data:(directory/(name+'.unexpected-readback')).write_bytes(actual)
    s.require(t.name==name and t.is_in_memory and not t.filepath and actual==data,'Exact internal reconstruction Text '+name)

def create_shared_groups(master,export,c):
    """The two objects share ONE mesh/group table; allocate seven groups once."""
    s.require(master.data is export.data,'One actual shared mesh before groups')
    s.require(not list(master.vertex_groups) and not list(export.vertex_groups),'No pre-existing shared groups')
    groups=s.groups(c)
    s.require(len(groups)==7,'Exactly seven shared control groups')
    for name,weights in groups:
        group=master.vertex_groups.new(name=name);buckets={}
        for i,w in enumerate(weights):
            if w:buckets.setdefault(s.f32(w),[]).append(i)
        for w,indices in buckets.items():group.add(indices,w,'REPLACE')
    names=[name for name,_ in groups]
    s.require([x.name for x in master.vertex_groups]==[x.name for x in export.vertex_groups]==names,'Actual shared seven-group identities after one allocation')

def create_source(c,b,g,out):
    import bpy
    from mathutils import Matrix
    emit('factory_reset.begin');bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.use_scripts_auto_execute=False;bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene
    for key in s.FLAGS:scene[key]=False
    for key,value in dict(source_version=g.VERSION,anchor_world_json='[3958, 0, 3667]',scale_one=True,edited_after_frozen_build=False,source_diagnostic_only=True,acceptance_mode=s.DIAGNOSTIC_MODE,historical_default_corner_geometry_passed=False).items():scene[key]=value
    cols={}
    for name in ('L58_SOURCE','L58_SEMANTIC_CONTROLS','L58_FIXED_INSPECTION'):
        col=bpy.data.collections.new(name);scene.collection.children.link(col);cols[name]=col
    folder=out/'embedded-text-inputs';folder.mkdir()
    for name,data in s.expected_texts(g.HERE,c,b).items():
        emit('text.begin',name=name,bytes=len(data));internal_text(name,data,folder);emit('text.complete',name=name)
    points=[s.local(p) for p in c['vertices_world']];mesh=bpy.data.meshes.new(s.MESH);mesh.from_pydata(points,[],c['faces']);mesh.update()
    master=bpy.data.objects.new(s.MASTER,mesh);cols['L58_SOURCE'].objects.link(master)
    export=bpy.data.objects.new(s.EXPORT,mesh);cols['L58_SOURCE'].objects.link(export)
    export.hide_render=True;export.hide_viewport=True;export.hide_select=True;export.hide_set(True)
    master['edit_contract']='Sole editable master: direct vertex heights and seven scalar controls; explicitly Run EDIT58L.py'
    export['derived_from']=s.MASTER;export['export_contract']='Hidden derived view of the SAME canonical mesh; no separate authoring or export has run'
    for ob in (master,export):ob.lock_location=ob.lock_rotation=ob.lock_scale=(True,True,True)
    m=bpy.data.materials.new(s.MATERIAL);m.use_nodes=True;spec=b['material'];m.diffuse_color=spec['linear_rgba'];m.use_backface_culling=spec['backface_culling']
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=spec['linear_rgba'];p.inputs['Roughness'].default_value=spec['roughness'];p.inputs['Metallic'].default_value=spec['metallic'];p.inputs['Emission Color'].default_value=(0.,0.,0.,1.);p.inputs['Emission Strength'].default_value=0.;mesh.materials.append(m)
    for f in mesh.polygons:f.use_smooth=False;f.material_index=0
    create_shared_groups(master,export,c)
    # Allocate every RNA layer before resolving handles (allocation invalidates handles).
    for name,kind,domain in s.schemas(c):mesh.attributes.new(name=name,type=kind,domain=domain)
    for name in (s.BASE,s.LAST):write_collection(mesh.attributes[name].data,'vector',points,'f',3)
    write_collection(mesh.attributes[s.INDEX].data,'value',list(range(len(points))),'i')
    write_collection(mesh.attributes[s.FACE].data,'value',list(range(len(c['faces']))),'i')
    for r in c['controls']:
        write_collection(mesh.attributes['l58_disp_'+r['id']].data,'vector',[s.vector(p) for p in r['displacements_world']],'f',3)
        h=bpy.data.objects.new(s.CONTROL_PREFIX+r['id'],None);cols['L58_SEMANTIC_CONTROLS'].objects.link(h)
        h.location=s.local(r['position_world']);h.empty_display_type='SPHERE';h.empty_display_size=18;h.hide_render=True;h.lock_location=h.lock_rotation=h.lock_scale=(True,True,True)
        for key in ('id','semantic','units','default','min','max'):h[key]=r[key]
        h['value']=float(r['default']);h['last_applied_value']=float(r['default'])
        for par in r.get('secondary_parameters',[]):
            write_collection(mesh.attributes['l58_disp_'+r['id']+'_'+par['id']].data,'vector',[s.vector(p) for p in par['displacements_world']],'f',3)
            h[par['id']]=float(par['default']);h['last_applied_'+par['id']]=float(par['default'])
            for key in ('default','min','max','semantic'):h[par['id']+'_'+key]=par[key]
            h.id_properties_ui(par['id']).update(min=par['min'],max=par['max'],soft_min=par['min'],soft_max=par['max'],description=par['semantic'])
        h.id_properties_ui('value').update(min=r['min'],max=r['max'],soft_min=r['min'],soft_max=r['max'],description=r['semantic']+' ['+r['units']+']')
    for r in b['world_cameras']:
        data=bpy.data.cameras.new(s.CAMERA_PREFIX+r['name']);ob=bpy.data.objects.new(data.name,data);cols['L58_FIXED_INSPECTION'].objects.link(ob)
        ob.matrix_world=Matrix(s.camera_matrix(r));data.type='PERSP';data.sensor_fit='VERTICAL';data.sensor_height=32.;data.lens=16.*s.projection(r)[1][1];data.clip_start=r['near'];data.clip_end=r['far']
        ob['declared_transform_hex']=r['camera_transform'];ob['declared_projection_hex']=r['camera_projection']
    lit=b['source_inspection_lighting'];w=bpy.data.worlds.new('L58_K_SOURCE_INSPECTION');w.use_nodes=True;bg=w.node_tree.nodes['Background'];bg.inputs['Color'].default_value=lit['world_linear_rgba'];bg.inputs['Strength'].default_value=lit['world_strength'];scene.world=w
    light=bpy.data.lights.new('L58_K_FIXED_SUN','SUN');light.energy=lit['sun_energy'];light.angle=lit['sun_angle_radians'];ob=bpy.data.objects.new(light.name,light);cols['L58_FIXED_INSPECTION'].objects.link(ob);ob.rotation_euler=lit['sun_source_rotation_xyz_radians']
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2
    scene.render.resolution_x=1179;scene.render.resolution_y=664;scene.render.resolution_percentage=100;scene.render.pixel_aspect_x,scene.render.pixel_aspect_y=s.calibrated_pixel_aspect(b);scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8';scene.render.film_transparent=False;scene.render.filepath=''
    scene.view_settings.view_transform='AgX';scene.view_settings.look='None';scene.view_settings.exposure=0.;scene.view_settings.gamma=1.;scene.use_nodes=False;scene.render.use_compositing=False;scene.render.use_sequencer=False;scene.camera=bpy.data.objects[s.CAMERA_PREFIX+b['world_cameras'][0]['name']]
    bpy.context.view_layer.objects.active=master;master.select_set(True);bpy.context.view_layer.update();emit('create.complete',vertices=len(points),triangles=len(c['faces']))

def capture(c,g):
    import bpy
    scene=bpy.context.scene;master=bpy.data.objects[s.MASTER];mesh=master.data;names=[r.name for r in master.vertex_groups];weights=[];memberships=[]
    for v in mesh.vertices:
        row=[0.]*len(names);members=[]
        for item in v.groups:row[item.group]=item.weight;members.append([item.group,item.weight])
        weights.append(row);memberships.append(sorted(members))
    attrs={}
    for name,kind,domain in s.schemas(c):
        att=mesh.attributes[name];attrs[name]=dict(data_type=att.data_type,domain=att.domain,values=read_collection(att.data,'vector' if kind=='FLOAT_VECTOR' else 'value','f' if kind=='FLOAT_VECTOR' else 'i',3 if kind=='FLOAT_VECTOR' else 1))
    objects=[]
    for ob in sorted(bpy.data.objects,key=lambda o:o.name):
        objects.append(dict(name=ob.name,type=ob.type,matrix_world=[list(r) for r in ob.matrix_world],parent=ob.parent.name if ob.parent else None,modifiers=[m.type for m in ob.modifiers],constraints=[x.type for x in ob.constraints],driver_count=len(ob.animation_data.drivers) if ob.animation_data else 0,hide_render=ob.hide_render,hide_viewport=ob.hide_viewport,hide_select=ob.hide_select,hidden=ob.hide_get(),mesh_name=ob.data.name if ob.type=='MESH' else None,vertex_group_names=[x.name for x in ob.vertex_groups]))
    controls=[]
    for r in c['controls']:
        h=bpy.data.objects[s.CONTROL_PREFIX+r['id']];controls.append(dict(secondary_parameters=[dict(id=p['id'],default=h[p['id']+'_default'],min=h[p['id']+'_min'],max=h[p['id']+'_max'],semantic=h[p['id']+'_semantic'],value=float(h[p['id']]),last_applied_value=float(h['last_applied_'+p['id']])) for p in r.get('secondary_parameters',[])],name=h.name,location=list(h.location),lock_location=list(h.lock_location),lock_rotation=list(h.lock_rotation),lock_scale=list(h.lock_scale),**{k:h[k] for k in ('id','value','default','min','max','semantic','units','last_applied_value')}))
    mat=bpy.data.materials[s.MATERIAL];p=mat.node_tree.nodes.get('Principled BSDF')
    material=dict(name=mat.name,use_nodes=mat.use_nodes,base_color_linear_rgba=list(p.inputs['Base Color'].default_value),roughness=float(p.inputs['Roughness'].default_value),metallic=float(p.inputs['Metallic'].default_value),backface_culling=mat.use_backface_culling,node_types=sorted(x.bl_idname for x in mat.node_tree.nodes),links=sorted([x.from_node.bl_idname,x.from_socket.name,x.to_node.bl_idname,x.to_socket.name] for x in mat.node_tree.links),emission_color=list(p.inputs['Emission Color'].default_value),emission_strength=float(p.inputs['Emission Strength'].default_value))
    cameras=[];graph=bpy.context.evaluated_depsgraph_get();sampling=s.render_projection_args(scene.render)
    for ob in sorted((x for x in bpy.data.objects if x.type=='CAMERA'),key=lambda o:o.name):
        d=ob.data;cameras.append(dict(name=ob.name.removeprefix(s.CAMERA_PREFIX),matrix_world=[list(r) for r in ob.matrix_world],projection_matrix=[list(r) for r in ob.calc_matrix_camera(graph,**sampling)],projection_sampling=sampling,declared_transform_hex=ob['declared_transform_hex'],declared_projection_hex=ob['declared_projection_hex'],type=d.type,sensor_fit=d.sensor_fit,sensor_height=d.sensor_height,lens=d.lens,clip_start=d.clip_start,clip_end=d.clip_end))
    texts=[]
    for t in sorted(bpy.data.texts,key=lambda t:t.name):
        data=t.as_string().encode();texts.append(dict(name=t.name,sha256=s.digest(data),bytes=len(data),is_in_memory=t.is_in_memory,filepath=t.filepath,use_module=t.use_module))
    bg=scene.world.node_tree.nodes['Background'];sun=bpy.data.objects['L58_K_FIXED_SUN']
    return dict(version=g.VERSION,blender_version=list(bpy.app.version),pid=os.getpid(),cpu_affinity=sorted(os.sched_getaffinity(0)),opened_filepath=bpy.data.filepath,
      mesh=dict(name=mesh.name,vertices=read_collection(mesh.vertices,'co','f',3),faces=[list(f.vertices) for f in mesh.polygons],group_names=names,weights=weights,memberships=memberships,attributes=attrs,polygon_normals=read_collection(mesh.polygons,'normal','f',3),corner_normals=read_collection(mesh.corner_normals,'vector','f',3),polygon_loop_counts=read_collection(mesh.polygons,'loop_total','i'),polygon_loop_starts=read_collection(mesh.polygons,'loop_start','i'),loop_vertex_indices=read_collection(mesh.loops,'vertex_index','i'),flat=[not x for x in read_collection(mesh.polygons,'use_smooth','b')],material_indices=read_collection(mesh.polygons,'material_index','i'),material_slots=[m.name for m in mesh.materials]),
      objects=objects,controls=controls,material=material,cameras=cameras,texts=texts,canonical_mesh_shared=(master.data is bpy.data.objects[s.EXPORT].data),mesh_names=sorted(bpy.data.meshes.keys()),material_names=sorted(bpy.data.materials.keys()),scene_flags={k:scene[k] for k in s.FLAGS+('source_version','anchor_world_json','scale_one','edited_after_frozen_build','source_diagnostic_only','acceptance_mode','historical_default_corner_geometry_passed')},
      settings=dict(render_filepath=scene.render.filepath,engine=scene.render.engine,device=scene.cycles.device,samples=scene.cycles.samples,denoising=scene.cycles.use_denoising,threads_mode=scene.render.threads_mode,threads=scene.render.threads,resolution=[scene.render.resolution_x,scene.render.resolution_y],percentage=scene.render.resolution_percentage,pixel_aspect=[scene.render.pixel_aspect_x,scene.render.pixel_aspect_y],view_transform=scene.view_settings.view_transform,look=scene.view_settings.look,exposure=scene.view_settings.exposure,gamma=scene.view_settings.gamma,use_nodes=scene.use_nodes,use_compositing=scene.render.use_compositing,use_sequencer=scene.render.use_sequencer,transparent=scene.render.film_transparent,active_camera=scene.camera.name),
      lighting=dict(world_color=list(bg.inputs['Color'].default_value),world_strength=float(bg.inputs['Strength'].default_value),sun_type=sun.data.type,sun_energy=sun.data.energy,sun_angle=sun.data.angle,sun_rotation=list(sun.rotation_euler)),external_libraries=[x.filepath for x in bpy.data.libraries],images=[dict(name=x.name,source=x.source,type=x.type,filepath=x.filepath) for x in bpy.data.images],autoexec_enabled=bpy.context.preferences.filepaths.use_scripts_auto_execute)

def exercise(c,b,g,baseline,out,label):
    import bpy
    reports=[];expected=s.expected_texts(g.HERE,c,b)
    specs=[(r,'value',r) for r in c['controls']]+[(r,p['id'],p) for r in c['controls'] for p in r.get('secondary_parameters',[])]
    for i,(r,field,spec) in enumerate(specs):
        h=bpy.data.objects[s.CONTROL_PREFIX+r['id']];v=float(h[field]);target=float(spec['exercise_value']);s.require(target!=v,'Nonzero explicitly validated control exercise')
        emit('control.begin',control=r['id'],field=field,value=target);h[field]=target;verdict=rebuild_from_controls();moved=capture(c,g);path=out/(label+'-control-'+str(i)+'-moved.json');write(path,moved,True)
        moved_validation=s.validate_capture(moved,c,b,expected);s.require(moved['mesh']['vertices']!=baseline['mesh']['vertices'],'Actual float32 control response')
        h[field]=v;rebuild_from_controls();restored=capture(c,g);rp=out/(label+'-control-'+str(i)+'-restored.json');write(rp,restored,True);s.require(s.identity(restored)==s.identity(baseline),'Exact full native identity restoration')
        reports.append(dict(id=r['id'],field=field,value=target,moved_path=str(path),moved_sha256=sha(path),restored_path=str(rp),restored_sha256=sha(rp),geometry=verdict['geometry'],exact_identity_restored=True,moved_validation=moved_validation,restored_validation=s.validate_capture(restored,c,b,expected)));write(out/(label+'-exercise.json'),reports);emit('control.complete',control=r['id'])
    probe=c['manual_edit_probe'];index=probe['vertex_index'];delta=probe['delta_local'];mesh=bpy.data.objects[s.MASTER].data
    original=[list(v.co) for v in mesh.vertices];mesh.vertices[index].co=[s.f32(a+d) for a,d in zip(original[index],delta)];mesh.update();verdict=rebuild_from_controls();manual=capture(c,g);mp=out/(label+'-manual.json');write(mp,manual,True)
    base=manual['mesh']['attributes'][s.BASE]['values'];s.require(base!=baseline['mesh']['vertices'],'Genuine manual edit');manual_validation=s.validate_capture(manual,c,b,expected,manual_base=base)
    r=c['controls'][0];h=bpy.data.objects[s.CONTROL_PREFIX+r['id']];h['value']=r['exercise_value'];rebuild_from_controls();combined=capture(c,g);cp=out/(label+'-manual-control.json');write(cp,combined,True);combined_validation=s.validate_capture(combined,c,b,expected,manual_base=base)
    h['value']=r['default'];rebuild_from_controls();manual_restored=capture(c,g);mrp=out/(label+'-manual-control-restored.json');write(mrp,manual_restored,True);s.require(s.identity(manual_restored)==s.identity(manual),'Manual offsets survive scalar exercise/restoration')
    # Undo the deliberate manual probe through the same explicit edit path.
    write_collection(mesh.vertices,'co',original,'f',3);mesh.update();rebuild_from_controls();restored=capture(c,g);rp=out/(label+'-manual-baseline-restored.json');write(rp,restored,True);s.require(s.identity(restored)==s.identity(baseline),'Manual exercise restored exact baseline identity')
    reports.append(dict(id='manual_edit',vertex_index=index,delta_local=delta,manual_path=str(mp),manual_sha256=sha(mp),combined_path=str(cp),combined_sha256=sha(cp),manual_restored_path=str(mrp),manual_restored_sha256=sha(mrp),restored_path=str(rp),restored_sha256=sha(rp),geometry=verdict['geometry'],exact_identity_restored=True,manual_validation=manual_validation,combined_validation=combined_validation,manual_restored_validation=s.validate_capture(manual_restored,c,b,expected,manual_base=base),restored_validation=s.validate_capture(restored,c,b,expected)));write(out/(label+'-exercise.json'),reports)
    return reports

def main(arguments=None):
    args=arguments if arguments is not None else (sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['build','verify','render']);ap.add_argument('--view');ap.add_argument('--out',type=Path);ap.add_argument('--admission',type=Path);a=ap.parse_args(args)
    if a.mode is None:print('No-op: explicit one-shot wrapper admission required; no engine import or action.');return 0
    import runtime58l
    runtime58l.runtime(native_process=True)
    s.require(a.mode in ('build','verify'),'Source-only admission; retained original render branch is unreachable')
    s.require(a.out is not None and a.admission is not None,'Explicit bounded wrapper admission required')
    g=geometry();ad=json.loads(a.admission.read_text());label=a.mode+('-'+a.view if a.view else '')
    s.require(ad['state']=='admitted_one_shot_not_complete' and ad['wrapper_pid']==os.getppid() and ad['native_sha256']==sha(Path(__file__)),'Actual owning wrapper/native admission')
    s.require(ad['stage']==('views' if a.mode=='render' else 'source') and Path(ad['source']).resolve()==g.SOURCE.resolve() and Path(ad['output']).resolve()==a.out.resolve(),'One fixed admitted stage/source/output')
    s.require(ad['runner_version']=='cloudbank58l-form-v3' and ad['prior_failure_admissions']==list(s.FAILURE_ADMISSIONS) and ad['acceptance_mode']==s.DIAGNOSTIC_MODE and ad['full_native_acceptance'] is False,'Explicit three-failure API diagnostic admission')
    import diagnostic58l
    s.require(ad['original_source_stage']=='failed' and ad['predecessor']==diagnostic58l.predecessor(), 'Immutable actual historical build/fresh/views prerequisite')
    s.require(ad['candidate_sha256']==sha(g.CANDIDATE_PATH) and ad['binding_sha256']==sha(g.BINDING_PATH),'Admitted source input identities')
    global _TELEMETRY
    _TELEMETRY=(a.out,label);emit('native_entry',mode=a.mode)
    report=dict(original_source_stage='failed',predecessor=ad['predecessor'],acceptance_mode=s.DIAGNOSTIC_MODE,full_native_acceptance=False,diagnostic_acceptance=False,historical_default_failure=dict(s.HISTORICAL_DEFAULT_FAILURE),historical_form_v2_default_failure=dict(s.HISTORICAL_FORM_V2_DEFAULT_FAILURE),version=g.VERSION,mode=a.mode,view=a.view,pid=os.getpid(),passed=False,state='started',source_saved=False,images=0,world_loaded=False,world_integration_allowed=False,contact_acceptance=False,world_acceptance=False,global_GOAL=False,visual_acceptance=False,weather_acceptance=False)
    try:
        import bpy
        c=g.read(g.CANDIDATE_PATH);b=g.read(g.BINDING_PATH);emit('candidate_validation.begin');g.validate_candidate(c);emit('candidate_validation.complete')
        if a.mode=='build':s.require(not g.SOURCE.exists(),'Never overwrite source');create_source(c,b,g,a.out)
        else:
            s.require(g.SOURCE.is_file(),'Fresh-open requires saved source; no fallback build');emit('fresh_open.begin');bpy.context.preferences.filepaths.use_scripts_auto_execute=False;bpy.ops.wm.open_mainfile(filepath=str(g.SOURCE),load_ui=False,use_scripts=False);emit('fresh_open.complete',opened_filepath=bpy.data.filepath)
            s.require(Path(bpy.data.filepath).resolve()==g.SOURCE.resolve(),'Actually opened fixed saved source')
        emit('capture.begin');raw=capture(c,g);rawpath=a.out/(label+'-raw.json');write(rawpath,raw,True);report.update(raw_path=str(rawpath),raw_sha256=sha(rawpath));write(a.out/(label+'-result.json'),report);emit('raw.persisted',bytes=rawpath.stat().st_size)
        report['validation']=g.validate_native_raw(raw,c,b)
        if a.mode in ('build','verify'):
            probes=exercise(c,b,g,raw,a.out,label);report.update(controls_exercised=7,secondary_exercised=sum(len(r.get('secondary_parameters',[])) for r in c['controls']),manual_edit_exercised=True,exercise_sha256=sha(a.out/(label+'-exercise.json')),exact_identity_restored=all(p['exact_identity_restored'] for p in probes))
        if a.mode=='build':
            emit('save.begin');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(g.SOURCE),compress=True,check_existing=True);report['source_saved']=True;emit('save.complete',bytes=g.SOURCE.stat().st_size)
        if a.mode=='render':
            s.require(a.view in [r['name'] for r in b['world_cameras']],'Exactly one original absolute camera');scene=bpy.context.scene;original_camera=scene.camera;original_filepath=scene.render.filepath;original_images=set(bpy.data.images.keys());scene.camera=bpy.data.objects[s.CAMERA_PREFIX+a.view];path=a.out/(a.view+'.png');scene.render.filepath=str(path);emit('render.begin',view=a.view);bpy.ops.render.render(write_still=True);emit('render.complete',view=a.view);report.update(images=1,image_sha256=sha(path),image_path=str(path),source_diagnostic_only=True)
            rendered=capture(c,g);rendered_path=a.out/(label+'-rendered-raw.json');write(rendered_path,rendered,True);report['rendered_raw_sha256']=sha(rendered_path);report['rendered_normals']=s.validate_normals(rendered['mesh'])
            for img in list(bpy.data.images):
                if img.name not in original_images:
                    s.require(img.type=='RENDER_RESULT' and img.source=='VIEWER','Only native transient render result may be released');bpy.data.images.remove(img)
            scene.camera=original_camera;scene.render.filepath=original_filepath;bpy.context.view_layer.update();restored=capture(c,g);rp=a.out/(label+'-restored-raw.json');write(rp,restored,True);s.require(s.identity(restored)==s.identity(raw),'Exact source camera/scene identity restored after render');report.update(restored_raw_sha256=sha(rp),exact_identity_restored=True,restored_validation=s.validate_capture(restored,c,b,s.expected_texts(g.HERE,c,b)))
        report.update(passed=True,diagnostic_acceptance=True,state='completed',source_sha256=sha(g.SOURCE),source_bytes=g.SOURCE.stat().st_size)
    except BaseException:
        report.update(state='failed',error=traceback.format_exc())
        try:
            failure=capture(c,g);failure_path=a.out/(label+'-failure-raw.json');write(failure_path,failure,True);report['failure_raw_sha256']=sha(failure_path)
        except BaseException:report['failure_capture_error']=traceback.format_exc()
        raise
    finally:emit('native_terminal',passed=report['passed'],state=report['state']);write(a.out/(label+'-result.json'),report)
    return 0

if __name__=='__main__':raise SystemExit(main())
