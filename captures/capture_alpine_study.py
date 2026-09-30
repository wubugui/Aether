"""Raw GPU views of an isolated native mountain modeling study."""
from pathlib import Path
import sys,subprocess
root=Path('D:/test6');label=sys.argv[1]
assert label in ['11a','11b','11c','11d','11e','11f','11g','11h','11i']
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
for view in sys.argv[2:]:
 assert view in ['opening','mountain-back','mountain-side']
 stem=root/'captures'/f'round-{label}-study-{view}';assert not stem.with_suffix('.png').exists()
 with stem.with_suffix('.stdout.log').open('w') as out,stem.with_suffix('.stderr.log').open('w') as err:
  result=subprocess.run([str(root/'.tools/godot/Godot_v4.5.1-stable_win64.exe'),'--path',str(root),'--script',str(root/'captures'/f'preview_alpine_{label}.gd'),'--','--capture','--view='+view,'--output='+str(stem.with_suffix('.png'))],cwd=root,stdout=out,stderr=err,startupinfo=startup,timeout=100)
 assert result.returncode==0 and stem.with_suffix('.png').exists()
 text=stem.with_suffix('.stdout.log').read_text(errors='replace')+stem.with_suffix('.stderr.log').read_text(errors='replace')
 assert not any(s in text for s in ['SCRIPT ERROR','ERROR:'])
 print(stem.with_suffix('.png'),flush=True)
