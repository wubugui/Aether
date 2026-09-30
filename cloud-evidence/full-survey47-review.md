# Game47 complete-reference visual gap review

2026-09-30 23:13 UTC. Developer self-review, not independent acceptance. Source: full-reference-survey-20260930T225223Z-Tc88Sk. All 61 actual frames were inspected through five front/reference paired sheets, five side/back sheets and the full-resolution original boot/reference pair. The sheets are navigation aids; original PNGs are retained. This is broad composition/geometry/weather review, not a fine-detail approval. Engine: official Godot4.5.1 Compatibility, Mesa llvmpipe software renderer. 169 limited runtime checks passed, exit0, only known VSync warning. No hardware GPU or physical-flight acceptance.

The survey holds weather at0.35s. Existing lightning only flashes during cycle0–0.10s and0.18–0.24s; this survey intentionally captures between flashes. Therefore absence of lightning in these stills is NOT evidence that lightning never operates. The rain/snow, moving storm and lightning cycle still need separately timed motion/flash review; previous operational tests remain valid.

Every row remains FAILED visually. Side/back are rotations in the same world, not flights. The UI/characters are excluded from new restoration scope. The visible airborne vehicle is retained for existing observation, not counted as new character work.

| Reference | Front discrepancy | Side discrepancy | Back discrepancy |
|---|---|---|---|
|1125|No dark advancing storm wall or spatial gold/storm division; pale uniform fog, tiny land silhouettes and oversized white cloud ceiling replace dramatic coast/river/mountains|Hard straight ocean/land cut, washed low hills, white near-cloud mass|Nearly empty sea, sparse isolated mound, no weather front continuity|
|1126|Too few small reefs; flat blue water; lighthouse beam and dense layered fog absent|Sparse isolated wedges on open water, no near/middle reef density|Sheer straight green terrain wall with tiny harbor at base, weak coastal transition|
|1128|Green plateau blocks intended lake; mountains too small/low; no reflection or pine islets|Long lawn shore and coarse bright cloud chain|Large solid cloud underside, continuous green shore, coarse water without mirror detail|
|1129|Same lake blockage; near rock isolated but no composed pine shores/islands; reflection absent|Broad open blue water and plain green strip instead of layered rocky shore|Trees on broad lawn under huge cloud underside, no layered snowy basin|
|1131|Straight tile coast, simple green hill and narrow river replace tall snowy serrated coast/forest archipelago|Empty sea except tiny distant island, missing island-chain depth|Angular coast cut, generic small lighthouse group and gigantic overhead cloud mass|
|1135|Minimal elevated flat dock on dry green plain; missing layered timber, railings, hoist, dense tools/barrels and lakeside relation|Bare stilt edge beside sparse house/terrain; assembly not integrated with water|Repeated sparse houses/trees on lawn under ceiling, no dock settlement context|
|1216|Clouds read as huge pale boulders, no layered dark storm valleys/lightning; scale too close and repetitive|Dark gaps expose floating green islands; repeated spherical upper clouds|Broad empty black channels and faceted rounded masses; lower storm depth missing|
|1217|Warm tint present but view is land/low hills rather than harbor bay; windmill only thin tiny mast; sunset reflection/town hierarchy missing|Generic hills and repeated bright cloud balls instead of coastal town|One giant green cone and roof of clouds, sparse settlement without coherent harbor geography|
|1218|Mostly open water and two plain rounded islands; no strong plateau cliffs/waterfalls/channels/village network|Straight land edge and sparse blank islands; no layered close cliff transitions|Featureless broad terrain under low uniform cloud slab|
|1220|Orange wash and solar glow but little sea reflection; silhouettes too flat, snowy headlands/forests unclear|Orange near-cloud boulders and empty horizon, little coast definition|Huge flattened cloud masses over unreadable haze; geography/contrast lost|
|1274|Basic block bed/window/walls; missing crafted stove, ropes, maps, furniture detail and convincing real exterior|Flat boards, minimal bed dressing, a few floating shapes beyond blocked window|Close blank wall/flat box; room lacks rounded timber joinery and props|
|1275|Dock is unsupported-looking thin-legged table against giant simple triangles; absent blizzard wall/snowy port detail|Nearby triangular mountain planes dominate; tiny remote structure seems isolated|Bright cloud/ground view with sparse visible snow instead of storm engulfment|
|1276|Sparse white triangle peaks and visible green valley replace tall closely enclosing snowy gorge; snow/fog weak|Simple pyramid slope, little erosion/rock strata or deep snow layering|Green lowland and broad cloud ceiling, no canyon continuation|
|1278|Basic bed/table/window layout present, but lacks curved hull, detailed stone stove, cloth/rope/maps/tools and rich warm light|Bare geometric furnishings and walls; box stove with no crafted fire details|Almost blank wall and chair-back, little all-around interior detail|
|1332|Tiny distant settlement/islands, no dense fog pockets, warm windows or readable lighthouse beam|Nearly empty blue sea; minimal reef hierarchy|Broad green generic hills abruptly meeting straight ocean border|
|1341|Dark global tint only; no dense slanting rain, low storm wall, strong lightning or foamy shore|Empty dark horizon, no storm volume|Cloud blobs over generic green terrain; no dense storm layering|
|1342|Moon/stars present, but sea/land almost black, town lamps sparse and reflection insufficient|Lighthouse recognizable but no long beam or dense coastal lighting|Nearly black sea, hard coast edge and repetitive lit cloud shapes|
|1343|Opening geography roughly recognizable, but cloud coverage/size much too large, peaks too sharp/simple, village and ground sparse, foreground rocks blocky|Long smooth coast line, empty sea and huge upper clouds|Sparse scatter/settlement on generic terrain under dense cloud ceiling|
|1344|Rainbow extremely faint/slender; generic green hills instead of detailed wet river plain and layered snowy range|Giant near-white cloud chunk dominates, weak rain-cleared valley detail|Oversized low cloud layer, plain terrain/water, weak rainbow/world integration|
|1347|Straight coast and generic green hill, no rich snowy mountain shoreline/forested islands; warm dusk hierarchy missing|Empty sea with few small islands|Hard shoreline corner and overhead cloud slab; distant island layout too sparse|

## Original opening (61st image)

Boot image identity remains assets/reference.jpg. Actual full-resolution screenshot has recognizable ocean, island/river and right snow range, but oversized overhead clouds occupy much of sky; snowy peaks are a tightly repeated spiky band; right foreground is coarse block towers; village/castle and road network sparse; coast beaches too uniformly bright. Reference has quieter sky, broader layered range, finer terrain/settlement density and more deliberately broken headlands. Failed, not accepted.

## Implementation priorities and limits

1. Lake48 is addressing the real shared1128/1129 plateau blockage first, using actual scene mesh/collision and 500 real renderer scatter transforms. Preserve surrounding native edits and verify neighboring mountain support, external tile seams, fixed cameras and seaY0. Creating a lake is not equivalent to completing its mirror water, pine islands or mountain shape.
2. Hard straight world/terrain coast edges affect1131/1347,1125,1218,1332; these need actual geographically continuous shores, not camera movement or fog masking.
3. Architectural interiors/docks need real asset and assembly work; adding color/lighting cannot replace timber mass, joins, supports and props.
4. Weather remains strongly underdeveloped: storm front1125, blizzard1275/1276, rain1341, rainbow1344, fog/beam1126/1332 and moon reflection1342. Prior rain/snow buffer restoration establishes operation only.
5. Cloud47 material wrap is a limited shading improvement on failed geometry. Huge overhead cover, repetitive lobes and high-altitude gaps remain. No further global brightening as substitute for shape.
6. All20 plus original remain open. 61 captured views and169 runtime checks establish reproducibility and limited consistency, not completion. Independent review and hardware GPU gate remain outstanding.
