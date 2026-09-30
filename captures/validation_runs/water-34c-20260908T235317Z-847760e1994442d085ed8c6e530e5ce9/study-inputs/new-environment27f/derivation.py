from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'captures/coast_environment_study_21b';assert not out.exists()
shutil.copytree(root/'captures/coast_environment_study_21a',out)
shutil.copy2(__file__,out/'derivation.py')
p=out/'open_sky.gdshader';s=p.read_text()
s=s.replace('vec3(.035,.085,.20),vec3(.003,.010,.039)','vec3(.065,.14,.30),vec3(.009,.028,.085)')
s=s.replace('vec2(650.,325.)','vec2(350.,175.)').replace('step(.73,seed)','step(.92,seed)')
s=s.replace('night=mix(night,vec3(.70,.79,1.)*facets,disk);','// Lunar disk is now the native Blender sphere in world space.')
p.write_text(s)
p=out/'cloud_surface.gdshader';s=p.read_text().replace('vec3(.024,.036,.082),vec3(.105,.155,.34)','vec3(.070,.105,.20),vec3(.24,.34,.62)');p.write_text(s)
p=out/'open_water.gdshader';s=p.read_text()
s=s.replace('cos(world_point.x*.17+world_point.z*.07+world_time*.7)*.105+sin(world_point.z*.39-world_time)*.045,1.,cos(world_point.z*.23-world_time*.85)*.115','cos(world_point.x*.19+world_point.z*.27+world_time*.7)*.105+sin(world_point.x*.71-world_point.z*.43-world_time)*.055,1.,cos(world_point.x*.25+world_point.z*.33-world_time*.85)*.10+sin(world_point.x*.47-world_point.z*.57+world_time)*.05')
s=s.replace('180.);','110.);').replace('vec3(.003,.011,.036),vec3(.010,.026,.070)','vec3(.012,.035,.105),vec3(.027,.070,.19)')
s=s.replace('sin(world_point.x*.85+world_point.z*1.5+world_time)','sin(world_point.x*.85+world_point.z*1.5+world_time)+.7*sin(world_point.x*1.33-world_point.z*.77-world_time*.6)')
p.write_text(s)
(out/'moon.gdshader').write_text('shader_type spatial;\nrender_mode unshaded,fog_disabled;\nuniform vec3 moon_color=vec3(.7,.8,1.);\nvoid fragment(){ALBEDO=moon_color;}\n')
p=root/'captures/coast_environment_21b.gd';assert not p.exists();s=(root/'captures/coast_environment_21a.gd').read_text()
s=s.replace('Vector3(.055,.085,.18)','Vector3(.22,.32,.60)').replace('Vector3(.008,.024,.065)','Vector3(.018,.045,.13)')
s=s.replace('Color(.40,.53,1.);sun.light_energy=.50','Color(.50,.63,1.);sun.light_energy=.85')
s=s.replace('Color(.15,.23,.43);environment.ambient_light_energy=.28','Color(.36,.46,.70);environment.ambient_light_energy=1.0')
s=s.replace('Color(.020,.049,.115)','Color(.045,.09,.20)')
anchor='\tif night:\n\t\tfor tower in region.get_children():'
insert='''\tvar sky_assets:=Node3D.new();sky_assets.name="NativeCoastalSky21b";game.add_child(sky_assets)
\tvar asset_records:Array=[]
\tvar cloud_positions:Array=[[-900,450,-1250,2.1,0],[-150,340,-1900,2.0,1],[650,520,-1550,2.7,2],[-1500,430,-2900,2.4,2],[1100,630,-3400,3.1,1],[-150,500,-4700,3.2,0],[400,250,-1000,1.3,0]]
\tfor item in cloud_positions:
\t\tvar document:=GLTFDocument.new();var state:=GLTFState.new()
\t\tvar asset_name:String="cloud_bank_"+str(item[4])
\t\tassert(document.append_from_file(folder.path_join("sky-assets/"+asset_name+".glb"),state)==OK)
\t\tvar node:Node3D=document.generate_scene(state);sky_assets.add_child(node)
\t\tnode.position=Vector3(-2350+item[0],item[1],-1650+item[2]);node.scale=Vector3.ONE*float(item[3]);node.rotation.y=.35
\t\tvar vapor:=ShaderMaterial.new();vapor.shader=shader_from("cloud_surface")
\t\tvapor.set_shader_parameter("study_night",1. if night else 0.);vapor.set_shader_parameter("moon_direction",MOON.normalized())
\t\tfor mesh in node.find_children("*","MeshInstance3D",true,false):mesh.material_override=vapor
\t\tasset_records.append({"asset":asset_name,"position":[node.position.x,node.position.y,node.position.z],"scale":item[3]})
\tif night:
\t\tvar document:=GLTFDocument.new();var state:=GLTFState.new()
\t\tassert(document.append_from_file(folder.path_join("sky-assets/moon.glb"),state)==OK)
\t\tvar moon:Node3D=document.generate_scene(state);sky_assets.add_child(moon)
\t\tmoon.position=Vector3(-2278,60,-1632)+MOON.normalized()*9000.
\t\tfor mesh in moon.find_children("*","MeshInstance3D",true,false):
\t\t\tfor index in range(mesh.mesh.get_surface_count()):
\t\t\t\tvar source:Material=mesh.mesh.surface_get_material(index)
\t\t\t\tvar shade:int=int(source.resource_name.get_slice(" ",2))
\t\t\t\tvar lunar:=ShaderMaterial.new();lunar.shader=shader_from("moon")
\t\t\t\tlunar.set_shader_parameter("moon_color",Vector3(.40+shade*.055,.46+shade*.055,.64+shade*.05))
\t\t\t\tmesh.set_surface_override_material(index,lunar)
\t\tasset_records.append({"asset":"moon","position":[moon.position.x,moon.position.y,moon.position.z],"radius_m":330.,"scope":"Fixed world position near9000m; angular direction matches reference-camera moon light, finite-distance approximation during flight."})
'''
assert s.count(anchor)==1;s=s.replace(anchor,insert+anchor).replace('"night":night,"moon_direction"','"native_sky_assets":asset_records,"night":night,"moon_direction"')
p.write_text(s);print(out,p)
