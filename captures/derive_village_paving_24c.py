from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'tools/prepare_village_paving_24b.py').read_text(encoding='utf-8').replace('24b','24c')
code=code.replace('poly=shapely.set_precision(poly,1e-5)','poly=shapely.set_precision(poly.simplify(.0005,preserve_topology=True),1e-5)')
code=code.replace("base=solid(polygon,level-.10,","base=solid(polygon,level-.012,")
(root/'tools/prepare_village_paving_24c.py').write_text(code,encoding='utf-8')
code=(root/'blender/model_village_paving_24b.py').read_text(encoding='utf-8').replace('24b','24c')
(root/'blender/model_village_paving_24c.py').write_text(code,encoding='utf-8')
