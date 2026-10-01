# C pre-build camera and support check

This is an actual-triangle static diagnostic before a Blender source prototype.
It is not a rendered world, a source beauty preview or visual acceptance. The
original accepted plan is unchanged in `control-plan58c.json`; the build input
is `authoring-plan58c.json`, with every changed control's original/new centre and
extent recorded. A/B stay frozen.

The actual saved1216 camera comes from the completed52hD comparison report:
position(3000,1150,4300), downward pitch9.4841°, verticalFOV62°,
horizontalFOV93.7468°, logical1672×941. The recorded basis is inverted explicitly
and the recorded projection matrix is used, including near0.35m. This is the
camera from the52f research branch; it does not establish the latest61 context.

`control-projection58c.json` records a conservative oriented-box envelope for
each control separately from actual control vertex angle ranges and actual
triangle visibility samples. If a box crosses the camera near plane its finite
box envelope is reported as null, not extrapolated from eight divided corners.
The triangle diagnostic clips near-plane triangles and rasterizes actual native
authoring triangles at836×471, with perspective-correct nearest depth. Pixel
bounds are converted to the reference axes. A sampled bounding span can include
disconnected visible pieces, so it is not a continuous silhouette-width metric.
External21roots, ship, sky and world objects are absent from this diagnostic.

The first result, preserved under `static-01/`, exposed696px and674px nearest
sample spans forP01/P02 and only12/18 medium controls with samples. It was not
accepted. `static-02/` and `static-03/` preserve subsequent intermediate static
geometry and the failing floor measurements.

Current build controls have16/18 medium and17/24 small controls with nearest
samples. All6 primary controls contribute samples. Their sampled pixel spans
are572,486,346,238,136,48px forP01…P06; full authored vertex horizontal angle
spans are31.36°,26.30°,17.53°,15.44°,9.84°,7.11°. P06's48px is partly occluded;
it must not be called its intrinsic visible width or the true far-horizon scale.
P01/P02 are still large and partially cropped. This remains a visual risk, not
an accepted match to the reference's approximate150…400px near features.

The primary and medium controls were reduced/repositioned so visible hierarchy
could survive. P05 originally occupied the declaredV1 valley and was moved to
(4270,800,2850), making it a localfar primary. Medium shoulders were moved toward
visible sides and connected down into real lower volumes. The9 lower volumes
were widened individually across actual unsupported joins. Local small folds
were lowered35m into their parents to remove floating caps. The authored counts
remain9+6+18+24. These changes are recorded, not hidden as a noise or lighting
pass. Current all-control silhouettes remain a modeling hypothesis.

The originalV1/V2 routes,25m spacing, transverse−half/0/+half lanes, declared
floor bands and160m first-solid thickness gate were retained. Actualcontrol
triangle entry/exit intervals are combined as a solid interval union. Current
pre-voxel results:

- V1:192/192; firstfloorY635.84…769.23m; minimumfirstinterval277.05m
- V2:138/138; firstfloorY610.14…753.74m; minimumfirstinterval296.68m

This does not prove the voxel union will retain these floors. The fresh Blender
readback independently recomputes actual union triangles, all330 rays, all3
cross-sections, camera point containment and strict onecomponent/genus0 gates.
No cavity or fragment may be silently removed; classify and preserve it first.
Full ship/sweptflight and the21root boundaries remain separate unproved work.

Scheduled source run is CPU2, total60s and1.5GiB RSS limit. It saves all57 native
editable controls, an unsimplified15-volume coarse checkpoint, then the full57
raw union using26m voxel and preserve_volume=False. A separate Blender process
performs readback. No QuadriFlow, decimation, GLB, Cycles or world is included.
