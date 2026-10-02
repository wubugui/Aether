"""Read-only native inspection of the existing failed G source.

Only wm.open_mainfile is called. Never rebuilds, saves, renders, clears blocks,
reads image pixels, or follows any reported image/library filepath.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import traceback
import bpy

P=Path(__file__).resolve().parent
ROOT=P.parents[3]


def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda:stream.read(1024*1024),b''):digest.update(part)
    return digest.hexdigest()


def write(path,data):
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');temporary.replace(path)


def library_ref(library):
    return None if library is None else dict(name=library.name,filepath=library.filepath)


def id_ref(block):
    return dict(name=block.name_full,type=block.bl_rna.identifier,
                library=library_ref(getattr(block,'library',None)))


def packed_metadata(block):
    packed=getattr(block,'packed_file',None)
    files=getattr(block,'packed_files',None)
    return dict(single_packed_file=packed is not None,
                single_packed_size_bytes=int(packed.size) if packed is not None else None,
                packed_files_count=len(files) if files is not None else None,
                packed_files=[dict(filepath=getattr(item,'filepath',None),
                    packed_size_bytes=int(item.packed_file.size) if getattr(item,'packed_file',None) is not None else None)
                    for item in files] if files is not None else [])


def active_scene_user_paths(block,users):
    paths=[];queue=[(block,[])];seen=set();scene=bpy.context.scene
    while queue:
        current,trail=queue.pop(0)
        if current in seen:continue
        seen.add(current)
        if current==scene:
            paths.append(trail);continue
        for owner in sorted(users.get(current,set()),key=lambda item:(item.bl_rna.identifier,item.name_full)):
            queue.append((owner,trail+[id_ref(owner)]))
    return paths


def inventory():
    # Native direct-ID ownership/reference map, without opening any filepath.
    users=bpy.data.user_map()
    ids=set(users)
    for references in users.values():ids.update(references)
    ids.update(bpy.data.images);ids.update(bpy.data.libraries);ids.update(bpy.data.objects)
    images=[];libraries=[]
    node_uses={image:[] for image in bpy.data.images};seen_trees=set()
    for owner in sorted(ids,key=lambda item:(item.bl_rna.identifier,item.name_full)):
        tree=owner if isinstance(owner,bpy.types.NodeTree) else getattr(owner,'node_tree',None)
        if tree is None or tree in seen_trees:continue
        seen_trees.add(tree)
        for node in tree.nodes:
            candidate=getattr(node,'image',None)
            if candidate in node_uses:
                node_uses[candidate].append(dict(owner=id_ref(owner),tree=tree.name,node=node.name,node_type=node.bl_idname,property='image'))
            for socket in list(node.inputs)+list(node.outputs):
                if socket.bl_idname=='NodeSocketImage':
                    candidate=getattr(socket,'default_value',None)
                    if candidate in node_uses:
                        node_uses[candidate].append(dict(owner=id_ref(owner),tree=tree.name,node=node.name,
                            node_type=node.bl_idname,property='socket:'+socket.name))
    for image in sorted(bpy.data.images,key=lambda ob:ob.name_full):
        packed=packed_metadata(image)
        direct=sorted(users.get(image,set()),key=lambda item:(item.bl_rna.identifier,item.name_full))
        file_backed=image.source in {'FILE','MOVIE','SEQUENCE','TILED'}
        single_packed=packed['single_packed_file'] or bool(packed['packed_files_count'])
        if not file_backed:dependency='not_file_backed'
        elif not single_packed:dependency='unpacked_file_backed_image'
        elif image.source in {'SEQUENCE','TILED'}:dependency='packed_entries_present_but_full_sequence_or_tile_coverage_not_proved'
        else:dependency='single_file_image_has_embedded_packed_data'
        images.append(dict(name=image.name_full,type=image.type,rna_type=image.bl_rna.identifier,source=image.source,
            users=image.users,use_fake_user=image.use_fake_user,packed=packed,filepath=image.filepath,
            filepath_raw=getattr(image,'filepath_raw',None),library=library_ref(image.library),
            direct_id_references=[id_ref(item) for item in direct],active_scene_user_paths=active_scene_user_paths(image,users),
            explicit_node_references=node_uses[image],dependency_classification=dependency,
            external_filepath_followed=False,image_pixels_read=False))
    for library in sorted(bpy.data.libraries,key=lambda ob:ob.name_full):
        linked=sorted((item for item in ids if getattr(item,'library',None)==library),key=lambda item:(item.bl_rna.identifier,item.name_full))
        direct=sorted(users.get(library,set()),key=lambda item:(item.bl_rna.identifier,item.name_full))
        libraries.append(dict(name=library.name_full,type=library.bl_rna.identifier,source=None,
            source_property_present=hasattr(library,'source'),users=library.users,packed=packed_metadata(library),
            filepath=library.filepath,library=library_ref(library.library),parent=library_ref(getattr(library,'parent',None)),
            direct_id_references=[id_ref(item) for item in direct],linked_datablock_count=len(linked),
            linked_datablocks=[dict(**id_ref(item),users=item.users,is_library_indirect=item.is_library_indirect,
                direct_id_references=[id_ref(user) for user in sorted(users.get(item,set()),key=lambda u:(u.bl_rna.identifier,u.name_full))],
                active_scene_user_paths=active_scene_user_paths(item,users)) for item in linked],
            dependency_classification='linked_datablocks_present' if linked else 'library_record_without_linked_datablocks_found',
            external_filepath_followed=False))
    weak=[]
    for block in sorted(ids,key=lambda item:(item.bl_rna.identifier,item.name_full)):
        reference=getattr(block,'library_weak_reference',None)
        if reference is not None:
            weak.append(dict(datablock=id_ref(block),library_filepath=reference.filepath,id_name=reference.id_name,
                             classification='append_provenance_metadata_not_a_strong_library_link'))
    linked_ids=[id_ref(item) for item in sorted(ids,key=lambda item:(item.bl_rna.identifier,item.name_full)) if getattr(item,'library',None) is not None]
    unresolved_images=[image['name'] for image in images if image['dependency_classification'] in
        ('unpacked_file_backed_image','packed_entries_present_but_full_sequence_or_tile_coverage_not_proved')]
    return dict(image_count=len(images),library_count=len(libraries),images=images,libraries=libraries,
                library_weak_references=weak,all_strongly_linked_ids=linked_ids,
                references_source='bpy.data.user_map plus direct node-image and image-socket pointers',
                active_scene_paths_are_native_id_graph_paths_not_render_visibility_proof=True,
                unresolved_file_backed_images=unresolved_images,
                no_external_dependency_identified_in_images_libraries_scope=not unresolved_images and not linked_ids,
                external_file_existence_or_bytes_checked=False)


def mesh_fingerprint(ob):
    vertices=hashlib.sha256();faces=hashlib.sha256()
    for vertex in ob.data.vertices:vertices.update(struct.pack('<3f',*vertex.co))
    for polygon in ob.data.polygons:
        assert len(polygon.vertices)==3
        faces.update(struct.pack('<3i',*polygon.vertices))
    return dict(vertices_sha256=vertices.hexdigest(),oriented_triangles_sha256=faces.hexdigest(),
                vertices=len(ob.data.vertices),triangles=len(ob.data.polygons))


def scene_summary():
    meshes=[];controls=[];cameras=[]
    for ob in sorted(bpy.data.objects,key=lambda ob:ob.name):
        if ob.type=='MESH':
            meshes.append(dict(name=ob.name,visible_get=ob.visible_get(),hide_render=ob.hide_render,
                hide_viewport=ob.hide_viewport,modifiers=len(ob.modifiers),mesh=mesh_fingerprint(ob),
                groups=[g.name for g in ob.vertex_groups],materials=[m.name if m else None for m in ob.data.materials],
                matrix_world=[list(row) for row in ob.matrix_world]))
        if ob.name.startswith('CONTROL58G_'):
            controls.append(dict(name=ob.name,type=ob.type,location=list(ob.location),rotation_mode=ob.rotation_mode,
                rotation_euler=list(ob.rotation_euler),scale=list(ob.scale),field_strength=ob.get('field_strength'),
                control_id=ob.get('control_id'),role=ob.get('role')))
        if ob.type=='CAMERA':
            cameras.append(dict(name=ob.name,type=ob.data.type,matrix_world=[list(row) for row in ob.matrix_world],
                lens=ob.data.lens,ortho_scale=ob.data.ortho_scale,sensor_fit=ob.data.sensor_fit,
                clip_start=ob.data.clip_start,clip_end=ob.data.clip_end,
                view_name=ob.get('view_name'),resolution_xy=list(ob.get('resolution_xy',[])),
                pixel_aspect_xy=list(ob.get('pixel_aspect_xy',[]))))
    return dict(active_scene=bpy.context.scene.name,objects=len(bpy.data.objects),meshes=meshes,
                controls=controls,cameras=cameras,texts=[dict(name=t.name,sha256=hashlib.sha256(t.as_string().encode()).hexdigest()) for t in bpy.data.texts],
                autoexec_disabled=not bpy.context.preferences.filepaths.use_scripts_auto_execute)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);assert args.out.is_dir()
    assert bpy.app.version[:3]==(4,5,14)
    plan=json.loads((P/'inspection-plan58g.json').read_text());source=ROOT/plan['source']['path']
    report=dict(state='running',passed=False,read_only=True,source_sha256_before=sha(source),
                rebuilt=False,source_saved=False,rendered=False,cleared_or_removed_datablocks=False,
                followed_reported_external_filepaths=False,read_image_pixels=False,world_loaded=False,visual_acceptance=False)
    out=args.out/'inspection-result58g.json';assert not out.exists()
    try:
        assert report['source_sha256_before']==plan['source']['sha256']
        original=ROOT/plan['original_build_report']['path'];assert sha(original)==plan['original_build_report']['sha256']
        built=json.loads(original.read_text());assert built['passed'] is False
        report['factory_startup_inventory']=inventory();write(out,report)
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
        assert Path(bpy.data.filepath).resolve()==source.resolve()
        report['loaded_inventory']=inventory();write(out,report)
        report['loaded_scene']=scene_summary()
        loaded=report['loaded_inventory']
        gates=dict(images_empty=loaded['image_count']==0,libraries_empty=loaded['library_count']==0)
        report['loaded_subgates']=gates;report['loaded_combined_no_external_data_gate']=all(gates.values())
        report['loaded_failing_subgates']=[name for name,passed in gates.items() if not passed]
        report['original_build_combined_gate']=built['native_identity']['checks']['no_external_data']
        report['original_build_separate_counts_recorded']=False
        report['retrospective_original_subgate_attribution_proved']=False
        report['interpretation']=('Readback reproduces the combined failure; listed subgates describe this fresh process. Original separate pre-save counts were not recorded.'
            if not all(gates.values()) else 'Both subgates pass after loading. This does not identify the original pre-save failure or justify changing its result.')
        native=report['loaded_scene'];banks=[r for r in native['meshes'] if r['name']=='CloudBank58G_multiscale_field_shell']
        report['source_mesh_matches_original_build']=len(banks)==1 and banks[0]['mesh']==built['native_identity']['mesh']
        expected_controls=built['native_identity']['controls']
        comparison=[{key:row[key] for key in expected_controls[0]} for row in native['controls']]
        report['controls_match_original_build']=comparison==expected_controls
        report['passed']=bool(report['source_mesh_matches_original_build'] and report['controls_match_original_build'] and native['autoexec_disabled'])
    except BaseException:
        report['error']=traceback.format_exc();raise
    finally:
        report['source_sha256_after']=sha(source);report['source_unchanged']=report['source_sha256_after']==report['source_sha256_before']
        report['passed']=bool(report['passed'] and report['source_unchanged'])
        report['state']='completed';write(out,report)
        print(json.dumps(report,indent=2),flush=True)
    assert report['passed'],'Read-only inspection identity failed; preserve report without edits'


if __name__=='__main__':main()
