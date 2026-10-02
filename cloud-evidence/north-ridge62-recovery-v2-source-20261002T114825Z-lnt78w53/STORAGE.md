# Exact native-source restoration from ordinary Git

The actual editable `north-ridge62.blend` is 10004835 bytes, SHA-256 `dd1d3c12b8c3f98fdcd42a21057d519f1cac48eeab468cbc7721d1c1673ab502`. **It is not a Git blob at its native path in this commit.** Its one canonical transport representation is lossless XZ split into three ordinary Git chunks of at most500000 bytes; this avoids previously unstable large connector payloads. The native path and every chunk have `filter: unspecified`, with no new LFS pointer or endpoint. No upload of this source has been denied or rerouted.

`native-storage.json` also binds the two actual raw native reports and the exact internally loaded BINDINGS text; all original size/SHA identities remain unchanged. Parts are a storage encoding, not new geometry or a separately maintained backup/source. The actual local .blend remains intact and ignored; no original native source was compressed in place or deleted.

From the repository root, verify all chunks without writing:

    python cloud-evidence/north-ridge62-recovery-v2-source-20261002T114825Z-lnt78w53/restore_native.py

After a fresh clone, restore only missing originals at their normal paths:

    python cloud-evidence/north-ridge62-recovery-v2-source-20261002T114825Z-lnt78w53/restore_native.py --restore-missing

For an independent clean reconstruction, add `--destination-root /absolute/new/empty/directory`. Each compressed chunk, concatenated stream, uncompressed size/SHA and final written file is checked. A different existing file is rejected without overwriting it. Existing exact originals are verified and left unchanged. The separate small protection manifests use gzip and the identities in storage.json.

The original creation and original fresh-open have passed. At this storage preparation stage, **a clean reconstruction and its independent native fresh-open have not yet been completed**. Remote Git byte readback and clean native reopen are required before claiming this encoded external delivery is fully verified. No source views or world integration has passed.
