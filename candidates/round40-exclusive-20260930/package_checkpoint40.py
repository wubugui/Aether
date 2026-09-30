from pathlib import Path
import zipfile,json
base=Path(__file__).resolve().parent
out=base/'evidence/checkpoint40-bc.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
    for run in ['gpu-b','gpu-c']:
        for path in (base/'evidence'/run).rglob('*'):
            if path.is_file():archive.write(path,str(path.relative_to(base)))
        for path in (base/'evidence'/(run+'-inputs')).rglob('*'):
            if path.is_file():archive.write(path,str(path.relative_to(base)))
        for suffix in ['-summary.json','-comparison.png','.log','.stdout.log','.stderr.log']:
            path=base/'evidence'/(run+suffix)
            if path.is_file():archive.write(path,str(path.relative_to(base)))
    for directory in ['source-assets/hub-cabins40-b']:
        for path in (base/directory).rglob('*'):
            if path.is_file():archive.write(path,str(path.relative_to(base)))
    for path in (base/'evidence').glob('probe-*'):
        if path.is_file():archive.write(path,str(path.relative_to(base)))
    for filename in ['hub-cabins40-b-task.json','hub-cabins40-b-result.json','independence-audit.json']:
        path=base/'evidence'/filename
        if path.is_file():archive.write(path,str(path.relative_to(base)))
    archive.write(base/'run-candidate40.cmd','run-candidate40.cmd')
print('checkpoint zip bytes',out.stat().st_size)
