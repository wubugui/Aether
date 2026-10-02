# Exact form-v3 source runtime evidence

44 original runtime JSON paths are represented by 27 unique byte objects: 12 gzip-mtime0 streams, 13 parts, 4581009 compressed bytes, and 15 literal byte-splice variants. The new324179B .blend is a direct ordinary Git blob at source-assets/cloud-bank58/revision-l/form-v3/cloud_bank58l_form_v3.blend. The actual eight captured Text inputs and their readback records are kept in this run; Git reuses identical source blob bytes where applicable.

Run `python restore_storage.py --out NEW_EMPTY_DIRECTORY` to reconstruct every original JSON byte. `--verify-only` checks without writing missing files. All fragment/compressed/full SHA and sizes plus original splice bytes are checked; existing files must match and are never overwritten. Original working evidence is unchanged and ignored only for this run, with one necessary lossless storage representation in Git. No JSON normalization, recreated experiment or duplicate model backup.

Independent remote objects must reconstruct in a new empty directory and match the source .blend before the next development/render item. Full native/visual/world acceptance is separate and remains unpassed.
