#!/usr/bin/env python3
"""Inventory printable strings and potential MIPS address references in a PS-X EXE.

References are heuristic: LUI followed within four instructions by ADDIU/ORI
using the same register, or an aligned literal pointer. Data may resemble code.
"""
import argparse,json,re,struct
from pathlib import Path

def analyze(path, raw_base=None):
    exe=path.read_bytes()
    if raw_base is None:
        if exe[:8]!=b'PS-X EXE': raise ValueError('Not a PS-X EXE')
        pc,gp,base,size=struct.unpack_from('<4I',exe,16)
        data=exe[2048:2048+size]
        if len(data)!=size: raise ValueError('Truncated payload')
    else:
        base=raw_base; pc=None; data=exe
        if not 0<=base<=0xffffffff or base+len(data)>0x100000000: raise ValueError('Invalid raw base or size')
    words=struct.unpack('<%dI'%(len(data)//4),data[:len(data)//4*4]); refs={}
    def ref(target, at, kind): refs.setdefault(target,[]).append({'address':f'0x{at:08x}','kind':kind})
    for i,w in enumerate(words):
        if base<=w<base+len(data): ref(w,base+i*4,'literal')
        if w>>26 != 15: continue
        reg=(w>>16)&31
        if not reg: continue
        for j in range(i+1,min(i+5,len(words))):
            x=words[j]; op=x>>26; rs=(x>>21)&31; rt=(x>>16)&31; imm=x&0xffff
            if rs==reg and rt==reg and op in (9,13):
                val=(((w&0xffff)<<16)+(imm if op==13 or imm<0x8000 else imm-0x10000))&0xffffffff
                if base<=val<base+len(data): ref(val,base+i*4,'lui/addiu' if op==9 else 'lui/ori')
                break
            # Stop on any instruction writing the LUI register when recognizable.
            if op in (8,9,10,11,12,13,14,15,32,33,35,36,37) and rt==reg: break
    strings=[]
    for m in re.finditer(rb'[\x20-\x7e]{6,}',data):
        address=base+m.start()
        strings.append({'address':f'0x{address:08x}','text':m.group().decode('ascii'),'references':refs.get(address,[])})
    return {'source':str(path),'load_address':f'0x{base:08x}','entry_point':f'0x{pc:08x}' if pc is not None else None,'strings':strings}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('exe',type=Path); p.add_argument('output',type=Path); p.add_argument('--raw-base',type=lambda x:int(x,0),help='treat input as a raw overlay loaded at this address'); a=p.parse_args(); result=analyze(a.exe,a.raw_base); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(f"{len(result['strings'])} strings; {sum(bool(s['references']) for s in result['strings'])} with potential references")
