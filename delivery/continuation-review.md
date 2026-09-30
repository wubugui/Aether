# Retained independent review and unresolved evidence

This is a handoff summary of the already completed read-only Game42b review, not a new review or a claim of Game42c acceptance. Original screenshots/reports are retained in the candidate evidence directory.

| Reference | Retained material differences |
|---|---|
| 1343 and original reference | Oversized gray cloud undersides; crude landforms and snowy massifs |
| 1131 | Lake, mountain, valley and fog composition absent |
| 1347 | Weak warm clouds and water glints; composition differs |
| 1218 | Sparse round islands; dense archipelago and cloud layers absent |
| 1344 | Native rainbow faint and small; snowy valley and warm spatial layers absent |
| 1217 | Coastal harbor replaced by inland hills; sunset glints/layered clouds absent |
| 1220 | Coast, mountain and island composition differs; golden water path absent |
| 1135 | Port exists, but cargo, railing, mooring and wood detail incomplete |
| 1126 | Fog, rock groups, waves and lighthouse beam incomplete |
| 1332 | Close cliff, beam, harbor lamps and spatial fog incomplete |
| 1342 | Night coast/port dark, moon path weak; ship lamps improved |
| 1125 | Cold storm/warm sun spatial division, rain and lightning absent in comparison |
| 1341 | Coarse rain boards; weak cloud wall and lightning depth |
| 1128 and 1129 | Snowy mountain mirror lake and nearby floating islets absent; faceted water |
| 1276 and 1275 | Large white geometry in captures; snowy pass/dock could not be judged |
| 1274 | Cabin enclosure preserved; furnishings, wood/stove warmth and window view incomplete |
| 1278 | Side view clear; flat furnishings/materials and harsh desk light |
| 1216 | Cloud sea resembles rocks/pancakes; depth, haze and local flash contrast weak |

Game42b's lightning illumination toggle produced a real image pixel difference (298.443), while the bolt silhouette remained a thin purple wire. Camera clearance and nearest static geometry diagnostics did **not** establish terrain occlusion as the cause of the white weather polygons. A prior report's geometry-occlusion explanation is unproven. The same-world rain/snow on/off GPU diagnosis implicated precipitation rendering; shader-driven movement was not represented by the static ray diagnostics.

Game42c changed precipitation to CPU instance movement and near-eye fading. Its captures removed conspicuous white/blue polygons, but rain/snow became difficult to see. Do not count that as a visual repair without an actual on/off image and motion test. Its saved build also emitted two MultiMesh buffer errors. Fix fresh allocation and verify visible precipitation on the cloud machine. All reference acceptance remains open.
