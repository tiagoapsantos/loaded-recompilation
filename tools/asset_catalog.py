#!/usr/bin/env python3
"""Create a disc asset catalog and validate the observed player-name table."""
import argparse, hashlib, json, re, struct
from pathlib import Path

BASE=0x80056f38
PLAYER_TABLE=0x800a07fc

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def info(path, root):
    return {'path':path.relative_to(root).as_posix(),'size':path.stat().st_size,'sha256':digest(path)}

def build(root):
    overlay=(root/'LOADED/GAME.BIN').read_bytes()
    def string_at(addr):
        offset=addr-BASE
        if not 0<=offset<len(overlay): raise ValueError(f'pointer outside overlay: {addr:#x}')
        end=overlay.find(b'\0',offset,min(len(overlay),offset+40))
        if end<0: raise ValueError('unterminated player name')
        value=overlay[offset:end].decode('ascii')
        if not re.fullmatch('[A-Z]+',value): raise ValueError('invalid player name')
        return value
    off=PLAYER_TABLE-BASE
    pointers=struct.unpack_from('<6I',overlay,off)
    players=[]
    for i,ptr in enumerate(pointers):
        name=string_at(ptr); path=root/'PLAYERS'/f'{name}.BIN'
        if not path.is_file(): raise FileNotFoundError(path)
        players.append({'index':i,'name':name,'string_address':f'0x{ptr:08x}',**info(path,root)})
    levels={}
    for folder,pattern,kind in [('LEVELS',r'L(\d+)(GFX|TEXT)\.BIN','level'),('SOUNDS',r'L(\d+)(SOUND)\.BIN','sound')]:
        for path in sorted((root/folder).iterdir()):
            m=re.fullmatch(pattern,path.name,re.I)
            if m:
                n=int(m.group(1)); levels.setdefault(n,{})[m.group(2).lower()]=info(path,root)
    if not levels: raise ValueError('No level assets found')
    groups={}
    for n,files in levels.items():
        if 'sound' in files: groups.setdefault(files['sound']['sha256'],[]).append(n)
    return {'scope':'Static inventory of supplied disc, not a verified complete runtime asset map',
            'player_table_address':f'0x{PLAYER_TABLE:08x}','players':players,
            'levels':[{'number':n,**files} for n,files in sorted(levels.items())],
            'common_sound':info(root/'SOUNDS/SOUNDS.BIN',root),
            'identical_level_sound_groups':[v for v in groups.values() if len(v)>1]}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('disc',type=Path); p.add_argument('output',type=Path); a=p.parse_args()
    result=build(a.disc); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f"{len(result['players'])} player files and {len(result['levels'])} numbered level groups")
