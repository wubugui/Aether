from pathlib import Path
R=Path(__file__).resolve().parents[1]
def put(p,s):
 assert not p.exists(),str(p);p.write_text(s,encoding='utf-8')
s=(R/'captures/prepare_rightcoast33a.py').read_text(encoding='utf-8').replace('33a','33b')
s=s.replace('from shapely.geometry import Polygon,Point,LineString,mapping','from shapely.geometry import Polygon,Point,LineString,mapping,shape')
start=s.index("origin=np.array(layout['origin']);regions=[]");end=s.index("bound=layout['boundary'];",start)
s=s[:start]+'''origin=np.array(layout['origin'])
actual=read(R/'reviews/round-33-occupied-regions.json')
occupied=shape(actual['hard_occupied_house_and_paving_union']).buffer(.30)
'''+s[end:]
s=s.replace("p=Polygon(v[ids,:2])\n  if p.area>1e-8 and p.intersects(occupied):","p=Polygon(v[ids,:2])\n  xyz=v[ids];normal=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0])\n  if max(xyz[:,2])>0 and normal[2]>1e-7 and p.area>1e-8 and p.intersects(occupied):")
s=s.replace('sitefade=smooth(d/22)','sitefade=smooth((d-8)/30)')
s=s.replace('ridge=max(31*lobe(x,y,-5,-74,66,81,-.30),38*lobe(x,y,-3,83,68,70,.28),28*lobe(x,y,-24,174,42,48,-.24))','ridge=max(18*lobe(x,y,8,-70,81,96,-.40),24*lobe(x,y,12,88,82,90,.35),16*lobe(x,y,-14,180,55,63,-.34))')
s=s.replace('shoulder=7*lobe(x,y,-92,-72,30,34,.20)+9*lobe(x,y,-69,154,30,35,-.3)','shoulder=4*lobe(x,y,-92,-72,30,34,.20)+6*lobe(x,y,-69,154,30,35,-.3)')
s=s.replace('dx=(-5*lobe(x,y,-94,-72,30,38,.2)-6*lobe(x,y,-74,160,26,35,-.3)+3*lobe(x,y,-47,0,30,38))*smooth(d/18)*seamfade*wetfade','dx=(3*lobe(x,y,-94,-72,30,38,.2)-3*lobe(x,y,-74,160,26,35,-.3)+5*lobe(x,y,-47,0,30,38))*smooth((d-2)/22)*seamfade*wetfade')
s=s.replace('Full conservative house pad and every paving-cap intersecting source face preserved.','Full actual house foundation and actual paving occupied upper faces preserved, plus8m no-height-change apron; no buried bottom projection used as a surface freeze region.')
s=s.replace('Nine conservative authored full pads plus all922 paving solid cap projections, 0.20m buffer. All original polygons intersecting this are frozen in full; actual asset footprint containment verified independently.','Independent actual nine foundation and922GLB paving domains,0.30m buffer; intersecting actual upward above-water polygons frozen in full. No hand-rotated pad surrogate.')
s=s.replace('Three unequal oblique inland height lobes31/38/28m additive maximum before site/seam fades; two seaward noses and two low coves.','Three wider offset inland ridges18/24/16m before fades; near-village apron retains old height for8m, gradual30m rise; first coast nose moves shoreward3m, two lowered bays.')
start=s.index("p=R/'captures/rightcoast33b-design-plan.json'")
end=s.index("print(json.dumps",start)
s=s[:start]+'''p=R/'captures/rightcoast33b-design-plan.json';assert not p.exists()
plan['actual_occupied_report_sha256']=sha(R/'reviews/round-33-occupied-regions.json')
plan['rework_reason']='33a visible long thin transitions and overly continuous tall rock slope. Use actual foundation domains, upward source faces only, broader apron and offset lower ridges.33a mistaken reversed design-pad angle and buried-face protection are not copied.'
p.write_text(json.dumps(plan,indent=2),encoding='utf-8')
'''+s[end:]
put(R/'captures/prepare_rightcoast33b.py',s)
put(R/'blender/model_rightcoast_33b.py',(R/'blender/model_rightcoast_33a.py').read_text(encoding='utf-8').replace('33a','33b'))
put(R/'tools/render_rightcoast_33b.py',(R/'tools/render_rightcoast_33a.py').read_text(encoding='utf-8').replace('33a','33b'))
print('33b prepared')
