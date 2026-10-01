extends SceneTree
func _initialize():
 var p=JSON.parse_string(FileAccess.get_file_as_string("/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/v2/final-source/cirque54v2-payload.json"))
 var rows=[]
 for part in p.mountains[0].components:
  var st=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
  var expected=PackedVector3Array();var colors=PackedColorArray()
  for i in part.vertices.size():
   var v=part.vertices[i];var c=part.colors[i];var point=Vector3(v[0],v[1],v[2]);var color=Color(c[0],c[1],c[2],c[3])
   expected.append(point);colors.append(color);st.set_color(color);st.add_vertex(point-Vector3(809.494140625,0,-1780))
  st.generate_normals();var mesh=st.commit();var actual=mesh.surface_get_arrays(0);var pos=PackedVector3Array()
  for v in actual[Mesh.ARRAY_VERTEX]:pos.append(v+Vector3(809.494140625,0,-1780))
  var count=0;var maximum=0.0
  for i in colors.size():
   if colors[i]!=actual[Mesh.ARRAY_COLOR][i]:count+=1;maximum=max(maximum,absf(colors[i].r-actual[Mesh.ARRAY_COLOR][i].r),absf(colors[i].g-actual[Mesh.ARRAY_COLOR][i].g),absf(colors[i].b-actual[Mesh.ARRAY_COLOR][i].b))
  rows.append({"component":part.name,"position_exact":pos.to_byte_array()==expected.to_byte_array(),"color_exact":colors.to_byte_array()==actual[Mesh.ARRAY_COLOR].to_byte_array(),"native_color_float32_hex_sha256":actual[Mesh.ARRAY_COLOR].to_byte_array().hex_encode().sha256_text(),"color_mismatch_count":count,"max_color_channel_error":maximum,"first_color_input":str(colors[0]),"first_color_native":str(actual[Mesh.ARRAY_COLOR][0])})
 var f=FileAccess.open("/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/v2/world-diagnostic/native-mesh-encoding.json",FileAccess.WRITE);f.store_string(JSON.stringify(rows,"  "));f.close();print(JSON.stringify(rows));quit()
