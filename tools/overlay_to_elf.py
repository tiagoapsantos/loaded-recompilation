#!/usr/bin/env python3
"""Wrap a headerless PS1 overlay as ELF32 for static analysis only."""
import argparse, struct
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__); p.add_argument('input',type=Path); p.add_argument('output',type=Path); p.add_argument('--base',type=lambda x:int(x,0),required=True); a=p.parse_args()
data=a.input.read_bytes()
if not data or not 0<=a.base<=0xffffffff or a.base+len(data)>0x100000000:p.error('invalid payload or base')
ident=b'\x7fELF'+bytes([1,1,1,0,0])+bytes(7)
offset=0x1000+(a.base&0xfff)
ehdr=struct.pack('<16sHHIIIIIHHHHHH',ident,2,8,1,0,52,0,0x1000,52,32,1,0,0,0)
phdr=struct.pack('<IIIIIIII',1,offset,a.base,a.base,len(data),len(data),7,0x1000)
a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_bytes(ehdr+phdr+bytes(offset-len(ehdr)-len(phdr))+data)
print(f'{a.output}: {len(data)} bytes at 0x{a.base:08x}; no entry point claimed')
