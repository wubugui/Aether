"""Read-only check; never parses GDScript natively or creates a scene/project."""
import ast
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_cache58k as r
g = r.g; c = g.c


def main():
    inputs = r.frozen_inputs(); source, expected, _, _ = g.reference()
    for path in g.HERE.glob('*.py'):
        ast.parse(path.read_text())
    c.require(c.sha(c.GODOT) == c.GODOT_SHA, 'Official pinned Godot binary')
    c.require(len(list(Path('/proc/self/task').iterdir())) == 1, 'Single-thread supervisor')
    c.require(not (g.HERE / 'native-attempt.json').exists() and not (g.HERE / 'native-terminal.json').exists(), 'No native attempt')
    c.require(not list(g.HERE.glob('*.glb')) and not list(g.HERE.glob('*.scn')) and not list(g.HERE.glob('*.tscn')), 'No new native/artifact outputs during preparation')
    print(c.json.dumps(dict(passed=True, version=g.VERSION, frozen_file_count=len(inputs), cache_sha256=g.CACHE_SHA,
                           source_sha256=c.SOURCE_SHA, original_cache_format=expected['format'], native_started=False,
                           reimport_performed=False, glb_derived=False, images=0, world_loaded=False), indent=2))


if __name__ == '__main__':
    main()
