#!/usr/bin/env python3
"""Create an analysis-only ELF representing the main EXE plus one loaded overlay.

The overlay replaces overlapping bytes in the executable's load image. This is
not a snapshot of initialized PS1 RAM and must not be run as a host executable.
"""
import argparse,struct
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('exe',type=Path); p.add_argument('overlay',type=Path); p.add_argument('output',type=Path); p.add_argument('--base',required=True,type=lambda x:int(x,0)); a=p.parse_args()
raw=a.exe.read_bytes(); overlay=a.overlay.read_bytes()
if len(raw)<2048 or raw[:8]!=b'PS-X EXE':p.error('invalid PS-X EXE')
pc,_,base,size=struct.unpack_from('<4I',raw,16)
if len(raw)<2048+size or not overlay or not base<a.base<base+size:p.error('invalid payload or overlay address')
main=raw[2048:2048+(a.base-base)]; replaced=raw[2048+(a.base-base):2048+size]
if any(replaced):p.error('overlay would replace nonzero main-executable bytes; investigate before proceeding')
if a.base+len(overlay)>0x100000000:p.error('overlay exceeds address space')
# ELF requires p_offset and p_vaddr to be congruent modulo p_align.
def file_offset(cursor,addr):return cursor+((addr-cursor)&0xfff)
off1=file_offset(52+2*32,base); off2=file_offset(off1+len(main),a.base)
ident=b'\x7fELF'+bytes([1,1,1,0,0])+bytes(7)
e=struct.pack('<16sHHIIIIIHHHHHH',ident,2,8,1,pc,52,0,0x1000,52,32,2,0,0,0)
e+=struct.pack('<IIIIIIII',1,off1,base,base,len(main),len(main),7,0x1000)
e+=struct.pack('<IIIIIIII',1,off2,a.base,a.base,len(overlay),len(overlay),7,0x1000)
e+=bytes(off1-len(e))+main; e+=bytes(off2-len(e))+overlay
a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_bytes(e)
print(f'{a.output}: main {len(main)} bytes, overlay {len(overlay)} bytes, {len(replaced)} overlapping zero bytes replaced')
