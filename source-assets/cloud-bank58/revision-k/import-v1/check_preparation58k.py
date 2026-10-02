"""Read-only preparation validation; never starts Blender/Godot or writes artifacts."""
import ast
import os
from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_import58k as run
c=run.c

def main():
    files=run.frozen_inputs();c.source_preconditions()
    for path in c.HERE.glob('*.py'):ast.parse(path.read_text())
    c.require(c.sha(c.BLENDER)==c.BLENDER_SHA and c.sha(c.GODOT)==c.GODOT_SHA,'Pinned installed binaries')
    c.require(len(list(Path('/proc/self/task').iterdir()))==1,'Supervising NumPy process must remain single-threaded')
    c.require(not (c.HERE/'native-attempt58k.json').exists() and not (c.HERE/'native-terminal58k.json').exists(),'Native trial already attempted')
    print(c.json.dumps(dict(passed=True,frozen_file_count=len(files),source_sha256=c.SOURCE_SHA,native_started=False,export_performed=False,godot_parse_performed=False,images=0,world_loaded=False,source_bytes=c.SOURCE.stat().st_size),indent=2))

if __name__=='__main__':main()
