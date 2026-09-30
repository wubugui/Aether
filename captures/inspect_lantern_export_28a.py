from pathlib import Path
import struct,json
R=Path(__file__).resolve().parents[1]
for name in ['lantern_beam','lantern_halo']:
    raw=(R/'captures/lantern_volume_assets_28a'/(name+'.glb')).read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n])
    print(json.dumps({'asset':name,'nodes':d['nodes'],'position_bounds':[{'min':d['accessors'][p['attributes']['POSITION']].get('min'),'max':d['accessors'][p['attributes']['POSITION']].get('max')} for m in d['meshes'] for p in m['primitives']]},indent=2))
