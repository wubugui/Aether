# Lossless authoring binding storage

The frozen original 5,424,728-byte bindings62.json remains locally available. Git stores its byte-identical lossless XZ form (Python standard-library lzma preset6). The original FINAL_SHA256.json and raw binding SHA are unchanged. This is source-data packaging, not a different candidate or native result.

After a fresh clone, restore the raw binding only when absent, using the exact command in bindings-storage.json. Verify raw bytes/SHA against that file and the original freeze. Never overwrite an existing differing binding. Run the ordinary no-engine source preflight afterward. No third-party decoder or credential is needed.
