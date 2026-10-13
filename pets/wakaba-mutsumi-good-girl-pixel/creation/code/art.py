from pathlib import Path
import json
from PIL import Image, ImageDraw

P = {
    'ink': '#000000', 'hair': '#E8FFE7', 'hair_shadow': '#5D722A',
    'hair_line': '#5D722A', 'skin': '#FFF5ED', 'blush_base': '#FCDDD2',
    'blush': '#E698AA', 'iris': '#E6C9B7', 'iris_line': '#8D614C',
    'shine': '#FEFFFF', 'bow': '#1C334D', 'bow_light': '#1C334D',
    'cloth': '#FEFFFF', 'cloth_shadow': '#5D722A', 'paper': '#E6C9B7',
    'cucumber': '#5D722A', 'cucumber_light': '#E8FFE7',
}
REFERENCE = Path(__file__).resolve().parents[1] / 'references'
CAPTIONS = json.loads((REFERENCE / 'caption-pixels.json').read_text(encoding='utf-8'))


def polygon(im, points, fill, width=1, outline=None):
    d = ImageDraw.Draw(im)
    d.polygon(points, fill=fill)
    if outline:
        d.line(points + [points[0]], fill=outline, width=width, joint='curve')


def reference_head():
    head = Image.open(REFERENCE / 'pixel-reference.png').convert('RGBA')
    for y in range(11):
        for x in range(15):
            head.putpixel((x,y),(0,0,0,0))
    return head


HEAD = reference_head()
EYE_BOXES = ((18,30,28,39),(36,32,48,41))
IRIS_COLORS = {Image.new('RGBA',(1,1),P[k]).getpixel((0,0)) for k in ('iris','shine')}
EYE_COLORS = IRIS_COLORS | {Image.new('RGBA',(1,1),P['iris_line']).getpixel((0,0))}
EYE_PIXELS = [{(x,y) for y in range(y1,y2) for x in range(x1,x2)
               if HEAD.getpixel((x,y)) in EYE_COLORS}
              for x1,y1,x2,y2 in EYE_BOXES]


def head_pose(expression='neutral', look=(0,0)):
    h = HEAD.copy()
    d = ImageDraw.Draw(h)
    brows={
        'smug': [(24,25),(25,25),(26,26)],
        'review': [(24,25),(25,25),(26,25)],
        'alert': [(24,25),(25,25),(26,25)],
        'failed': [(24,25),(25,26),(26,26)],
        'focused': [(24,26),(25,26),(26,27)],
    }
    if expression in brows:
        for x in (24,25,26):
            d.point((x,26),fill=P['hair'])
        for point in brows[expression]:
            d.point(point,fill=P['blush'])
    if look != (0,0):
        dx, dy = look
        sclera=Image.new('RGBA',(1,1),P['skin']).getpixel((0,0))
        for eye in EYE_PIXELS:
            interior={point for point in eye if HEAD.getpixel(point) in IRIS_COLORS}
            for x,y in interior:
                source=(x-dx,y-dy)
                h.putpixel((x,y),HEAD.getpixel(source) if source in interior else sclera)
    return h


def hand(im, x, y, gesture='closed'):
    d=ImageDraw.Draw(im)
    if gesture == 'wave':
        polygon(im, [(x,y+7),(x-1,y+3),(x,y+1),(x+1,y+2),(x+1,y-1),
                     (x+3,y-1),(x+3,y+2),(x+4,y),(x+6,y+1),(x+6,y+5),
                     (x+4,y+8),(x+1,y+8)], P['skin'], 1, P['ink'])
    else:
        polygon(im, [(x,y+1),(x+2,y),(x+5,y),(x+6,y+2),(x+5,y+5),
                     (x+2,y+6),(x,y+4)], P['skin'], 1, P['ink'])
        d.line([(x+2,y+1),(x+2,y+3)], fill=P['blush_base'])


def cucumber(im,x,y,lean=0):
    polygon(im, [(x,y+2),(x+2,y),(x+4,y+1),(x+5+lean,y+9),
                 (x+3+lean,y+12),(x+1+lean,y+11)], P['cucumber'], 1, P['ink'])
    d=ImageDraw.Draw(im)
    d.line([(x+2,y+2),(x+2+lean,y+9)], fill=P['cucumber_light'])
    for px,py in ((x+3,y+3),(x+2,y+6),(x+3+lean,y+8)):
        d.point((px,py), fill=P['ink'])


def horizontal_cucumber(im,x,y):
    asset=Image.new('RGBA',(7,13))
    cucumber(asset,0,0)
    im.alpha_composite(asset.transpose(Image.Transpose.ROTATE_90),(x,y))


def gift_bag(im,returned=False):
    d=ImageDraw.Draw(im)
    if returned:
        cucumber(im,11,40,-1)
        cucumber(im,18,41,1)
        polygon(im,[(7,47),(25,45),(26,56),(10,57)],P['paper'],1,P['ink'])
        d.line([(10,48),(23,47)],fill=P['iris_line'])
        d.line([(15,49),(19,53)],fill=P['blush'],width=1)
        d.line([(19,49),(15,53)],fill=P['blush'],width=1)
        hand(im,25,48)
    else:
        cucumber(im,5,37)
        cucumber(im,11,36,1)
        polygon(im,[(1,47),(20,46),(19,56),(3,56)],P['paper'],1,P['ink'])
        d.line([(4,49),(17,49)],fill=P['iris_line'])
        hand(im,0,48)
        hand(im,19,47)


def watering(im):
    d=ImageDraw.Draw(im)
    polygon(im,[(1,37),(8,37),(10,41),(8,45),(1,45)],P['bow'],1,P['ink'])
    polygon(im,[(8,38),(12,35),(14,36),(10,42)],P['bow'],1,P['ink'])
    d.rectangle((2,34,7,38),outline=P['ink'])
    d.line([(3,35),(6,35)],fill=P['shine'])
    hand(im,3,43)
    for p in ((14,39),(15,41),(17,44)):
        d.point(p,fill=P['bow'])
    d.line([(18,45),(18,51)],fill=P['ink'])
    polygon(im,[(18,47),(15,43),(12,43),(13,46),(17,48)],P['cucumber'],1,P['ink'])
    polygon(im,[(18,47),(21,43),(24,43),(23,46),(19,48)],P['cucumber'],1,P['ink'])
    polygon(im,[(12,50),(25,50),(23,56),(14,56)],P['paper'],1,P['ink'])
    d.line([(13,51),(24,51)],fill=P['iris_line'])


def pixel_text(text):
    data = CAPTIONS[text]
    image = Image.new('RGBA', (data['width'], data['height']))
    draw = ImageDraw.Draw(image)
    for y, row in enumerate(data['rows']):
        for x, bit in enumerate(row):
            if bit == '1':
                draw.point((x, y), fill=P['ink'])
    return image


def bubble(im,text=None,icon=None,head_y=48):
    if not text and not icon:
        return
    label=pixel_text(text) if text else None
    w=(label.width if label else 22)+12
    h=(label.height if label else 15)+9
    x,y=max(3,52-w),head_y-h-6
    polygon(im, [(x+5,y),(x+w-5,y),(x+w-5,y+1),(x+w-2,y+1),
                 (x+w-2,y+3),(x+w,y+3),(x+w,y+h-4),(x+w-2,y+h-4),
                 (x+w-2,y+h-1),(x+w-5,y+h-1),(x+w-5,y+h),
                 (x+5,y+h),(x+5,y+h-1),(x+2,y+h-1),(x+2,y+h-3),
                 (x,y+h-3),(x,y+4),(x+2,y+4),(x+2,y+1),(x+5,y+1)],
            P['shine'],1,P['ink'])
    d=ImageDraw.Draw(im)
    d.rectangle((43,y+h+3,46,y+h+5), fill=P['shine'], outline=P['ink'])
    d.point((49,y+h+8), fill=P['ink'])
    if label:
        im.alpha_composite(label,(x+6,y+5))
    else:
        cucumber(im,x+16,y+4,1)

