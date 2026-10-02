# First saved-scatter collection: failed, partial evidence retained

Godot4.5.1 native child2/wrapper1,8.429111191seconds,520152KiB,CPU2, original60-second boundary not triggered. All1568 protected inputs and full1483 dependency/startup/cache/absence controls unchanged. No world instantiated or resource saved.

The partial report has741 group records (not741 complete groups),52628 counted instances,316 query hits and245 design-box hits. It stopped at World/Vegetation/Authored_WestRoadCopse with independent_saved_transform_mismatch. Native JSON's printed actual/expected values appear identical; the existing log does not preserve enough float64 bits to diagnose that equality failure. The independent prepared values include -107.0479736328125,14.084564208984375,-168.0250244140625. They must not simply be epsilon-relaxed. A canonical float32/JSON parsing diagnosis is next.

Raw stderr also has17 HashingContext.update(empty) failures. Empty hashes must use start/finish without update(empty), as already established separately in the orbit fixture; this collector currently does not check hashing return codes. These errors stay fatal in the wrapper; they are not filtered. Neither all775 buffer agreement nor final occupancy completeness is established.

Native3,634,488-byte JSON and prepared2,283,728-byte metadata are retained through lossless gzip with original SHA256 and exact restoration commands in storage.json. All raw logs and source snapshots are preserved. Old source/preparation, successful syntax-only parse and this failed run remain unchanged. native_collection_passed/native_buffer_retention_verified/all_occupancy_complete are false.
