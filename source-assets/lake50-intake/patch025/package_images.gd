extends SceneTree
const OUT := "/workspace/scratch/a29d03198654/Aether/source-assets/lake50-intake/patch025/"
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var manifest: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(OUT+"patches.json"))
	var records := []
	for patch in manifest.patches:
		var bytes := FileAccess.get_file_as_bytes(OUT+patch.raw_float32_file)
		var image := Image.create_from_data(int(patch.size[0]),int(patch.size[1]),false,Image.FORMAT_RF,bytes)
		var resource_path: String=OUT+patch.image_resource
		var exr_path: String=OUT+patch.exr_file
		if FileAccess.file_exists(resource_path) or FileAccess.file_exists(exr_path): push_error("Refuse overwrite patch image");quit(1);return
		if ResourceSaver.save(image,resource_path)!=OK or image.save_exr(exr_path,true)!=OK: push_error("Patch image save failed");quit(1);return
		var reload: Image=ResourceLoader.load(resource_path,"Image",ResourceLoader.CACHE_MODE_IGNORE)
		var exr := Image.load_from_file(exr_path)
		if reload==null or exr==null or exr.is_empty(): push_error("Patch reload failed");quit(1);return
		exr.convert(Image.FORMAT_RF)
		var ok := reload.get_data()==bytes and exr.get_data()==bytes
		var row := {"name":patch.name,"resource":resource_path,"resource_sha256":FileAccess.get_sha256(resource_path),"exr":exr_path,"exr_sha256":FileAccess.get_sha256(exr_path),"raw_sha256":FileAccess.get_sha256(OUT+patch.raw_float32_file),"bit_exact_RF_EXR_roundtrip":ok,"format":"Image.FORMAT_RF","mipmaps":false,"size":patch.size,"world_bounds":patch.world_bounds,"source_scene_sha256":manifest.source_scene_sha256}
		records.append(row)
		if not ok: push_error("Patch RF/EXR precision differs");quit(1);return
	var file := FileAccess.open(OUT+"image-package-report.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"passed":true,"images":records,"scene_modified":false,"frozen_base_modified":false},"  "));file.close()
	print(JSON.stringify(records));quit(0)
