# Building utakata

For players, the [releases](https://github.com/vita-recomps/utakata/releases/latest)
need no building: see [INSTALLING](INSTALLING.md). This guide builds the
game's front end from source, installs a game into a development folder,
and makes a release.

## Contents

* [Requirements](#requirements)
* [Building from a fresh clone](#building-from-a-fresh-clone)
* [Installing your game into a build](#installing-your-game-into-a-build)
* [Playing a build](#playing-a-build)
* [Making a release](#making-a-release)
* [Toolchain](#toolchain)
* [Tools](#tools)

## Requirements

* Your own dump of the game, update 1.02 and, if you have it, the Mirror
  Spirits add-on, and the firmware update files `PSVUPDAT.PUP` and
  `PSP2UPDAT.PUP` (as for Vita3K; `third_party/recomp/tools/fetch-firmware.py`
  downloads them from Sony), as in [INSTALLING](INSTALLING.md#what-you-need).
* Git, Python 3.12 with `capstone`, `pyyaml` and `numpy` (`pip install
  capstone pyyaml numpy`).
* **Windows:** Visual Studio 2022 or its Build Tools with "Desktop
  development with C++" (MSVC x64, the Windows SDK, CMake and Ninja), the
  Vulkan SDK, and Qt 6.11 for MSVC x64 for Vita3K's own interface (e.g. with
  `aqtinstall` into `C:\Qt`; `--games-only` builds without it).
* **Linux:** GCC 14 or newer, CMake, Ninja. Release builds use the Steam
  Runtime 3 (sniper) SDK, whose glibc the game then needs at most.
* **macOS:** Apple's Command Line Tools (or Xcode), CMake and Ninja.

## Building from a fresh clone

```
git clone --recurse-submodules https://github.com/vita-recomps/utakata.git utakata
cd utakata
python -I third_party/recomp/tools/build-vita3k.py --target shinobido2
```

On Windows the script finds MSVC (vswhere) and Qt (`Qt6_ROOT`, `--qt <dir>`,
or the newest `C:\Qt\<version>\msvc20*_64`). The first build takes about ten
minutes and puts `shinobido2.exe` in `build/vita3k/bin/RelWithDebInfo/`.
`--games-only` builds the single-game executables without Qt into
`build/vita3k-games/`.

On Linux and macOS the same command builds `shinobido2.x86_64` or
`shinobido2.arm64` (the games only). The release workflow
(`.github/workflows/release.yml`) shows each platform's build exactly.

## Installing your game into a build

The game needs update 1.02, the final one. Sony's update server still has
it; this fetches it (21 MB) into `downloads/`:

```
python -I third_party/recomp/tools/fetch-update.py PCSE00015 downloads
```

Then install the firmware, the game, the update and (optionally) the add-on
into a self-contained folder, `dist/utakata/`:

```
python -I third_party/recomp/tools/install-game.py --name utakata ^
    --firmware PSVUPDAT.PUP PSP2UPDAT.PUP ^
    --install "<game>.pkg" --license "<game's work.bin>" ^
    --install downloads/UP0700-PCSE00015_00-APP0000000000000-A0102-V0100-<...>-PE.pkg ^
    --install "<add-on>.pkg" --license "<add-on's work.bin>"
```

(A decrypted dump: `--install "<folder, .zip or .vpk>"`.) The update needs
no `--license`: it uses the game's. The script installs the firmware and
the game into a Vita file system, checks that `eboot.bin` is 1.02, runs the
game briefly to write its modules out, recompiles them and the firmware
modules to C++ and compiles them (this takes a while), then lays out
`dist/utakata/`: the front end, the recompiled `ssd_aot_*` modules, a
commented `shinobido2.ini` and the Vita file system in `fs/`. Everything in
it is derived from your copy: don't share it. `--toolchain <dir>` compiles
with the downloaded toolchain instead of MSVC (`toolchain.py fetch`), as a
release's importer does.

## Playing a build

Run `dist/utakata/shinobido2.exe` (Linux: `shinobido2.x86_64`; macOS:
`shinobido2.arm64`). `README.txt` in that folder, and
[INSTALLING](INSTALLING.md#playing), explain the settings and saves.
`--help` lists the command line.

## Making a release

A release is the game's own folder: the front end, its files, and in
`setup/` the importer (Python with Tk, and the recompiler kit), which builds
the game on the player's computer the first time it starts
([D11](decisions.md), after ss-delta's D22). Nothing in it is derived from
the game.

```
python -I third_party/recomp/tools/build-vita3k.py --games-only --target shinobido2
python -I third_party/recomp/tools/make-setup.py build third_party/recomp/tools/setup-windows.json ^
    --project . --bin build/vita3k-games/bin/RelWithDebInfo --out build/release/utakata ^
    --zip --archive build/release/utakata-<version>-windows
```

Linux and macOS take `setup-linux.json` and `setup-macos.json` (run there,
with Python 3.12). Pushing a tag `v*` runs `.github/workflows/release.yml`,
which builds all three archives on GitHub, with their SHA-256 and build
attestations, into a draft release.

## Toolchain

The Vita3K fork and the recompiler are git submodules, repositories of their
own, shared with ss-delta (Soul Sacrifice Delta; [D4](decisions.md)):

* `third_party/vita3k`: our Vita3K fork, branch `games` (the single-game
  front end `vita3k/game-frontend/` and one executable per game,
  `vita3k/games/shinobido2/` for `shinobido2.exe`);
* `third_party/recomp`: vita-recomp-kit, the recompiler (`recomp/`), the
  generic tools and the build, install and packaging scripts. `game.json`
  describes this game to those scripts.

## Tools

This game's own:

| Script | What |
|---|---|
| `tools/fadebabe.py` | Acquire's FADEBABE archives (`volume.dat`, `StreamPack*.dat`): stats, table listing, raw members |
| `tools/to-mission.py` | drive a running `shinobido2.exe` from boot to the first mission's field (needs a hub save in slot 1) |
| `tools/sfx-soak.py` | sound effects measured over repeated mission restarts (the Phase 5 dropout) |
| `tools/untranslatable.py` | the functions the recompiler leaves to the fallback CPU, and why |
| `tools/xref.py` | a dumped ELF explored: disassembly with names, callers, strings |
| `tools/memwatch.ps1` | the game's and the system's memory as CSV, for long runs |
| `tools/make-icon.py` | draws the executable's icon (a throwing star, no game artwork) |
| `game.json` | this game for the shared scripts: title, supported eboot, modules to recompile, the folder's README per platform |

From the shared toolchain (`third_party/recomp/`; its README lists
everything, and each script's docstring has its options):

| Script | What |
|---|---|
| `tools/build-vita3k.py` | configure and build our Vita3K fork (`third_party/vita3k`) into `build/vita3k` (MSVC found with vswhere, Qt in its default folder; `--games-only`, `--no-jit`) |
| `tools/install-game.py`, `tools/make-dist.py` | a playable folder in `dist/` from the player's dump and firmware, as `game.json` describes it |
| `tools/make-setup.py`, `tools/setup.py` | a release, and its importer |
| `tools/fetch-update.py`, `tools/fetch-firmware.py` | the game's update and the firmware from Sony's servers |
| `tools/velf.py`, `tools/inventory.py`, `tools/imix.py` | Vita ELFs: segments, imports and exports; the code inventory; the instruction mix |
| `tools/v3kdrive.py` | drive Vita3K or `shinobido2.exe` without focus: launch, buttons, touches, FPS sampling, screenshots |
| `tools/sfo.py`, `tools/mkzrif.py` | `param.sfo` fields; a zRIF from a `work.bin` |
| `tools/proccap`, `tools/wavstats.py` | record one process's audio; loudness over time |
| `recomp/recompile.py` | recompile a module to C++ in `generated/<module>/` |
