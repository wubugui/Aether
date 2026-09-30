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
	checks.append({"name":"Unedited terrain keeps its existing native default material","passed":reopened.first_mesh(normal).material_override==normal.surface_material and normal.surface_material.resource_path=="res://materials/world.tres"})
	checks.append({"name":"Production World file remains unchanged","passed":FileAccess.get_sha256(source)==before})
	var passed:=checks.all(func(item):return item.passed)
	var report:Dictionary={"passed":passed,"checks":checks,"scope":"GPU native scene material save, reopen and real World startup. No release or visual acceptance.","source_world_sha256":before,"runtime_sha256":FileAccess.get_sha256("res://scripts/open_world.gd"),"saved_fixture":saved}
	mesh=null;stored=null;tile=null;normal=null;reopened.queue_free();reopened=null
	await process_frame
	await process_frame
	var file:=FileAccess.open(directory+"/report.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	for check in checks:print("PASS " if check.passed else "FAIL ",check.name)
	print("NATIVE MATERIAL REPORT ",directory+"/report.json")
	quit(0 if passed else 1)
