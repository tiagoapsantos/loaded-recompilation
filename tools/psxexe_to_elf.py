#!/usr/bin/env python3
"""Wrap a PS-X EXE payload in a minimal ELF32 little-endian MIPS executable.

The ELF is for static analysis, not a Linux or Windows executable. It contains
only the bytes declared by the PS-X EXE text-size field, not PS1 hardware maps.
"""
import argparse, struct
from pathlib import Path

def build(src, dst):
    raw=src.read_bytes()
    if len(raw)<2048 or raw[:8]!=b'PS-X EXE': raise ValueError('Not a PS-X EXE')
    pc, gp, addr, size=struct.unpack_from('<4I',raw,0x10)
    if not size or len(raw)<2048+size: raise ValueError('Invalid payload size')
    ident=b'\x7fELF'+bytes([1,1,1,0,0])+bytes(7)
    # Executable, EM_MIPS, current version; one load segment, no sections.
    ehdr=struct.pack('<16sHHIIIIIHHHHHH',ident,2,8,1,pc,52,0,0x1000,52,32,1,0,0,0)
    offset=0x1000
    phdr=struct.pack('<IIIIIIII',1,offset,addr,addr,size,size,7,0x1000)
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_bytes(ehdr+phdr+bytes(offset-len(ehdr)-len(phdr))+raw[2048:2048+size])
    print(f'{dst}: MIPS ELF32 LE, load 0x{addr:08x}, entry 0x{pc:08x}, {size} bytes')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('input',type=Path); p.add_argument('output',type=Path); a=p.parse_args(); build(a.input,a.output)
