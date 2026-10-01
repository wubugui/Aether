# Read-only native GitHub connector publishing assessment

Checkpoint:85bb7c7b9bb675784708d4ac1cc8e5539f25ddfa, remote migration base851f7374f1f9625c57aa1c992f4550efaa8e6bee. No connector blob/tree/commit/ref mutations have been performed by this task. Parent approval of route is pending. Current uncommitted53 work and pending52e verification are outside this frozen checkpoint.

## Measured local facts

37 local commits add1950 unique blobs totaling1,668,214,715bytes. The final tree needs1933new unique blobs totaling1,667,957,808bytes across2859added paths; there are no modifications/deletions against the final migration tree.221code/config blobs total1,286,388bytes, but publishing these alone would omit the actual native scenes, editable source assets and evidence.12new scene blobs exceed50MiB; none exceeds100MiB. Largest isGame47 at104,193,781bytes (about99.367MiB), base64 length138,925,044. Largest8scene files compress with zlib6 to32.2–32.8MB each, but compressed bytes are not the required native blob content. Complete inventory and exactSHA/path/mode mapping are inblob-inventory.json.

## Exposed native interface and limits

The current GitHub connector DOES expose create_blob(content:string,encoding:utf-8|base64), create_tree(base_tree_sha,tree_elements), create_commit(message,parent_sha,additional_parent_shas,tree_sha) and update_ref(branch_name,sha,force). The earlier assertion that no binary blob API exists was incorrect. It does not expose a file-path upload, multipart/chunk-append blob, compression encoding, or author/committer/date fields in create_commit. Its own maximum tool/string/request payload is undocumented in the exposed metadata and has not been tested. A104MB UTF8 scene therefore requires one complete104MB content argument, or139MBbase64; compression or partial chunks cannot transparently reconstruct the same Git blob through this interface. Do not invent success or a hidden upload method.

GitHub documents regular Git files above100MiB as blocked; the present checkpoint has none, so newLFS is not required by this measured file-size condition. GitHub documents utf8/base64 for create_blob. It also documents general secondary content limits80/minute and500/hour, with endpoint-specific/undisclosed limits possible;A naive1,933blob-write route plus tree/commit/ref operations requires paced execution if supported and may take hours. create_tree also officially accepts inlineUTF8 content per entry, allowing small text files to be batched; roughly981extension-classified binary blobs still need exactbinary creation, while12large text scenes retain the same whole-payload constraint. ConfirmUTF8 bytes before using inlinecontent. This is not a guaranteed exact duration.

## Minimum complete supported sequence, conditional on payload support

1. Through the connected GitHub app, read the target repository, exact final migration commit/tree and destination development branch state. Do not extract credentials, restart blockedCLI login or repurpose a denied network route.
2. Freeze an immutable local publication checkpoint and compare every intended added path/mode/blobSHA. Reuse all remote base objects and deduplicate new blobSHA. A bounded capability check may create a real required blob only after parent confirms this route; do not update any ref during preparation.
3. Create every required binary/large blob using its exact original bytes, and batch verified smallUTF8 contents through normal create_tree entries (content instead ofsha); verify returnedGitSHA against local SHA. Preserve a per-object ledger, honor rate-limit errors/Retry-After, and do not repeat successful objects. The100MB scene payloads are a distinct unverified transport gate. If they fail, stop this route as incomplete rather than leaving native scenes out.
4. Build the exact target tree using the verified remote base tree and2859additions, with actual executable/file modes. Split tree construction only according to normal Git subtree semantics. Verify resulting root treeSHA equals the local checkpoint treeSHA; no partial tree counts as complete.
5. Because create_commit lacks author/date parameters, it cannot reproduce the37 original commitSHAs. A single new publication commit with parent851f and the exact current tree is possible in principle; label it as a checkpoint publication and preserve original local history separately. Do not claim the original37commit history was pushed. If original commit identity is required, this exposed endpoint set is insufficient.
6. Only after everyblob/tree verification, update the explicitly authorized independentdevelopment/feiting-cloud-20260930 ref with force=false, re-read it, and verify commit/treeSHA. Never touchmigration/default branches or declare fullpublication before exact remote verification.

No native endpoint for uploading Gitpack/bundle and server-side unpack is exposed. A compressed scene or bundle committed as a file is an archive, not a runnable native checkout or imported history. No proxy, copiedtoken, hidden API, GitHubActions workflow or alternate credential mechanism is proposed.

Sources checked2026-10-01:
- https://docs.github.com/en/rest/git/blobs#create-a-blob
- https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
- https://docs.github.com/en/rest/git/trees#create-a-tree
- https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
