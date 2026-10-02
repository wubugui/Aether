# Lossless storage for the generated preparation

The original frozen source-bounds-preparation.json is1,049,150bytes. It is retained locally and stored in Git as source-bounds-preparation.json.gz with exact raw/stored SHA256 in storage.json. No original preparation, source code, test or freeze was changed by this packaging.

After a fresh clone, if and only if the raw file is absent, restore it before the original static/native command:

    gzip -dc source-bounds-preparation.json.gz > source-bounds-preparation.json

Then the unmodified run_proxy62.py first requires the original raw SHA from FINAL_SHA256.json and independently rebuilds and byte-compares the entire result. Do not replace an existing differing raw file or adopt changed data as a new baseline. The current raw bytes already roundtrip exactly. The separate storage files are packaging records, not new native inputs or engine proof.
