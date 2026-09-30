"""Run untouched GPU game captures for a disposable modeling study."""
import sys,subprocess
from pathlib import Path
root=Path('D:/test6');study=sys.argv[1]
assert study in ('10b','10c','10d','10e','10f','10g','10h','10i','10j','10k','10l')
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
for view in sys.argv[2:]:
    assert view in ('opening','cliff-side','cliff-back','cliff-top','cliff-low')
    stem=root/'captures'/f'round-{study}-study-{view}'
    assert not stem.with_suffix('.png').exists(),'Keep prior images immutable'
    cmd=[str(root/'.tools/godot/Godot_v4.5.1-stable_win64.exe'),'--path',str(root),'--script',str(root/'captures'/f'preview_cliff_sections_{study}.gd'),'--','--capture','--view='+view,'--output='+str(stem.with_suffix('.png'))]
    with stem.with_suffix('.stdout.log').open('w') as out,stem.with_suffix('.stderr.log').open('w') as err:
        result=subprocess.run(cmd,cwd=root,stdout=out,stderr=err,startupinfo=startup,timeout=90)
    assert result.returncode==0 and stem.with_suffix('.png').exists(),str(stem)
    print(stem.with_suffix('.png'),flush=True)
