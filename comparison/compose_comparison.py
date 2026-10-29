"""Compose labeled matching-camera sheets from final actual-mesh PNGs."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys, os
ROOT=Path(__file__).resolve().parent
SELECTED=set(sys.argv[1:])
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def font(n,b=False):
    candidates=[os.environ.get('RENDER_FONT_BOLD' if b else 'RENDER_FONT'),BOLD if b else FONT,'DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf']
    for candidate in candidates:
        if not candidate:continue
        try:return ImageFont.truetype(candidate,n)
        except OSError:pass
    return ImageFont.load_default(size=n)
def sheet(name,title,rows):
    if SELECTED and name not in SELECTED:return
    w,h=2400,235+len(rows)*860+85
    im=Image.new('RGB',(w,h),'#f7f7f7');d=ImageDraw.Draw(im)
    d.text((65,35),title,fill='#183241',font=font(48,True))
    d.text((65,101),'Matching cameras, scale and material · Actual exported geometry · Dimensions in millimeters',fill='#526976',font=font(25))
    d.text((65,162),'BEFORE · James Rich v1.0 / 9981cb6',fill='#183241',font=font(31,True))
    d.text((1255,162),'AFTER · Separate v1.1 revision',fill='#183241',font=font(31,True))
    for i,(view,label,description) in enumerate(rows):
        y=235+i*860
        for j,rev in enumerate(['before','after']):
            pic=Image.open(ROOT/f'{rev}-{view}.png').convert('RGB')
            pic.thumbnail((1130,740),Image.Resampling.LANCZOS)
            x=55+j*1190
            im.paste(pic,(x+(1130-pic.width)//2,y))
        d.text((65,y+745),label,fill='#183241',font=font(31,True))
        d.text((65,y+793),description,fill='#526976',font=font(25))
    d.line((65,h-70,w-65,h-70),fill='#ccd3d9',width=2)
    d.text((65,h-51),'Original © James Rich · CC BY-SA 4.0 · Digital CAD comparison · Physical fit / heat / road retention untested',fill='#526976',font=font(23))
    im.save(ROOT/f'{name}.png')
sheet('before-after-overview','SenseCAP P1 mount | Before and after',[
 ('n-overview','N-type frame','The original pylon and mounting interfaces are preserved; the frame junctions are refined.'),
 ('stock-overview','Stock RP-SMA frame','Same frame refinements, with a separately testable stock-connector interface.')])
sheet('before-after-details','Detail comparison | Frame windows and underside',[
 ('window','Spine, hub and rail junctions','Local rounded blends replace abrupt internal window corners; hardware interfaces remain distinct.'),
 ('underside','Underside / print orientation','Matching views expose loaded roots, tool access and the bed-contact faces.')])
sheet('before-after-pylon','Interface comparison | Stock connector and N-type section',[
 ('stock-bore','Stock bore entry','D-flat antirotation geometry is preserved; inspect the revised entry treatment and bearing roof.'),
 ('n-section','N-type center section at X = 0','True Boolean sections of the final exported meshes; no reference hardware obscures the boundary.')])
sheet('before-after-cable-saddles','Cable support | Left-rear mounting region',[
 ('saddle-n','N-type saddle and rear foot','After: rounded tie cradle follows the proposed coax route; the magnet and nut interfaces are retained.'),
 ('saddle-stock','Stock saddle and rear shoulder','After: variant-specific cradle location; actual tie fit and cable loading require a coupon test.')])
sheet('before-after-assembly','Assembly context | Complete nominal cable routes',[
 ('assembly-n','N-type assembly reference','Approximate node / antenna / hardware. After route is nominal; 300 mm cable-length datum is unverified.'),
 ('assembly-stock','Stock assembly reference','Before has no full cable model. After includes the proposed route; surplus cable and real fit unverified.')])
