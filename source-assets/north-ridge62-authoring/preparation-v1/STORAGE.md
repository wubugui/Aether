# Lossless support-plan storage

The frozen original instance-support-plan.json is retained locally but stored in Git as lossless gzip. Its original bytes/SHA and the unchanged preparation freeze remain authoritative. support-plan-storage.json gives both hashes. After a fresh clone, if and only if the raw file is absent, run from this directory:

gzip -dc instance-support-plan.json.gz > instance-support-plan.json

Verify its original SHA against support-plan-storage.json and FINAL_SHA256.json before any preparation/build. Never overwrite an existing differing raw file. This packaging does not change the candidate or any of the 676 decisions; no new native evidence is claimed.
