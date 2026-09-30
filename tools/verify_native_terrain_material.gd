extends SceneTree
## Exercise native material persistence through real World startup on the GPU.
func _initialize() -> void:call_deferred("verify")
func verify() -> void:
	if DisplayServer.get_name()=="headless":quit(2);return
	var source:="res://scenes/world/World.tscn";var before:=FileAccess.get_sha256(source)
	var directory:="res://captures/native_material_checks/"+Time.get_datetime_string_from_system().replace(":","-")+"-"+str(Time.get_ticks_msec())
	DirAccess.make_dir_recursive_absolute(directory)
	var marker:=FileAccess.open(directory+"/.gdignore",FileAccess.WRITE);marker.store_string("Native material regression only\n");marker.close()
	var fixture:Node3D=ResourceLoader.load(source,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE_DEEP).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var expected_default:String=fixture.get_node("Terrain/Ground_0_-1").surface_material.resource_path
	var authored:=StandardMaterial3D.new();authored.resource_name="Artist terrain material";authored.albedo_color=Color(.09,.22,.31,1)
	fixture.get_node("Terrain/Ground_0_0").surface_material=authored
	var packed:=PackedScene.new();assert(packed.pack(fixture)==OK)
	var saved:=directory+"/EditedWorld.tscn";assert(ResourceSaver.save(packed,saved)==OK);fixture.free();packed=null;authored=null
	var reopened:Node3D=ResourceLoader.load(saved,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE_DEEP).instantiate()
	var tile:Node3D=reopened.get_node("Terrain/Ground_0_0")
	var stored:Material=tile.surface_material
	var checks:Array=[]
	checks.append({"name":"Native scene save and reopen retain the selected terrain material","passed":stored is StandardMaterial3D and stored.resource_name=="Artist terrain material" and stored.albedo_color.is_equal_approx(Color(.09,.22,.31,1))})
	root.add_child(reopened)
	await physics_frame
	await physics_frame
	var mesh:MeshInstance3D=reopened.first_mesh(tile)
	checks.append({"name":"World startup preserves the reopened artist terrain material","passed":mesh.material_override==stored})
	var normal:Node3D=reopened.get_node("Terrain/Ground_0_-1")
	checks.append({"name":"Unedited terrain keeps its existing native default material","passed":reopened.first_mesh(normal).material_override==normal.surface_material and normal.surface_material.resource_path==expected_default})
	checks.append({"name":"Production World file remains unchanged","passed":FileAccess.get_sha256(source)==before})
	var defaults_ok:=true
	for native_tile in reopened.get_node("Terrain").get_children():
		if native_tile==tile:continue
		defaults_ok=defaults_ok and native_tile.surface_material.resource_path==expected_default and reopened.first_mesh(native_tile).material_override==native_tile.surface_material
	checks.append({"name":"All other native ground tiles retain their selected default material","passed":defaults_ok})
	var generated:MeshInstance3D=reopened.apply_chunk_data(Vector2i(200,200),reopened.generate_chunk_data(Vector2i(200,200)))
	checks.append({"name":"Generated terrain uses the same native ground material","passed":generated.material_override.resource_path==expected_default})
	var rock:MultiMeshInstance3D=reopened.get_node("Vegetation/rock_0_-1")
	checks.append({"name":"Non-terrain scatter keeps the separate world material","passed":rock.material_override.resource_path=="res://materials/world.tres"})
	var passed:=checks.all(func(item):return item.passed)
	var report:Dictionary={"passed":passed,"checks":checks,"scope":"GPU native scene material save, reopen and real World startup. No release or visual acceptance.","source_world_sha256":before,"runtime_sha256":FileAccess.get_sha256("res://scripts/open_world.gd"),"saved_fixture":saved}
	var run_id:="";var requested_output:=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--validation-run="):run_id=arg.trim_prefix("--validation-run=")
		if arg.begins_with("--output="):requested_output=arg.trim_prefix("--output=")
	report.run_id=run_id;report.default_material=expected_default;report.native_tiles=208
	generated=null;rock=null
	mesh=null;stored=null;tile=null;normal=null;reopened.queue_free();reopened=null
	await process_frame
	await process_frame
	var file:=FileAccess.open(directory+"/report.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	if not requested_output.is_empty():
		var copy:=FileAccess.open(requested_output,FileAccess.WRITE);copy.store_string(JSON.stringify(report,"\t"));copy.close()
	for check in checks:print("PASS " if check.passed else "FAIL ",check.name)
	print("NATIVE MATERIAL REPORT ",directory+"/report.json")
	quit(0 if passed else 1)
