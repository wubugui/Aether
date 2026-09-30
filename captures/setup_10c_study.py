"""Prepare disposable source copies; never change production assets or World."""
from pathlib import Path
root=Path('D:/test6');out=root/'captures'
module=(out/'cliff_sections_10b.py').read_text()
insertion='''
# Study-only terrain cage edit underneath the southwest buttress.
# This alters native ground geometry in metre space, not camera/render data.
import copy
import world_definition as W
W.SCULPTS=copy.deepcopy(W.SCULPTS)
for cage in W.SCULPTS:
    if cage['name']!='Crown Escarpment foothills':continue
    for p in cage['points']:
        x,y,z=p
        influence=W.smooth(-5,20,x)*(1-W.smooth(90,130,x))*W.smooth(-80,-20,z)*(1-W.smooth(65,110,z))
        p[1]=float(y-13*influence)
'''
module=module.replace('from cliff_terrace_topology import ground_at','from cliff_terrace_topology import ground_at\n'+insertion)
(out/'cliff_sections_10c.py').write_text(module)
writer=(out/'verify_cliff_sections_10b.py').read_text().replace('cliff_sections_10b','cliff_sections_10c')
(out/'verify_cliff_sections_10c.py').write_text(writer)
terrain=(root/'blender/rebuild_terrain_modules.py').read_text()
terrain=terrain.replace("ROOT=Path(__file__).resolve().parents[1]","ROOT=Path('D:/test6')")
terrain=terrain.replace('import terrain_topology as T','import terrain_topology as T\nsys.path.insert(0,str(ROOT/"captures"))\nimport cliff_sections_10c')
terrain=terrain.replace("native=ROOT/'blender/terrain_modules'","native=ROOT/'captures'")
terrain=terrain.replace("path='assets/terrain/'+name+'.glb'","path='captures/round-10c-'+name+'.glb'")
terrain=terrain.replace("native/(name+'.blend')","native/('round-10c-'+name+'.blend')")
terrain=terrain.replace("ROOT/'assets/terrain_updates.json'","ROOT/'captures/round-10c-terrain-updates.json'")
(out/'build_10c_ground.py').write_text(terrain)
preview=(out/'preview_cliff_sections.gd').read_text().replace('cliff_sections_"','cliff_sections_10c_"')
preview=preview.replace('\troot.add_child(game)', '\tfor cell in ["Ground_0_0","Ground_0_-1"]:\n\t\treplace_asset(game.get_node("World/Terrain/"+cell),"D:/test6/captures/round-10c-"+cell+".glb")\n\troot.add_child(game)')
preview=preview.replace('\tvar prior:Node3D=asset.get_node("Model")','\treplace_asset(asset,"D:/test6/captures/cliff_sections_10c_"+suffix+".glb")\n\nfunc replace_asset(asset:Node3D,file:String) -> void:\n\tvar prior:Node3D=asset.get_node("Model")')
preview=preview.replace('document.append_from_file("D:/test6/captures/cliff_sections_10c_"+suffix+".glb",state)','document.append_from_file(file,state)')
(out/'preview_cliff_sections_10c.gd').write_text(preview)
