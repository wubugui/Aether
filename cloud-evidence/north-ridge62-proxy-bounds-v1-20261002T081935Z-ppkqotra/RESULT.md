# First native proxy read: version guard rejection

2026-10-02 08:19 UTC. The native child exited 2 and wrapper exited 1 after 0.454313382 seconds, peak 128944 KiB, CPU2. The 60-second bound did not fire. There were no engine log errors, and protected inputs/full 1483-file dependency closure plus startup controls remained unchanged.

The native result contains exactly the issue `fixed engine version`, no visual meshes, and passed=false. No arrays or rock faces were collected. The original source checked whether Engine.get_version_info().string began with `4.5.1.stable.official`, incorrectly treating the human display string as the startup banner. A prior native result from this exact binary (nearbay61-continuous-v6-20261002T064755Z-ip7pcsa8/result.json) records `4.5.1-stable (official)`, major=4, minor=5, patch=1, status=stable, build=official and full hash f62fdbde15035c5576dad93e586201f4d41ef0cb.

The wrapper separately pins the exact executable SHA db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199. A separate source-only version-guard-v2 will record the observed dictionary before checking exact structured version fields and full hash; it must not replace this failure or relax the executable pin. No world instantiated, runtime collision observed, occupancy completeness, or terrain/asset change is claimed.
