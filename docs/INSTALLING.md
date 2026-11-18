# Installing utakata

utakata runs **Shinobido 2: Revenge of Zen** natively on Windows, Linux (and
the Steam Deck) and macOS on Apple Silicon. The downloads contain no game
files and no code derived from the game: the first start builds the game on
your computer from **your own dump** of it.

## Contents

* [What you need](#what-you-need)
* [Windows](#windows)
* [Linux and the Steam Deck](#linux-and-the-steam-deck)
* [macOS (Apple Silicon)](#macos-apple-silicon)
* [The first start: building the game](#the-first-start-building-the-game)
* [Playing](#playing)
* [Saves](#saves)
* [Files and folders](#files-and-folders)
* [Command-line options](#command-line-options)
* [Updating](#updating)
* [Uninstalling](#uninstalling)
* [Reporting a problem](#reporting-a-problem)

## What you need

| | |
|---|---|
| Windows | Windows 10 or 11, x64, a GPU with Vulkan |
| Linux | x64, glibc 2.30 or newer (any current distribution, SteamOS), a GPU with Vulkan |
| macOS | macOS 13.3 or newer on Apple Silicon (M1 and later) |
| Disk space | about 1.5 GB for the game's folder, and up to 2 GB more while it builds |
| Internet | the first start downloads the PS Vita firmware from Sony and a compiler |

**Your own copy of the game, US version (PCSE00015), at update 1.02**, the
final one. Any of these forms works:

* a decrypted dump (a folder, a `.zip` or a `.vpk`) with the 1.02 update,
  merged into the game or beside it as NoNpDrm dumps keep it (`app/` and
  `patch/`);
* the PSN `.pkg` of the game with its licence (`work.bin` or a `.rif`, or a
  zRIF), plus the 1.02 update's `.pkg`. Sony's update server still has it
  (21 MB): `fetch-update.py` in [BUILDING](BUILDING.md#installing-your-game-into-a-build)
  fetches it.

The **Mirror Spirits** add-on (its `.pkg` and `work.bin`) is optional. Its
missions are listed after an ending.

Download the archive for your system from the
[latest release](https://github.com/vita-recomps/utakata/releases/latest).
Each unpacks to a folder `utakata`: that folder **is** the game. Keep it
wherever you like (not inside a folder that needs administrator rights, such
as `C:\Program Files`).

## Windows

1. Download `utakata-<version>-windows.zip` and unzip it.
2. Start `shinobido2.exe`. Windows may warn that it doesn't know the program
   (it isn't signed with a publisher's certificate): click "More info", then
   "Run anyway".
3. The importer opens: see [the first start](#the-first-start-building-the-game).
   On Windows, also tick that you accept Microsoft's licence for the C++
   runtime and Windows SDK the compiler uses (it downloads them from
   Microsoft).

The importer can put a shortcut on the desktop.

## Linux and the Steam Deck

1. Download `utakata-<version>-linux.tar.gz` and unpack it (on a Steam
   Deck, in desktop mode: Dolphin can unpack it with a right-click).
2. Start `shinobido2.x86_64`: double-click it, or `./shinobido2.x86_64` in a
   terminal.
3. The importer opens: see [the first start](#the-first-start-building-the-game).
   Tick **Add the game to Steam** (Steam must be running) to play it from
   the Steam Deck's Game Mode, and the applications-menu box for a menu
   entry.

It is a Linux program, not a Windows one: no Proton or other compatibility
tool is needed. If the game didn't reach Steam, run
`./shinobido2.x86_64 --add-to-steam` with Steam running, or add
`shinobido2.desktop` from the folder with Steam's "Add a Non-Steam Game". On
the Deck the controls are a gamepad to the game, and the touchscreen is the
Vita's front touchscreen.

## macOS (Apple Silicon)

1. Download `utakata-<version>-macos.tar.gz` and open it (Archive Utility
   unpacks it).
2. Double-click **Shinobido 2 - Revenge of Zen.app** in the folder. macOS
   refuses it the first time, as it does anything downloaded that isn't
   signed by a registered Apple developer: click Done, open System Settings
   > Privacy & Security, scroll down to "Shinobido 2 - Revenge of Zen was
   blocked" and click **Open Anyway** (once).
3. The importer opens: see [the first start](#the-first-start-building-the-game).
   It can also put the game in Applications (Launchpad and Spotlight list it).

In fullscreen the game runs in macOS's Game Mode.

## The first start: building the game

The importer's window asks for your dump:

1. **Game**: the game's folder, `.zip`, `.vpk` or `.pkg` (File... or
   Folder...). The importer looks inside a folder or archive: when it
   already holds the 1.02 update and the licence, it says so and doesn't ask
   for them.
2. **Update**: the 1.02 update, if the game's dump doesn't hold it.
3. **Licence** (for a `.pkg`): its `work.bin` or `.rif`, found beside it when
   it's there, or a zRIF typed in.
4. **Add an add-on (DLC)...**: Mirror Spirits, if you have it, with its
   licence.

Then **Build**. The importer:

* downloads the PS Vita firmware from Sony and a compiler (Windows: about
  650 MB, LLVM's clang with Microsoft's C++ runtime and SDK; Linux and
  macOS: about 240 MB, zig);
* installs the game into the folder, starts it once unseen to read its code,
  translates that code to C++ and compiles it on your computer;
* deletes the downloads and its work files.

This takes a few minutes (longer on a Steam Deck). Then **Play** starts the
game. From then on, starting the game goes straight to it.

Without the window (for scripts and launchers), each part of the dump after
`--dump`, in order (the game, the update, the add-on):

```
shinobido2.exe --dump "<game>" --dump "<1.02 update>" --accept-microsoft-license   (Windows)
./shinobido2.x86_64 --dump "<game>" --dump "<1.02 update>"                         (Linux)
```

A `.pkg` takes its licence after it: `--dump "<game>.pkg" --license
"<work.bin>"`. `--build-only` builds and quits instead of playing.

## Playing

* **Settings:** F1, or Select (Back/View) held for a second on a gamepad,
  opens the settings menu over the paused game. Everything is also in
  `shinobido2.ini`, which can be edited by hand (key bindings only there).
* **Fullscreen:** F11 or Alt+Enter (Option+Return on a Mac). On a Mac
  keyboard the F keys need fn held, unless they are set as standard function
  keys.
* **Touch:** the mouse (or trackpad) is the touchscreen: left button front,
  right button rear. F and the gamepad's right trigger touch the caution
  eye in a mission, which turns the camera to that enemy.
* **Frame rate:** 30 fps by default, as on the Vita; `frame_rate = 60` under
  `[display]` runs missions at 60 at the right speed. The title, menus, hub,
  mission results and the scenes after a loading screen stay at 30; the HUD
  and pause menu animate twice as fast at 60.
* **Textures:** `mipmaps` (on by default) smooths ground and wall textures
  that shimmer in motion, on a Vita too.
* **Sound:** `[audio] effects` turns the reverb and fade-outs the game asks
  for on or off.
* **Screenshots:** F12, into `shinobido2/screenshots`.

`README.txt` in the game's folder describes every setting.

## Saves

Saves are in the game's folder, in the Vita file system:
`fs/ux0/user/00/savedata/PCSE00015`. The game has ten save slots, 0–9, one
file each (`data0000.bin` to `data0009.bin`); they are the same files on
every platform.

To use saves from a Vita (decrypted, for example with VitaShell or Apollo),
or from another computer, with the game closed:

```
shinobido2.exe --import-save <folder or .zip> [--slot N]
shinobido2.exe --export-save <folder> [--slot N]
```

Without `--slot`, every file goes to its own slot; with it, one save goes
to slot N. An import keeps the saves as they were in
`shinobido2/save-backups`.

## Files and folders

Everything the game uses is in its folder; nothing is written anywhere else
(apart from the shortcut, menu entry, Steam entry or Applications copy, if you
let the importer make one).

| In the game's folder | What |
|---|---|
| `shinobido2.exe`, `shinobido2.x86_64`, `Shinobido 2 - Revenge of Zen.app` | the game: the one thing to start |
| `shinobido2.ini` | settings |
| `fs/` | the Vita file system: the installed game, the firmware, your saves |
| `ssd_aot_*.dll` / `.so` / `.dylib` | the game's code, compiled for your computer |
| `shinobido2/` | log (`vita3k.log`), save backups, screenshots |
| `cache/` | the shader cache |
| `patch/` | Vita3K-style patches, if you add any |
| `setup/` | the importer (its Python and the recompiler kit), kept for `--install` |
| `data/`, `shaders-builtin/`, `icons/` | files from Vita3K the game reads |

Everything in `fs/`, `ssd_aot_*` and `cache/` is derived from your copy of the
game: don't share it.

## Command-line options

`--help` prints these and every setting of `shinobido2.ini`.

| Option | What |
|---|---|
| `--game <folder>` | play the game in that folder (default: the program's own) |
| `--install` | open the importer again (another dump, the add-on), then play |
| `--dump <file> [--license <work.bin\|.rif> \| --zrif <zRIF>]` | build from this dump without the window (repeat for the update and add-on), then play |
| `--build-only` | build if needed (or with `--install` / `--dump`), then quit |
| `--accept-microsoft-license` | Windows, with `--dump`: accept Microsoft's licence for the compiler's runtime and SDK |
| `--shortcut`, `--steam` | with `--dump`: a desktop shortcut, menu entry or Applications copy; add the game to Steam (Linux) |
| `--cache <folder>`, `--jobs <n>` | with `--dump`: keep the downloads there for next time; compile with n jobs |
| `--add-to-steam` | Linux, Steam Deck: add the game to Steam (Steam running), then quit |
| `--set <section.key=value>` | a setting of `shinobido2.ini` for this run only |
| `--fullscreen`, `--windowed` | the same as `--set display.fullscreen=true` / `false` |
| `--import-save <folder\|zip>`, `--export-save <folder>`, `--slot <0-9>` | saves, then quit (`--quiet`: no message box) |
| `--write-ini <file>` | write the default settings file there, then quit |

On macOS the program inside the app takes them:
`"Shinobido 2 - Revenge of Zen.app/Contents/MacOS/shinobido2" --help`.

## Updating

To move to a newer release, unpack it over your game's folder (replace the
files), then start the game with `--install` and build again from the same
dump: saves and settings are kept.

## Uninstalling

Delete the game's folder. If you let the importer make them, also delete the
desktop shortcut (Windows), the menu entry and the Steam entry (Linux), or the
copy in Applications (macOS).

## Reporting a problem

Open an [issue](https://github.com/vita-recomps/utakata/issues) with your
system, the release, what you did and what happened. Attach the log,
`shinobido2/vita3k.log` in the game's folder (for the importer, the messages
in its window). Never attach game files, saves you don't want public, or
anything from `fs/`.
