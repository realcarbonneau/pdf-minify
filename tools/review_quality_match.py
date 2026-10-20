"""Exact-pixel diagnostic crops of actual LOSSY-04 decoded image candidates."""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def crop_positions(source,jpeg,alternative,side=256):
    width,height=source.size
    if min(width,height)<side:
        raise ValueError('Review crop larger than original pixels')
    images=[np.asarray(img,dtype=np.float32) for img in (source,jpeg,alternative)]
    tiles=[]
    for y in range(0,height-side+1,side):
        for x in range(0,width-side+1,side):
            blocks=[a[y:y+side,x:x+side] for a in images]
            tiles.append(((x,y),float(np.mean((blocks[0]-blocks[1])**2)),
                          float(np.mean((blocks[0]-blocks[2])**2)),float(np.var(blocks[0]))))
    selected=[]
    for criterion in (1,2,3):
        ordered=sorted(tiles,key=lambda t:t[criterion],reverse=True)
        selected.append(next(t[0] for t in ordered if t[0] not in selected))
    return selected


def render_case(rate,psnr,output):
    left,right=rate['job']['canvas'],psnr['job']['canvas']
    if left!=right or not rate['complete'] or not psnr['complete']:
        raise ValueError('Review must compare the identical completed source/reference')
    images=[Image.open(p).convert('RGB') for p in (left['source_png'],left['jpeg_decoded_png'],
                                                  rate['selected']['decoded_png'],psnr['selected']['decoded_png'])]
    if len({im.size for im in images})!=1:
        raise ValueError('Mismatched pixel geometry')
    positions=crop_positions(images[0],images[1],images[3])
    labels=['Original RGB','JPEG q75',f"Ratio-scale q{rate['selected_q']}",f"PSNR-scale q{psnr['selected_q']}"]
    side,padding,caption=256,12,32
    canvas=Image.new('RGB',(4*(side+padding)+padding,3*(side+caption+padding)+padding),'#cccccc')
    draw=ImageDraw.Draw(canvas)
    for i,(x,y) in enumerate(positions):
        for j,(img,label) in enumerate(zip(images,labels,strict=True)):
            xx,yy=padding+j*(side+padding),padding+i*(side+caption+padding)
            draw.text((xx,yy),f'{label} · {x},{y}',fill='black',font_size=13)
            # Crop and paste only: no resize, smoothing, sharpening or AA.
            canvas.paste(img.crop((x,y,x+side,y+side)),(xx,yy+caption))
    output.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(output)
    return dict(output=str(output),document=left['document'],force_raster=left['force_raster'],
                positions=positions,source=left['source_png'],jpeg=left['jpeg_decoded_png'],
                ratio_selected=rate['selected_q'],psnr_selected=psnr['selected_q'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rate',type=Path,required=True)
    parser.add_argument('--psnr',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    rate=json.loads(args.rate.read_text())
    psnr=json.loads(args.psnr.read_text())
    index={(r['job']['canvas']['document'],r['job']['canvas']['force_raster']):r for r in psnr['records']}
    manifest=[]
    for row in rate['records']:
        source=row['job']['canvas'];key=source['document'],source['force_raster']
        other=index.get(key)
        if other:
            output=args.output/f"{key[0]}-{'ffpr' if key[1] else 'native'}.png"
            manifest.append(render_case(row,other,output))
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'review.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'{len(manifest)} exact-pixel comparison sheets; view before claiming visual review')


if __name__=='__main__':
    main()
