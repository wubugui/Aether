# Same K working project relocated and GUI-read verified

Actual one-shot relocation2026-10-02T12:10:51Z:exit0,total16.513337153s; move phase11.150482880s against180s and outer300s. All4889 original files and93 directories moved from exec /tmp to the fixed shared workspace. Every destination was verified and synced before its source was removed. No second full project copy/rebuild, engine or image.

Before/after relative tree SHA both ca20cd38af18e7ec63d325891af470449e1014388c05b965a79414e45bc4e59c. Old source absent, all4889 members recoverable at the fixed destination,0 partition read errors,0 finalization errors. Main4884-file project and27 frozen inputs unchanged. Original47-file freeze/parse remain bound.

The actual cloud GUI terminal then ran the read-only --check-shared-copy entrance and returned passed:true,members4889,engine_started:false. Its exact output is GUI_SHARED_CHECK.json; stderr empty. This proves the graphical process can now read and verify that same directory. No display/network/security settings were changed. Original v1 failure remains preserved.

All full journals, member partitions and protection trees are preserved losslessly in gzip with original identities in storage.json. restore_storage.py verifies them and restores missing raw only. Renderer still uses the same moved working copy, original fixed four images and240/300/CPU2/3GiB limits. Visual, flight, hardwareGPU and completeGOAL acceptance remain false.
