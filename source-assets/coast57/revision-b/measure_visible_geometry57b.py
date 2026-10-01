from visible_geometry_core57b import *
seated=json.loads((D/'scatter-replacements-seated.json').read_text())
foot=json.loads((D/'diagnostics-foot57b/continuous-foot-support57b.json').read_text())
foot_rows={(r['node'],r['index']):r for r in foot['placements']}
results=[]
for r in seated:
    key=(r['node'],r['index']);fr=foot_rows[key]
    before=measure(r,r['before_buffer'],terrain_data[0]);after=measure(r,r['candidate_buffer'],terrain_data[1]);sy=abs(float(r['before_buffer'][5]));m=models[r['node']]
    results.append({'node':r['node'],'index':r['index'],'kind':r['kind'],'affected':fr['affected'],'before':before,'after':after,'after_to_before_above_terrain_area_ratio':after['area_above_terrain_m2']/before['area_above_terrain_m2'],'after_to_before_top_clearance_ratio':after['top_above_terrain_at_root_m']/before['top_above_terrain_at_root_m'],'seat_depth_m':r.get('foot_seat_depth',0.),'seat_fraction_of_original_model_above_root_height':r.get('foot_seat_depth',0.)/(m['max_y']*sy),'penetration_fraction_of_total_model_height':fr['final']['max_penetration_m']/(m['height']*sy),'foot_burial_fraction_of_first_nonzero_tree_layer':fr['final']['max_penetration_m']/(m['first_segment']*sy) if m['first_segment'] else None})
report={'method':'Original rendered mesh triangles clipped against each overlapping actual terrain triangle vertical prism and height plane; reports above-ground surface area and height. This is not a solid-volume estimate or self-occlusion calculation.','source_mesh_caution':'Native rock/bush signed surface volume does not equal convex hull volume; no convex-volume assumption is used. Surface area is derived from the actual native rendered triangles.','placements':results}
(D/'diagnostics-foot57b/visible-geometry57b.json').write_text(json.dumps(report,indent=2)+'\n')
for r in results:
    if r['kind'] in ['rock','bush'] and r['affected']:
        print(r['kind'],r['index'],'seat',round(r['seat_depth_m'],3),'seat/above-root',round(r['seat_fraction_of_original_model_above_root_height'],3),'burial/fullheight',round(r['penetration_fraction_of_total_model_height'],3),'aboveground area old/new',round(r['before']['area_above_terrain_fraction'],3),round(r['after']['area_above_terrain_fraction'],3),'relative area',round(r['after_to_before_above_terrain_area_ratio'],3),'top clearance old/new',round(r['before']['top_above_terrain_at_root_m'],3),round(r['after']['top_above_terrain_at_root_m'],3))
