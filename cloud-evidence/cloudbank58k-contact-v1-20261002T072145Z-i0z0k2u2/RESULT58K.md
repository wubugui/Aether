# First K native trial: Blender crash before source save

Native build terminated with signal11/SIGSEGV after0.863265728s; wrapper1 at1.526201368s,316248KiB peak childRSS,CPU2. The30-second/1.5GiB limits were not reached. No native source or image exists.773 historical and35 preparation inputs remained unchanged. Verification/render stages were not started.

Raw Blender4.5.14 stdout says Writing:/tmp/blender.crash.txt. The3463-byte matching crash was copied verbatim into this run before unrelated work could replace it (SHA256c161427c2d022509acd84204e57d533f2e6c6c1429db99832755c396b01169f8). Its Python backtrace ends at rebuild58k.py:28 group_signature while iterating vertex deform groups, through source58k.py native_identity/build:100. The partial build JSON retains state running because a native crash cannot run Python finally; the wrapper's actual signal/exit is the terminal authority.

No actual saved topology, control editability, source size, fresh dependencies or visual acceptance can be inferred. Mathematical K feasibility remains tied to its prior preparation, not a native pass. Original K recipe/scripts/freezes and this failed run are immutable; there was no retry in place.

Initial source inspection shows cached FACE/POINT RNA attribute handles crossing later structural allocations, including first VertexGroup.add. That is a concrete lifetime hazard being investigated, not yet proven as the specific crash cause. A separate recovery-01 will order structural operations safely, reacquire named attributes and verify full weights/metadata without changing K geometry, cameras, rendering inputs or gates. No repaired native trial has run at this checkpoint.
