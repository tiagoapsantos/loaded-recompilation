#!/usr/bin/env python3
"""Inspect the observed header and nested offset table of a level GFX file.

Based on static MIPS analysis; this is an inventory, not a graphics decoder.
Zero offsets are retained as zero: their runtime meaning is not yet established.
"""
import argparse,hashlib,json,struct
from pathlib import Path

HEADER_INDICES=(0,1,2,4,5,6,7,8,9)

def inspect(data):
    if len(data)<40: raise ValueError('file too short for observed header')
    words=struct.unpack_from('<10I',data); count=words[3]
    if any(words[i]>=len(data) for i in HEADER_INDICES): raise ValueError('header offset outside file')
    table=words[2]
    if count>(len(data)-table)//4: raise ValueError('nested offset table outside file')
    nested=struct.unpack_from('<%dI'%count,data,table)
    if any(o>=len(data) for o in nested): raise ValueError('nested offset outside file')
    return {'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),
            'header_offsets':{str(i):words[i] for i in HEADER_INDICES},
            'nested_count':count,'nested_table_offset':table,
            'nested_offsets':list(nested),'zero_entries':sum(o==0 for o in nested),
            'notes':'Offsets may alias or be zero; lengths and contents are not inferred.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('source',type=Path); p.add_argument('output',type=Path); a=p.parse_args()
    obj=inspect(a.source.read_bytes()); obj['source']=str(a.source)
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
    print(f"{a.source.name}: {obj['nested_count']} offsets, {obj['zero_entries']} zero")
