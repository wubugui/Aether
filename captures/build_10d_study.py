import sys
from pathlib import Path
root=Path('D:/test6')
for flag in ['--front-columns','--western-slab','--crown','--central-wall','--shadow-buttress']:
    sys.argv=['blender','--',flag]
    path=root/'captures/verify_cliff_sections_10d.py'
    exec(compile(path.read_text(),str(path),'exec'),{'__file__':str(path),'__name__':'__main__'})
sys.argv=['blender','--','0,-1','0,0']
path=root/'captures/build_10d_ground.py'
exec(compile(path.read_text(),str(path),'exec'),{'__file__':str(path),'__name__':'__main__'})
