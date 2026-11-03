#!/usr/bin/env python3
"""Experimental 4-bit-indexed preview of Loaded level TEXT block.

Requires Pillow. A single palette is applied to the entire 1024x512 image.
This is a research visualization, not the game's final rendered scene.
"""
import argparse,struct
from pathlib import Path
from PIL import Image
from extract_level_text import split_bytes

def convert_color(word):
    # PS1 15-bit color uses low-to-high red, green, blue; bit 15 is STP.
    def expand(v): return (v<<3)|(v>>2)
    return expand(word&31),expand((word>>5)&31),expand((word>>10)&31)

def preview(data,index):
    offsets,count,parts=split_bytes(data)
    if not 0<=index<count: raise ValueError(f'palette index must be 0..{count-1}')
    words=struct.unpack_from('<16H',data,offsets[1]+index*32)
    palette=[component for word in words for component in convert_color(word)]
    pixels=bytearray(1024*512)
    for i,b in enumerate(parts[1]): pixels[2*i]=b&15; pixels[2*i+1]=b>>4
    image=Image.frombytes('P',(1024,512),bytes(pixels)); image.putpalette(palette+[0]*(768-len(palette)))
    return image

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('source',type=Path); p.add_argument('output',type=Path); p.add_argument('--palette',type=int,default=0); a=p.parse_args()
    im=preview(a.source.read_bytes(),a.palette); a.output.parent.mkdir(parents=True,exist_ok=True); im.save(a.output); print(f'{a.output}: 1024x512 indexed preview, palette {a.palette}; bit-15 blending not represented')
