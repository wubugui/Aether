# Exact runtime evidence storage

14 original runtime JSON paths are represented by 9 unique byte objects: 2 gzip-mtime0 streams, 3 parts, 939502 compressed bytes, and 7 strict literal byte-splice variants. The four original PNG files are direct ordinary Git blobs. The already published source .blend is referenced, not duplicated.

Run `python restore_storage.py --out NEW_EMPTY_DIRECTORY` to reconstruct every original JSON byte; `--verify-only` checks reconstruction without creating missing files. Existing files must match exactly and are never overwritten. Original working raw files remain unchanged and are ignored only for this run; Git carries one necessary lossless representation. Each fragment, compressed stream, full raw SHA/length and literal original splice is checked. No JSON normalization or source regeneration.

This storage verification is separate from scene acceptance. A fresh empty directory must also reconstruct the bytes fetched from the published remote objects before the next development item.
