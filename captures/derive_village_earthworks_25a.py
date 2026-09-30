from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'tools/prepare_village_grading.py').read_text(encoding='utf-8')
code=code.replace("label=sys.argv[1];", "label='25a';")
code=code.replace("root/'captures'/('village_paving_design_'+label)/'paving.json'", "root/'captures/village_paving_design_24m/paving.json'")
old="    collar=local(shapely.from_geojson(g['grading_footprint_geojson']))"
new="""    # Keep the house-foundation exclusions of the reviewed grading design.
    original_collar=local(shapely.from_geojson(g['grading_footprint_geojson']))
    houses=[h for h in layout['houses'] if h['name'].startswith('fore_' if g['name']=='foreground' else 'bay_')]
    protected=[]
    for house in houses:
        wx,wz=(3.9,5.4) if house['asset']=='keeper_house' else ((3.26,4.1) if house['asset']=='fisher_cottage' else (4.4,3.4))
        c,s=math.cos(house['yaw']),math.sin(house['yaw']);hx,_,hz=house['position']
        protected.append(Polygon([(hx-origin[0]+c*u+s*v,hz-origin[2]-s*u+c*v) for u,v in [(-wx,-wz),(wx,-wz),(wx,wz),(-wx,wz)]]).buffer(.025,join_style=2))
    collar=foot.buffer(4.,quad_segs=6).difference(shapely.union_all(protected)).intersection(domain)
    assert collar.intersection(shapely.union_all(protected)).area<1e-6
"""
assert old in code;code=code.replace(old,new)
code=code.replace('ceiling=min(h-.06+.5*poly.distance(point) for h,poly in bands)','ceiling=min(h-.06+.5*poly.distance(point) for h,poly in bands)-.5*distance')
code=code.replace("'scope':'Conforming original-edge and street-band subdivision. New native heights must be evaluated against original editable Blender core; no GPU or art acceptance.'", "'earth_fill_enabled':True,'earth_fill_outer_width_m':4.,'paving_candidate':'24m','prior_graded_headland':'24l','scope':'Conforming original-edge and actual street-band subdivision for cut-and-fill earthworks around reviewed24m paving. Original house foundations excluded; old shore/bottom/side mesh retained in Blender. Four metre outer blending is an art proposal, not yet visually accepted.'")
(root/'tools/prepare_village_grading_25a.py').write_text(code,encoding='utf-8')
code=(root/'blender/grade_headland_for_village.py').read_text(encoding='utf-8')
old='    for ceiling,weight in constraints:height=min(height,old_height+weight*(min(old_height,ceiling)-old_height))'
new="""    for ceiling,weight in constraints:
        target=ceiling if design.get('earth_fill_enabled',False) else min(old_height,ceiling)
        proposed=old_height+weight*(target-old_height)
        height=proposed if len(constraints)==1 else min(height,proposed)"""
assert old in code;code=code.replace(old,new)
code=code.replace("'cut_m':old_height-height", "'cut_m':max(0.,old_height-height),'fill_m':max(0.,height-old_height)")
code=code.replace("'scope':'Editable local ground cuts under authored road bands.", "'earth_fill_enabled':design.get('earth_fill_enabled',False),'scope':'Editable local cut-and-fill terrain around authored road bands.")
(root/'blender/grade_village_earthworks_25a.py').write_text(code,encoding='utf-8')
