# Independent J2 review and supplemental intersection scope

Read-only review reconstructed the translation constraints directly from frozen
J and checked the stored positive-radius minimum-norm certificates. Both
certificates pass. The same reviewer independently evaluated all 247 cage
subsets for both designs, including every higher-order set skipped by the
preparation audit: the audit agrees within 4.2e-13 m, and every omitted higher
intersection is empty (maximum radius after repair at most -9.223 m).
Exactly the two intended positive triples are added, with no lost positive
intersection. The overlap nerve's Betti numbers change from (1,2,0) to (1,0,0),
consistent with the separately checked genus-zero exterior shell.

Minimum-norm means minimum among translations of the two selected cages while
their other two triple members stay fixed and the common-ball radius is 0.5 m.
It is not a claim of optimality among arbitrary cloud redesigns.

## Inherited coplanar-contact coverage gap

The original unchanged `poly58j2.py` coplanar branch checks positive intersection
area, then continues without checking whether a zero-area contact lies on an
indexed shared edge/vertex. The original `intersection_check` pass alone must
therefore not be described as exhaustive proof against every possible
self-contact. This coverage gap was found during review, after the original
preparation freeze; the frozen checker, preparation result and README remain
unchanged.

A separate read-only numerical check of this exact candidate found **no actual
non-indexed coplanar contact**:

- Double physical coordinates: 5,132 coplanar pairs checked. All 433 pairs
  sharing no indices are separated, minimum projected separation 0.0200006679 m
- Shared contact lies on its indexed vertex or edge, with maximum locus residual
  1.67e-15 m in double coordinates
- Source-basis float32 coordinates: the inherited predicate identifies four
  coplanar pairs; all share indexed edges, with maximum locus residual 5.43e-20 m
- The original intersection tolerance remains 1e-8 m. The fixed candidate
  rebuild fingerprint matches `candidate-probe58j2.json` exactly

The supplemental check and its stdout are retained separately. It does not
modify the original checker or geometry. It covers only this candidate's
mathematical coordinates and predicted source-basis float32 coordinates.
Actual Blender Empty-transform reconstruction and saved-source readback have
not run. A future native verifier must apply an equivalent contact-locus check
to its actual readback arrays before claiming this coverage for native geometry.
This package is still source-only, with no native or visual acceptance.

## Reproduction

From the repository root:

`PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python source-assets/cloud-bank58/revision-j2/check_coplanar_contacts58j2.py .`

The retained original stdout is `coplanar-contact-results58j2.log`. The script
exports `check_coplanar_contacts(V, F, eps=1e-8)` for reuse on actual saved-source
arrays in a future verification. Dependencies for the recorded run: Python
3.12.14 / NumPy 2.3.5; CPU2, 30 CPU seconds / 512 MiB address-space bounds.
Observed elapsed 4.96 seconds, peak RSS 26,680 KiB. Three abstract contact
controls pass. It is a numerical check, not an exact-arithmetic theorem.

Script SHA256: `b3f584413b33daed104a64634984c1de6b5ce7c1765327f47b1952823679a426`.
Original stdout SHA256: `c836cca86f1111d3b50258e6a6e09456e0765d0c46974d3bce79a0e6be3c0416`.
