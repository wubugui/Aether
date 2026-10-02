"""Read-only preparation check: no adjusted GLB, native child or file writes."""
import ast
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_transfer58k as r
t = r.t; c = t.c


def main():
    inputs = r.frozen_inputs(); source = t.evidence_source()
    for path in t.HERE.glob('*.py'):
        ast.parse(path.read_text())
    c.require(c.sha(c.GODOT) == c.GODOT_SHA, 'Pinned official Godot')
    c.require(len(list(Path('/proc/self/task').iterdir())) == 1, 'Single-threaded supervisor')
    c.require(not (t.HERE / 'native-attempt.json').exists() and not (t.HERE / 'native-terminal.json').exists(), 'No prior transfer attempt')
    c.require(not list(t.HERE.glob('*.glb')), 'No prepared GLB artifact')
    c.require((t.HERE / 'probe58k.gd').read_bytes() == (c.HERE / 'probe58k.gd').read_bytes(), 'Inherited native probe unchanged')
    print(c.json.dumps(dict(passed=True, version=t.VERSION, frozen_file_count=len(inputs), source_sha256=c.SOURCE_SHA,
                           actual_native_normal_sha256=t.RAW_SHA, original_glb_sha256=t.g.FAILED_GLB_SHA,
                           native_started=False, adjusted_glb_created=False, images=0, world_loaded=False,
                           original_readback_validation_passed=source['original_native_validation_passed']), indent=2))


if __name__ == '__main__':
    main()
