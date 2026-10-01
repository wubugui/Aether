# Lake49 native island design

Source48 is read-only. Four new independent native assets are anchored at Godot coordinates (1045,0,-1150), (1060,0,-1650), (1380,0,-1120), (1200,0,-1070). Dimensions: near-left 68×42m with 10/14m pines; far-middle revised from 36×24 to 72×42m with 10/14/17m pines after both camera projections showed the initial island too small; near-right 40×26m with 9/11m pines; foreground rock18×14m and grass tufts. Coordinates are authored inference, not image-derived facts.

Each island has an independent closed, bed-conforming rock root; angular asymmetrical shoulder; discrete light wet-edge boulders; irregular thin grass patches supported on the shoulder; trunks and branches; and separate offset pine bough tiers. Roots and tops overlap below water rather than ending at a floating disk. No cone or circular grass hat primitive is used. Pine feet are raycast against actual authored support triangles, not an analytic height approximation.

The initial central anchor and 36m width project to only 33/30px in1128/1129. Enlarging it to72m gives the correct visual weight relative to the near islands without shifting the fixed cameras. Its full dry and underwater geometry remains ≤X1100, preserving the X1120–1160 water lane. The right island is outside1128 but at X976 in1129, consistent with the changing viewpoint. Center projections: near-left1128(214,418),1129(156,386); middle1128(516,390),1129(525,376); right1128(1621,427),1129(976,395); stone1128(976,459),1129(315,397). Full geometry bboxes are exported after authoring.

Unchanged camera routes:1128 lateral(1150,10,-1000)→(1300,10,-1000), approach→(1150,28.668,-1199.127);1129 lateral(1300,7,-950)→(1446.889,7,-980.391), approach→(1259.596,22.219,-1145.284). All new triangles are distance-tested against those line segments. The pre-existing+350m terrain-blocked route remains documented by48; no terrain edit is permitted to hide it.

Source evidence is CPU Blender rendering; it does not certify hardware GPU quality or reference completion.49 does not change water, cameras, trees/scatter already in48, surrounding peaks, or the world generator.
