# Round 27 — actual cloud volume/light and moon reflection

Full20-reference Goal remains active. Prior turn is progress:25f local earth fill and26b continuous lane studies completed native/GPU/independent checks.26b whole art remains unaccepted. Production17e/18c/19h unchanged; no migration or previous GPU restarted.

## 27a

The old21b native convex cloud lobes had a single flat bottom plane, mostly seen from below.21c cloud shader normal lighting kept that underside dark, with sea-level fog further damping distant clouds.27a raises native lobe height and adds asymmetric lower points, plus explicit sparse altitude-cloud haze and a small transmitted-light approximation. Original21b moon BLEND/GLB retained byte-for-byte.

Three cloud banks authored in Blender at `captures/coastal_sky_assets_27a`; actual saved source reopened gate `round-27a-sky-native-check.json` passed. Build PID15696/gate24472 ended. Shader water field removes the former two-sine product mask, using continuous wind-aligned noise heights and actual world normal/view/moon reflection.

Run `coast-environment-27a-20260908T145044Z-a01744c1b93444ce9c8d80e533918f2d` is terminal passed, root session43582 ended. Root directly viewed night-reference, night-reverse and day-reference. Unchanged26b streets/terrain are frozen as the same assets and not resampled with the old8839road probes for this environment-only edit.

**27a remains rejected for final visual use.** Cloud lighting improves, but large banks retain thin hull-like bases; water swaps the old grid for overly dense continuous horizontal scanline-like glints. Independent final report `round-27a-cloud-water-independent-review.md/json` agrees. The reverse view has no screen-fixed moon stripe; that limited spatial property does not establish full water fidelity.

## 27b completed and rejected

New native clouds use seven coherent cross-sections, twelve radial samples and an uneven roof ridge, with a rounded underside replacing the large flat hull face. Original moon and27a shader light basis preserved.

Water removes the sinusoidal swell and samples one common continuous wave-height field at irregular world-space Voronoi facet centers. Final normals are constant within each region, so the material normal field itself is discontinuous. This is a material normal approximation, not a physically displaced ocean mesh or final weather system. Build PID28468 and gate24796 ended successfully. Run `coast-environment-27b-20260908T145749Z-86704eae999c425590f3ff5cadced574` terminal passed, root session87895 ended; all three actual images viewed by root and reviewer. Saved native gate and frozen newGLB consumption confirmed. Moon remains exact21b bytes.

**27b rejected:** clouds remained saucers supporting shallow hills;10.5x3.6m wave facets became giant ice/mosaic patches in the near sea while retaining dense rows farther away. See `round-27b-cloud-water-independent-review.md/json` and `round-27b-cloud-screen-projection.json`. All failed outputs retained.

## 27c completed: pointed clouds rejected; water improvement limited

Native clouds used higher asymmetric pointed ridges. Seven cloud banks moved to deliberately designed fixed world positions to better fill the1342 framing; authored deprojection is recorded as design, not original-map geography. Runtime clouds remain actual world volumes. Water facets reduced to3.2x1.15m, blended28percent live normal gradient, with view-dependent sky reflection in day/night.

Build27688 and saved-source gate6800 ended successfully. Run `coast-environment-27c-20260908T151320Z-766da6d8e2214d7f9879e2c4b050ad09` terminal passed, root session54075 ended. Root and reviewer directly inspected all4 images: night reference/reverse, day reference, night reference18seconds later. Root verified175 frozen artifact hashes in `round-27c-root-evidence.json`; independent final `round-27c-cloud-water-independent-review.md/json` confirms new assets/world positions and actual time response. Near-water rootROI12975/13000pixels differ, upper sky control0/53100. This is two time samples, not smooth animation proof.

**27c cloud shape rejected:** tall pointed pyramidal mountain ridges replaced the former saucers. Water's giant patches reduce and day waves become visible, but bright fine horizontal ripples remain unlike1342. Existing island reverse mostly sees old World clouds, so it does not establish the new cloud banks' complete rear appearance. No production installation or whole-reference acceptance.

## 27d completed and independently reviewed; art still rejected

New saved Blender volumes replace the pointed peaks with nine broad convex cross-sections, lower height and asymmetric rounded shoulders.12 independent editable lobes plus unchanged21b moon; saved-source gate passed. Same fixed27c cloud positions retained. Water uses3x3m facets with8percent live gradient blend to address narrow strips. Build944 and gate2956 ended. Run `coast-environment-27d-20260908T151758Z-b4454b3270604da4830004650d16e7dc` terminal passed, root session82796 ended. Root directly viewed all5 GPU samples, including a deliberate new-cloud rear/underside day view.182 frozen hashes verified in `round-27d-root-evidence.json`. Independent final `round-27d-cloud-water-independent-review.md/json` supports the round-shoulder volume and visible underside direction, but rejects cloud layering/flat broad undersides and large tiled water glints. No whole-cloud/reference acceptance or production install.

## 27e completed; oversized wave triangles rejected

Water now derives normals from a continuous virtual piecewise-planar height field with shared jittered grid vertices and alternating triangle diagonals. The actual ocean mesh remains flat; this is material-normal geometry, not a displaced sea surface. Exact27d cloud BLEND/GLB and original moon retained without needless native re-open. Run `coast-environment-27e-20260908T152222Z-bded23dbcd5c4849967297a6ad1a8f20` terminal passed, root session41558 ended. All4 root images viewed,179 bound hashes verified in `round-27e-root-evidence.json`.4.8x2.6m wave cells make visibly oversized triangular plates and far horizontal rows: rejected. Independent final `round-27e-cloud-water-independent-review.md/json` agrees with the limited direction change and remaining large/regular bright facets.

## 27f completed; water still strips; missing-moon diagnosis withdrawn

Water cells reduced to3.2x1.1m, specular lobe narrowed and random brightness amplitude reduced. Run `coast-environment-27f-20260908T152526Z-f1543e06af9f4533a1689edaf5dc0add` terminal passed, root session57978 ended. Root directly viewed4 images;181 frozen bindings verified. Smaller glints remain horizontally repetitive. **The earlier root claim that the moon disappeared was a visual observation error and is withdrawn.** Exact saved-PNG moon-region comparison subsequently proved the moon is present and identical to27e in both samples. There is no established moon rendering regression.

`round-27f-moon-missing-input-diagnostic.json` retains the original input-comparison investigation, superseded by `round-27h-moon-observation-correction.json`. The latter directly decodes saved images: all7 moon regions from27e/f/g/h are byte-identical,90x92pixels with3036 bright pixels each. No engine, UI, compiler or warmup defect is established. Do not repeat a missing-moon investigation.

## 27g/h completed; diagnostic mistake corrected

27g unnecessarily added3seconds plus240settlingframes and sky mesh state to investigate the misread. Run `coast-moon-diagnostic-27g-20260908T153017Z-e0efc52dc9094edc9316da694d642a7f` terminal passed, root41958 ended.27h then added a projected-moon25pixel readiness gate and resampled only the two night views: run `coast-moon-readiness-27h-20260908T153333Z-8b7579b40e2d437a8b1142c3bfdb7403`, root45975 ended. Both gates passed on attempt0 with25/25 bright samples; both final PNG bytes are exactly the corresponding27f PNGs. These runs did not repair a moon defect and must not be credited as such.

Initial independent27h visual review repeated the root misread. The fresh reviewer subsequently independently decoded and directly viewed the original moon-region pixels, confirmed the moon, and amended `round-27h-cloud-water-independent-review.md/json` with an explicit correction. The actual remaining rejection is regular bright water strips/clumps and cloud layering. Preserve the diagnostic artifacts and correction, but do not carry the withdrawn claim forward.

The old village reviewer was interrupted after prolonged silence on27d; fresh bounded `/root/cloud_water_27_final_review` completed27d/e/h. All root native and GPU sessions for27c–h have ended. Further work should retain27d editable cloud geometry as a local iteration basis, continue real cloud layers/water/lighting/coast and all20 references, and avoid repeating these unchanged native gates.

Lighthouse beams, warm local reflections, primary coast/rock massing and all remaining reference scenes are still unfinished. Full Goal was read back active with all20 references and original scene scope. No old migration or unchanged26b road/terrain gate was repeated. Production remains17e/18c/19h.
