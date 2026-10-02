# 58J: one metric-plane mound candidate, rejected by math gate

The original `ref/1216.png` and both 58I original PNGs were actually viewed.
58I remains visually rejected for its roof slabs, near-vertical walls, stacked
ledge and exposed block feet. No I/H source or evidence has been edited.

## Explicit candidate and coordinate contract

`author_design58j.py` authors one candidate, with no search or fitting. Six major
cages each have 14 independently specified planes: four short upper planes,
five unequal shoulders, four sloping lower returns, and a lower oblique clip.
The two smaller accents each have ten planes. Directions, support distances and
heights are independently written per cage. The lower front root was raised
32 m and the rear root 26 m. Both accents were brought inward. The source-local
UVY frame is physical metres with Y vertical; it is not a normalized cage frame.

For x = c + R S q and physical normal N, the author stores n_local = S Rᵀ N and
local support h once in `design58j.json`. `poly58j.planes_for` applies the inverse
transform to those stored local planes. `rebuild58j.py` reads the stored planes;
it never reruns metric authoring. Editing an Empty therefore edits geometry
rather than being canceled by recomputing normals. Authorship metadata is
informational only. The neutral material, source frame, original E cameras and
projections, and 7% side/back margin remain fixed. Nothing auto-fits the source.

## Exact result of the one candidate

`candidate-probe58j.json` stopped at the existing `Shell is not genus zero` gate.
No native application ran. No valid preparation freeze exists and no native
trial is authorized by these files. No local shape repair has been attempted.

The read-only `failure-diagnostics58j.json` explains the unchanged rejection:

- 662 vertices / 1,328 triangles / 1,992 edges; Euler characteristic −2
- The unchanged 800-vertex / 1,600-triangle budget is respected
- The topology code had already checked one surface component, two-sided edge
  incidence, winding and one-cycle vertex links before the Euler gate failed
- Two pairwise-overlap cycles have empty triple intersections. Main / Rear /
  Back mound has a 4.2467 m negative common inscribed radius around physical
  UVY (1.4476, 37.4507, 755.6431). Main / Front / Left accent has a 2.0295 m
  negative common radius around (−157.2844, −41.6596, 729.4098)
- Actual exposed-union triangle area, measured after all cage transforms and
  clipping, is 0% within 15° of horizontal, 0% within 15° of vertical, and
  96.6637% inclined 15–60°. These are design diagnostics, never a visual pass
- All eight semantic regions retain exposed area. Static full-source margins
  are 24.3449% front and 12.1678% side/back. The original projected-area gates
  for the back mound and both lower returns have sufficient measured area

The diagnostic solver measures intersection of existing halfspaces only. It
neither changes geometry nor generates candidate parameter trials. An initial
diagnostic-report script failed with a missing dictionary key; that script and
its traceback remain retained as `diagnose_failure58j-initial-error.py` and
`failure-diagnostics58j-initial-error.log`. Fixing the reporting lookup did not
change the design. The successful diagnostic report is not a waived math gate.

## Remaining work and staged native pipeline

The candidate is not fit for native execution. A bounded, specifically approved
local geometry change is needed before any new test. The parent has been given
the two overlap-loop locations and the proposed direction of a local response:
move the rear mound toward the crown junction and bury the left accent inward.
Neither move has been made.

The copied J native entry points preserve I's eight Empty controls, eight
semantic vertex groups, per-face region/plane attributes, and embedded JSON /
math / rebuild texts. Native identity and editability remain unverified for J.
The eventual authorized flow remains one build, independent fresh saved-source
verification, then two fresh original PNGs, all within one 30-second CPU2 /
1.5 GiB / 200,000-byte source trial. No Godot or four-root/world integration,
Git, CLOUD_RESUME edit, publication or external message was performed here.
