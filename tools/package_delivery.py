"""Package final artifacts and reproducible evidence, excluding runtime/scratch data."""
from pathlib import Path
from html.parser import HTMLParser
import zipfile

root=Path(__file__).resolve().parents[1]
files=set()
for pattern in ['*.scad','*.stl','*.3mf','README.md','LICENSE','CHANGELOG.md','BUILD-MANIFEST.json','COMPARISON.html','toolpaths-*.png','toolpath-review.json']:
    files.update(root.glob(pattern))
extensions={'.py','.txt','.md','.scad','.png','.json','.html','.3mf','.log','.stl'}
for folder in ['docs','tools','comparison','audits','slicer','validation']:
    for p in (root/folder).rglob('*'):
        if not p.is_file() or any(x in ['__pycache__','input','assembly-assets'] for x in p.parts):continue
        if p.name.startswith(('last-','candidate-','stock-coupon-test','route-n-interim','route-stock-interim','blend-simplify-test')):continue
        relative=p.relative_to(root)
        if p.name.startswith('gui-') and p.suffix == '.3mf':continue
        if relative.parts[:2]==('validation','cantilever-reopen') and p.suffix not in {'.py','.txt','.md','.png','.json','.log'}:continue
        if relative.parts[:2]==('validation','slicer-fix'):
            # Retain analysis reports/scripts; omit repeated raw G-code,
            # experimental meshes/projects, caches and third-party source.
            # Final print toolpaths remain embedded in the delivered 3MFs.
            if p.suffix not in {'.py','.txt','.md','.png','.json','.log'}:continue
        elif p.suffix not in extensions:continue
        files.add(p)
target=root/'p1-mount-v1.1-package.zip';prefix='p1-car-mount-v1.1/'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):z.write(p,prefix+str(p.relative_to(root)))
with zipfile.ZipFile(target) as z:
    names=set(z.namelist())
    class Check(HTMLParser):
        def handle_starttag(self,tag,attrs):
            for k,v in attrs:
                if k in ['href','src'] and not v.startswith('https://'):
                    assert prefix+v in names,v
    Check().feed((root/'COMPARISON.html').read_text())
    assert z.testzip() is None
print(f'Package checked: {len(files)} files, {target.stat().st_size/1024/1024:.1f} MB. All report links included.')
