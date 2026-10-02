"""Pure design-contract checks; never accepts or writes candidate geometry."""
from pathlib import Path
import hashlib,json,math,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
class Rejected(ValueError):pass
def need(v,code):
    if not v:raise Rejected(code)
def signed_gap(new_interval,neighbor_intervals):
    b,t=new_interval;need(math.isfinite(b) and math.isfinite(t) and b<t,'NEW_INTERVAL')
    need(len(neighbor_intervals)>0,'EMPTY_NEIGHBOR')
    last=-math.inf
    for l,u in neighbor_intervals:
        need(math.isfinite(l) and math.isfinite(u) and l<u and l>=last,'ORDERED_DISJOINT_INTERVALS');last=u
    return min(max(b,l)-min(t,u) for l,u in neighbor_intervals)
def classify_rim(distance,origin):
    need(origin=='external-rim.json','INTERNAL_SEAM_IS_NOT_RIM')
    need(math.isfinite(distance) and distance>=0,'DISTANCE')
    return 'core' if distance>=80 else 'rim_return'
def validate(c,b,e):
    need(c['schema']=='cloudbank-l-contact-contract-v3' and c['route']=='B','EXPLICIT_ROUTE_B')
    need(c['selected']=='SkyRegion39/CloudSea_1_1/cloud_sea_46_0_continuous_crown','SELECTED_IDENTITY')
    need(c['frozen_neighbors']==['CloudSea_0_1','CloudSea_1_0','CloudSea_1_2','CloudSea_2_1'] and c['other_roots_frozen']==24,'FROZEN_NEIGHBORS')
    need(c['external_lock']['segments']==203 and len(b['source_segments'])==203,'BOUNDARY_COUNT')
    need(c['external_lock']['source_y_locked'] is False and c['external_lock']['old_positive_area_surface_patches_locked']==[],'NO_OLD_Y_LOCK')
    need(c['released_identity']['old_lower_seam_locked'] is False,'OLD_SEAM_RELEASED')
    g=c['unchanged_gates'];need(g['interior_distance_from_external_rim_m']==80 and g['interior_min_vertical_thickness_m']==120 and g['interior_belly_y_m']==[560,630] and g['world_y_envelope_m']==[533.4189910888672,1057.0673217773438] and g['triangle_ceiling']==5164 and g['new_interior_seam_exception'] is False,'UNCHANGED_GATES')
    v=c['v2_preservation'];need(v['A_xyz_m']==[4140,1005,3910] and v['A_belly_xyz_m']==[4140,570,3910] and v['V2_xyz_m']==[4480,740,4070] and v['definition_sha256']=='4d6e3c1126569e5cb9a9a28204ee04ad467edef7c9e10482e617ca126b4dfc30' and v['old_grid_guard_retained'] is True,'V2_IDENTITY')
    for k,k2 in [('A','A_xyz_m'),('A_belly','A_belly_xyz_m'),('V2','V2_xyz_m')]:need(e['nodes'][k]==v[k2],'EVIDENCE_NODE:'+k)
    w=c['frozen_world'];need(w['anchor_xyz_m']==[3958,0,3667] and w['basis']==[[1,0,0],[0,1,0],[0,0,1]] and w['scale']==[1,1,1],'WORLD_FRAME')
    need(c['contact_contract']['local_witnesses_are_global_proof'] is False,'SAMPLES_NOT_GLOBAL_PROOF')
    stage=c['stage'];need(all(stage[k] is False for k in ['candidate_created','native_allowed','contact_accepted','visual_accepted']) and stage['next_item_requires_independent_review_and_full_plugin_publication_readback'] is True,'STAGE_CLOSED')
    need(e['engine_started'] is False and e['candidate_created'] is False and e['contact_acceptance'] is False and e['visual_acceptance'] is False,'EVIDENCE_SCOPE')
    raw=json.dumps(b,sort_keys=True,separators=(',',':'),allow_nan=False).encode();need(hashlib.sha256(raw).hexdigest()==e['boundary_canonical_sha256'],'BOUNDARY_IDENTITY')
    need(all(r['violations']==[] for r in e['profile_true_rim_checks']),'PROFILE_TRUE_RIM_CONFLICT')
    need(len(e['finite_local_witnesses'])==8,'LOCAL_WITNESS_COUNT')
    comps={name:[] for name in c['frozen_neighbors']}
    for r in e['finite_local_witnesses']:
        need(r['halfwidth_m']>0 and r['halfwidth_m']*math.sqrt(2)<r['all_projected_edge_clearance_m'],'LOCAL_OPEN_SQUARE')
        if 'archived_component' in r:comps[r['neighbor']].append(r['archived_component'])
        interval=r['existential_constant_interval_y_m'];need(560<=interval[0]<=630 and interval[1]-interval[0]>=120 and interval[1]<=g['world_y_envelope_m'][1],'LOCAL_FEASIBLE_INTERVAL')
        gaps=[signed_gap(interval,[q]) for q in r['source_intervals']['neighbor']['corner_intervals_y_m']]
        need(max(gaps)<0 and abs(max(gaps)+r['existential_interval_min_overlap_m'])<1e-8,'LOCAL_VOLUME_OVERLAP')
    need(list(comps.values())==[[1,2,3],[1],[1],[1,2]],'ARCHIVED_COMPONENT_IDENTITIES')
    return {'design_consistent':True,'external_rim_segments':203,'local_affine_squares':8,'whole_candidate_contact_accepted':False,'native_allowed':False}
def candidate_acceptance(_):
    raise Rejected('DESIGN_ONLY_NO_CANDIDATE_ACCEPTANCE_IMPLEMENTATION')
def main():
    c,b,e=[json.loads((HERE/name).read_text()) for name in ['contact-contract.json','external-rim.json','contact-evidence.json']]
    print(json.dumps(validate(c,b,e),indent=2))
if __name__=='__main__':main()
