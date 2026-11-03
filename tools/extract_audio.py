#!/usr/bin/env python3
"""Split CUE audio tracks into raw 2352-byte CD-DA sectors (no decoding)."""
import argparse, json, re
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('image',type=Path); p.add_argument('cue',type=Path); p.add_argument('output',type=Path); a=p.parse_args()
tracks=[]; current=None
for line in a.cue.read_text().splitlines():
    t=re.match(r'\s*TRACK\s+(\d+)\s+(\S+)',line,re.I)
    i=re.match(r'\s*INDEX\s+(\d+)\s+(\d+):(\d+):(\d+)',line,re.I)
    if t:
        current={'track':int(t[1]),'type':t[2].upper(),'indexes':{}}; tracks.append(current)
    elif i and current is not None:
        current['indexes'][int(i[1])]=(int(i[2])*60+int(i[3]))*75+int(i[4])
a.output.mkdir(parents=True,exist_ok=True)
total=a.image.stat().st_size//2352
with a.image.open('rb') as f:
    for n,t in enumerate(tracks):
        if t['type'] != 'AUDIO': continue
        start=t['indexes'][1]
        # Include the next track's INDEX 00 pregap in this file; preserve all sectors.
        end=tracks[n+1]['indexes'][1] if n+1<len(tracks) else total
        f.seek(start*2352); remaining=(end-start)*2352
        with (a.output / ('track%02d.cdda' % t['track'])).open('wb') as out:
            while remaining:
                b=f.read(min(1024*1024,remaining))
                if not b: raise EOFError('Disc image is shorter than CUE')
                out.write(b); remaining-=len(b)
        print('Track %02d: sectors %d..%d' % (t['track'],start,end-1))
(a.output/'tracks.json').write_text(json.dumps(tracks,indent=2)+'\n')
