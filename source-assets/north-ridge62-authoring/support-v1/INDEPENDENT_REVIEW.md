# Independent source-only support review

## Conclusion

The reviewed finite pre-solver is suitable as a **conditional source-design diagnostic**, with no remaining defect identified that changes its current 167-row result. It is not a native support pass or integration authorization. The reported result is 31 conditional Y candidates, 7 unchanged placements, 117 empty-interval blocks and 12 visible-geometry blocks; all support/native-acceptance flags remain false. The 509 query keeps remain individually recorded, including the two protected entries.

Review made no persistent edit except this report; the changed-pin test creates and removes its own temporary fixture. No engine, image, network, Git, Slack, cloud execution, source-asset edit or placement write was performed. The solver's complete final normal/optimized rerun and final freeze belong to the authoring process; this review independently ran the current 20-test suite normally and with Python `-O`, both passing.

## Math and source identity

- The saved column affine is applied correctly as a row-vector multiplication by the stored columns. The capsule's `B`, horizontal `H`, inverse mapping and transformed plane gradient are consistent with it. All 167 observed matrices are upright, with positive vertical scale; the source capsule rejects unsupported tilt/shear involving Y and singular horizontal bases.
- For each planar contact polygon and terrain triangle, the clipped intersection is convex and terrain-minus-foot is affine. Its extrema therefore occur at the enumerated clipped vertices. This is a continuous polygon method, not a root/four-corner-ray test. Per-polygon projected coverage is checked.
- The lower capsule is the actual source recipe's bottom hemisphere, transformed to an ellipsoid. The unconstrained stationary point, clipped-edge stationary points/endpoints, inside vertices and circle-boundary critical point exhaust the possible maxima over triangle intersect disk. The edge derivative formula is correct for positive vertical scale. Natural cap air gaps are not incorrectly constrained to zero.
- In addition to the checked-in fixtures, the review compared 77 nondegenerate intersecting randomized/special cap domains with an independent smooth 3D-ball constrained optimizer, within 1e-6 m. Cases included a triangle inside the disk, disk inside a triangle, clockwise triangles and a thin clipped cap. A sheared horizontal affine on a sloping plane matched its closed form within 4.5e-16 m. Exact tangency has the correct analytic value; the generic optimizer overestimated it by about 3.9e-6 m under its feasibility tolerance and was not treated as contradictory evidence.
- Five decoded canonical meshes reproduce their complete recorded native vertex/ordered-face identities, and the separately snapped rock faces reproduce the actual imported `get_faces` identity. The mapping identity binds the original terrain corners; the proposed surface retains original XZ/topology and survey-coordinate correspondence.

## Issues found and addressed during review

1. The earlier solver recorded current survey/native/wrapper hashes without enforcing their frozen preparation identities. The current `check_pin` calls now verify bytes and SHA against the frozen candidate plan before consuming those three files. Positive and changed-pin negative tests were added. The earlier current survey already matched, so this correction does not change the result.
2. The new oak/poplar definition previously relied on the observed first mesh layer being lower than the trunk-connected ring. It now explicitly uses their minimum; pine retains its historical first-whole-mesh-layer rule. All current values are unchanged.
3. Preserved tree rows now explicitly distinguish unchanged capsule maximum-contact metric from preservation of every natural cap gap. The README and result limits also distinguish float64 evaluation of saved float32 affines from unobserved native per-vertex rounding.

The added immutable original-source manifest check binds the queried resource files and runtime recipe without another 775-group decode/census.

## Interval, preservation and visibility checks

- The visual/rock contact interval implements burial and gap limits with the original 0.001 m gap and geometry-relative burial/extra-seat bounds. The original 0.002 m pad remains a selection preference, not an enlarged tolerance. The conservative oak/poplar rule is explicitly new, not retroactively described as historical acceptance.
- A positive-area unchanged visual-foot piece forces dy=0. Entirely unchanged actual-foot cases retain their original placement/defects instead of being subjected to an invented repair requirement. For current rock rows, the presence of unchanged visual and snapped-proxy pieces agrees. Preserved trees additionally retain the continuous capsule maximum metric, not all natural gaps.
- The chosen world-Y values are float32-representable and the 31 conditional values satisfy their final continuous intervals. The nearest-representable adjustment and highest-legal-Y calculation are sound for these finite inputs. No successful candidate needed the visibility fallback in the inspected report.
- For fixed XZ and vertical translation, the set of material points above the heightfield is nested as Y rises; above-terrain area and maximum above-terrain Y are monotone. All evaluated baseline area/top denominators are positive, so the highest-legal-Y failure correctly rules out the remaining interval under the stated metrics. These metrics are surface area/top clearance, not renderer occlusion, volume or visual composition.

## Remaining boundaries

- Candidate collision transfer is not authored/read back. Source capsule scaling, margins, focus activation and physics-server behavior remain unobserved. The tightest conditional gap-bound margin is approximately 1.15953e-7 m, much smaller than possible world-coordinate float32 rounding changes. Native contact validation cannot be inferred from these candidates.
- Coverage checks sum clipped areas. They are appropriate to the pinned nonoverlapping terrain heightfield; they are not a general proof that an arbitrary overlapping/gapped triangle soup is a valid heightfield. Likewise, these finite-upright-input conclusions should not be generalized to tilted rock/bush inputs without added validation.
- The 129 bench records are constraints/witness proposals, not a connected feasible surface. Of these, 35 fail the selected two-witness +/-2 m diagnostic and 94 pass only necessary bounds. Three full proposed boxes extend outside the ridge polygon and cannot be accepted as drawn. A smaller explicitly designed domain might differ.
- All proposed bench domains are within the original expanded query rectangle, so the 676-row inventory covers their conservative neighbor search. This does not discharge neighbor support, low-floor/80 m wet guard, cloud 40 m margin, shared seam, collision, or protected-resource checks after any actual bench edit.
- No low-shoulder relocation has been designed or accepted. The 129 blocked rows remain blocked, and large allowed Y changes still require source-form and live-view review.

The documented separation between source diagnostics, actual collision evidence and final visual/runtime acceptance should remain intact in the final freeze.
