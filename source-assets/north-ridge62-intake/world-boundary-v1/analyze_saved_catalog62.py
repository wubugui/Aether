#!/usr/bin/env python3
"""Reconcile immutable failed-run saved bounds only; no Godot or live-world claim."""
from __future__ import annotations
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AETHER = HERE.parents[2]
RUN = AETHER / 'cloud-evidence/north-ridge62-collect-20261002T050835Z-k8_cwtci'

def require(ok, reason):
    if not ok: raise ValueError(reason)

def overlap(bounds, box):
    a,b=bounds['min'],bounds['max']
    return b[0]>=box[0] and a[0]<=box[1] and b[2]>=box[2] and a[2]<=box[3]

def axis_overlap(bounds, box, axis):
    q=0 if axis==0 else 2
    return bounds['max'][axis]>=box[q] and bounds['min'][axis]<=box[q+1]

def union(records):
    return {'min':[min(r['whole_bounds']['min'][i] for r in records) for i in range(3)],
            'max':[max(r['whole_bounds']['max'][i] for r in records) for i in range(3)]}

def compact(row):
    return {k:row[k] for k in ['root','whole_bounds','whole_bounds_plus_40m_xz','hits_design','hits_query']} | {'part_count':len(row['parts']),'part_paths':[p['path'] for p in row['parts']]}

def main():
    raw=(RUN/'native-intake.json').read_bytes() if (RUN/'native-intake.json').exists() else gzip.decompress((RUN/'native-intake.json.gz').read_bytes())
    require(len(raw)==1211462,'immutable input length changed')
    require(hashlib.sha256(raw).hexdigest()=='bd48c7ccbaee51cbf43dba1efeac7a78957de59166eeafcecddbfb1038744b04','immutable input SHA changed')
    data=json.loads(raw)
    require(data['issues']==[{'class':'WorldBoundaryShape3D','kind':'unbounded_saved_shape','path':'World/Ocean/SeaCollision/Shape'}],'historical failure changed')
    require(data['saved_data_read_complete'] is False and data['all_occupancy_complete'] is False,'historical failure status changed')
    catalog=data['settlement_identity_catalog']; query=data['query_box_with_40m']; design=data['design_box']
    require(len(catalog)==172 and len({r['root'] for r in catalog})==172,'172 unique identities required')
    for row in catalog:
        b=row['whole_bounds'];parts=row['parts']
        require(parts and b is not None,'unsupported saved settlement')
        merged={'min':[min(p['bounds']['min'][i] for p in parts) for i in range(3)],'max':[max(p['bounds']['max'][i] for p in parts) for i in range(3)]}
        require(merged==b,'whole bounds do not equal all-part union: '+row['root'])
        require(overlap(b,query)==row['hits_query'] and overlap(b,design)==row['hits_design'],'stored hit mismatch')
    west=[r for r in catalog if axis_overlap(r['whole_bounds'],query,2) and r['whole_bounds']['max'][0]<query[0]]
    east=[r for r in catalog if axis_overlap(r['whole_bounds'],query,2) and r['whole_bounds']['min'][0]>query[1]]
    xhits=[r for r in catalog if axis_overlap(r['whole_bounds'],query,0)]
    require(len(west)==12 and len(east)==12 and not xhits,'unexpected spatial split')
    require([r['root'].split('/')[-1] for r in west]==[f'cottage_{i}' for i in range(57299,57311)],'west catalog identities changed')
    query_entities=[]
    for row in data['entities']:
        b=row['whole_bounds']
        require(overlap(b,query),'reported query entity no longer overlaps')
        p=[r['path'] for r in row['parts'] if overlap(r['bounds'],query)]
        query_entities.append(compact(row)|{'part_query_hits':len(p),'part_query_hit_paths':p,
          'whole_group_only_hit':not p,'interpretation':'Conservative whole-group AABB; not exact occupied volume or live visibility.'})
    def cluster(items, side):
        b=union(items)
        return {'selection':f'All saved catalog bounds overlapping query Z and entirely {side} of query X; no nearest-N selection.',
          'historical_northern_12_identity_proved':False,'count':len(items),'union_bounds':b,
          'minimum_x_gap_to_query_m':query[0]-b['max'][0] if side=='west' else b['min'][0]-query[1],
          'minimum_x_gap_to_design_m':design[0]-b['max'][0] if side=='west' else b['min'][0]-design[1],
          'identities':[compact(r) for r in items]}
    summary={'status':'analysis_of_failed_saved_native_run_only','input':str((RUN/'native-intake.json').relative_to(AETHER)),
      'input_bytes':len(raw),'input_sha256':hashlib.sha256(raw).hexdigest(),
      'historical_issue':data['issues'][0],'historical_failure_preserved':True,
      'design_box':design,'query_box_with_40m':query,'saved_catalog_count':len(catalog),
      'saved_catalog_type_counts':dict(Counter(r['root'].split('/')[-1].rsplit('_',1)[0] for r in catalog)),
      'all_saved_settlement_part_unions_recomputed':True,'settlement_x_overlap_count':len(xhits),
      'settlement_z_overlap_count':len(west)+len(east),'settlement_query_hit_count':sum(r['hits_query'] for r in catalog),
      'bounded_query_entity_count':len(query_entities),'bounded_query_entities':query_entities,
      'west_z_overlapping_cluster':cluster(west,'west'),'east_z_overlapping_cluster':cluster(east,'east'),
      'expected_northern_12_identity_proved':False,'saved_catalog_is_house_count':False,
      'scatter_unresolved_count':len(data['scatter_unresolved']),'curves_count':len(data['curves']),
      'runtime_generated_entities_proved':False,'all_occupancy_complete':False,
      'scope':'Saved complete-part conservative AABBs only. No scatter placement, runtime membership, road width, terrain-edit footprint, visibility or collision clearance is established.'}
    (HERE/'saved-catalog-analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
    (HERE/'saved-settlement-catalog.json').write_text(json.dumps({'input_sha256':summary['input_sha256'],'identities':[compact(r) for r in catalog]},indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ['input_sha256','saved_catalog_count','settlement_x_overlap_count','settlement_z_overlap_count','settlement_query_hit_count','bounded_query_entity_count','all_occupancy_complete']},indent=2))

if __name__=='__main__': main()
