"""Pure frozen-preparation check. No child launch, exports, or writes."""
import ast
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_readback58k as r
g = r.g; c = g.c


def main():
    inputs = r.frozen_inputs(); c.source_preconditions()
    for path in g.HERE.glob('*.py'):
        ast.parse(path.read_text())
    c.require(c.sha(c.BLENDER) == c.BLENDER_SHA, 'Pinned official Blender executable')
    c.require(len(list(Path('/proc/self/task').iterdir())) == 1, 'Single-threaded supervisor')
    c.require(not (g.HERE / 'native-attempt.json').exists() and not (g.HERE / 'native-terminal.json').exists(), 'No prior native attempt')
    c.require(c.sha(g.FAILED_GLB) == g.FAILED_GLB_SHA, 'Failed GLB retained')
    print(c.json.dumps(dict(passed=True, version=g.VERSION, frozen_file_count=len(inputs),
                           source_sha256=c.SOURCE_SHA, failed_glb_sha256=g.FAILED_GLB_SHA,
                           native_started=False, export_performed=False, images=0, world_loaded=False), indent=2))


if __name__ == '__main__':
    main()
