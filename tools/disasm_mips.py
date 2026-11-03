#!/usr/bin/env python3
"""Disassemble MIPS I words from a PS-X EXE without external dependencies.

This linear sweep does not distinguish code from data and is not a decompiler.
Unknown instructions remain .word; branch targets include the MIPS delay slot.
"""
import argparse,struct
from pathlib import Path
R=['zero','at','v0','v1','a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','s0','s1','s2','s3','s4','s5','s6','s7','t8','t9','k0','k1','gp','sp','fp','ra']
def decode(w,pc):
    op=w>>26; rs=(w>>21)&31; rt=(w>>16)&31; rd=(w>>11)&31; sh=(w>>6)&31; fn=w&63; u=w&65535; s=u if u<32768 else u-65536
    a,b,d=('$'+R[rs],'$'+R[rt],'$'+R[rd]); dest=(pc+4+(s<<2))&0xffffffff
    if w==0:return 'nop'
    if op==0:
        if fn in (0,2,3):return f"{ {0:'sll',2:'srl',3:'sra'}[fn]} {d}, {b}, {sh}"
        if fn in (4,6,7):return f"{ {4:'sllv',6:'srlv',7:'srav'}[fn]} {d}, {b}, {a}"
        if fn==8:return f'jr {a}'
        if fn==9:return f'jalr {d}, {a}'
        if fn in (12,13):return 'syscall' if fn==12 else 'break'
        if fn in (16,18):return f"{ {16:'mfhi',18:'mflo'}[fn]} {d}"
        if fn in (17,19):return f"{ {17:'mthi',19:'mtlo'}[fn]} {a}"
        if fn in (24,25,26,27):return f"{ {24:'mult',25:'multu',26:'div',27:'divu'}[fn]} {a}, {b}"
        if fn in (32,33,34,35,36,37,38,39,42,43):return f"{ {32:'add',33:'addu',34:'sub',35:'subu',36:'and',37:'or',38:'xor',39:'nor',42:'slt',43:'sltu'}[fn]} {d}, {a}, {b}"
    if op in (2,3):return f"{'j' if op==2 else 'jal'} 0x{((pc+4)&0xf0000000)|((w&0x3ffffff)<<2):08x}"
    if op in (4,5):return f"{'beq' if op==4 else 'bne'} {a}, {b}, 0x{dest:08x}"
    if op in (6,7):return f"{'blez' if op==6 else 'bgtz'} {a}, 0x{dest:08x}"
    if op==1 and rt in (0,1,16,17):return f"{ {0:'bltz',1:'bgez',16:'bltzal',17:'bgezal'}[rt]} {a}, 0x{dest:08x}"
    if op in (8,9,10,11):return f"{ {8:'addi',9:'addiu',10:'slti',11:'sltiu'}[op]} {b}, {a}, {s}"
    if op in (12,13,14):return f"{ {12:'andi',13:'ori',14:'xori'}[op]} {b}, {a}, 0x{u:04x}"
    if op==15:return f'lui {b}, 0x{u:04x}'
    if op in (32,33,34,35,36,37,38,40,41,42,43,46,50,58):return f"{ {32:'lb',33:'lh',34:'lwl',35:'lw',36:'lbu',37:'lhu',38:'lwr',40:'sb',41:'sh',42:'swl',43:'sw',46:'swr',50:'lwc2',58:'swc2'}[op]} {b if op not in (50,58) else '$c2r'+str(rt)}, {s}({a})"
    if op in (16,18):
        cop=op-16
        if rs in (0,2,4,6):return f"{ {0:'mfc',2:'cfc',4:'mtc',6:'ctc'}[rs]}{cop} {b}, ${rd}"
        if op==16 and w==0x42000010:return 'rfe'
        if op==18 and rs>=16:return f'gte 0x{w&0x1ffffff:07x}'
    return f'.word 0x{w:08x}'
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('exe',type=Path); p.add_argument('--start',type=lambda x:int(x,0)); p.add_argument('--raw-base',type=lambda x:int(x,0),help='treat input as raw bytes loaded at this address'); p.add_argument('--count',type=int,default=64); p.add_argument('--output',type=Path); a=p.parse_args(); data=a.exe.read_bytes()
    if a.raw_base is None:
        if data[:8]!=b'PS-X EXE':p.error('not a PS-X EXE')
        entry,_,base,size=struct.unpack_from('<4I',data,16); offset=2048
        if len(data)<offset+size:p.error('truncated executable')
    else:
        base=a.raw_base; size=len(data); entry=base; offset=0
        if not 0<=base<=0xffffffff or base+size>0x100000000:p.error('invalid raw base or size')
    start=a.start if a.start is not None else entry
    if start%4 or not base<=start<base+size or a.count<1 or start+a.count*4>base+size:p.error('range is unaligned or outside executable payload')
    lines=[]
    for pc in range(start,start+a.count*4,4):
        word=struct.unpack_from('<I',data,offset+pc-base)[0]; lines.append(f'{pc:08x}  {word:08x}  {decode(word,pc)}')
    result='\n'.join(lines)+'\n'
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(result,encoding='utf-8')
    else:print(result,end='')
if __name__=='__main__':main()
