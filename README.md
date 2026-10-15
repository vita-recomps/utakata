# utakata

A native PC port of **Shinobido 2: Revenge of Zen** (PS Vita, US PCSE00015,
update 1.02) by static recompilation, built from the player's own dump. The
game's code, and the firmware modules it loads, are recompiled ahead of time
to C++ and run natively inside a fork of Vita3K, which supplies the rest of
the console. Utakata is the land the game is set in.

Licence: MIT ([LICENSE](LICENSE)). The Vita3K fork it builds on
(`third_party/vita3k`) is GPL-2.0-or-later.

> This repository contains *no* game data, *no* firmware and *no* code
> derived from the game. You bring your own dump; everything game-derived is
> generated locally from it ([D2](docs/decisions.md)).

## Status

The whole story plays to the ending on native code, without a JIT, and the
Mirror Spirits add-on's missions load and play; checked on AMD and NVIDIA
GPUs ([compatibility](docs/06-compatibility.md)). Other endings and
difficulties than the one played through are untested. Windows only for
now; Linux and macOS builds are planned.

## Features

Compared with running the game in Vita3K:

* **Native code.** The game's code, and the firmware modules it loads, are
  recompiled ahead of time to C++ and run natively; the build ships without
  the JIT. Each module is checked against the game in memory before its
  native code runs.
* **Sound effects that last.** In Vita3K the game's sound effects go silent
  after a few missions: its sound manager waits for voices to finish
  fading, and Vita3K never reported it. The fork tracks the fades, so no
  voice is lost; reverb and fade-outs are implemented too (Phase 5 in the
  [plan](docs/03-plan.md)).
* **60 fps.** `frame_rate = 60` runs missions at 60 fps at the right
  speed, by changing the game's frame pacing as data in memory, with no
  code patch. Menus, the hub, mission results and the scenes that step
  per frame stay at 30 so they keep their speed. Known: the HUD and pause
  menu animate twice as fast at 60. The default, 30, is the Vita's rate.
* **No texture shimmer.** Many ground textures ship without mipmaps and
  shimmer in motion, on a Vita too. The fork builds the mipmaps at load
  time, on by default ([D8](docs/decisions.md)).
* **Higher resolution**: Vita3K's multiplier, tested at 2× (1920×1088).
* **An in-game settings menu** (F1, or Select held on a gamepad) over the
  paused game, and a commented `shinobido2.ini`.
* **The caution eye on a key:** F or the right trigger touches the eye
  that locks on to an enemy, wherever it is on screen; the mouse is the
  touchscreens.
* **Vita saves** imported and exported (`--import-save`, `--export-save`).
* **One executable**, `shinobido2.exe`, without Vita3K's interface and
  offline, installed from your own dump with one command.

## The setup (no building)

Each release on GitHub has a setup, `utakata-setup-<version>.zip`, for
players who don't want to build anything. Unzip it, run `setup.bat`, and
in its window:

1. choose your dump: the game, update 1.02 and, if you have it, the Mirror
   Spirits add-on (the parts described below);
2. choose the folder to play from;
3. accept Microsoft's licence.

The setup downloads the PS Vita firmware from Sony and a compiler (about
650 MB in all, kept in `%LOCALAPPDATA%\vita-recomps`). It then installs
the game, translates its code and compiles it on your PC, which takes a
few minutes. Play from the folder it made (by default `shinobido2`, next
to the setup's folder) or from the desktop shortcut it offers; the setup's
own folder can be deleted afterwards. Nothing of the game is in the setup
or leaves your PC. The setup is not signed yet, so Windows may warn about
it ("More info", "Run anyway"). Its SHA-256 and build attestation are on
the release page.

## What you need

* Windows 10 or 11, x64, a GPU with Vulkan.
* Your own copy of the game, US version (PCSE00015): the PSN `.pkg` with its
  licence `work.bin`, or a decrypted dump (folder, `.zip` or `.vpk`). The
  Mirror Spirits add-on (`.pkg` + `work.bin`) is optional.
* The PS Vita firmware update files `PSVUPDAT.PUP` and `PSP2UPDAT.PUP` (as
  for Vita3K; Sony publishes them, and the setup downloads them).
* To build (not needed with the setup): Git, Python 3.12 (`pip install capstone pyyaml numpy`), Visual
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
minutes and puts `shinobido2.exe` in `build/vita3k/bin/RelWithDebInfo/`.

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

Run `dist/utakata/shinobido2.exe`. F1, or holding Select (Back/View) on a
gamepad for a second, opens the settings menu over the paused game. The
settings live in `shinobido2.ini` next to it, and the `README.txt` there
describes them: resolution, window,
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
| [01-research](docs/01-research.md) | the dump, the FADEBABE archives, the eboot measured, prior work |
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
