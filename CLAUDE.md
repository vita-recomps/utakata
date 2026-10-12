# CLAUDE.md

A static-recompilation PC port of Shinobido 2: Revenge of Zen (PS Vita,
PCSE00015). Start with `README.md` and `docs/03-plan.md` to find the current
phase. Sibling project: `<ss-delta>` (Soul Sacrifice Delta), whose
recompiler, Vita3K fork and tools this project reuses (D4); its `CLAUDE.md`
and docs hold most of the know-how.

## Hard rules

- Never commit anything derived from the dump or the firmware: pkgs,
  extracted or decrypted files, ELFs, licences (`work.bin`, `.rif`, zRIFs),
  generated C++, screenshots, logs, PUPs. Check `git status` before every
  commit. Hashes, addresses and notes are fine.
- Treat `rom/` as read-only. Write to `extracted/`, `generated/` or `build/`.
- Never change anything under `<ss-delta>` from this project without the
  owner's OK. Use its tools by path, read-only, and copy executables out
  (as `build/ssd-shim/` does).
- Mark unverified claims in docs as **hypothesis**. Promote them only after
  checking against the binary or Vita3K.
- Vita3K is the reference. When behaviour differs, compare against it
  before guessing.
- Write docs and code as if public (D6): no personal data, and no new
  absolute paths outside the documented local setup.
- Run Python that reads game data with `python -I` and pass paths as
  arguments. (`recomp/recompile.py` needs its own directory on the path, so
  it runs without `-I`; it is ss-delta's code.)

## Environment

- Windows 11, Radeon 760M mini PC. PowerShell for Windows-native commands;
  Bash (Git Bash) is also available.
- Portable Vita3K: `extracted/vita3k/` (`pref-path` = `fs/`), firmware 3.74,
  the game and its DLC installed. It is the upstream release ss-delta uses;
  its Vulkan crashes on this GPU (ss-delta 02-baseline), so use OpenGL with
  it, or our fork.
- Installing a pkg: `Vita3K.exe --pkg <pkg> --zrif <zRIF>`, the zRIF from
  `python -I tools/mkzrif.py <ss-delta fork>/external/psvpfstools/libzrif/src/keyflate.c <work.bin>`.
  Keep zRIFs out of the repo.
- Phase 0 shim (D5): `build/ssd-shim/ss-delta.exe` is a copy of ss-delta's
  exe with its own `ss-delta.ini` (JIT only, `vita_fs = build/shimfs`).
  `build/shimfs/ux0/app/PCSA00152` is a junction to our PCSE00015 install.
  Drive it with `python -I <ss-delta>\tools\v3kdrive.py build/ssd-shim
  start|run|close`. `--dump-elfs 45` writes ELFs to
  `build/ssd-shim/ss-delta/elfdumps/PCSE00015/`.
- Main menu: the cursor wraps, cross confirms, circle backs out. Taps under
  250 ms can be missed; use `hold:down:250`. System dialogs (Load, Save) are
  Vita3K overlays: `frame:` doesn't capture them, `shot:` does.
- The target is **1.02** (D3), merged into `ux0/app/PCSE00015`. 1.00 is
  kept in `extracted/app-1.00-PCSE00015/` and `extracted/elf-1.00/`.
  `python -I tools/fetch-update.py PCSE00015 <dir>` fetches the update.
- `imix.py` from ss-delta hard-codes SSD's segment offset and exidx; the
  1.02 eboot needs `SEG_OFF 0x1000` and `EXIDX 0x813dfc14` (1.00:
  `0x813d8dec`).
- 1.02's logos run longer than 1.00's: wait about 40 s before the first
  `start` on the title.
- In Bash heredocs and `python -c`, backslashes get mangled. Use the Write
  tool for scripts, or `chr(92)`.

## Keep docs current

- When a phase task completes, tick it in `docs/03-plan.md`.
- Record irreversible choices in `docs/decisions.md`.
- Put new binary facts in `docs/01-research.md`, baseline changes in
  `docs/02-baseline.md`.
