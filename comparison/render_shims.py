"""Render actual exported calibration shims; no chosen screw stack is implied."""
import subprocess,json,hashlib,os,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
EXE=os.environ.get('OPENSCAD_RENDER') or shutil.which('openscad') or '/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD'
font='/System/Library/Fonts/Supplemental/Arial.ttf';bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def label_font(n,strong=False):
    for candidate in [os.environ.get('RENDER_FONT_BOLD' if strong else 'RENDER_FONT'),bold if strong else font,'DejaVuSans-Bold.ttf' if strong else 'DejaVuSans.ttf']:
        if not candidate:continue
        try:return ImageFont.truetype(candidate,n)
        except OSError:pass
    return ImageFont.load_default(size=n)
manifest=[]
parts=[('0p5','0.5'),('1','1.0'),('1p5','1.5'),('2','2.0')]
for token,label in parts:
    source=ROOT.parent/f'p1-screw-shim-{token}mm.stl'
    scad=ROOT/f'shim-{token}.scad'
    scad.write_text(f'$vpt=[0,0,0.5];$vpr=[58,0,28];$vpd=56;\ncolor("#bbc5cd") import({json.dumps(str(source))});\n')
    cmd=[EXE,'--preview','--projection','o','--colorscheme','Tomorrow','--imgsize','900,700','-o',str(scad.with_suffix('.png')),str(scad)]
    r=subprocess.run(cmd,capture_output=True,text=True)
    (ROOT/f'shim-{token}.log').write_text(r.stdout+r.stderr)
    if r.returncode or 'ERROR:' in r.stderr:raise RuntimeError(r.stderr)
    manifest.append({'part':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'command':cmd})
im=Image.new('RGB',(2200,1450),'#f7f7f7');d=ImageDraw.Draw(im)
d.text((65,35),'Screw-stack calibration kit | Four separate shims',fill='#183241',font=label_font(45,True))
d.text((65,101),'Actual exported parts · Same camera and scale · Thickness choice requires measured insert depth',fill='#526976',font=label_font(25))
for i,(token,label) in enumerate(parts):
    x=60+(i%2)*1090;y=175+(i//2)*580
    pic=Image.open(ROOT/f'shim-{token}.png').convert('RGB');pic.thumbnail((1030,500),Image.Resampling.LANCZOS)
    im.paste(pic,(x+(1030-pic.width)//2,y))
    d.text((x+60,y+502),label+' mm thickness',fill='#183241',font=label_font(32,True))
d.text((65,1360),'Capsule 14 × 20 mm · Bore 6.8 × 12.8 mm · Metal washer still required · Fit/creep untested',fill='#526976',font=label_font(25))
im.save(ROOT/'calibration-shims.png')
(ROOT/'shim-render-manifest.json').write_text(json.dumps(manifest,indent=2))
