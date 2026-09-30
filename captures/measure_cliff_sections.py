import ast,json
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
source=ast.parse(Path('D:/test6/tools/verify_geology_assets.py').read_text())
namespace={}
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'geometry-reader','exec'),namespace)
read=namespace['triangles']
def measure(path):
    _,tri=read(path);normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1)
    roof=(tri[:,:,1].max(axis=1)>0)&(normals[:,1]/np.maximum(length,1e-9)<-.1)
    result={'path':str(path),'downward_nonfloor_triangles':int(roof.sum()),'sections':[]}
    for h in [55.,65.,70.,75.]:
        crossing=tri[(tri[:,:,1].min(axis=1)<h)&(tri[:,:,1].max(axis=1)>h)]
        points=[]
        for face in crossing:
            for a,b in zip(face,np.roll(face,-1,axis=0)):
                if (a[1]-h)*(b[1]-h)<0:points.append((a+(b-a)*(h-a[1])/(b[1]-a[1]))[[0,2]])
        points=np.unique(np.round(points,5),axis=0)
        if len(points)<3:continue
        hull=ConvexHull(points);p=points[hull.vertices]
        _,_,axes=np.linalg.svd(p-p.mean(axis=0),full_matrices=False)
        widths=np.ptp((p-p.mean(axis=0))@axes.T,axis=0)
        result['sections'].append({'height_m':h,'xz_span_m':np.ptp(p,axis=0).tolist(),'principal_spans_m':widths.tolist(),'convex_section_area_m2':float(hull.volume)})
    return result
results=[measure(Path('D:/test6/assets/models/cliff_crown.glb')),measure(Path('D:/test6/captures/cliff_sections_crown.glb'))]
Path('D:/test6/captures/round-10-study8-sections.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
