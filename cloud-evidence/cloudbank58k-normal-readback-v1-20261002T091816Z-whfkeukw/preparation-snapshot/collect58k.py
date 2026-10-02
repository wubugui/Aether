"""One scheduled source-normal read only. No source save, export, render or Godot."""
import argparse
import os
from pathlib import Path
import sys
import traceback
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import guard58k as g
c = g.c


def scene_state(scene):
    return dict(active_camera=scene.camera.name if scene.camera else None,
                **{key: getattr(scene.render, key) for key in ('resolution_x', 'resolution_y', 'resolution_percentage', 'pixel_aspect_x', 'pixel_aspect_y')})


def camera_identities(bpy, core):
    # Unlike the legacy camera_proof, this does not assign scene.camera or any
    # render setting. Resolution/aspect arguments come from each saved camera.
    rows = []
    for name in core.VIEWS:
        camera = bpy.data.objects['VIEW58K_' + name]
        resolution = list(camera['resolution_xy']); aspect = list(camera['pixel_aspect_xy'])
        projection = camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),
                    x=resolution[0], y=resolution[1], scale_x=aspect[0], scale_y=aspect[1])
        rows.append(dict(name=camera['view_name'], matrix_world=[list(row) for row in camera.matrix_world],
                         projection=[list(row) for row in projection], resolution_xy=resolution, pixel_aspect_xy=aspect))
    return rows


def main():
    import bpy
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:]); out = args.out.resolve()
    c.require(out.is_dir() and not any(out.iterdir()), 'Fresh output directory')
    result = dict(version=g.VERSION, pid=os.getpid(), passed=False, state='failed', source_saved=False,
                  export_performed=False, godot_started=False, world_loaded=False, images=0, visual_acceptance=False)
    try:
        verified = c.source_preconditions()
        c.require(bpy.app.version == (4, 5, 14), 'Pinned Blender 4.5.14')
        bpy.context.preferences.filepaths.use_scripts_auto_execute = False
        before_sha = c.sha(c.SOURCE)
        bpy.ops.wm.open_mainfile(filepath=str(c.SOURCE))
        scene_before = scene_state(bpy.context.scene)
        core = c.load(c.K / 'recovery-01/source_contact58k.py').recovery_core()
        bank = bpy.data.objects[c.BANK]
        identity_before = core.native_identity(bank)
        c.require(identity_before == verified['native_identity'] and identity_before['passed'], 'Accepted source identity')
        dependencies_before = core.dependency_state()
        frame, settings, _, reference = core.inputs()
        core.light_material_identity(bpy.context.scene, bank, settings)
        cameras_before = camera_identities(bpy, core)
        vertices, faces = core.rebuild.geometry_arrays(bank)
        polygons = [list(p.normal) for p in bank.data.polygons]
        corners = [list(n.vector) for n in bank.data.corner_normals]
        polygon_loops = [list(p.loop_indices) for p in bank.data.polygons]
        loop_vertices = [int(loop.vertex_index) for loop in bank.data.loops]
        owners = [-1] * len(loop_vertices)
        for polygon, indices in enumerate(polygon_loops):
            for loop in indices:
                c.require(owners[loop] == -1, 'Loop has one polygon owner')
                owners[loop] = polygon
        core.light_material_identity(bpy.context.scene, bank, settings)
        data = dict(version=g.VERSION, state='captured', pid=os.getpid(), blender_version=list(bpy.app.version),
                    cpu_affinity=sorted(os.sched_getaffinity(0)), source_sha256_before=before_sha,
                    source_sha256_after=c.sha(c.SOURCE), identity_before=identity_before,
                    identity_after=core.native_identity(bank), dependencies_before=dependencies_before,
                    dependencies_after=core.dependency_state(), cameras_before=cameras_before,
                    cameras_after=camera_identities(bpy, core), scene_state_before=scene_before,
                    scene_state_after=scene_state(bpy.context.scene),
                    positions=vertices.tolist(), triangles=faces.tolist(), polygon_normals=polygons,
                    corner_normals=corners, polygon_loop_indices=polygon_loops,
                    loop_vertex_indices=loop_vertices, loop_polygon_indices=owners,
                    source_saved=False, export_performed=False, godot_started=False, world_loaded=False,
                    images=0, visual_acceptance=False)
        # Preserve actual arrays even when an ensuing numerical diagnostic fails.
        c.write(out / 'source-normal-arrays.json', data)
        result['raw_sha256'] = c.sha(out / 'source-normal-arrays.json')
        result['validation'] = g.validate_readback(data, os.getpid(), verified)
        result.update(passed=True, state='completed')
    except BaseException:
        result['error'] = traceback.format_exc()
        raise
    finally:
        c.write(out / 'native-result.json', result)


if __name__ == '__main__':
    main()
