# Exact runtime evidence storage

The source attempt failed before saving a model. No `.blend` or PNG exists for this run.

Four original JSON files remain unchanged in the working tree but are excluded from Git as raw duplicates. `storage.json` describes their exact bytes and SHA-256. Two unique gzip streams (`mtime=0`) are stored in three ordinary-Git parts of at most 500,000 bytes, totalling 918,236 bytes. These paths have `filter: unspecified`; no LFS or alternate upload route is involved.

- `protected-before.json` and `protected-after.json`: each 2,823,330 bytes, identical SHA-256 `023502e456db2b606c673d8397726296b401e22d6b40b41d734038a28511e866`
- `outputs/build-raw.json` and `outputs/build-failure-raw.json`: each 1,556,139 bytes, identical SHA-256 `73dfbbf9a376d4c32d29f27f02ff3ca99d72e1e7686f4e4a2a11de55b2e7182a`

After checkout, run `python restore_storage.py` from this directory to restore missing raw paths. Existing files must match exactly and are never overwritten. `--verify-only` checks all compressed parts, reconstructed full bytes, and any existing originals without writing. `--out /new/empty/directory` performs an independent reconstruction there. This does not regenerate or reinterpret JSON.

All other actual logs, native Text input/readback files, process receipts and external caller code/observations are preserved directly. The embedded inputs that equal already published source files reuse normal Git blob identities. Only required runtime evidence is retained; there is no second project or native-model backup.

This representation is not a claim that the raw paths are direct Git blobs. Complete external storage requires remote byte verification of the parts plus a new-directory exact restoration; that verification is recorded separately after publication.
