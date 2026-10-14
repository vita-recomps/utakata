# utakata

A native PC port of **Shinobido 2: Revenge of Zen** (PS Vita, US PCSE00015)
by static recompilation, built from the player's own dump. Utakata is the
land the game is set in. It is a sibling of ss-delta (Soul Sacrifice
Delta), whose recompiler, Vita3K fork and tools it shares.

Licence: MIT ([LICENSE](LICENSE)). The Vita3K fork it builds on
(`third_party/vita3k`) is GPL-2.0-or-later.

> This repository contains *no* game data, *no* firmware and *no* code
> derived from the game. You bring your own dump; everything game-derived is
> generated locally from it ([D2](docs/decisions.md)).

## Status

Playable start to finish ([plan](docs/03-plan.md)): the owner played the
whole story to the ending on it, and the DLC missions load and play. The
game runs on native code recompiled from your own copy, without a JIT, at
2× internal resolution and 30 or 60 fps. Phases 0–5 are done (the Vita3K
sound-effects dropout is fixed in the fork); what is left is listed in the
plan: an NVIDIA check, the texture shimmer the game has on a Vita too,
and publishing.

## What you need

* Windows 10 or 11, x64, a GPU with Vulkan.
* Your own copy of the game, US version (PCSE00015): the PSN `.pkg` with its
  licence `work.bin`, or a decrypted dump (folder, `.zip` or `.vpk`). The
  Mirror Spirits add-on (`.pkg` + `work.bin`) is optional.
* The PS Vita firmware update files `PSVUPDAT.PUP` and `PSP2UPDAT.PUP` (as
  for Vita3K; Sony publishes them).
* To build: Git, Python 3.12 (`pip install capstone pyyaml numpy`), Visual
  Studio 2022 or its Build Tools with "Desktop development with C++" (MSVC
  x64, the Windows SDK, CMake and Ninja), Qt 6.11 for MSVC x64 (Vita3K's own
  interface is built too; e.g. with `aqtinstall` into `C:\Qt`), and the
  Vulkan SDK. These are Vita3K's build requirements.

## Building from a fresh clone

```
git clone --recurse-submodules <this repository's URL> utakata
cd utakata
python -I third_party/recomp/tools/build-vita3k.py --target shinobido2
```

The script finds MSVC (vswhere) and Qt (`Qt6_ROOT`, `--qt <dir>`, or the
newest `C:\Qt\<version>\msvc20*_64`). The first build takes about ten
minutes and puts `shinobido2.exe` (and `Vita3K.exe`, `ss-delta.exe`) in
`build/vita3k/bin/RelWithDebInfo/`.

## Installing your game

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

The update needs no `--license`: it uses the game's. The script checks that
the installed `eboot.bin` is 1.02, then lays out `dist/utakata/` with
`shinobido2.exe`, its DLLs, a commented `shinobido2.ini` and the Vita file
system in `fs/`. Everything in it is derived from your copy: don't share it.

## Playing

Run `dist/utakata/shinobido2.exe`. Settings are in `shinobido2.ini` next
to it, and the `README.txt` there describes them: resolution, window,
fullscreen (F11 or Alt+Enter), 30 or 60 fps, volume and sound effects,
keyboard and gamepad bindings, and keys that touch the screen (the caution
eye: F or the right trigger). F12 saves a screenshot. The mouse is the
touchscreens: left button front, right button rear.

Saves move in and out with the game closed: `shinobido2.exe --import-save
<folder|zip> [--slot N]` takes saves decrypted on a Vita (VitaShell,
Apollo: `data0000.bin`–`data0009.bin`), `--export-save <folder> [--slot N]`
copies them out.

## Documentation

| Doc | Contents |
|---|---|
| [01-research](docs/01-research.md) | the dump, the FADEBABE archives, the eboot measured, prior work, differences from ss-delta |
| [02-baseline](docs/02-baseline.md) | how the game behaves today, the SFX dropout repro, and how to re-run it |
| [03-plan](docs/03-plan.md) | phases, exit criteria, risks |
| [06-compatibility](docs/06-compatibility.md) | what has been played and checked, and what not yet |
| [decisions](docs/decisions.md) | decision log |
| [hashes](docs/hashes.md) | input hashes and pins |

## Tools

This game's own:

| Script | What |
|---|---|
| `tools/fadebabe.py` | Acquire's FADEBABE archives: stats, table listing, raw members |

The shared toolchain is a submodule, `third_party/recomp`
(vita-recomp-kit; its README lists everything): the recompiler
(`recomp/recompile.py`), the build, install and packaging scripts,
`velf.py`, `inventory.py`, `imix.py`, `v3kdrive.py` (drives the game for
tests), `sfo.py`, `mkzrif.py`, `fetch-update.py`, `proccap` (records one
process's audio) and `wavstats.py` (loudness over time). The Vita3K fork is
the other submodule, `third_party/vita3k`.
