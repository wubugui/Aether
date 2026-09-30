from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'tools/prepare_village_paving_24f.py').read_text(encoding='utf-8').replace('24f','24g')
old="def solid(poly,top,bottom,kind,material,name):\n    poly=shapely.set_precision(poly.simplify(.0005,preserve_topology=True),.001)\n    if poly.is_empty or poly.area<.0001:return None"
new="""def solid(poly,top,bottom,kind,material,name):
    cleaned=shapely.set_precision(poly.simplify(.0005,preserve_topology=True),.001)
    return [component_solid(p,top,bottom,kind,material,name+' component '+str(i)) for i,p in enumerate(pieces(cleaned)) if p.area>=.0001]
def component_solid(poly,top,bottom,kind,material,name):"""
assert old in code;code=code.replace(old,new)
code=code.replace('if base:solids.append(base)','solids.extend(base)')
code=code.replace('if item:solids.append(item)','solids.extend(item)')
(root/'tools/prepare_village_paving_24g.py').write_text(code,encoding='utf-8')
code=(root/'blender/model_village_paving_24f.py').read_text(encoding='utf-8').replace('24f','24g')
(root/'blender/model_village_paving_24g.py').write_text(code,encoding='utf-8')
