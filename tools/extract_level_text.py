#!/usr/bin/env python3
"""Inspect and split the verified outer structure of Loaded level TEXT files.

No image encoding, palette behavior, or interpretation of the remaining
sections is assumed. The four output parts concatenate to the original file.
"""
import argparse, hashlib, json, struct
from pathlib import Path

HEADER_SIZE=68

def split_bytes(data):
    if len(data)<HEADER_SIZE: raise ValueError('file is shorter than 68-byte header')
    words=struct.unpack_from('<17I',data)
    offsets=words[:16]; count=words[16]
    if any(x<HEADER_SIZE or x>=len(data) for x in offsets):
        raise ValueError('one or more offsets lie outside file data')
    first,second,third=offsets[:3]
    if first!=HEADER_SIZE or second-first!=0x40000:
        raise ValueError('unexpected first data region layout')
    if third<second or third>len(data) or third-second!=count*32:
        raise ValueError('unexpected 32-byte table layout')
    return offsets,count,[data[:first],data[first:second],data[second:third],data[third:]]

def sha(data): return hashlib.sha256(data).hexdigest()

def extract(src,out):
    data=src.read_bytes(); offsets,count,parts=split_bytes(data)
    names=['header.bin','block_256k.bin','table_32byte_entries.bin','remaining.bin']
    out.mkdir(parents=True,exist_ok=True)
    for name,part in zip(names,parts): (out/name).write_bytes(part)
    meta={'source':str(src),'source_size':len(data),'source_sha256':sha(data),
          'offsets':[{'index':i,'offset':o,'hex':f'0x{o:x}'} for i,o in enumerate(offsets)],
          'entry_count':count,
          'parts':[{'file':n,'size':len(v),'sha256':sha(v)} for n,v in zip(names,parts)],
          'notes':'Concatenate parts in listed order to reproduce source. Offsets 2..15 may alias or point into other sections; their extents and semantics are not established.'}
    (out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    return meta

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('source',type=Path); p.add_argument('output',type=Path); a=p.parse_args()
    m=extract(a.source,a.output); print(f"{a.source}: {m['entry_count']} entries, {m['source_size']} bytes, SHA-256 {m['source_sha256']}")
