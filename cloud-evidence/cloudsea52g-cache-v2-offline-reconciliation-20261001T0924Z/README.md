# 52g cache v2: read-only gate reconciliation and bounded result

Reconciled diagnostic execution gate: passed. This does not grant pixel or visual acceptance. No engine/GUI was rerun, no runtime/source/scene files were edited, and the original failed external gate remains unchanged.

Source run: `cloudsea52g-cache-diagnostic-v2-front-20261001T091704Z-5rx_5cuu`.

The child completed0 in174.64s with clean logs and complete native restoration. All88 native checks passed. There are five material-proof sets, not four: initial `prepare_view("1216")`, followed by A0,A1,R0,R1. Each set contains the same125 unique CloudSea meshes across25 roots,75 original upper meshes and50 low bodies, exactly3 active materials and every required live flag true. The wrapper had incorrectly required len==4.

`reconcile.py` parses the frozen run's exact `runner.py` and executes only its validation block offline. First it replays the unmodified gate and reproduces the sole material-count error. Then it changes exactly that expression to a stricter five-label/125-unique-path/25-root proof and replays every original requirement, PNG signature/dimension/hash and full-RGBA comparison. Pixel derivative reports are redirected only into this independent directory. No original file is written.

`reconciled-diagnostic-gate.json` binds the original process report, native report, runner, inputs, baseline binary and every run file by SHA256; it also records matching after-hashes. It includes all re-evaluated requirements and the original versus corrected validation errors. The original run's failure is preserved as historical evidence rather than rewritten.

## What the pixel result establishes

A0=A1 exactly, and R0=R1 exactly. A0 versus R0 differs only at:

- (436,452): [83,98,131,255] → [82,97,130,255]
- (435,453): [68,81,110,255] → [66,79,107,255]
- (434,458): [63,77,104,255] → [63,76,104,255]

Three of782,856 pixels differ, seven RGB channels total, maximum3/255, absolute channel sum11. Every alpha value is identical. The entire signed RGBA difference field is exactly equal to the old failed D A/A2 difference field, including location, sign and magnitude.

Therefore, in this fixed52f front view under the recorded llvmpipe renderer, re-registering identical mesh geometry is sufficient to reproduce that three-pixel residual without loading D geometry. The two before samples match, as do the two after samples. This supports an effect associated with renderer state after resource rebind; it does not distinguish shadow-map behavior, draw-list ordering, caching, or another internal renderer mechanism.

The cross-process baseline images are not globally identical:76 other pixels differ between old A and new A0 (maximum79/255), and that same cross-process difference field remains after restoration. Thus this is a precise reproduction of the three-pixel intervention difference, not proof of whole-frame cross-process determinism or a hardware-GPU result.

`pixel-residual-reproduction.json` stores the quantitative comparison. Original strict A/A2 pixel equality remains failed. No tolerance, crop, ignored pixel mask, image substitution or favorable-frame selection was introduced. The rejected D cloud shape remains rejected. B source files were not edited or rendered.
