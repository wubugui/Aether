from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'captures/headland_runtime_23d.gd').read_text(encoding='utf-8').replace('23d','23e')
anchor='\t# Refit only temporary scatter copies intersecting the new local terrain.'
insertion='''	var trees:Array=[]
	var tree_sites:Array=[[-2251,-1730,.52],[-2239,-1725,.63],[-2225,-1715,.7],[-2240,-1778,.54],[-2222,-1788,.72],[-2210,-1777,.83],[-2200,-1760,.90],[-2207,-1728,.7],[-2188,-1743,.9],[-2165,-1750,.75],[-2188,-1800,.8],[-2175,-1813,.67],[-2200,-1818,.6],[-2214,-1805,.64],[-2196,-1839,.7],[-2190,-1855,.95],[-2200,-1880,.73],[-2210,-1900,.76],[-2223,-1907,.52],[-2185,-1910,.85],[-2160,-1897,.9],[-2170,-1860,.75],[-2215,-1930,.73],[-2200,-1950,.95],[-2225,-1977,.62],[-2235,-2010,.69],[-2215,-2005,.85],[-2160,-1730,.8]]
	for item in tree_sites:
		var at:=Vector3(item[0],0,item[1]);var ground:=hit(at)
		if ground.is_empty():continue
		at.y=ground.position.y;var near_house:=false
		for house in houses:
			var local:Vector3=house.to_local(at)
			if absf(local.x)<6.1 and absf(local.z)<8.4:near_house=true;break
		if near_house:continue
		var tree:Node3D=load("res://scenes/prefabs/pine.tscn").instantiate()
		tree.name="HeadlandPine_"+str(trees.size());tree.position=at;tree.scale=Vector3.ONE*float(item[2]);region.add_child(tree)
		trees.append({"node":str(tree.name),"position":[at.x,at.y,at.z],"scale":item[2],"ground_collider":str(ground.collider.get_path())})
'''
assert anchor in code;code=code.replace(anchor,insertion+anchor).replace('"scatter_changes":scatter_changes','"scatter_changes":scatter_changes,"trees":trees')
target=root/'captures/headland_runtime_23e.gd';assert not target.exists();target.write_text(code,encoding='utf-8')
driver=(root/'tools/render_headland_23d.py').read_text(encoding='utf-8').replace('23d','23e')
needle='headland_adapter.configure(game,directory,environment_mode=="night",camera,view)\\n'
assert needle in driver
driver=driver.replace(needle,needle+'\\tawait physics_frame;await physics_frame;await physics_frame\\n\\tvar headland_report:Dictionary=headland_adapter.finish()\\n')
driver=driver.replace("'\\tvar headland_report:Dictionary=headland_adapter.finish()')","'')")
target=root/'tools/render_headland_23e.py';assert not target.exists();target.write_text(driver,encoding='utf-8')
