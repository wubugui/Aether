from pathlib import Path
import json,shapely
from shapely import affinity
from shapely.geometry import Polygon,Point
root=Path(__file__).resolve().parents[1]
d=json.loads((root/'captures/village_paving_design_24i/paving.json').read_text());g=d['groups'][0]
q=Point(-2257.72192382813,-1750.06359863281);hub=(-2254,-1751);row=-3185;col=-2823
x=col*.8+.4*(row%2);z=row*.55;tile=Polygon([(x+.004,z+.004),(x+.796,z+.004),(x+.796,z+.546),(x+.004,z+.546)])
for h in [10.5,10.65]:
    band=shapely.from_geojson(next(r['geojson'] for r in g['grading_bands'] if abs(r['height']-h)<1e-6))
    rotated=affinity.rotate(band,20,origin=hub);cut=rotated.intersection(tile);paver=affinity.rotate(cut,-20,origin=hub)
    clean=shapely.set_precision(paver.simplify(.0005,preserve_topology=True),.001)
    print(json.dumps({'level':h,'valid_band':shapely.is_valid_reason(band),'valid_rotated':shapely.is_valid_reason(rotated),'valid_paver':shapely.is_valid_reason(paver),'band_precision':shapely.get_precision(band),'rotated_precision':shapely.get_precision(rotated),'rotated_point_covers':rotated.covers(affinity.rotate(q,20,origin=hub)),'tile_covers':tile.covers(affinity.rotate(q,20,origin=hub)),'band_contains_q':band.covers(q),'band_distance':band.distance(q),'cut_area':cut.area,'paver_covers':paver.covers(q),'clean_covers':clean.covers(q),'paver_wkt':paver.wkt,'clean_wkt':clean.wkt},indent=2))

