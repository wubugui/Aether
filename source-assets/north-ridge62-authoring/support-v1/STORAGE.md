# Lossless report storage

The current full167-row report and the rejected earlier report are retained locally. Their raw bytes are too large for the bounded publishing path, so Git should store the lossless gzip counterparts. `storage.json` records raw and gzip sizes/SHA256. No numeric precision or row has been removed.

After a fresh checkout, run:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-authoring/support-v1/restore_reports62.py

This only restores absent raw reports and verifies all bytes. An existing differing report is an error and is never overwritten. Restore before tests, which inspect the full current result. The preparation-v1 original support-plan storage contract remains unchanged.
