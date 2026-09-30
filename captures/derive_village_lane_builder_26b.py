from pathlib import Path
R=Path(__file__).resolve().parents[1];p=(R/'blender/model_village_paving_24m.py').read_text().replace('24m','26b')
p=p.replace("vertices=[(x-origin[0],-(z-origin[2]),y) for y in [item['bottom_y'],item['top_y']] for x,z in points]","vertices=[(x-origin[0],-(z-origin[2]),heights[i]) for heights in [item['bottom_heights'],item['top_heights']] for i,(x,z) in enumerate(points)]")
p=p.replace('Connected real stone courtyard and contour stairs','Connected real stone courtyard and continuous inclined lanes').replace('Actual headland-derived shared level field','Shared continuous face-gradient constrained surface field')
(R/'blender/model_village_paving_26b.py').write_text(p,encoding='utf-8')
