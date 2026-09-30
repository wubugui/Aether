"""Read exported section cliffs; check that their upper terrain surfaces do not overlap."""
import ast,json,hashlib
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from shapely import union_all
root=Path('D:/test6')
syntax=ast.parse((root/'tools/verify_geology_assets.py').read_text())
reader={}
exec(compile(ast.Module(body=[n for n in syntax.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'existing GLB accessor reader','exec'),reader)
results=[]
for kind in ['crown','western_slab','front_columns','shadow_buttress','central_wall']:
    path=root/'assets/models'/('cliff_'+kind+'.glb');doc,tri=reader['triangles'](path)
    n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(n,axis=1)
    downward=(tri[:,:,1].max(axis=1)>0)&(n[:,1]/np.maximum(area,1e-9)<-.001)
    roof=tri[n[:,1]>1e-6]
    polygons=[Polygon(t[:,[0,2]]) for t in roof]
    invalid=sum(not p.is_valid for p in polygons)
    overlap=sum(p.area for p in polygons)-union_all(polygons).area
    passed=invalid==0 and not downward.any() and abs(overlap)<.001
    results.append({'name':'cliff_'+kind,'passed':bool(passed),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'roof_faces':len(polygons),'invalid_projected_faces':invalid,'downward_nonfloor_faces':int(downward.sum()),'overlapping_projected_roof_area_m2':float(overlap)})
report={'passed':all(r['passed'] for r in results),'scope':'Five exported section cliff assets: projected upper-surface overlaps and downward folds. Complements the separate manifold and volume check; does not test overlap between placed assets or terrain contact.','assets':results}
(root/'captures/round-10a-section-overlap-check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
