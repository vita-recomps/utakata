"""Which functions of a module the recompiler leaves to the fallback CPU, and why: the instructions
without a translation, with their addresses and forms.

usage: python untranslatable.py <recomp dir> <elf> [--load-base HEX]
  (runs without -I: it imports the recompiler's package from <recomp dir>)
"""
import sys

recomp_dir, elf = sys.argv[1], sys.argv[2]
sys.path.insert(0, recomp_dir)
sys.path.insert(0, recomp_dir + '/../tools')
from armrecomp.frontend import Module  # noqa: E402
from armrecomp import semantics  # noqa: E402

load_base = int(sys.argv[sys.argv.index('--load-base') + 1], 16) if '--load-base' in sys.argv else None
mod = Module(elf, load_base=load_base)
for f in mod.functions:
    if f.kind != 'code':
        continue
    bad = []
    for ins in f.instructions:
        t = semantics.translate(ins, f.thumb, mod.imports, f.start, f.end, f.jumptables, mod.patched)
        if t.kind == 'unsupported':
            bad.append(ins)
    if not bad:
        f.release()
        continue
    vector = [i for i in bad if i.mnemonic.startswith('v')]
    kept = (not f.thumb or f.uses_neon) and (vector or not f.thumb)
    print(f'{f.start:#010x}-{f.end:#010x} {"thumb" if f.thumb else "arm"}'
          f'{" neon" if f.uses_neon else ""}: {len(bad)} unsupported'
          f'{" -> left to the fallback CPU" if kept else " (trap, not reached)"}')
    for ins in bad[:8]:
        print(f'    {ins.address:#010x}  {ins.cs.mnemonic} {ins.cs.op_str}')
    f.release()
