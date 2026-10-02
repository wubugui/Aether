# Fixed shared work-copy relocation and renderer admission

Preparation only: no actual member of the bound work copy has been moved, no
second project has been copied, and no engine or new image has been produced.
The original v1 freeze, successful parse, failed renderer admission and terminal
records remain unchanged.

The v1 parse completed successfully in the execution namespace. Its project
`/tmp/cloud58k-world-trial-v1-d92irkqc` remained complete at read-only diagnosis:
all 4889 files matched the successful parse manifest, SHA256
`0cc6c72f733f51320a460a1e31be153b1516aafba3576abe792a3569685201ea`.
The GUI terminal namespace could not see that same /tmp path and rejected the
renderer before launching Godot. That failure is not a native render failure.

The source /tmp device is 39 and the authorized shared workspace device is 27;
an atomic same-filesystem rename cannot relocate between these mounts. This v2
therefore implements one explicitly authorized cross-device move, with the fixed
destination outside the repository:

`/workspace/scratch/a29d03198654/Aether-working/cloud58k-world-trial-v2`

## Move protocol and failure behavior

1. Revalidate the old 47-file freeze, actual successful parse terminal/report and
   original full manifest. Read/hash all original 4889 members. Require destination
   absence. Record the original files, empty directories and complete directory set,
   plus before/after root and every directory's device/inode/mode/time identities
2. For each member, exclusively create its destination, stream no more than 1 MiB
   at once, hash the copied source bytes, independently rehash destination, preserve
   metadata and fsync file plus destination directory
3. Durably journal verified destination bytes/inode metadata. Recheck the original
   source identity/hash, remove only that source file, fsync its directory and
   durably journal the completed move. Fsync each newly created directory's parent,
   the evidence run's parent and the journal's parent when first created
4. Verify the final relative member names, all SHA values and directories exactly
   equal the original. Remove the now-empty original directories/root. Bind both
   full before/after manifests and the original parse authority into one receipt

At most the single current file exists on both sides before verification/deletion;
this does not create a second complete working project. The original main project
is never moved or modified. The move phase has a finite 180-second filesystem
budget and CPU2 affinity; its outer 300-second guard remains active during final
partition/protection checks. A read error is recorded for that member/side and
does not discard other partition entries. Main-project and frozen-input final
checks run independently; if the outer deadline is exhausted, remaining checks
are marked failed rather than performed outside the budget. This starts no native
process and changes none of the original renderer budgets.

Any error stops the move. It preserves both sides, the fsynced per-file journal
and a final per-member partition of moved/unmoved/both/unresolved hashes. A source
file is never removed before its verified destination is durable. There is no
automatic retry, rollback, resume, tree rebuild or fallback copy. A failed or
interrupted admission requires reviewing the retained partition before a separate
explicit recovery. The tool cannot guarantee final JSON after SIGKILL; the
fsynced journal and file contents still allow read-only reconciliation.

## Same render experiment, new fixed path

The v2 renderer accepts only the exact fixed destination of a successful
same-v2-freeze migration. It rechecks the complete actual shared tree against
the SHA-bound original relative parse manifest and directory set. All five
existing trial/native files are moved unchanged. No GDScript, camera, material,
geometry, weather, original 47-file freeze or parse result is modified.

The four-image result validator is source/AST-equivalent to v1, including original
front off/on camera/projection, geometry and material byte identity, fixed
1216/.35 weather, PNG SHA/IHDR/native Image 1179×664, and opt-out restore. The
actual original 1180×664 window/texture metadata distinctions remain unchanged.
CPU2, aggregate 3 GiB, native 240 s and outer wrapper 300 s remain the original
limits. Hardware/visual/full-world acceptance remains false until actual images
are independently reviewed. Known one-unit size mismatch and neighbor obstruction
risks are unchanged.

The renderer uses only the existing parent-provided DISPLAY environment. Neither
tool searches for a display, changes networking, starts a display server, nor
changes a permission setting. The parent first verifies the shared copy from the
GUI process namespace with the read-only check below.

## Parent-scheduled commands, not executed during preparation

After freezing/reviewing/publishing v2, run the relocation once in the execution
namespace that can currently see the original /tmp project:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-k/world-trial-v2/relocate58k.py --relocate-approved-copy

From the existing GUI terminal, prove that its namespace can read all the same
actual shared files. This does not start Godot or write a receipt:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-k/world-trial-v2/run_renderer58k.py --check-shared-copy

Only after that read succeeds and the parent coordinates the graphical window:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-k/world-trial-v2/run_renderer58k.py --run-approved-world-trial

No project-copy or parse fallback exists. Default invocations do nothing.
Source preparation checks and synthetic tiny-file failure tests are not proof
that actual cross-namespace relocation or rendering has succeeded.
