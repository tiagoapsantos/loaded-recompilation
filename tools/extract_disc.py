#!/usr/bin/env python3
"""Extract ISO 9660 files from a raw MODE2/2352 PS1 data track."""
import argparse, hashlib, json, struct
from pathlib import Path

SECTOR = 2352

def extract(image, out):
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    with image.open('rb') as f:
        def sector(n):
            f.seek(n * SECTOR)
            raw = f.read(SECTOR)
            if len(raw) != SECTOR or raw[15] != 2 or raw[16:20] != raw[20:24]:
                raise ValueError(f'Invalid Mode 2 sector {n}')
            return raw
        def read_extent(lba, size):
            data = bytearray()
            form2 = []
            for n in range(lba, lba + (size + 2047)//2048):
                raw = sector(n)
                if raw[18] & 0x20: form2.append(n)
                data.extend(raw[24:2072])
            return bytes(data[:size]), form2
        pvd = sector(16)[24:2072]
        if pvd[:7] != b'\x01CD001\x01': raise ValueError('No ISO 9660 primary volume descriptor')
        def walk(lba, size, dest):
            data, _ = read_extent(lba, size)
            pos = 0
            while pos < len(data):
                length = data[pos]
                if not length:
                    pos = (pos//2048 + 1)*2048
                    continue
                rec = data[pos:pos+length]
                if len(rec) < 34: raise ValueError('Invalid directory record')
                extent, length_bytes = struct.unpack_from('<I', rec, 2)[0], struct.unpack_from('<I', rec, 10)[0]
                flags, name_len = rec[25], rec[32]
                name = rec[33:33+name_len]
                pos += length
                if name in (b'\x00', b'\x01'): continue
                name = name.decode('ascii').split(';')[0].rstrip('.')
                if name in ('', '.', '..') or '/' in name or '\\' in name: raise ValueError('Unsafe filename')
                path = dest / name
                if flags & 2:
                    path.mkdir(parents=True, exist_ok=True)
                    walk(extent, length_bytes, path)
                else:
                    try:
                        contents, form2 = read_extent(extent, length_bytes)
                    except ValueError as e:
                        manifest.append(dict(path=str(path.relative_to(out)).replace('\\','/'), lba=extent, size=length_bytes, skipped=str(e)))
                        continue
                    path.write_bytes(contents)
                    if form2:
                        raw_path = Path('analysis/raw_sectors') / path.relative_to(out)
                        raw_path.parent.mkdir(parents=True, exist_ok=True)
                        f.seek(extent * SECTOR)
                        raw_path.write_bytes(f.read(((length_bytes + 2047)//2048) * SECTOR))
                    manifest.append(dict(path=str(path.relative_to(out)).replace('\\','/'), lba=extent, size=length_bytes, sha256=hashlib.sha256(contents).hexdigest(), form2_sectors=form2))
        root = pvd[156:190]
        walk(struct.unpack_from('<I',root,2)[0], struct.unpack_from('<I',root,10)[0], out)
    return manifest

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('image',type=Path); p.add_argument('output',type=Path); p.add_argument('--manifest',type=Path,default=Path('analysis/manifest.json'))
    a=p.parse_args(); m=extract(a.image,a.output); a.manifest.parent.mkdir(parents=True,exist_ok=True); a.manifest.write_text(json.dumps(m,indent=2)+'\n'); print(f'Extracted {len(m)} files; {sum(bool(x.get("form2_sectors")) for x in m)} contain Form 2 sectors.')
