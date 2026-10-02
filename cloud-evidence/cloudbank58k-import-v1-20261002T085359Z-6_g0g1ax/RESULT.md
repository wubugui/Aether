# K first isolated import trial: exported normal-fidelity rejection

2026-10-02 08:53–08:54 UTC. The wrapper ended with exit 1 after 7.035966707 seconds. Its one official Blender 4.5.14 child exited 1 after .742388028 seconds, CPU2, peak child 267240 KiB / observed wrapper+child 291668 KiB. Neither 120-second total, 30-second stage, nor 1.5 GiB resource bound fired.

Blender opened the accepted 136389-byte K source and completed one selected-mesh GLB export. The actual candidate `export/cloud58k.glb` is 31144 bytes. Export validation then failed at the original `Flat outward corner normals changed` (3e-5 component error) gate. Its traceback and stdout are retained; wrapper passed=false despite the log-error classifier's empty list. This GLB is a failed candidate, not an accepted import or new source.

Because export58k.py writes source-readback.json only after both transfer validations, no source readback file exists for this failed trial. The fresh native source-identity checks and post-export same-identity checks preceded the failed validator in code, but no complete successful exporter report is claimed. All Godot editor/import/readback/fresh-reload stages were never started. Zero images, no world, no applied world anchor.

The wrapper's complete original main-project manifest (including .godot/import files), all 1026 prepared/protected identities and the original accepted .blend were unchanged. Main-project before and after manifests are byte-identical, retained locally and losslessly gzipped with hashes and restore commands in manifest-storage.json. The one-shot admission marker and terminal receipt are retained; this v1 attempt is not automatically rerun or overwritten.

Next is a pure Python diagnosis from the actual failed GLB and saved source data. Locate exact face/corner, winding, mapping and normal values before deciding whether exporter, validator or source is at fault. Do not silently loosen epsilon, drop flat-normal protection or alter the accepted source. Any needed native source-normal read must be a separately scheduled minimal observation.
