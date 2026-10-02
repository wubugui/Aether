# Shadow arrays v3 source review

Completed 2026-10-02 09:20 UTC. No remaining source-level blocker found. No engine was invoked.

The schema/test author separately reviewed the collector, wrapper and replay adapter. The collector/wrapper author cross-reviewed the strict schema. Both independently ran the final 60 pure test groups in normal Python and `-O`; all passed.

Reviewed scope:

- Reuse of the exact existing strict compressed-shadow decoder and complete base/LOD oriented-triangle equivalence logic; no world or PhysicsServer preparation calls
- Inherited v2 engine gate and original six-mesh / first-imported-rock source binding
- Explicit actual indexed geometry versus separately observed primary `get_faces` snapping, exact hash/bounds proof and conservative unions without an epsilon
- Shadow evidence does not claim unsupported native `get_faces` output; the missing API-vertex allowance stays limited to the known compressed no-normal shadow branch
- Complete coverage ledger and per-level digest/count/threshold agreement, winding and multiplicity preservation
- Runtime rock bounds come from actual `get_faces_bounds`
- Original all-group replay function retains exactly three checked adapter substitutions
- Three-level native script-copy inheritance, immutable inputs, full source dependency guard and unchanged one-child/two-CPU/60-second launch
- Terminal writer matches the original byte-for-byte except full-precision JSON, consistent with the existing successful scatter collector; source guards enforce that sole difference

The reviewer found a static token guard expecting a quoted dictionary key while the collector used property assignment. The guard was corrected to the actual assignment and a regression now invokes the full v3 source guard.

The original v1/v2 frozen files and prior failures are unchanged. Native parsing, completed six-mesh/rock reads, live collisions, full occupancy and visual acceptance remain unverified. These pure fixtures and source reviews are not native execution evidence.
