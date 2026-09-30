"""Validate real asset geometry and that no photographic world material is packed."""
from pathlib import Path
import json,struct
ROOT=Path(__file__).resolve().parents[1]
def glb(path):
    data=path.read_bytes();size=struct.unpack_from('<I',data,12)[0]
    return json.loads(data[20:20+size])
files=[ROOT/'assets/open_world.glb',ROOT/'assets/airship.glb',ROOT/'assets/propeller.glb',*sorted((ROOT/'assets/models').glob('*.glb'))]
report=[]
for path in files:
    doc=glb(path);mins=[];maxs=[];triangles=0
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            position=doc['accessors'][primitive['attributes']['POSITION']]
            mins.append(position['min']);maxs.append(position['max'])
            count=doc['accessors'][primitive['indices']]['count'] if 'indices' in primitive else position['count']
            triangles+=count//3
    extent=[max(v[i] for v in maxs)-min(v[i] for v in mins) for i in range(3)]
    assert all(v>.01 for v in extent),(path,'flat model')
    assert not doc.get('images') and not doc.get('textures'),(path,'world image texture')
    report.append(dict(file=str(path.relative_to(ROOT)),meshes=len(doc['meshes']),triangles=triangles,local_extent=extent,image_textures=0))
layout=json.loads((ROOT/'assets/world_layout.json').read_text())
assert len(layout['chunks'])==208
assert len(layout['ports'])==6
result=dict(passed=True,assets=report,terrain_chunks=len(layout['chunks']),model_placements=len(layout['props']),ports=len(layout['ports']),world_uses_photographic_textures=False)
(ROOT/'captures/asset-validation.json').write_text(json.dumps(result,indent=2))
print('ASSET VALIDATION PASS:',len(report),'3D GLBs, zero world image textures,',len(layout['props']),'placements')
