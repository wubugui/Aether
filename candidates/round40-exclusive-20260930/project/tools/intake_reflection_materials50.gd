extends SceneTree
var rows=[]
func _initialize():call_deferred("run")
func walk(n:Node,t:Transform3D,path:String=""):
 path+="/"+str(n.name)
 if n is Node3D:t=t*n.transform
 if n is MeshInstance3D and n.mesh!=null and n.name!="Ocean":
  var box:AABB=t*n.get_aabb()
  if box.position.y<0:
   var materials=[]
   for i in range(n.mesh.get_surface_count()):
    var m=n.get_active_material(i)
    var row={"class":m.get_class() if m!=null else "null","id":m.get_instance_id() if m!=null else 0}
    if m is ShaderMaterial:row.shader_id=m.shader.get_instance_id();row.shader_sha=m.shader.code.sha256_text();row.has_vertex=m.shader.code.contains("void vertex");row.has_fragment=m.shader.code.contains("void fragment")
    if m is BaseMaterial3D:
     row.values={}
     for k in ["albedo_color","metallic","roughness","metallic_specular","vertex_color_use_as_albedo","vertex_color_is_srgb","diffuse_mode","specular_mode","transparency","cull_mode","shading_mode","emission_enabled","normal_enabled","rim_enabled","clearcoat_enabled","anisotropy_enabled","subsurf_scatter_enabled","backlight_enabled","refraction_enabled","detail_enabled"]:row.values[k]=str(m.get(k))
    materials.append(row)
   rows.append({"path":path,"name":str(n.name),"bounds":str(box),"below_only":box.end.y<0,"layers":n.layers,"materials":materials})
 for c in n.get_children():walk(c,t,path)
func run():
 var s=load("res://scenes/candidate48/Game48.tscn").instantiate()
 # Off-tree path unavailable: names and material identities are sufficient here.
 walk(s,Transform3D.IDENTITY)
 var f=FileAccess.open("/workspace/scratch/a29d03198654/Aether/cloud-evidence/water48-readonly-intake/underwater-materials.json",FileAccess.WRITE);f.store_string(JSON.stringify(rows,"  "));f.close();s.free();quit()
