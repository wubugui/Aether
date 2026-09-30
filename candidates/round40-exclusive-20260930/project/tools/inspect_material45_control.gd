extends SceneTree
var resource_cache := {}
var resource_debug := {}
func stable_variant(value: Variant) -> Variant:
	# Godot 4.5.1 var_to_bytes(NodePath) contains non-deterministic alignment
	# padding. Preserve exact path text + explicit type, never those unused bytes.
	if value is NodePath: return {"__godot_variant_type__":TYPE_NODE_PATH,"path":str(value)}
	# Dictionary key ordering is not content. Make its representation stable
	# while retaining every key/value, including dictionaries nested in arrays.
	# The observed resource drift was NodePath padding, handled above.
	if value is Dictionary:
		var keys: Array = value.keys()
		keys.sort_custom(func(a: Variant,b: Variant) -> bool: return str(typeof(a))+":"+str(a)<str(typeof(b))+":"+str(b))
		var result := {}
		for key in keys: result[key]=stable_variant(value[key])
		return result
	if value is Array:
		var result := []
		for item in value: result.append(stable_variant(item))
		return result
	return value
func digest(value: Variant) -> String: return var_to_bytes(stable_variant(value)).hex_encode().sha256_text()
func dictionary_orders(value: Variant, path := "") -> Dictionary:
	var result := {}
	if value is Dictionary:
		result[path]=value.keys()
		for key in value: result.merge(dictionary_orders(value[key],path+"/"+str(key)))
	elif value is Array:
		for i in range(value.size()): result.merge(dictionary_orders(value[i],path+"/"+str(i)))
	return result
func canonical(value: Variant) -> Variant:
	if value is Resource:
		var id: int = value.get_instance_id()
		if resource_cache.has(id): return resource_cache[id]
		if value is Script: return [value.get_class(),value.resource_path,FileAccess.get_sha256(value.resource_path)]
		var state := {"class":value.get_class()}
		for property in value.get_property_list():
			var key: String = property.name
			if property.usage & PROPERTY_USAGE_STORAGE and key not in ["resource_path"]:
				state[key] = canonical(value.get(key))
		var result := digest(state)
		if value is PackedScene or value is Material or value is Shader:
			resource_debug[str(id)]={"class":value.get_class(),"path":value.resource_path,"hash":result,"state":state,"encoded":var_to_bytes(stable_variant(state)).hex_encode()}
		resource_cache[id] = result
		return result
	if value is Node: return str(value.name)
	if value is Array:
		var array := []
		for item in value: array.append(canonical(item))
		return array
	if value is Dictionary:
		var dictionary := {}
		for key in value: dictionary[key] = canonical(value[key])
		return dictionary
	return value
func _initialize() -> void:
	for text in [".","./Collision","/root/World:material","../Bush/Leaf:albedo",""]:
		var path:=NodePath(text)
		var normalized: Dictionary=stable_variant(path)
		if normalized.__godot_variant_type__!=TYPE_NODE_PATH or NodePath(normalized.path)!=path: quit(1);return
	print("NODEPATH_EXACT_TYPE_AND_ROUNDTRIP true")
	var a := {"outer":[{"x":1,"y":2}],"second":3}
	var b := {"second":3,"outer":[{"y":2,"x":1}]}
	var changed := {"second":3,"outer":[{"y":2,"x":4}]}
	print("REORDERED_EQUAL ",a==b," raw_bytes_differ ",var_to_bytes(a)!=var_to_bytes(b)," stable_digest_equal ",digest(a)==digest(b)," changed_digest_different ",digest(a)!=digest(changed))
	if digest(a)!=digest(b) or digest(a)==digest(changed): quit(1);return
	for path in ["res://scenes/prefabs/bush.tscn","res://scenes/prefabs/rock.tscn"]:
		var resource: Resource=load(path)
		resource_cache.clear()
		var first: Variant=canonical(resource)
		var before:=resource_debug.duplicate(true)
		resource_cache.clear()
		var second: Variant=canonical(resource)
		print("RESOURCE_DOUBLE_READ ",path," ",first==second)
		if first!=second:
			var f=FileAccess.open("/tmp/material45-parse/stable-control-diff.json",FileAccess.WRITE)
			f.store_string(JSON.stringify({"before":before,"after":resource_debug,"first":first,"second":second},"  "));f.close()
		if first!=second: quit(1);return
	quit()
