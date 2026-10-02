"""One explicit restored-source fresh open and read; no build, save or render."""
import argparse, os, sys, traceback
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import restore_contract62 as r
c = r.c
sys.path.insert(0, str(r.V2))
import telemetry62 as telemetry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--restore-root', type=Path, required=True)
    parser.add_argument('--restored-source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    out = r.no_symlinks(args.out)
    c.require(out.is_dir() and out.is_relative_to(c.ROOT / 'cloud-evidence') and
              not out.is_relative_to(r.ACTUAL_RUN), 'Separate new evidence output required')
    telemetry.initialize(out, 'restore-read')
    report = dict(version=r.VERSION, recovery_version=c.RECOVERY_VERSION, mode='restore-read',
                  pid=os.getpid(), passed=False, state='started', source_saved=False,
                  rebuild_performed=False, images=0, world_loaded=False,
                  world_integration_allowed=False, visual_acceptance=False)
    before = None
    try:
        before = r.restore_identity(args.restore_root, args.restored_source)
        r.preparation_inputs(require_local_freeze=True)
        canonical_before = c.sha(c.SOURCE)
        binding = c.read(c.BINDING_PATH); c.check_binding(binding)
        # Importing frozen native62 does not run its main or rebuild entrypoint.
        import bpy
        import native62
        telemetry.emit('fresh_open.begin', restored_source=str(args.restored_source))
        bpy.ops.wm.open_mainfile(filepath=str(args.restored_source), load_ui=False, use_scripts=False)
        report['actual_opened_filepath'] = bpy.data.filepath
        c.require(Path(bpy.data.filepath) == args.restored_source, 'Actual bpy.data.filepath must equal explicit restored source')
        telemetry.emit('fresh_open.complete')
        raw = native62.capture(binding)
        rawpath = out / 'restore-read-raw.json'
        c.require(not rawpath.exists(), 'Never overwrite actual raw')
        c.write(rawpath, raw)
        # Preserve complete actual raw and its hash BEFORE any native validator.
        report.update(raw_sha256=c.sha(rawpath), raw_path=str(rawpath))
        c.write(out / 'restore-read-result.json', report)
        telemetry.emit('raw.persisted', sha256=report['raw_sha256'], bytes=rawpath.stat().st_size)
        report['validation'] = c.validate_raw(raw, binding)
        r.same_raw(raw, c.read(c.ROOT / r.RAW_REL))
        c.require(c.sha(c.SOURCE) == canonical_before == r.EXPECTED[r.SOURCE_REL][1], 'Canonical original remained unchanged')
        report.update(passed=True, state='completed', source_sha256=c.sha(args.restored_source),
                      source_bytes=args.restored_source.stat().st_size, original_build_raw_sha256=r.EXPECTED[r.RAW_REL][1],
                      raw_equal_except_pid_affinity=True)
    except BaseException:
        report.update(passed=False, state='failed', error=traceback.format_exc())
        raise
    finally:
        try:
            report['restored_tree_unchanged'] = bool(before and before == r.restore_identity(args.restore_root, args.restored_source))
            report['canonical_source_unchanged'] = c.sha(c.SOURCE) == r.EXPECTED[r.SOURCE_REL][1]
            report['passed'] = bool(report['passed'] and report['restored_tree_unchanged'] and report['canonical_source_unchanged'])
        except BaseException:
            report.update(passed=False, finalization_error=traceback.format_exc())
        report['state'] = 'completed' if report['passed'] else 'failed'
        telemetry.emit('native_terminal', passed=report['passed'], state=report['state'])
        report['native_stage_timing'] = telemetry.report()
        c.write(out / 'restore-read-result.json', report)
    c.require(report['passed'], 'Restored-source read failed')


if __name__ == '__main__':
    main()
