# Proxy v2 native read: structured version passed, shadow arrays unavailable

2026-10-02 08:50 UTC. Child exit 2 / wrapper exit 1; 0.505831178 seconds, CPU2, peak 129548 KiB. The original 60-second bound did not fire. No logged engine errors, no changed inputs, and complete 1483-file saved closure/startup controls still matched.

The full observed Engine dictionary is now retained. All nine exact version/type fields and full commit hash passed, correctly resolving the prior display-string failure. The old v1 failure is unchanged.

The sole new issue is `native arrays unavailable`: the first selected CoastalPines36b primary ArrayMesh_8qhtw supplied 120 surface vertices and 168 face vertices, but shadow ArrayMesh_bpun8 did not expose the required vertex array through this native call. The partial result retains resource identities, surface storage hashes, actual primary vertices/faces bounds and hashes. This is not six completed visual meshes, rock-face evidence, an empty shadow, or completed occupancy. No world was instantiated or changed.

Next is a source-only diagnosis against the already-pinned shadow handling in coast61 visible_geometry61.gd. Any faithful correction must retain or prove shadow coverage, not drop the shadow or relabel metadata as actual vertex readback. The small difference between compressed surface extrema and get_faces extrema must also be explained rather than silently widening a tolerance. No automatic native rerun or new source download occurred.
