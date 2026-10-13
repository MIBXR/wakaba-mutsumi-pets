from pathlib import Path
import json
from PIL import Image, ImageDraw
import art

PET = Path(__file__).resolve().parents[2]
PACKAGE = PET / 'package'
MATERIALS = PET / 'materials'
PREVIEWS = PACKAGE / 'previews'
SLUG = 'wakaba-mutsumi-good-girl-pixel'
NAME = '若叶睦 · 好女孩'
P = art.P
GROUPS = [
    ('idle', '睦头人护瓜', None, [1680,660,660,840,840,1920]),
    ('running-right', '向右移动', '祥 移动', [120]*7+[220]),
    ('running-left', '向左移动', '祥 移动', [120]*7+[220]),
    ('waving', '举瓜打招呼', '好女孩?', [140,140,140,280]),
    ('jumping', '抛瓜庆祝', '太好了呢', [140,140,140,140,280]),
    ('failed', '收到退货', '又退货?', [140]*7+[240]),
    ('waiting', '请收下黄瓜', '不许退货', [150]*5+[260]),
    ('running', '种瓜工作中', '瓜在长了', [120]*5+[220]),
    ('review', '检查黄瓜堆', '不会长久的', [150]*5+[280]),
]
LOOK_VECTORS = [(0,-2),(1,-2),(1,-1),(2,-1),(2,0),(2,1),(1,1),(1,2),
                (0,2),(-1,2),(-1,1),(-2,1),(-2,0),(-2,-1),(-1,-1),(-1,-2)]


def cuke(im, x, y, horizontal=False, lean=0):
    if horizontal:
        art.horizontal_cucumber(im,x,y)
    else:
        art.cucumber(im,x,y,lean)


def shifted_layer(im, draw, dx=0, dy=0):
    layer=Image.new('RGBA',im.size)
    draw(layer)
    im.alpha_composite(layer,(dx,dy))


def water_phase(im, i):
    art.watering(im)
    draw=ImageDraw.Draw(im)
    growth=[0,1,2,2,1,0][i]
    for px,py in [(14,39),(15,41),(17,44)]:
        draw.point((px,py),fill=(0,0,0,0))
    if i in (1,2,3,4):
        for x,y in [(14,38+i%2),(16,41+i%2),(17,44)]:
            draw.point((x,y),fill=P['bow'])
    if growth:
        draw.line([(18,45-growth),(18,50)],fill=P['ink'])
        art.polygon(im,[(18,47-growth),(15,43-growth),(12,43-growth),
                        (13,46-growth),(17,48-growth)],P['cucumber'],1,P['ink'])
        art.polygon(im,[(18,47-growth),(21,43-growth),(24,43-growth),
                        (23,46-growth),(19,48-growth)],P['cucumber'],1,P['ink'])
    if i in (2,3):
        cuke(im,19,40)
    if i==4:
        cuke(im,8,46,horizontal=True)
        art.hand(im,6,49)


def props_for(state, i):
    props=Image.new('RGBA',(54,54))
    if state=='idle':
        y=[46,45,43,42,44,46][i]
        cuke(props,8,y)
        art.hand(props,6,49)
    elif state in ('running-right','running-left'):
        x=8+[0,1,1,0,-1,-1,0,0][i]
        cuke(props,x,46,horizontal=True)
        art.hand(props,x-2 if state=='running-right' else x+10,49)
    elif state=='waving':
        y=[44,37,36,44][i]
        cuke(props,8,y,lean=[0,-1,1,0][i])
        art.hand(props,7,min(49,y+10))
    elif state=='jumping':
        y=[44,46,28,35,44][i]
        x=[8,8,5,6,8][i]
        cuke(props,x,y,lean=1 if i==2 else 0)
        art.hand(props,19,49)
        art.hand(props,42,49)
    elif state=='failed':
        dx=[-8,-3,0,2,0,-2,-5,-8][i]
        shifted_layer(props,lambda layer:art.gift_bag(layer,returned=True),dx)
    elif state=='waiting':
        dx=[2,0,-3,-4,-2,2][i]
        dy=[0,-1,-2,-2,-1,0][i]
        shifted_layer(props,art.gift_bag,dx,dy)
    elif state=='running':
        water_phase(props,i)
    elif state=='review':
        cuke(props,1,46,horizontal=True)
        cuke(props,[4,4,5,4,4,4][i],40,horizontal=True)
        x,y,horizontal=[(0,34,True),(1,34,True),(3,35,True),
                        (0,39,False),(0,35,False),(0,34,True)][i]
        cuke(props,x,y,horizontal)
        art.hand(props,[14,12,12,8,6,14][i],[47,46,44,47,43,47][i])
    return props


def position_for(state,i):
    x,y=28,48
    if state in ('running-right','running-left'):
        direction=1 if state=='running-right' else -1
        x+=direction*[0,1,2,1,0,-1,-1,0][i]
        y+=[0,-1,-1,0,1,1,0,0][i]
    elif state=='jumping':
        y+=[0,2,-6,-2,0][i]
    return x,y


def face_for(state):
    expression={'waving':'alert','jumping':'smug','failed':'failed',
                'waiting':'smug','running':'focused','review':'review'}.get(state,'neutral')
    look=(1,0) if state=='running-right' else (-1,0) if state=='running-left' else (0,0)
    return art.head_pose(expression,look)


def frame(state,i,caption):
    face=face_for(state)
    portrait=face.copy()
    portrait.alpha_composite(props_for(state,i))
    for eye in art.EYE_PIXELS:
        for point in eye:
            portrait.putpixel(point,face.getpixel(point))
    art.finish_portrait(portrait)
    canvas=Image.new('RGBA',(96,104))
    x,y=position_for(state,i)
    canvas.alpha_composite(portrait,(x,y))
    art.bubble(canvas,caption,head_y=y)
    draw=ImageDraw.Draw(canvas)
    if state in ('running-right','running-left'):
        shift=i%3
        if state=='running-right':
            lines=[(x-4-shift,y+30,x+1-shift,y+30),(x-7,y+36,x-2,y+36)]
        else:
            lines=[(x+56+shift,y+28,x+61+shift,y+28),(x+58,y+34,x+64,y+34)]
        for line in lines:draw.line(line,fill=P['ink'])
    elif state=='jumping' and i in (2,3):
        draw.line([(86,y+11),(86,y+17)],fill=P['ink'])
        draw.line([(83,y+14),(89,y+14)],fill=P['ink'])
    return canvas


def gaze(vector):
    portrait=art.head_pose(look=vector)
    portrait.alpha_composite(props_for('idle',0))
    art.finish_portrait(portrait)
    canvas=Image.new('RGBA',(96,104))
    canvas.alpha_composite(portrait,(28,48))
    return canvas


def gif_palette():
    ref=Image.open(art.REFERENCE/'pixel-reference.png').convert('RGBA')
    colors=[(0,0,0,0)]+sorted({c for c in ref.get_flattened_data() if c[3]})
    palette=[]
    for color in colors:palette.extend(color[:3])
    palette.extend([0]*(768-len(palette)))
    return colors,palette


def save_gif(frames,durations,path,scale=2):
    colors,palette=gif_palette()
    index={color:i for i,color in enumerate(colors)}
    encoded=[]
    for rgba in frames:
        rgba=rgba.resize((rgba.width*scale,rgba.height*scale),Image.Resampling.NEAREST)
        image=Image.new('P',rgba.size)
        image.putpalette(palette)
        image.putdata([index[c] if c[3] else 0 for c in rgba.get_flattened_data()])
        encoded.append(image)
    encoded[0].save(path,save_all=True,append_images=encoded[1:],duration=durations,
                    loop=0,transparency=0,disposal=2,optimize=False)


def build():
    for path in (PACKAGE,MATERIALS,PREVIEWS):path.mkdir(parents=True,exist_ok=True)
    logical=Image.new('RGBA',(96*8,104*11))
    for row,(state,title,caption,durations) in enumerate(GROUPS):
        frames=[frame(state,i,caption) for i in range(len(durations))]
        for col,image in enumerate(frames):logical.alpha_composite(image,(col*96,row*104))
    gazes=[gaze(v) for v in LOOK_VECTORS]
    for i,image in enumerate(gazes):logical.alpha_composite(image,((i%8)*96,(9+i//8)*104))
    logical.save(MATERIALS/'spritesheet-logical.png')
    logical.resize((1536,2288),Image.Resampling.NEAREST).save(PACKAGE/'spritesheet.png')
    decoded=Image.open(PACKAGE/'spritesheet.png').convert('RGBA')
    for row,(state,title,caption,durations) in enumerate(GROUPS):
        frames=[decoded.crop((i*192,row*208,(i+1)*192,(row+1)*208)) for i in range(len(durations))]
        save_gif(frames,durations,PREVIEWS/f'{state}.gif')
    look_frames=[decoded.crop(((i%8)*192,(9+i//8)*208,(i%8+1)*192,(10+i//8)*208)) for i in range(16)]
    save_gif(look_frames,[220]*16,PREVIEWS/'look-directions.gif')
    metadata={'id':SLUG,'displayName':NAME,
              'description':'好女孩像素睦：抱瓜移动、举瓜招手、浇水种瓜，面无表情地送出黄瓜再收到退货。',
              'spritesheetPath':'spritesheet.png','spriteVersionNumber':2}
    (PACKAGE/'pet.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    mapping={'sprite_version':2,'frame_size':[192,208],'grid':[8,11],
             'states':[{'state':s,'title':t,'caption':c,'row':r,'frame_count':len(ds),'durations_ms':ds}
                       for r,(s,t,c,ds) in enumerate(GROUPS)],
             'gaze':{'rows':[9,10],'angles_degrees':[i*22.5 for i in range(16)],
                     'zero':'up','rotation':'clockwise'},
             'timing_note':'Preview timings follow the inspected Codex desktop renderer; client scheduling may differ.'}
    (MATERIALS/'animation-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'atlas':[1536,2288],'animation_frames':57,'look_directions':16,'gifs':10}))


if __name__=='__main__':
    build()
