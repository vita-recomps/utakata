"""Reverse-engineering helper over a dumped Vita ELF and its inventory (third_party/recomp's
inventory.py output in generated/inventory/<module>/).

  python -I xref.py <elf> <inventory dir> index            build the reference index (once; cached)
  python -I xref.py <elf> <inventory dir> fn <addr>        the function holding <addr>, disassembled
                                                         with import names, callee names, string
                                                         and data references
  python -I xref.py <elf> <inventory dir> callers <addr>   call sites of the function at <addr>
  python -I xref.py <elf> <inventory dir> refs <addr>      code that builds the address <addr>
                                                         (movw/movt, literal loads)
  python -I xref.py <elf> <inventory dir> str <regex>      strings matching <regex>, with the
                                                         functions that reference them
  python -I xref.py <elf> <inventory dir> imp <name>       call sites of imports whose name
                                                         starts with <name>

The index (<inventory dir>/refs.csv) lists every 32-bit constant code builds that points into the
module (movw/movt pairs and pc-relative literal loads), so it is derived from the game's code:
generated/ is never committed.
"""
import bisect
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'third_party', 'recomp', 'tools'))
import vitaelf  # noqa: E402
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_ARM, Cs  # noqa: E402
from capstone.arm import ARM_OP_IMM, ARM_OP_MEM, ARM_OP_REG, ARM_REG_PC  # noqa: E402


def load(elf_path, inv):
    elf = vitaelf.load(elf_path)
    funcs = []
    with open(os.path.join(inv, 'functions.csv')) as f:
        for r in csv.DictReader(f):
            funcs.append((int(r['start'], 16), int(r['end'], 16), r['mode'], r['kind'], r['name']))
    funcs.sort()
    imports = {}
    with open(os.path.join(inv, 'imports.csv')) as f:
        for r in csv.DictReader(f):
            stub = r.get('stub') or r.get('address')
            if stub:
                imports[int(stub, 16)] = r.get('name') or r.get('nid')
    return elf, funcs, imports


def func_at(funcs, addr):
    i = bisect.bisect_right([f[0] for f in funcs], addr) - 1
    if i >= 0 and funcs[i][0] <= addr < funcs[i][1]:
        return funcs[i]
    return None


def in_module(elf, va):
    return any(s.type == 1 and s.vaddr <= va < s.vaddr + s.memsz for s in elf.segments)


def cstring(elf, va, limit=120):
    raw = elf.read(va, limit)
    if not raw:
        return None
    end = raw.find(b'\0')
    if end < 4:
        return None
    s = raw[:end]
    if all(32 <= c < 127 or c in (9, 10, 13) for c in s):
        return s.decode('ascii')
    return None


def disasm(elf, f):
    start, end, mode = f[0], f[1], f[2]
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB if mode == 'thumb' else CS_MODE_ARM)
    md.detail = True
    code = elf.read(start, end - start) or b''
    return list(md.disasm(code, start))


def constants(elf, insns):
    """(site, value) for every movw/movt pair and pc-relative literal load"""
    lo = {}
    out = []
    for ins in insns:
        m = ins.mnemonic
        ops = ins.operands
        if m.startswith('movw') and len(ops) == 2 and ops[1].type == ARM_OP_IMM:
            lo[ops[0].reg] = (ins.address, ops[1].imm & 0xffff)
        elif m.startswith('movt') and len(ops) == 2 and ops[1].type == ARM_OP_IMM and ops[0].reg in lo:
            site, low = lo.pop(ops[0].reg)
            out.append((site, ((ops[1].imm & 0xffff) << 16) | low))
        elif m.startswith('ldr') and len(ops) == 2 and ops[1].type == ARM_OP_MEM and ops[1].mem.base == ARM_REG_PC:
            pc = (ins.address + 4) & ~3
            lit = pc + ops[1].mem.disp
            raw = elf.read(lit, 4)
            if raw:
                out.append((ins.address, int.from_bytes(raw, 'little')))
        elif ops and ops[0].type == ARM_OP_REG and ops[0].reg in lo and not m.startswith(('str', 'cmp', 'tst')):
            lo.pop(ops[0].reg, None)
    return out


def index(elf, funcs, inv):
    path = os.path.join(inv, 'refs.csv')
    xpath = os.path.join(inv, 'xcalls.csv')
    with open(path, 'w', newline='') as out, open(xpath, 'w', newline='') as xout:
        w = csv.writer(out)
        w.writerow(['site', 'func', 'value', 'string'])
        x = csv.writer(xout)
        x.writerow(['site', 'func', 'target'])
        n = nx = 0
        for f in funcs:
            if f[3] != 'code':
                continue
            insns = disasm(elf, f)
            for site, value in constants(elf, insns):
                if in_module(elf, value):
                    w.writerow([f'{site:#010x}', f'{f[0]:#010x}', f'{value:#010x}', cstring(elf, value) or ''])
                    n += 1
            for ins in insns:
                if ins.mnemonic in ('bl', 'blx', 'b.w', 'b') and ins.operands and ins.operands[0].type == ARM_OP_IMM:
                    t = ins.operands[0].imm & 0xffffffff
                    if not (f[0] <= t < f[1]):
                        x.writerow([f'{ins.address:#010x}', f'{f[0]:#010x}', f'{t:#010x}'])
                        nx += 1
    print(f'{n} references -> {path}; {nx} calls -> {xpath}')


def read_refs(inv):
    path = os.path.join(inv, 'refs.csv')
    if not os.path.exists(path):
        sys.exit('run "index" first')
    with open(path) as f:
        return list(csv.DictReader(f))


def show_fn(elf, funcs, imports, addr):
    f = func_at(funcs, addr)
    if not f:
        sys.exit(f'{addr:#x} is not in a function')
    names = {s: n for s, n in imports.items()}
    print(f'function {f[0]:#010x}-{f[1]:#010x} {f[2]} {f[4]}')
    insns = disasm(elf, f)
    consts = dict(constants(elf, insns))
    for ins in insns:
        note = ''
        if ins.mnemonic in ('bl', 'blx', 'b.w', 'b') and ins.operands and ins.operands[0].type == ARM_OP_IMM:
            t = ins.operands[0].imm & 0xffffffff
            if t in names:
                note = f'  ; {names[t]}'
            elif not (f[0] <= t < f[1]):
                g = func_at(funcs, t)
                note = f'  ; fn {t:#010x}' + (f' {g[4]}' if g and g[4] else '')
        if ins.address in consts:
            v = consts[ins.address]
            s = cstring(elf, v)
            note += f'  ; {v:#010x}' + (f' "{s}"' if s else '')
        print(f'  {ins.address:#010x}  {ins.mnemonic:8} {ins.op_str}{note}')


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    elf_path, inv, cmd = sys.argv[1:4]
    arg = sys.argv[4] if len(sys.argv) > 4 else None
    elf, funcs, imports = load(elf_path, inv)
    if cmd == 'index':
        index(elf, funcs, inv)
    elif cmd == 'fn':
        show_fn(elf, funcs, imports, int(arg, 16))
    elif cmd == 'callers':
        target = int(arg, 16)
        with open(os.path.join(inv, 'xcalls.csv')) as f:
            for r in csv.DictReader(f):
                if int(r['target'], 16) & ~1 == target & ~1:
                    print(f"{r['site']} in {r['func']}")
    elif cmd == 'refs':
        target = int(arg, 16)
        for r in read_refs(inv):
            if int(r['value'], 16) == target:
                print(f"{r['site']} in {r['func']}")
    elif cmd == 'str':
        rx = re.compile(arg)
        for r in read_refs(inv):
            if r['string'] and rx.search(r['string']):
                print(f"{r['value']} \"{r['string']}\" <- {r['site']} in {r['func']}")
    elif cmd == 'imp':
        with open(os.path.join(inv, 'importcalls.csv')) as f:
            for r in csv.DictReader(f):
                if r['name'].startswith(arg):
                    print(f"{r['site']} in {r['func']}: {r['name']}")
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
