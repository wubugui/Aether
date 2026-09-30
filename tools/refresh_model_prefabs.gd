extends "res://tools/install_cliff_kit.gd"
## Refresh only the explicitly supplied native prefab. Existing placement,
## Inspector overrides and unrelated asset libraries are preserved.
func build() -> void:
	if DisplayServer.get_name()=="headless":quit(1);return
	backup_directory="res://captures/edit_backups/models-"+Time.get_datetime_string_from_system().replace(":","-")
	var kit:Array=JSON.parse_string(FileAccess.get_file_as_string("res://assets/settlement_kit.json"))
	var catalog_path:="res://assets/asset_catalog.json"
	backup_file(catalog_path)
	var catalog:Array=JSON.parse_string(FileAccess.get_file_as_string(catalog_path))
	# Validate the entire kit before touching even one derived resource.
	for item in kit:
		assert(item.name=="castle","Only the current castle refresh is authorized by this kit")
		assert(item.path=="assets/models/"+item.name+".glb")
		assert(FileAccess.file_exists("res://"+item.path))
		assert(FileAccess.file_exists("res://scenes/prefabs/"+item.name+".tscn"))
		assert(catalog.any(func(entry):return entry.name==item.name),"Unknown catalog asset")
	for item in kit:
		refresh_prefab(item.name,"res://"+item.path,"res://scenes/prefabs/"+item.name+".tscn")
		var found:=false
		for entry in catalog:
			if entry.name==item.name:entry.merge(item,true);found=true;break
		assert(found,"This refresh tool must not silently add world assets")
	var file:=FileAccess.open(catalog_path,FileAccess.WRITE);file.store_string(JSON.stringify(catalog,"\t"));file.close()
	print("REFRESHED NATIVE MODEL PREFABS ",kit.size(),"; saved world transforms unchanged")
	await process_frame
	quit()
