"""Save one small editable D source; no render, remesh, modifier or export."""
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
    assert args.out.is_dir() and not c.SOURCE.exists(), 'Preserve any existing source; use a new candidate'
    start = time.monotonic()
    def stage(name, **extra):
        row = dict(state='running', passed=False, stage=name, pid=os.getpid(),
                   elapsed_seconds=time.monotonic()-start, **extra)
        c.write(args.out/'build-stage.json', row)
        print(json.dumps(c.native(row)), flush=True)
    stage('verify_frozen_static_input')
    plan, cage, settings = c.frozen_inputs()
    assert bpy.app.version[:3] == (4, 5, 14)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Remove only unused factory datablocks in this fresh isolated process.
    for store in [bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras,
                  bpy.data.lights, bpy.data.worlds, bpy.data.images]:
        for block in list(store):
            if block.users == 0:
                store.remove(block)
    bpy.context.preferences.filepaths.save_version = 0
    scene = bpy.context.scene
    scene['source_origin_godot_world'] = plan['anchor_godot_world_xyz']
    scene['scope'] = 'One isolated 640x625m D fold junction, reconstructed after workspace reset; no world integration'
    scene['visual_acceptance'] = False
    scene['input_cage_sha256'], scene['input_plan_sha256'] = c.sha(c.CAGE), c.sha(c.PLAN)
    scene.unit_settings.system, scene.unit_settings.scale_length = 'METRIC', 1
    collections = {}
    for name in ['SOURCE58D', 'EDIT58D_authored_curve_guides', 'VIEW58D']:
        collections[name] = bpy.data.collections.new(name)
        scene.collection.children.link(collections[name])
    stage('create_exact_cage_and_edit_groups')
    mesh = bpy.data.meshes.new(c.MESH_NAME)
    expected = c.source_coordinates(cage['vertices'], plan).astype(np.float32)
    mesh.from_pydata(expected.tolist(), [], cage['faces'])
    mesh.update()
    bank = bpy.data.objects.new(c.MESH_NAME, mesh)
    collections['SOURCE58D'].objects.link(bank)
    bank['authoring_master'] = 'This editable mesh is authoritative. Curve guides do not automatically deform it.'
    bank['upper_constrained_edges_json'] = json.dumps(cage['upper_constraints'], separators=(',', ':'))
    bank['input_cage_sha256'] = c.sha(c.CAGE)
    for row in cage['upper_curve_vertex_rows']:
        group = bank.vertex_groups.new(name='EDIT_' + row['id'])
        group.add(row['vertex_ids'], 1, 'REPLACE')
    for i, ring in enumerate(cage['side_ring_indices']):
        group = bank.vertex_groups.new(name='EDIT_side_ring_' + str(i))
        group.add(ring, 1, 'REPLACE')
    for role in sorted(set(cage['vertex_roles'])):
        ids = [i for i, value in enumerate(cage['vertex_roles']) if value == role]
        group = bank.vertex_groups.new(name='ROLE_' + role)
        group.add(ids, 1, 'REPLACE')
    for polygon in mesh.polygons:
        polygon.use_smooth = False
    stage('create_34_editable_unbeveled_poly_guides')
    for row in c.all_guides(plan):
        curve = bpy.data.curves.new('GUIDE58D_' + row['id'], 'CURVE')
        curve.dimensions, curve.resolution_u, curve.bevel_depth = '3D', 1, 0
        spline = curve.splines.new('POLY')
        points = c.source_coordinates(row['knots_godot_world_xyz_m'], plan).astype(np.float32)
        spline.points.add(len(points)-1)
        for point, position in zip(spline.points, points):
            point.co = (*position, 1)
        ob = bpy.data.objects.new(curve.name, curve)
        collections['EDIT58D_authored_curve_guides'].objects.link(ob)
        ob.hide_render, ob.show_in_front, ob.display_type = True, True, 'WIRE'
        ob['role'], ob['control_id'] = row['role'], row['id']
        ob['scope'] = 'Editable guide only; mesh vertex groups are the native cage editing controls'
        if 'left_right_halfwidth_m' in row:
            ob['left_right_halfwidth_json'] = json.dumps(row['left_right_halfwidth_m'])
        if 'shared_parent_junction' in row:
            ob['shared_parent_junction_json'] = json.dumps(row['shared_parent_junction'])
    collections['EDIT58D_authored_curve_guides'].hide_render = True
    stage('create_single_neutral_material_and_fixed_lighting')
    material = bpy.data.materials.new('58D neutral shape inspection, no textures')
    material.use_nodes = True
    material.diffuse_color = settings['material_linear_rgba']
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = settings['material_linear_rgba']
    bsdf.inputs['Roughness'].default_value = settings['material_roughness']
    mesh.materials.append(material)
    world = bpy.data.worlds.new('58D fixed neutral source lighting')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = settings['world_linear_rgba']
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = settings['world_strength']
    scene.world = world
    sun_data = bpy.data.lights.new('58D fixed Sun', 'SUN')
    sun_data.energy, sun_data.angle = settings['sun_energy'], settings['sun_angle_radians']
    sun = bpy.data.objects.new(sun_data.name, sun_data)
    sun.rotation_euler = settings['sun_source_rotation_xyz_radians']
    collections['VIEW58D'].objects.link(sun)
    scene.render.engine = settings['engine']
    scene.cycles.device, scene.cycles.samples = settings['device'], settings['samples']
    scene.cycles.use_denoising = settings['denoising']
    scene.render.threads_mode, scene.render.threads = 'FIXED', settings['threads']
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure, scene.view_settings.gamma = 0, 1
    stage('prepare_five_cameras_without_rendering')
    cameras = c.create_cameras(scene, collections['VIEW58D'], bank, plan, settings)
    c.write(args.out/'build-camera-proof.json', dict(passed=all(r['passed'] for r in cameras), cameras=cameras, rendered=False))
    assert all(r['passed'] for r in cameras), 'Camera gate failed; keep evidence'
    notes = bpy.data.texts.new('READ_ME_58D_SOURCE.txt')
    notes.write('Isolated reconstructed D fold junction. No visual acceptance or world integration.\n'
                'Edit the SOURCE58D mesh in Edit Mode; named ridge, valley and side groups select authored controls.\n'
                'The 34 POLY curves are editable guides, not automatic mesh deformation modifiers.\n'
                'The 12 small E folds are guide-only. Keep all original flat faces and full underside.\n'
                'Five cameras are prepared. The exact 1216 front may crop the underside; other views must retain margins.\n'
                'Neutral material, no textures or reference image. Rendering is a separate scheduled task.\n'
                'Cage SHA256: ' + c.sha(c.CAGE) + '\nPlan SHA256: ' + c.sha(c.PLAN) + '\n')
    bpy.context.view_layer.objects.active = bank
    bank.select_set(True)
    stage('save_one_compressed_native_checkpoint')
    bpy.ops.wm.save_as_mainfile(filepath=str(c.SOURCE), compress=True, check_existing=True)
    report = dict(state='completed', passed=True, saved=True, native_geometry_pending_fresh=True,
                  source=str(c.SOURCE.relative_to(c.ROOT)), source_sha256=c.sha(c.SOURCE), source_bytes=c.SOURCE.stat().st_size,
                  exceeds_1MiB_report_threshold=c.SOURCE.stat().st_size>1048576,
                  build_pid=os.getpid(), blender_version=bpy.app.version_string, vertices=325, triangles=646,
                  editable_poly_guides=34, cameras=5, materials=1, images=len(bpy.data.images),
                  rendered=False, world_loaded=False, visual_acceptance=False, elapsed_seconds=time.monotonic()-start)
    c.write(args.out/'build-result.json', report)
    c.write(args.out/'build-stage.json', report)
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
