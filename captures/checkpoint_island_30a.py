from pathlib import Path
import json, hashlib

R = Path(__file__).resolve().parents[1]
run = R / 'captures/validation_runs/lantern-island-30a-20260908T180129Z-961944bd320b46a4bb5f15256ceb5c8f'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
m = read(run / 'manifest.json')
assert m['status'] == 'passed' and m['passed']
for name, item in m['artifacts'].items():
    assert sha(run / name) == item['sha256'], name
sites = read(run / 'actual-site-rebuild.json')
assert sites['passed']
views = []
for name in ['night-reference', 'day-reference', 'day-d-front', 'day-d-back', 'day-c-front']:
    p = run / 'images' / (name + '.png')
    side = Path(str(p) + '.json')
    d = read(side)
    assert d['world_sha256'] == sha(R / 'scenes/world/World.tscn')
    views.append(dict(name=name, path=str(p.relative_to(R)), png_sha256=sha(p), sidecar_sha256=sha(side), root_directly_viewed=True, camera=d['camera']))
review = R / 'reviews/round-30a-island-independent-review.md'
assert review.exists(), 'Independent visual review still pending'
out = dict(run_id=m['run_id'], manifest_sha256=sha(run/'manifest.json'), terminal_passed=True,
    binding_count=len(m['artifacts']), all_bound_hashes_match=True, actual_site_rebuild=sites,
    root_views=views, independent_review=str(review.relative_to(R)), independent_review_sha256=sha(review),
    visual_accepted=False, production_installed=False, full_goal_status='active',
    root_visual_findings=['Fixed reference view: compact island and keeper house now right of tower improve the proportion/composition direction; not exact reference acceptance.',
    'Front/back reveal persistent large upper rock slabs and continuous paired tidal bands; rock roots remain too regular and detached in places.',
    'Day C/front and D/front confirm editable 3D land, buildings and paths; screenshots and sampled supports do not prove complete flight/walking or all contacts.',
    'Cloud/water/light, other islands and mainland remain visibly different; full20 plus original reference remains unfinished.'])
p = R / 'reviews/round-30a-root-evidence.json'
assert not p.exists()
p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
registry = read(R / 'reviews/reference-view-1342-progress-29e.json')
d = read(run / 'images/night-reference.png.json')
registry.update(run_id=m['run_id'], camera=d['camera'], reference_image=views[0],
    final_lantern_configuration=d['lantern_lighting'],
    geometry_basis={'islands':'A/B20l; C/D30a native compact land, full-size rebuilt pads and refitted paths; D authored position/yaw changed', 'lighthouse':'19h native', 'harbor':'22g', 'village_and_headland':'26b', 'production':'17e/18c/19h unchanged'},
    evidence=['reviews/round-30-worklog.md', 'reviews/round-30a-root-evidence.json', 'reviews/round-30a-island-independent-review.md', 'reviews/round-30a-independent-geometry.json'],
    remaining=['Retain improved compact-land/native-building proportion direction; compare exact composition and refine only where reference evidence warrants.',
    'Rebuild shoreline/midsection topology to interrupt continuous tidal bands and wide shield slabs; preserve actual occupied pads and refit affected support geometry.',
    'All20 references plus opening, weather/time, warm water/light, clouds, mainland/villages and flying-space observation remain incomplete.'])
(R / 'reviews/reference-view-1342-progress-30a.json').write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding='utf-8')
maxpos = max(v['unchanged_maximum_position_delta_m'] for v in sites['views'])
maxfoot = max(v['unaffected_foundation_delta_m'] for v in sites['views'])
note = f'**最新30a已完成原生保存重开、五实际GPU及独立审查，总目标继续active。** C/D实际网格水平缩至0.72、高度0.65，建筑原生尺寸保留，切分重建两个完整pad及315路径顶面；实际路径约45mm贴地、最大坡10.863°。D位置/朝向为有记录的设计调整，守塔屋在固定参考视角中已转至塔右，岛体比例方向改善；上台大岩板、连续双层水线与规则岩根仍需返工，未装生产。{len(m["artifacts"])}冻结绑定SHA匹配；四受影响建筑重新落地、每座九基础样本通过，未改区域落点最大差{maxpos:.9f}m、基础差{maxfoot:.9f}m。全部30a原生/GPU进程已结束，无待等引擎句柄，不重跑已通过检查。接续 `reviews/round-30-worklog.md`、`reviews/round-30a-island-independent-review.md`、`reviews/reference-view-1342-progress-30a.json`；以30a保存源继续岸线/中段拓扑，不回到29e过大比例。生产17e/18c/19h未改，全部20参考及原图仍未完成。'
for name in ['WORKSPACE_RESUME.md', 'reviews/LOOP.md']:
    p = R / name
    s = p.read_text(encoding='utf-8')
    assert '**最新30a已完成' not in s
    first, rest = s.split('\n', 1)
    p.write_text(first + '\n\n' + note + '\n' + rest, encoding='utf-8')
for name in ['REFERENCE_SCENES.md', 'WORLD_SCENE_PLAN.md']:
    p = R / name
    s = p.read_text(encoding='utf-8')
    assert '30a紧凑岛体接续' not in s
    p.write_text(s + '\n\n30a紧凑岛体接续：实际网格比例、完整建筑pad、贴地路径及D朝向调整通过原生和实际装配核验；五视图支持保留比例方向，连续水线/上台岩板仍需重塑。最新 `reviews/reference-view-1342-progress-30a.json` 与独立报告记录有限结论；不能把几何、支承抽样或局部改进视为视觉完成。全部20参考及原图Goal active，生产未变。\n', encoding='utf-8')
print('30a checkpoint', len(m['artifacts']), 'bindings; Goal active; max unaffected delta', maxpos, maxfoot)
