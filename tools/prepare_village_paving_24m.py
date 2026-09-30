"""Keep24j bedding; clip rotated simple tile rectangles against stationary valid road bands."""
from pathlib import Path
from collections import Counter
import ast,json,math,hashlib,copy
import shapely
from shapely.geometry import Polygon,Point
from shapely import affinity
root=Path(__file__).resolve().parents[1];source=root/'captures/village_paving_design_24j/paving.json'
out=root/'captures/village_paving_design_24m';assert not out.exists();out.mkdir()
data=json.loads(source.read_text());data['label']='24m'
# Reuse the reviewed ring/cap serializer only, without executing old preparation.
module=ast.parse((root/'tools/prepare_village_paving_24i.py').read_text())
functions=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in ['pieces','solid','component_solid']]
exec(compile(ast.Module(body=functions,type_ignores=[]),'reviewed-solid-serializer','exec'))
repairs=[];outside=[]
def cap(s):return shapely.union_all([Polygon([s['vertices_xz'][i] for i in t]) for t in s['cap_triangles']])
for group in data['groups']:
    foundations=[s for s in group['solids'] if s['kind']=='foundation'];levels={}
    for s in foundations:levels.setdefault(round(s['top_y']+.012,7),[]).append(cap(s))
    solids=list(foundations);hub=(-2254,-1751) if group['name']=='foreground' else (-2238,-1878)
    angle=-20 if group['name']=='foreground' else -10
    for height,polys in sorted(levels.items()):
        band=shapely.union_all(polys);assert band.is_valid
        # Rotation is used for a bounding box only. All boolean operations use
        # the original valid band and convex, independently rotated rectangles.
        bx,bz,ex,ez=affinity.rotate(band,-angle,origin=hub).bounds
        for row in range(math.floor(bz/.55),math.ceil(ez/.55)):
            offset=.4*(row%2)
            for col in range(math.floor((bx-offset)/.8),math.ceil((ex-offset)/.8)):
                x=col*.8+offset;z=row*.55
                tile=affinity.rotate(Polygon([(x+.004,z+.004),(x+.796,z+.004),(x+.796,z+.546),(x+.004,z+.546)]),angle,origin=hub)
                assert tile.is_valid
                cuts=band.intersection(tile);assert cuts.is_valid
                for piece_index,poly in enumerate(pieces(cuts)):
                    if poly.area<.022:continue
                    name=group['name']+' worn limestone %.3f %d %d cut%d'%(height,row,col,piece_index)
                    items=solid(poly,height,height-.10,'paver',1+(row+col)%4,name)
                    for item in items:
                        degrees=Counter(i for edge in item['boundary_edges'] for i in edge)
                        bad=[i for i,count in degrees.items() if count!=2]
                        if bad:
                            geometry=cap(item)
                            patched=shapely.set_precision(shapely.union_all([geometry]+[Point(item['vertices_xz'][i]).buffer(.003,quad_segs=1) for i in bad]),.001)
                            replacements=[component_solid(p,height,height-.10,'paver',item['material'],item['name']+' filled contact') for p in pieces(patched)]
                            repairs.append({'name':item['name'],'contact_points':[item['vertices_xz'][i] for i in bad]})
                        else:replacements=[item]
                        for repaired in replacements:
                            degrees=Counter(i for edge in repaired['boundary_edges'] for i in edge);assert all(n==2 for n in degrees.values()),repaired['name']
                            polygon=cap(repaired)
                            # Allow only the explicit <=3mm contour contact fill,
                            # never the large region inversion found in24j.
                            escape=polygon.difference(band.buffer(.0031)).area
                            assert escape<1e-8,('Paver left its authored level',repaired['name'],escape)
                            outside.append(polygon.difference(band).area)
                            solids.append(repaired)
    group['solids']=solids
    print(group['name'],len(solids),'editable solids; bedding unchanged',flush=True)
data.update(source_24j_design_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),unchanged_bedding_from='24j',paver_contact_repairs=repairs,maximum_paver_area_outside_original_bedding_m2=max(outside),scope='24j authored bedding and street grades retained; simple tile rectangles rotated into world coordinates and clipped there. This avoids rotation-induced invalid complex polygons. Actual meshes and GPU remain to verify.')
(out/'paving.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
