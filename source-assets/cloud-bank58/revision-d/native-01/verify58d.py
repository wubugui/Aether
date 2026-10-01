"""New Blender process: inspect stored source arrays, curves and cameras."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common58d as c


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    start = time.monotonic()
    def stage(name):
        row = dict(state='running', passed=False, stage=name, pid=os.getpid(), elapsed_seconds=time.monotonic()-start)
        c.write(args.out/'fresh-stage.json', row)
        print(json.dumps(row), flush=True)
    stage('verify_input_and_read_source_in_new_process')
    plan, cage, settings = c.frozen_inputs()
    build = json.loads((args.out/'build-result.json').read_text())
    digest = c.sha(c.SOURCE)
    assert build['passed'] and digest == build['source_sha256']
    assert bpy.app.version[:3] == (4,5,14) and os.getpid() != build['build_pid']
    bpy.ops.wm.open_mainfile(filepath=str(c.SOURCE))
    scene, bank = bpy.context.scene, bpy.data.objects[c.MESH_NAME]
    stage('stored_mesh_exact_float32_identity_and_full_geometry')
    actual_source = np.asarray([tuple(v.co) for v in bank.data.vertices], float)
    expected_source = c.source_coordinates(cage['vertices'], plan).astype(np.float32).astype(float)
    faces = np.asarray([list(p.vertices) for p in bank.data.polygons], int)
    identity = dict(float32_source_vertices_exact=np.array_equal(actual_source, expected_source),
                    ordered_oriented_faces_exact=np.array_equal(faces,np.asarray(cage['faces'],int)),
                    object_matrix_identity=np.array_equal(np.asarray(bank.matrix_world),np.eye(4)),
                    no_modifiers=len(bank.modifiers)==0, all_faces_flat=all(not p.use_smooth for p in bank.data.polygons),
                    source_cage_sha_exact=bank.get('input_cage_sha256')==c.sha(c.CAGE),
                    scene_plan_sha_exact=scene.get('input_plan_sha256')==c.sha(c.PLAN),
                    origin_exact=list(scene['source_origin_godot_world'])==plan['anchor_godot_world_xyz'])
    vertices = c.world_coordinates(actual_source, plan)
    checker = c.load_pure(c.STATIC)
    helper = checker.load_pure(checker.NARROW)
    examples = checker.checker_examples(helper)
    geometry = checker.geometry(vertices, faces, checker.load_topology(), helper)
    # Verify the actual native object can be displayed through its collection.
    source_collection=bpy.data.collections['SOURCE58D']
    guide_collection=bpy.data.collections['EDIT58D_authored_curve_guides']
    source_layer=scene.view_layers[0].layer_collection.children['SOURCE58D']
    visibility=dict(bank_visible_get=bank.visible_get(),bank_not_hide_viewport=not bank.hide_viewport,
                    bank_not_hide_render=not bank.hide_render,bank_not_hide_set=not bank.hide_get(),
                    source_collection_visible=not source_collection.hide_viewport and not source_collection.hide_render,
                    source_layer_included=not source_layer.exclude and not source_layer.hide_viewport,
                    bank_linked_to_expected_collection=list(bank.users_collection)==[source_collection],
                    guide_collection_hidden_from_render=guide_collection.hide_render,
                    every_guide_object_hidden_from_render=all(ob.hide_render for ob in guide_collection.objects))
    stage('actual_native_valley_rays_25m_three_lanes')
    corridors = [dict(id=v['id'], xz=np.asarray(v['knots_godot_world_xyz_m'])[:,[0,2]].tolist(),
                      half_width_m=v['half_width_m'], intended_floor_y_range_m=v['first_surface_worldY_band_m']) for v in plan['valley_controls']]
    valleys = checker.load_pure(checker.RAYS).valley_report(vertices[faces], corridors)
    stage('saved_poly_guides_and_named_mesh_edit_groups')
    guides=[]
    for row in c.all_guides(plan):
        ob=bpy.data.objects['GUIDE58D_'+row['id']]
        points=np.asarray([list(p.co)[:3] for p in ob.data.splines[0].points],float)
        expected=c.source_coordinates(row['knots_godot_world_xyz_m'],plan).astype(np.float32).astype(float)
        checks=dict(points_exact=np.array_equal(points,expected),one_poly_spline=len(ob.data.splines)==1 and ob.data.splines[0].type=='POLY',
                    no_bevel=ob.data.bevel_depth==0,hidden_from_render=ob.hide_render,role=ob.get('role')==row['role'],
                    no_extrusion=ob.data.extrude==0,three_dimensional=ob.data.dimensions=='3D',
                    no_modifiers=len(ob.modifiers)==0,matrix_identity=np.array_equal(np.asarray(ob.matrix_world),np.eye(4)))
        if 'left_right_halfwidth_m' in row:
            checks['width_metadata_exact']=json.loads(ob['left_right_halfwidth_json'])==row['left_right_halfwidth_m']
        if 'shared_parent_junction' in row:
            checks['junction_metadata_exact']=json.loads(ob['shared_parent_junction_json'])==row['shared_parent_junction']
        guides.append(dict(id=row['id'],checks=checks,passed=all(checks.values())))
    groups=[]
    expected_groups={'EDIT_'+row['id']:sorted(row['vertex_ids']) for row in cage['upper_curve_vertex_rows']}
    expected_groups.update({'EDIT_side_ring_'+str(i):sorted(ring) for i,ring in enumerate(cage['side_ring_indices'])})
    expected_groups.update({'ROLE_'+role:[i for i,value in enumerate(cage['vertex_roles']) if value==role] for role in sorted(set(cage['vertex_roles']))})
    for name,expected_ids in expected_groups.items():
        group=bank.vertex_groups[name]
        weights=[[v.index,float(g.weight)] for v in bank.data.vertices for g in v.groups if g.group==group.index]
        expected_weights=[[i,1.0] for i in expected_ids]
        groups.append(dict(id=name,vertex_weights=weights,passed=weights==expected_weights))
    group_inventory_exact=sorted(g.name for g in bank.vertex_groups)==sorted(expected_groups)
    stage('saved_camera_projection_and_complete_shape_margins')
    camera_rows=[]
    stored_camera_proof=json.loads((args.out/'build-camera-proof.json').read_text())['cameras']
    for expected in stored_camera_proof:
        cam=bpy.data.objects['VIEW58D_'+expected['name']]
        row=c.camera_proof(scene,cam,[bank.matrix_world@v.co for v in bank.data.vertices],plan,settings)
        row['matrix_exact_after_reopen']=row['matrix_world']==expected['matrix_world']
        row['passed']=row['passed'] and row['matrix_exact_after_reopen']
        camera_rows.append(row)
    front=bpy.data.objects['VIEW58D_'+settings['front']['name']]
    basis=np.asarray(plan['camera']['camera_transform'],float)
    conversion=np.array([[1.,0,0],[0,0,-1.],[0,1.,0]])
    expected_basis=conversion @ basis[:9].reshape(3,3).T
    front_identity=dict(maximum_basis_error=float(np.abs(np.asarray(front.matrix_world)[:3,:3]-expected_basis).max()),
                        maximum_location_error_m=float(np.abs(np.asarray(front.location)-c.source_coordinates(basis[9:],plan)).max()),
                        camera_type=front.data.type,near_error=abs(front.data.clip_start-plan['camera']['camera_near']),
                        far_error=abs(front.data.clip_end-plan['camera']['camera_far']))
    front_identity['passed']=bool(front_identity['maximum_basis_error']<2e-6 and front_identity['maximum_location_error_m']<1e-4
                                 and front.data.type=='PERSP' and front_identity['near_error']<1e-6 and front_identity['far_error']<1e-6)
    c.camera_resolution(scene,bpy.data.objects['VIEW58D_'+settings['front']['name']])
    mat=bank.data.materials[0]
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    material_nodes=dict(node_types=sorted(n.bl_idname for n in mat.node_tree.nodes),
                        no_image_nodes=all(n.bl_idname not in {'ShaderNodeTexImage','ShaderNodeTexEnvironment'} for n in mat.node_tree.nodes),
                        links=[dict(source=l.from_node.bl_idname,source_socket=l.from_socket.name,target=l.to_node.bl_idname,target_socket=l.to_socket.name) for l in mat.node_tree.links])
    material_nodes['passed']=(material_nodes['node_types']==['ShaderNodeBsdfPrincipled','ShaderNodeOutputMaterial']
                              and material_nodes['no_image_nodes'] and material_nodes['links']==[dict(source='ShaderNodeBsdfPrincipled',source_socket='BSDF',target='ShaderNodeOutputMaterial',target_socket='Surface')])
    inventory=dict(mesh_objects=sum(ob.type=='MESH' for ob in bpy.data.objects),poly_curve_objects=sum(ob.type=='CURVE' for ob in bpy.data.objects),
                   cameras=len(bpy.data.cameras),lights=len(bpy.data.lights),materials=len(bpy.data.materials),images=len(bpy.data.images),
                   external_libraries=len(bpy.data.libraries),objects=len(bpy.data.objects),neutral_material_rgba=list(bsdf.inputs['Base Color'].default_value))
    inventory_ok=(inventory['mesh_objects']==1 and inventory['poly_curve_objects']==34 and inventory['cameras']==5
                  and inventory['lights']==1 and inventory['materials']==1 and inventory['images']==0
                  and inventory['external_libraries']==0 and inventory['objects']==41
                  and np.array_equal(np.asarray(inventory['neutral_material_rgba']),np.asarray(settings['material_linear_rgba'],dtype=np.float32).astype(float)))
    unchanged=c.sha(c.SOURCE)==digest
    passed=bool(all(identity.values()) and geometry['passed'] and valleys['passed'] and all(g['passed'] for g in guides+groups)
                and all(r['passed'] for r in camera_rows) and front_identity['passed'] and all(visibility.values())
                and material_nodes['passed'] and group_inventory_exact and inventory_ok and unchanged)
    report=dict(state='completed',passed=passed,build_pid=build['build_pid'],fresh_pid=os.getpid(),source_sha256=digest,
                source_unchanged=unchanged,source_bytes=c.SOURCE.stat().st_size,stored_mesh_identity=identity,
                maximum_authored_world_vertex_error_m=float(np.linalg.norm(vertices-np.asarray(cage['vertices']),axis=1).max()),
                actual_native_geometry=geometry,actual_native_valleys=valleys,editable_guides=guides,editable_groups=groups,
                edit_group_inventory_exact=group_inventory_exact,
                cameras=camera_rows,front_camera_reference_identity=front_identity,effective_visibility=visibility,
                material_nodes=material_nodes,inventory=inventory,inventory_passed=inventory_ok,checker_examples=examples,
                sample_limit='25m stations and endpoints at three lanes are not continuous-band or ship-path clearance',
                native_source_only=True,rendered=False,world_loaded=False,visual_acceptance=False,elapsed_seconds=time.monotonic()-start)
    c.write(args.out/'fresh-readback58d.json',report)
    c.write(args.out/'fresh-stage.json',dict(state='completed',passed=passed,pid=os.getpid(),elapsed_seconds=time.monotonic()-start))
    print(json.dumps(dict(passed=passed,pid=os.getpid(),source_sha256=digest,source_bytes=c.SOURCE.stat().st_size)),flush=True)
    assert passed,'Preserve failed source and all diagnostics; no automatic repair or rendering'


if __name__=='__main__':
    main()
