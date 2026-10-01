extends SceneTree
const OUT := "/workspace/scratch/a29d03198654/Aether/source-assets/lake50-intake/"
const WIDTH := 769
const HEIGHT := 1537
func _initialize() -> void: call_deferred("run")
func hash_bytes(bytes: PackedByteArray) -> String:
	var hash := HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(bytes)
	return hash.finish().hex_encode()
func run() -> void:
	var records := []
	for label in ["height","depth"]:
		var path: String=OUT+label+"49-1m-rf.f32"
		var bytes := FileAccess.get_file_as_bytes(path)
		if bytes.size()!=WIDTH*HEIGHT*4: push_error("Wrong float32 input size "+label);quit(1);return
		var image := Image.create_from_data(WIDTH,HEIGHT,false,Image.FORMAT_RF,bytes)
		var resource_path: String=OUT+label+"49-1m-rf.res"
		var exr_path: String=OUT+label+"49-1m.exr"
		if FileAccess.file_exists(resource_path) or FileAccess.file_exists(exr_path): push_error("Refuse overwrite image outputs");quit(1);return
		if ResourceSaver.save(image,resource_path)!=OK or image.save_exr(exr_path,true)!=OK:
			push_error("Independent RF image save failed "+label);quit(1);return
		var reload: Image=ResourceLoader.load(resource_path,"Image",ResourceLoader.CACHE_MODE_IGNORE)
		var exr := Image.load_from_file(exr_path)
		if exr==null or exr.is_empty() or reload==null: push_error("RF/EXR read-back failed");quit(1);return
		var exr_original_format := exr.get_format()
		exr.convert(Image.FORMAT_RF)
		var f0 := bytes.to_float32_array();var f1 := exr.get_data().to_float32_array()
		var max_error := 0.0
		for i in range(f0.size()): max_error=maxf(max_error,absf(f0[i]-f1[i]))
		var record := {"label":label,"resource_path":resource_path,"resource_class":reload.get_class(),"resource_sha256":FileAccess.get_sha256(resource_path),"format":"Image.FORMAT_RF","width":WIDTH,"height":HEIGHT,"mipmaps":false,"resource_roundtrip_data_exact":reload.get_data()==bytes,"raw_f32_sha256":hash_bytes(bytes),"exr_path":exr_path,"exr_sha256":FileAccess.get_sha256(exr_path),"exr_loaded_godot_format":exr_original_format,"exr_roundtrip_max_error_m":max_error,"exr_float32_data_exact":exr.get_data()==bytes,"sampling":"Read RF Image with ResourceLoader.load(abs_path) then ImageTexture.create_from_image(image), or Image.load_from_file(EXR) then create ImageTexture. This headless command only saves newly created independent Image resources; no scene or MultiMesh is loaded/saved."}
		records.append(record)
		if not record.resource_roundtrip_data_exact or max_error>.00001: push_error("Float precision lost in packaging");quit(1);return
	var file := FileAccess.open(OUT+"image-package-report.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"passed":true,"images":records,"scene_changed":false,"candidate_created":false},"  "));file.close()
	print(JSON.stringify(records))
	quit(0)
