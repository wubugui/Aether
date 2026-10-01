extends SceneTree
func _initialize():
 var shader=load('res://assets/lake_depth50/lake_water_depth50.gdshader') as Shader
 var ledger=JSON.parse_string(FileAccess.get_file_as_string('/workspace/scratch/a29d03198654/Aether/source-assets/lake_depth50/shader-change-ledger.json'))
 if shader==null or shader.code.sha256_text()!=ledger.new_shader_sha256:push_error('Depth shader source hash mismatch');quit(1);return
 var stripped=shader.code.replace(ledger.inserted_declarations_and_helpers,'').replace(ledger.inserted_depth_assignment,'')
 if stripped.sha256_text()!=ledger.original_ocean_shader_sha256:push_error('Reverse shader injection mismatch');quit(1);return
 var uniforms=shader.get_shader_uniform_list()
 var world=Node3D.new();var ocean=MeshInstance3D.new();ocean.name='Ocean';world.add_child(ocean)
 var material=ShaderMaterial.new();material.shader=shader;ocean.material_override=material
 var controller=Node3D.new();controller.name='LakeDepth50';controller.set_script(load('res://scripts/lake_depth50.gd'));world.add_child(controller)
 controller.base_height_image=load('/workspace/scratch/a29d03198654/Aether/source-assets/lake50-intake/height49-1m-rf.res')
 var dir='/workspace/scratch/a29d03198654/Aether/source-assets/lake50-intake/patch025/'
 var patches=JSON.parse_string(FileAccess.get_file_as_string(dir+'patches.json'))
 for patch in patches.patches:
  controller.patch_images.append(load(dir+patch.image_resource))
  controller.patch_bounds.append(Vector4(patch.world_bounds[0],patch.world_bounds[1],patch.world_bounds[2],patch.world_bounds[3]))
  controller.patch_sizes.append(Vector2i(patch.size[0],patch.size[1]))
 controller._ready()
 var state=controller.get_diagnostic_state()
 if not state.bound or state.texture_count!=5:push_error('Height binding failed '+JSON.stringify(state));world.free();quit(1);return
 controller.set_depth_enabled(false)
 if material.get_shader_parameter('lake50_depth_enabled')!=false:push_error('disable failed');world.free();quit(1);return
 controller.set_depth_enabled(true)
 if material.get_shader_parameter('lake50_depth_enabled')!=true:push_error('enable failed');world.free();quit(1);return
 print('DEPTH50 API/SHADER/5IMAGE/FLAG test passed (dummy world; no scene saved; not renderer acceptance), uniforms=',uniforms.size())
 world.free();quit(0)
