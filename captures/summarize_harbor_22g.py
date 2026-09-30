from pathlib import Path
import json
from PIL import Image
root=Path(__file__).resolve().parents[1]
run=root/'captures/validation_runs/harbor-assembly-22g-20260908T112011Z-00f0a7b4c813446e842b280476463e21'
manifest=json.loads((run/'manifest.json').read_text(encoding='utf-8'));assert manifest['passed']
views=[]
for file in sorted((run/'images').glob('*.png.json')):
    data=json.loads(file.read_text(encoding='utf-8'));harbor=data['harbor_study'];paths=harbor['stone_paths'];checks=paths['runtime_checks']
    assert data['run_id']==manifest['run_id'] and checks['passed']
    boats=[]
    for boat in harbor['boat_ground_samples']:
        modes=[]
        for mode in ['previous_22a','candidate_22g']:
            samples=[p for p in boat['samples'] if p['placement']==mode];known=[p['clearance_m'] for p in samples if p['clearance_m'] is not None]
            modes.append({'placement':mode,'samples':len(samples),'known_ground_hits':len(known),'min_clearance_m':min(known) if known else None,'negative_clearances':sum(p<0 for p in known)})
        boats.append({'node':boat['node'],'modes':modes})
    tops=[p for path in checks['paths'] for p in path['treads']];bases=[p for path in checks['paths'] for p in path['foundations']]
    png=Path(str(file)[:-5]);size=list(Image.open(png).size)
    views.append({'view':file.name.removesuffix('.png.json'),'size':size,'path_count':len(checks['paths']),'top_probes':len(tops),'bottom_original_ground_pairs':len(bases),'max_top_height_error_m':max(abs(p['error_m']) for p in tops),'foundation_gap_range_m':[min(p['gap_m'] for p in bases),max(p['gap_m'] for p in bases)],'lights':len(harbor['lights']),'path_lamps':len(paths['lamp_sites']),'removed_scatter_instances':sum(len(g['removed_from_temporary_copy']) for g in paths['vegetation_adjustments']),'boat_ground_evidence':boats})
model=json.loads((root/'captures/harbor_paths_study_22f/model-report.json').read_text(encoding='utf-8'))
summary={'run_id':manifest['run_id'],'status':'limited_candidate_progress_not_art_accepted','root_directly_viewed_all_seven_pngs':True,'scope':'Four Blender stone approaches and sampled boat grounding correction in the same temporary20l/21c world. No production install, audio, all-face clearance, full movement or all-reference acceptance.','native_parts':sum(a['parts'] for a in model['assets']),'routes':[{'asset':r['asset'],'length_m':r['length_m'],'cells':len(r['cells']),'landing_groups':len(r['landing_groups']),'start_y':r['start_top_y'],'end_y':r['end_top_y'],'max_riser_m':r['max_riser_m']} for r in model['routes']],'views':views,'next_visual_priority':'Reference1342 near-right rocky headland and clustered coastal villages. Current long stairs to isolated identical houses on an empty straight grass coast remain visually rejected.'}
output=root/'reviews/round-22g-root-evidence.json';assert not output.exists();output.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'parts':summary['native_parts'],'routes':summary['routes'],'views':[{k:v for k,v in view.items() if k!='boat_ground_evidence'} for view in views]},ensure_ascii=False,indent=2))
