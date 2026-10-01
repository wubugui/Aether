extends SceneTree
## Isolated Variant serialization reproduction. No game/GLB load, scene save or GUI.
func _initialize() -> void:
	var node:=MeshInstance3D.new()
	var actual:={"custom_aabb":node.custom_aabb,"skeleton":node.skeleton,"material_overlay":node.material_overlay,"layers":node.layers,"extra_cull_margin":node.extra_cull_margin}
	var encoded:=JSON.stringify(actual)
	var decoded:Dictionary=JSON.parse_string(encoded)
	var rows:=[]
	for key in actual:
		var same_type:bool=typeof(actual[key])==typeof(decoded[key])
		rows.append({"property":key,"native_type":type_string(typeof(actual[key])),"parsed_json_type":type_string(typeof(decoded[key])),"same_native_type":same_type,"typed_equal":actual[key]==decoded[key] if same_type else false,"json_encoding":JSON.stringify(actual[key])})
	var native_again:={"custom_aabb":node.custom_aabb,"skeleton":node.skeleton,"material_overlay":node.material_overlay,"layers":node.layers,"extra_cull_margin":node.extra_cull_margin}
	var proved:bool=actual==native_again and actual!=decoded and decoded==JSON.parse_string(JSON.stringify(actual))
	var report:={"isolated_json_type_loss_reproduced":proved,"native_repeat_equal":actual==native_again,"native_vs_json_equal":actual==decoded,"flags":rows,"game_loaded":false,"scene_saved":false,"renderer_images_created":false,"scope":"Proves loss of nativeVariant types duringJSON transport only; does not prove52f mesh/source equality or waive failed world audit."}
	var path:="/workspace/scratch/a29d03198654/Aether/cloud-evidence/cloudsea52f-integration-preparation/flag-json-type-reproduction.json"
	var file:=FileAccess.open(path,FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close();node.free()
	print(JSON.stringify(report));quit(0 if proved else 1)
