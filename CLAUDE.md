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
  the game and its DLC installed. It is the upstream release ss-delta uses
  (`v0.2.1 4152-38bce160`). With this game both its OpenGL and its Vulkan
  work on this GPU (Vulkan crashed with Soul Sacrifice). Driven with
  `v3kdrive.py extracted/vita3k launch PCSE00015 OpenGL|Vulkan`; its input
  is posted keys, and the sticks did not move the player.
  `fs/ux0/user/00/savedata/PCSE00015/` holds a copy of the `hub-day1` save.
- Installing a pkg: `Vita3K.exe --pkg <pkg> --zrif <zRIF>`, the zRIF from
  `python -I third_party/recomp/tools/mkzrif.py <ss-delta fork>/external/psvpfstools/libzrif/src/keyflate.c <work.bin>`.
  Keep zRIFs out of the repo.
- Submodules: `third_party/vita3k` (the fork, branch `shinobido-2` until
  the integration branch exists) and `third_party/recomp` (the shared
  toolchain, `main`). Their hub remotes are bare repos in `<git>\`
  (stand-ins for GitHub, D4/D6). After `git submodule update`, the fork's
  own submodules need `git -c protocol.file.allow=always submodule update
  --init --recursive` inside it. Commit inside a submodule first, push it
  to the hub, then commit the new pointer here.
- Build: `python -I third_party/recomp/tools/build-vita3k.py` (from the
  repo root; finds MSVC with vswhere) → `build/vita3k/bin/RelWithDebInfo/`
  with `shinobido2.exe`, `ss-delta.exe` and `Vita3K.exe`. A full build
  takes ~12 min; `--target shinobido2` for the exe alone.
- Install and package: `python -I third_party/recomp/tools/install-game.py
  --firmware <PUPs> --install <game pkg> --license <work.bin> --install
  <patch pkg> --install <DLC pkg> --license <its work.bin> [--name N]`
  → `dist/<name>/` with its own `fs/` (reads `game.json`). The PUPs are in
  `<ss-delta>\extracted\firmware\`. `dist/shinobido2-test/` is such an
  install, with the `hub-day1` save and `volume = 0`.
- Running: `python -I third_party/recomp/tools/v3kdrive.py
  dist/shinobido2-test start|run|close`. `shinobido2.exe` reads
  `shinobido2.ini` next to it and logs to `shinobido2/vita3k.log`;
  `--dump-elfs 45` writes to `shinobido2/elfdumps/PCSE00015/`.
- The Phase 0 shim (`build/ssd-shim/`, D5) is retired: `shinobido2.exe`
  replaces it. Its folder stays for comparison runs (fork `1f100891`).
- Stopping a background shell that runs a `v3kdrive.py` loop leaves its
  `sh.exe` and `python.exe` children running, and they keep pressing
  buttons. That caused "phantom input" twice on 2026-10-13 (first blamed
  on the Xbox adapter, which was unplugged at the same moment). Kill the
  children by PID (`Get-CimInstance Win32_Process`), and check none are
  left before driving the game by hand. The front end also merges real
  gamepads and the keyboard with the input pipe.
- Main menu: the cursor wraps, cross confirms, circle backs out. Taps under
  250 ms can be missed; use `hold:down:250`. System dialogs (Load, Save) are
  Vita3K overlays: `frame:` doesn't capture them, `shot:` does.
- The target is **1.02** (D3), merged into `ux0/app/PCSE00015`. 1.00 is
  kept in `extracted/app-1.00-PCSE00015/` and `extracted/elf-1.00/`.
  `python -I third_party/recomp/tools/fetch-update.py PCSE00015 <dir>` fetches the update.
- Shared tools are in the `third_party/recomp` submodule (D4); fix them
  there, not in copies. Its `imix.py` reads the segment offset and exidx
  from the ELF (1.02: `0x1000`, `0x813dfc14`). Its `v3kdrive.py` picks
  `shinobido2.exe` or `ss-delta.exe` from the folder (`--exe` to choose).
- 1.02's logos run longer than 1.00's: wait about 40 s before the first
  `start` on the title.
- In Bash heredocs and `python -c`, backslashes get mangled. Use the Write
  tool for scripts, or `chr(92)`.

## Keep docs current

- When a phase task completes, tick it in `docs/03-plan.md`.
- Record irreversible choices in `docs/decisions.md`.
- Put new binary facts in `docs/01-research.md`, baseline changes in
  `docs/02-baseline.md`.
