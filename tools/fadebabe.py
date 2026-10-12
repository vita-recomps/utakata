"""Acquire's FADEBABE archives (volume.dat, StreamPack*.dat): table listing and stats.

The layout is in docs/01-research.md. Names and the compression of kinds 2-5 are not
decoded yet, so `extract` only handles kind 0 (raw) members, named by hash.

usage:
  python -I fadebabe.py stats   <archive.dat>
  python -I fadebabe.py list    <archive.dat>
  python -I fadebabe.py extract <archive.dat> <out dir>     kind 0 members only
"""
import collections
import os
import struct
import sys


def read_table(f):
    head = f.read(0x14)
    magic, count, count2, data_start, total = struct.unpack('>5I', head)
    if magic != 0xFADEBABE:
        sys.exit('not a FADEBABE archive')
    raw = f.read(count * 24)
    # {hash, offset, size, kind, end, name_len}; end - offset is the stored size
    entries = [struct.unpack_from('>6I', raw, i * 24) for i in range(count)]
    return (count, count2, data_start, total), entries


def main():
    cmd, path = sys.argv[1], sys.argv[2]
    with open(path, 'rb') as f:
        (count, count2, data_start, total), entries = read_table(f)
        if cmd == 'stats':
            print(f'entries {count} ({count2}), data from {data_start:#x}, total {total:#x}')
            runs = 1 + sum(1 for a, b in zip(entries, entries[1:]) if a[0] >= b[0])
            print(f'hash-sorted runs: {runs}')
            kinds = collections.Counter(e[3] for e in entries)
            for k in sorted(kinds):
                es = [e for e in entries if e[3] == k]
                size = sum(e[2] for e in es)
                stored = sum(e[4] - e[1] for e in es)
                print(f'kind {k}: {len(es)} members, {size} bytes, stored {stored}')
        elif cmd == 'list':
            for h, off, size, kind, end, name_len in entries:
                print(f'{h:08x} {off:#010x} {size:10d} kind {kind} stored {end - off:10d} name_len {name_len}')
        elif cmd == 'extract':
            out = sys.argv[3]
            os.makedirs(out, exist_ok=True)
            n = 0
            for h, off, size, kind, end, name_len in entries:
                if kind != 0:
                    continue
                f.seek(off)
                with open(os.path.join(out, f'{h:08x}.bin'), 'wb') as o:
                    o.write(f.read(size))
                n += 1
            print(f'{n} raw members written to {out}')
        else:
            sys.exit(__doc__)


if __name__ == '__main__':
    main()
