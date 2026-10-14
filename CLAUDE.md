# CLAUDE.md

utakata: a static-recompilation PC port of Shinobido 2: Revenge of Zen (PS Vita,
PCSE00015). Start with `README.md` and `docs/03-plan.md` to find the current
phase. Sibling project: ss-delta (Soul Sacrifice Delta), whose recompiler,
Vita3K fork and tools this project shares (D4); its `CLAUDE.md` and docs
hold most of the know-how. `CLAUDE.local.md` (not committed) imports the
owner's machine-specific notes, kept in a private repo.

## Hard rules

- Never commit anything derived from the dump or the firmware: pkgs,
  extracted or decrypted files, ELFs, licences (`work.bin`, `.rif`, zRIFs),
  generated C++, screenshots, logs, PUPs. Check `git status` before every
  commit. Hashes, addresses and notes are fine.
- Never commit anything local either (D6): no absolute paths, host names,
  user or machine names, tokens. Those go in the private notes. Use
  repo-relative paths, or `<ss-delta>` for the sibling checkout.
- Treat `rom/` as read-only. Write to `extracted/`, `generated/` or `build/`.
- Never change anything in the ss-delta checkout from this project without
  the owner's OK.
- Mark unverified claims in docs as **hypothesis**. Promote them only after
  checking against the binary or Vita3K.
- Vita3K is the reference. When behaviour differs, compare against it
  before guessing.
- Run Python that reads game data with `python -I` and pass paths as
  arguments. (`recomp/recompile.py` needs its own directory on the path, so
  it runs without `-I`.)

## Environment

- Developed on Windows 11 (an AMD Radeon 760M PC; an RTX 4090 PC for
  NVIDIA checks). PowerShell for Windows-native commands; Bash (Git Bash)
  is also available.
- Submodules: `third_party/vita3k` (the fork, branch `games`: the
  integration branch both game repos track) and `third_party/recomp`
  (vita-recomp-kit, the shared toolchain, `main`). Their URLs in
  `.gitmodules` are relative (`../vita3k`), so they resolve next to wherever
  this repo was cloned from. After `git submodule update --init`, the fork's
  own submodules need `git submodule update --init --recursive` inside it.
  Commit and push inside a submodule first, then commit the new pointer
  here. The fork's `upstream` remote is Vita3K on GitHub.
- Build: `python -I third_party/recomp/tools/build-vita3k.py` (from the
  repo root; finds MSVC with vswhere and Qt in `C:\Qt`) →
  `build/vita3k/bin/RelWithDebInfo/` with `shinobido2.exe`, `ss-delta.exe`
  and `Vita3K.exe`. A full build takes ~10 min; `--target shinobido2` for
  the exe alone.
- Install and package: `python -I third_party/recomp/tools/install-game.py
  --firmware <PUPs> --install <game pkg> --license <work.bin> --install
  <patch pkg> --install <DLC pkg> --license <its work.bin> [--name N]`
  → `dist/<name>/` with its own `fs/` (reads `game.json`).
- Running: `python -I third_party/recomp/tools/v3kdrive.py dist/<name>
  start|run|close`. In `build/vita3k/bin/...`, which holds every game's
  exe, add `--exe shinobido2.exe`. `shinobido2.exe` reads `shinobido2.ini`
  next to it and logs to `shinobido2/vita3k.log`; `--dump-elfs 45` writes
  to `shinobido2/elfdumps/PCSE00015/`.
- Upstream Vita3K for comparison: a portable copy in `extracted/vita3k/`
  (`pref-path` = `fs/`), driven with `v3kdrive.py extracted/vita3k launch
  PCSE00015 OpenGL|Vulkan`; its input is posted keys, and the sticks did
  not move the player. Installing a pkg there: `Vita3K.exe --pkg <pkg>
  --zrif <zRIF>`, the zRIF from `python -I third_party/recomp/tools/mkzrif.py
  third_party/vita3k/external/psvpfstools/libzrif/src/keyflate.c <work.bin>`.
  Keep zRIFs out of the repo.
- To reach gameplay: `python -I tools/to-mission.py dist/<name>` (after
  `v3kdrive.py dist/<name> start`) goes boot → Continue → slot 1 → hub →
  first mission's field, waiting for each screen (references in
  `build/screens/`, made with `--capture <screen> <png>`). It needs a hub
  save in slot 1. The title plays an attract movie if left alone.
- Native code: `python third_party/recomp/recomp/recompile.py
  extracted/elf/<m>.elf generated/<m>`, then `python -I
  third_party/recomp/tools/build-recomp.py --jobs 6` → `build/recomp/
  ssd_aot_<m>.dll`; copy them next to `shinobido2.exe`. Counters:
  `SSD_AOT_COUNT=1 SSD_AOT_STATS=<file>`; differential check
  `SSD_AOT_DIFF=2000` (denser intervals slow the game and disturb it).
  Firmware modules: recompile them from `extracted/elf/firmware/<m>.elf`
  into `generated/fw_<m>` (the runtime finds modules by that file name; a
  dump's `0x...-0x..._<m>.elf` name breaks it). The whole flow, no JIT:
  `install-game.py --no-jit ...` (game.json lists the modules); the exe
  without dynarmic is `build-vita3k.py --no-jit` → `build/vita3k-nojit`.
  `dist/utakata-p4/` is such an install (with the hub save, volume 0).
  `tools/untranslatable.py` lists what the recompiler can't translate,
  `tools/xref.py` explores the ELF (disassembly with names, callers,
  strings).
- Long runs: log memory with `powershell -NoProfile -File
  tools/memwatch.ps1 -Out <csv> [-Minutes 30]` alongside (the game holds
  ~1.6 GB; the machine has 14 GB). Don't overlap long runs with builds of
  generated code (6 jobs ≈ 3 GB). `tools/sfx-soak.py <dist> <cycles>`
  measures sound effects over mission restarts.
- Stopping a background shell that runs a `v3kdrive.py` loop leaves its
  `sh.exe` and `python.exe` children running, and they keep pressing
  buttons ("phantom input", 2026-10-13). Kill the children by PID
  (`Get-CimInstance Win32_Process`), and check none are left before
  driving the game by hand. The front end also merges real gamepads and
  the keyboard with the input pipe.
- Main menu: the cursor wraps, cross confirms, circle backs out. Taps under
  250 ms can be missed; use `hold:down:250`. System dialogs (Load, Save) are
  Vita3K overlays: `frame:` doesn't capture them, `shot:` does.
- The target is **1.02** (D3), merged into `ux0/app/PCSE00015`.
  `python -I third_party/recomp/tools/fetch-update.py PCSE00015 <dir>`
  fetches the update.
- Shared tools are in the `third_party/recomp` submodule (D4); fix them
  there, not in copies. Its `imix.py` reads the segment offset and exidx
  from the ELF (1.02: `0x1000`, `0x813dfc14`).
- 1.02's logos run longer than 1.00's: wait about 40 s before the first
  `start` on the title.
- In Bash heredocs and `python -c`, backslashes get mangled. Use the Write
  tool for scripts, or `chr(92)`.

## Keep docs current

- When a phase task completes, tick it in `docs/03-plan.md`.
- Record irreversible choices in `docs/decisions.md`.
- Put new binary facts in `docs/01-research.md`, baseline changes in
  `docs/02-baseline.md`.
