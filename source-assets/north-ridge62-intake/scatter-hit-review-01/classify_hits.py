#!/usr/bin/env python3
"""Offline classification of a fixed completed native report. No engine or project writes."""
import collections
import gzip
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent
PROJECT = ROOT / 'candidates/round40-exclusive-20260930/project'
RUN = 'cloud-evidence/north-ridge62-scatter-float32-collect-20261002T065622Z-6k1gbidm'
BASE = 'cloud-evidence/north-ridge62-collect-20261002T053100Z-3mmbw0ol/native-intake.json'
RAW_SHA = '62482b889a2dc6c5687274748397f5d4bf9da3be6898b8fbca6d372a5a2452bf'
PINS = {}
CHECKS = []

def require(condition, label):
    if not condition:
        raise RuntimeError(label)
    CHECKS.append(label)

def read(path, expected=None):
    path = pathlib.Path(path)
    b = path.read_bytes()
    sha = hashlib.sha256(b).hexdigest()
    if expected is not None:
        require(sha == expected, 'source identity: ' + str(path.relative_to(ROOT)))
    PINS[str(path.relative_to(ROOT))] = {'bytes': len(b), 'sha256': sha}
    return b

def local(uri):
    require(uri.startswith('res://'), 'resource URI: ' + uri)
    return PROJECT / uri[6:].split('::', 1)[0]

def intersects(bounds, box):
    lo, hi = bounds['min'], bounds['max']
    return hi[0] >= box[0] and lo[0] <= box[1] and hi[2] >= box[2] and lo[2] <= box[3]

def inside(point, box):
    return box[0] <= point[0] <= box[1] and box[2] <= point[2] <= box[3]

def union(rows):
    return {'min': [min(r['min'][a] for r in rows) for a in range(3)],
            'max': [max(r['max'][a] for r in rows) for a in range(3)]}

def main():
    read(pathlib.Path(__file__).resolve())
    raw = read(ROOT / RUN / 'native-scatter.json', RAW_SHA)
    stored = read(ROOT / RUN / 'native-scatter.json.gz', 'c84be8b53195ddd894c52f37b2b111fbbef4b0d7bdb2536e9a5e7a724773e8ba')
    require(gzip.decompress(stored) == raw, 'lossless raw/gzip byte identity')
    d = json.loads(raw)
    w = json.loads(read(ROOT / RUN / 'wrapper-report.json'))
    require(w['passed'] and w['native_collection_passed'] and w['native_scatter_sha256'] == RAW_SHA, 'completed native wrapper and raw binding')
    require(not w['changed_inputs'] and not w['log_errors'], 'native wrapper unchanged inputs and no log errors')
    require(d['status'] == 'complete' and not d['issues'] and d['saved_data_read_complete'], 'complete saved read, no issues')
    require(len(d['groups']) == 775 and sum(g['instance_count'] for g in d['groups']) == 57797, '775 groups / 57797 saved instances')
    require(all(g['saved_data_complete'] and g['transform_identity']['passed'] for g in d['groups']), 'all saved groups and exact transform checks passed')
    require(not d['all_occupancy_complete'], 'original complete occupancy flag stays false')
    base = json.loads(read(ROOT / BASE, d['baseline_native_intake_sha256']))
    dep = json.loads(read(ROOT / 'source-assets/north-ridge62-intake/DEPENDENCY_REVIEW.json'))
    read(ROOT / 'source-assets/north-ridge62-intake/plan.json')
    read(ROOT / RUN / 'collect_scatter62.gd')
    read(ROOT / RUN / 'transform-float32-identities.json', d['expected_transform_bytes_sha256'])
    read(ROOT / RUN / 'prepared-inputs.json.gz')
    read(ROOT / RUN / 'storage.json')
    nodes = {}
    text_sources = {}
    for uri, sha in d['scene_sources'].items():
        text = read(local(uri), sha).decode()
        text_sources[uri] = text
        ext = dict(re.findall(r'^\[ext_resource[^\n]*path="([^"]+)"[^\n]*id="([^"]+)"\]', text, re.M))
        ext = {v:k for k,v in ext.items()}
        for m in re.finditer(r'^\[node name="([^"]+)"[^\n]*parent="([^"]+)"[^\n]*\]\n([\s\S]*?)(?=^\[|\Z)', text, re.M):
            name, parent, body = m.groups()
            path = (parent + '/' + name).lstrip('./')
            dest = nodes.setdefault(path, {})
            for ln in body.splitlines():
                if ' = ' not in ln:
                    continue
                key, value = ln.split(' = ', 1)
                match = re.fullmatch(r'ExtResource\("([^"]+)"\)', value)
                dest[key] = {'value': value, 'resolved': ext.get(match[1]) if match else None, 'source': uri}
    hits = [g for g in d['groups'] if g['query_instance_count']]
    require(len(hits) == 33, '33 query-hit groups')
    summaries = collections.defaultdict(lambda: {'groups':0, 'query':0, 'design':0, 'buffer_only':0})
    results = []
    root_misses = {'query':0, 'design':0}
    for g in hits:
        props = nodes[g['path']]
        species = pathlib.PurePosixPath(g['model_scene_runtime_binding']).stem
        require(species in ['pine','oak','poplar','rock','bush'], 'known model class: '+g['path'])
        require(json.loads(props['metadata/asset_kind']['value']) == species, 'metadata matches model binding: '+g['path'])
        require(props['model_scene']['resolved'] == g['model_scene_runtime_binding'], 'saved prefab binding: '+g['path'])
        require(props['script']['resolved'] == 'res://scripts/scatter_group.gd', 'saved scatter script: '+g['path'])
        require(g['saved_visible'] and g['saved_visible_instance_count'] == -1, 'saved visible/all allocated instances: '+g['path'])
        require(g['path'].startswith('World/Vegetation/') and not g['material_overlay'], 'vegetation branch and no overlay: '+g['path'])
        require(g['material_override'] == 'res://scenes/candidate53d-west/Game53dWest.tscn::ShaderMaterial_4hw14', 'one effective saved override: '+g['path'])
        read(local(g['resource']), g['source']['source_sha256'])
        mesh = d['mesh_resources'][g['mesh_resource']]
        read(local(mesh['source_file']), mesh['source_sha256'])
        canonical = d['mesh_resources']['res://assets/meshes/' + species + '.res']
        read(local(canonical['source_file']), canonical['source_sha256'])
        require(mesh['surface_storage_sha256'] == canonical['surface_storage_sha256'], 'actual mesh surface identity matches class: '+g['path'])
        rows = g['instances_overlapping_query']
        require(len(rows) == g['query_instance_count'], 'query row count: '+g['path'])
        require(sum(i['hits_design'] for i in rows) == g['design_instance_count'], 'design row count: '+g['path'])
        for i in rows:
            require(intersects(i['world_bounds_including_shadow'],d['query_box_with_40m']), 'query rectangle predicate: '+g['path']+'/'+str(i['index']))
            require(intersects(i['world_bounds_including_shadow'],d['design_box']) == i['hits_design'], 'design rectangle predicate: '+g['path']+'/'+str(i['index']))
            root_misses['query'] += not inside(i['world_origin'],d['query_box_with_40m'])
            root_misses['design'] += i['hits_design'] and not inside(i['world_origin'],d['design_box'])
        for key,val in [('groups',1),('query',len(rows)),('design',g['design_instance_count']),('buffer_only',len(rows)-g['design_instance_count'])]:
            summaries[species][key] += val
        results.append({
            'path':g['path'], 'class':species, 'class_evidence':'bound mesh + resolved saved prefab + effective metadata/asset_kind; not group name',
            'mesh_resource':g['mesh_resource'], 'mesh_surface_storage_sha256':mesh['surface_storage_sha256'],
            'model_scene':g['model_scene_runtime_binding'], 'metadata_source':props['metadata/asset_kind']['source'],
            'saved_resource':g['resource'], 'saved_resource_sha256':g['source']['source_sha256'],
            'buffer_sha256':g['buffer_sha256'], 'saved_property_source':g['saved_property_source'],
            'query_count':len(rows), 'design_count':g['design_instance_count'],
            'query_indices':[i['index'] for i in rows], 'design_indices':[i['index'] for i in rows if i['hits_design']],
            'buffer_only_indices':[i['index'] for i in rows if not i['hits_design']],
            'hit_union_summary_not_a_keepout_polygon':union([i['world_bounds_including_shadow'] for i in rows]),
            'root_y_range':[min(i['world_origin'][1] for i in rows),max(i['world_origin'][1] for i in rows)],
            'saved_visible':g['saved_visible'], 'saved_visible_instance_count':g['saved_visible_instance_count'],
            'source_collision_rule':'none (bush skip)' if species == 'bush' else ('tree capsule r=2.4 h=11, center Y=5.5' if species in ['oak','pine','poplar'] else 'rock first imported prefab mesh faces'),
            'runtime_collision_observed':False,
            'whole_tile_protected_neighbor':g['path'].endswith('_-5_-5') or '_-5_-5_CoastalPines36b' in g['path'],
            'raw_rows_locator':{'array':'groups','path_match':g['path'],'instances_array':'instances_overlapping_query','index_field':'index'}
        })
    expected={'poplar':(4,33,22),'oak':(4,79,48),'rock':(8,142,123),'bush':(7,62,52),'pine':(10,360,330)}
    require(all(tuple(summaries[k][i] for i in ['groups','query','design']) == v for k,v in expected.items()), 'all five class totals exact')
    require(sum(g['query_count'] for g in results)==676 and sum(g['design_count'] for g in results)==575, '676 query / 575 design / 101 buffer-only hits')
    require(root_misses == {'query':8,'design':8}, 'root-only filters would miss 8 query and 8 design hits')
    require(nodes['World']['script']['resolved'] == 'res://scripts/world39.gd', 'effective world script uses reviewed runtime path')
    shader_material=d['material_resources']['res://scenes/candidate53d-west/Game53dWest.tscn::ShaderMaterial_4hw14']
    require(not shader_material['next_pass'], 'effective override has no next pass')
    src=text_sources['res://scenes/candidate53d-west/Game53dWest.tscn']
    shader=re.search(r'\[sub_resource type="Shader" id="Shader_pk3vb"\]\n([\s\S]*?)(?=\n\[)',src)[1]
    material=re.search(r'\[sub_resource type="ShaderMaterial" id="ShaderMaterial_4hw14"\]\n([\s\S]*?)(?=\n\[)',src)[1]
    require('shader_parameter/cloud_drift = false' in material, 'saved cloud_drift false')
    require('if(cloud_drift)VERTEX.x+=sin(world_time*.018)*9.;' in shader and shader.count('VERTEX.x')==1, 'specific conditional vertex write present')
    for rel in ['scripts/scatter_group.gd','scripts/open_world.gd','scripts/world39.gd','scripts/asset_instance.gd','scripts/environment42b.gd','assets/asset_catalog.json','assets/models/rock.glb','assets/models/rock.glb.import'] + ['scenes/prefabs/'+s+'.tscn' for s in expected]:
        uri='res://'+rel
        pinned=dep['files'].get(uri)
        expected_sha=pinned.get('sha256') if isinstance(pinned,dict) else None
        read(PROJECT/rel,expected_sha)
    imported='res://.godot/imported/rock.glb-9fe9ded640b9e8b845c59e36f0f83d1b.scn'
    read(local(imported))
    sg=(PROJECT/'scripts/scatter_group.gd').read_text()
    require(not re.search(r'^func _(ready|process|physics_process)\(',sg,re.M), 'scatter_group has no automatic lifecycle callback')
    require(not any(e['hits_query'] for e in base['settlement_identity_catalog']), 'all 172 saved settlement entries have no query AABB hit')
    require(not any(c['hits_query'] for c in base['curves']), 'all 3 saved curve control hulls have no query hit')
    original_false={k:d[k] for k in ['all_occupancy_complete','runtime_generated_entities_proved','runtime_model_scene_and_collision_proved','shader_deformation_envelopes_proved','road_width_proved','vertex_payload_bounds_independently_recomputed','visual_acceptance']}
    require(not any(original_false.values()), 'all original unproved/acceptance flags retained false')
    doc={
        'status':'completed_offline_source_bound_hit_classification_no_engine',
        'raw_report':RUN+'/native-scatter.json','raw_sha256':RAW_SHA,
        'published_report_commit_as_supplied_by_parent':'d01f8a19 (not Git-verified by this worker)',
        'design_box_xmin_xmax_zmin_zmax':d['design_box'],'query_box_with_40m':d['query_box_with_40m'],
        'counts':{'all_saved_groups':775,'all_saved_instances':57797,'hit_groups':33,'query_instances':676,'design_instances':575,'buffer_only_instances':101},
        'classes':dict(summaries),'root_only_false_negatives':root_misses,
        'saved_render_binding':{'all_hit_groups_visible':True,'all_visible_instance_count_minus_one':True,'material_override':shader_material['resource'],'shader_resource':shader_material['shader']['resource'],'shader_code_utf8_sha256_as_recorded_by_native':shader_material['shader_code_utf8_sha256'],'saved_cloud_drift':False,'saved_vertex_displacement_for_this_branch':'zero; conditional X displacement is disabled','next_pass':'','scope':'saved source state, not a live material-state observation'},
        'source_runtime_path':{'world_script':'res://scripts/world39.gd','base_script':'res://scripts/open_world.gd','ready_lines':'35-76: reads metadata/asset_kind and full saved composed transforms into layout.props/prop_transforms','collision_lines':'289-331: nearby index selection; bush skip; tree capsule or prefab first-mesh triangle collision; exact saved transform applied','activation':'source rule: 3x3 focus-cell neighborhood, horizontal root distance <=350m, |focus.y-root.y|<=150m; refreshed after >0.4s; presence depends on focus, not proved by saved read','tree_local_proxy_aabb':{'min':[-2.4,0,-2.4],'max':[2.4,11,2.4]},'tree_query_candidate_count':472,'tree_design_candidate_count':400,'rock_query_candidate_count':142,'rock_design_candidate_count':123,'bush_query_visual_only_count':62,'bush_design_visual_only_count':52,'model_scene_role':'editor extract_selected only in scatter_group; not the runtime collision switch','runtime_source_effect_observed':False},
        'footprint_interpretation':[
            '575 design hits constrain any actual changed footprint by per-instance whole visual bounds and terrain support. 101 buffer-only hits protect transition/edge work; neither count authorizes removal or moving entire groups.',
            'Pines dominate with 330 design hits. Two -4_-6 pine groups contribute 260; these are existing authored groves, not generic oak/poplar from their names.',
            'Bushes remain visual/support constraints despite source collision skip. Rocks are bounded saved rock meshes, not houses or terrain. All hit origins must be reconciled against changed terrain before moving, retaining or replacing them.',
            'Two buffer-only coast61 hits (one bush, one pine) belong to the protected -5_-5 neighbor resources; preserve the whole protected tile and its existing adjustment work.',
            'Group union boxes in this report are summaries only. Retrieve precise saved bounds/transforms with the raw path+instance-index locator; do not flatten groves into a blanket exclusion rectangle.'
        ],
        'other_intake_context':{'source':BASE,'saved_settlement_count':172,'saved_settlement_query_hits':0,'historical_northern_12_identity_proved':False,'curve_count':3,'curve_control_hull_query_hits':0,'road_width_proved':False,'warning':'This does not erase the four non-scatter saved hit entities: ocean, native cloud bank, rainbow and coastal-storm union. Their nature/height and state need separate footprint/composition treatment; weather unions are not ground-building exclusions.'},
        'smallest_useful_next_bounded_read':[
            'Qualify actual source-specific collision footprints: use the existing proved saved buffers and metadata to compute transformed tree capsule envelopes, and read just the rock prefab first imported mesh and its actual face/vertex extent. Do not substitute the saved rock visual mesh or assets/collision/rock.res without proving identity: runtime uses model_meshes[kind] from the prefab first mesh.',
            'Re-query the union of visual and collision envelopes from the relevant proved saved buffers, including groups just outside the visual query; checking only these 676 rows could miss a proxy-only intersection. The source formulas are a bounded prediction, not proof that live colliders are present.',
            'For ground support, retain exact source mesh/transform identifiers; independently read vertex payload extrema for the few bound geometries and shadows when needed for the exact edited footprint. Six bound resource identities here reduce to five recorded primary surface-storage hashes (pine is duplicated). No new full-world export is needed.',
            'Stop this read when there is a path/index-keyed conservative visual+source-collision keep/reconcile list and exact rock-source identity, then draw the first constrained mountain footprint with the 16 tile/border protections. A later bounded live snapshot at that footprint remains necessary before claiming runtime clearance. Do not block conceptual design on universal shader/model replacement audits unsupported by current source.'
        ],
        'priorities_not_expanded_now':[
            'The actual hit shader has saved cloud_drift=false, no overlay and no next pass. A generic deformation audit is not the leading new uncertainty for these 33 groups; saved-state review is not a live-state guarantee.',
            'No saved settlement or curve control hull hits this query. Keep the old 12-house claim unproved instead of selecting the nearest 12; do not launch a general road/world audit solely because the legacy boolean is false.'
        ],
        'original_unproved_flags_unchanged':original_false,'engines_started':0,'project_or_orbit_inputs_written':False,
        'source_pins':PINS,'checks_passed_count':len(CHECKS),'groups':results
    }
    # Recheck every consulted source immediately before output; concurrent changed inputs fail closed.
    for rel,pin in PINS.items():
        require(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==pin['sha256'],'final source unchanged: '+rel)
    doc['checks_passed_count']=len(CHECKS)
    (OUT/'classification.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    lines=['# North-ridge62 scatter hit classification','',
      'Completed offline, source-bound review. No engine, project/terrain/asset/orbit edits, Git, CLOUD_RESUME or Slack actions.', '',
      f'Raw native report: `{RUN}/native-scatter.json`',f'SHA256: `{RAW_SHA}`. Its lossless gzip was byte-compared to the raw report. All source pins and exact group/index membership are in `classification.json`.', '',
      '## What constrains the footprint','',
      '33 groups contain 676 saved whole-bound-mesh AABB query hits: 575 intersect the design rectangle and 101 only its 40 m buffer. All 33 are saved visible World/Vegetation groups with all allocated instances visible. These are bounds hits, not confirmed terrain contacts, deletion permission or a final edit footprint.', '',
      '| Actual binding class | Groups | Query | Design | Buffer only |','|---|---:|---:|---:|---:|']
    for species in ['poplar','oak','rock','bush','pine']:
        s=summaries[species];lines.append(f"| {species} | {s['groups']} | {s['query']} | {s['design']} | {s['buffer_only']} |")
    lines += ['',
      'Class is established by actual bound mesh plus resolved prefab and effective metadata/asset_kind, never node names. The ten pine hit groups retain misleading oak/poplar names. The two -4_-6 pine groups alone account for 260 design hits. A root-only test would miss eight query and eight design hits.', '',
      'Every design hit requires an explicit keep/support/reposition decision where the eventual changed terrain intersects it. Buffer-only hits constrain the blend boundary. Bushes are still visual and support constraints; lack of a runtime collider is not permission to bury them. Two buffer-only coast61 hits (one bush, one pine) belong to the protected -5_-5 neighbor resources. Never edit whole groups from these counts. Per-group union boxes are summaries only; use the pinned raw path + instance index for actual bounds and full transform.', '',
      '## What the sources actually do','',
      '- All hit groups use ShaderMaterial_4hw14 in Game53dWest, no overlay or next pass. Saved cloud_drift is false. The shader\'s only vertex-position write is conditional local X += sin(world_time*.018)*9; it is inactive for that saved branch. This does not observe live uniform values.',
      '- scatter_group.gd has editor tool buttons/copy/extraction functions and no automatic _ready/_process/_physics_process. model_scene alone is not evidence of runtime visual replacement.',
      '- The concrete runtime path is world39.gd → open_world.gd. _ready (35–76) reads metadata/asset_kind and the full composed saved instance transform into layout.props/prop_transforms. refresh_collisions (289–331) skips bushes; oak/pine/poplar use radius 2.4, height 11 capsules centered at local Y=5.5; rocks use faces of model_meshes[kind], loaded from the first mesh of the imported prefab. It applies the saved full transform.',
      '- These are conditional nearby proxies: source rules select the 3×3 focus-cell neighborhood, <=350 m horizontal root distance and <=150 m vertical difference, refreshing after >0.4 s. 472 query / 400 design tree hits and 142 / 123 rock hits are potential source-rule candidates, not observed active colliders. 62 / 52 bushes remain visual-only under this rule.', '',
      '## Smallest useful next read','',
      '1. Reuse the exact saved buffers to derive tree capsule envelopes, and inspect only the rock prefab\'s first imported mesh/actual face extent. Pin that path before equating it with the saved rock visual resource. Runtime does not use assets/collision/rock.res for these scatter rocks.',
      '2. Re-query visual-plus-proxy bounds, including adjacent groups outside the visual-only hit list. Capsule-only intersections could otherwise be missed. Read the few bound mesh/shadow vertex extrema needed for exact support; there are six bound resource identities and five distinct recorded primary surface-storage hashes here. No second full-world buffer dump or world run is needed for this preparation.',
      '3. Stop once the path/index-keyed conservative keep/reconcile list and rock source identity are established, then sketch the constrained mountain footprint with existing tile/border protections. A later focused live check is required for runtime clearance, rather than treating source formulas as executed evidence.', '',
      'The shader branch is a resolved saved-state fact, so hypothetical universal deformation/replacement audits are not the leading next task. The prior 172-entry saved settlement catalog has zero query hits, and all three saved road control hulls miss it; retain the old twelve-house identity and road-width booleans as unproved rather than inventing blockers or houses. The non-scatter cloud bank/weather/ocean hits remain separate height/state/composition constraints, not a blanket ground-building mask.', '',
      '## Verification and limits','',
      f'{len(CHECKS)} explicit offline checks passed, including raw/gzip identity, original terminal wrapper binding, all five class totals, membership predicates, saved metadata/prefab/script/material bindings and before/after consulted-source hashes. Reproduce from Aether with `PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/scatter-hit-review-01/classify_hits.py`.', '',
      'The review preserves every original unresolved flag as false: full occupancy, runtime generated/model_scene/collision geometry, full shader envelopes, road width, independently recomputed vertex bounds and visual acceptance. No original report or failed evidence is rewritten. Saved visibility does not imply terrain contact or present live visibility. No mountain asset/footprint has been approved or built.', '']
    (OUT/'README.md').write_text('\n'.join(lines))
    print(json.dumps({'status':doc['status'],'counts':doc['counts'],'classes':doc['classes'],'source_files':len(PINS),'checks':len(CHECKS),'output_bytes':{p.name:p.stat().st_size for p in OUT.iterdir() if p.is_file()}},indent=2))

if __name__ == '__main__':
    main()
