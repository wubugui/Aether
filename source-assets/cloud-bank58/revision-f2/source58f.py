"""F2 adapter: use the exact frozen F native builder without copying it.

The inherited internal VIEW58F/EDIT58F labels and *58f.json report schema remain
unchanged. Candidate identity is the F2 directory, mesh and distinct blend path.
The native build and both fresh render processes use F2's coordinate authority.
No F file, E camera, lighting, material, margin or assertion is modified.
"""
from pathlib import Path
import hashlib
import sys

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parent / 'revision-d/native-01'))
import common58d as c

F_BUILDER = P.parent / 'revision-f/source58f.py'
assert hashlib.sha256(F_BUILDER.read_bytes()).hexdigest() == 'addcc0d93958da217e2fc8e280fe44a2f7a8b340731c477ccc736445e59cf232'
base = c.load_pure(F_BUILDER)
base.P = P
base.SOURCE = P / 'shared_patch58f2.blend'
base.NAME = 'CloudBank58F2_shared_crown_shoulder_belly_skin'
base.patch = c.load_pure(P / 'patch58f.py')

if __name__ == '__main__':
    base.main()
