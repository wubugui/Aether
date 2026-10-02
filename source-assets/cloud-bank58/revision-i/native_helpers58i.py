def light_material_identity(scene, bank, settings):
    material = bank.data.materials[0]
    bsdf = material.node_tree.nodes['Principled BSDF']
    poly.require(len(bpy.data.materials) == 1 and len(bank.data.materials) == 1, 'Required invariant')
    poly.require(sorted((n.bl_idname for n in material.node_tree.nodes)) == ['ShaderNodeBsdfPrincipled', 'ShaderNodeOutputMaterial'], 'Required invariant')
    poly.require(np.array_equal(np.asarray(bsdf.inputs['Base Color'].default_value), np.asarray(settings['material_linear_rgba'], np.float32).astype(float)), 'Required invariant')
    poly.require(abs(bsdf.inputs['Roughness'].default_value - settings['material_roughness']) < 1e-07, 'Required invariant')
    bg = scene.world.node_tree.nodes['Background']
    sun = bpy.data.objects['58I fixed Sun']
    poly.require(np.array_equal(np.asarray(bg.inputs['Color'].default_value), np.asarray(settings['world_linear_rgba'], np.float32).astype(float)), 'Required invariant')
    poly.require(abs(bg.inputs['Strength'].default_value - settings['world_strength']) < 1e-07, 'Required invariant')
    poly.require(sun.data.energy == settings['sun_energy'] and abs(sun.data.angle - settings['sun_angle_radians']) < 1e-07, 'Required invariant')
    poly.require(np.array_equal(np.asarray(sun.rotation_euler), np.asarray(settings['sun_source_rotation_xyz_radians'], np.float32).astype(float)), 'Required invariant')
    poly.require(scene.render.engine == 'CYCLES' and scene.cycles.device == 'CPU' and (scene.cycles.samples == 8), 'Required invariant')
    poly.require(not scene.cycles.use_denoising and scene.render.threads_mode == 'FIXED' and (scene.render.threads == 2), 'Required invariant')
    poly.require(scene.view_settings.view_transform == 'Standard' and scene.view_settings.look == 'None', 'Required invariant')
    poly.require(scene.view_settings.exposure == 0 and scene.view_settings.gamma == 1 and (not scene.use_nodes), 'Required invariant')
    return True

def cameras(scene, bank, frame, settings, reference):
    rows = []
    for name in VIEWS:
        ob = bpy.data.objects['VIEW58I_' + name]
        row = c.camera_proof(scene, ob, [bank.matrix_world @ v.co for v in bank.data.vertices], frame, settings)
        expected = next((r for r in reference['cameras'] if r['name'] == name))
        row['same_E_camera_matrix'] = row['matrix_world'] == expected['matrix_world']
        row['same_E_camera_projection'] = row['projection'] == expected['projection']
        row['passed'] = bool(row['passed'] and row['same_E_camera_matrix'] and row['same_E_camera_projection'])
        rows.append(row)
    return rows
