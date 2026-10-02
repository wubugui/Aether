# Design v1: rejected offline review, preserved unchanged

The13 original author-package files are preserved byte-for-byte, including PACKAGE_MANIFEST.json SHA2cab9cd3e86437c2e1c11ff0b409566d3b89609b51a2452c0a0ca2e0bd2822ed. This publication preserves a completed but rejected offline design item; it grants no model construction or native execution approval.

Independent review found three internally inconsistent design constraints:

1. Near-profile right endpoint t225 maps to worldXZ(4303.845,3755.785),top780/bottom700,thickness80m. The archived5m sample lies in the selected old bank's exclusive coverage; all8 neighbor masks are absent. The external-boundary distance is conservatively over117m after cell uncertainty, so it cannot use the edge exception to the design's120m inner-thickness requirement. A nearby small internal empty cell is not an external boundary or interface
2. At the A center t0, the near-profile top is990, while the plan and section03/landmark crown specify1005. The near-profile's1005 peak is shifted to t−60. These cannot all be treated as the same exact control point without an explicit revised definition
3. The main and branch trough share the same XZ junction but specify740 and750m respectively. An unexplained10m discrepancy cannot be used as one consistent surface target

The broad concept and the correctly limited projected-coverage/camera/ray evidence remain useful, but they do not remove these blockers. Four actual camera records match, finite projections/rays were independently recomputed, and real3D interfaces/native surfaces/pixels remain unproved. See INDEPENDENT_REVIEW.md for the full distinction.

No original package file, mathematical figure, old K evidence, material, camera, source asset or world was changed to hide this review failure. New files in this directory outside the original manifest are only publication status and independent review. The complete current item must be uploaded through the GitHub plugin and independently read back before any separately named revision starts. A later revision must retain this v1 record, explicitly resolve all three discrepancies, update its figures/data together and rerun bounded pure consistency checks. Do not construct from the rejected v1.
