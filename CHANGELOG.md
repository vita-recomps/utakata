# Changelog

The changes in each release of utakata. The downloads and each release's
full notes are on the [releases page](https://github.com/vita-recomps/utakata/releases);
[INSTALLING](docs/INSTALLING.md#updating) explains how to update.

## 0.2.1 (2026-11-25)

ss-delta 0.5.2's fixes to the front end and the setup.

### Fixed

* **Android: the game's files wouldn't install on some phones**
  ([ss-delta #23](https://github.com/vita-recomps/ss-delta/issues/23)),
  such as a Galaxy S25: the setup stopped at "Failed to load archive
  file". The app now reads the files you pick through the access Android's
  file picker gives it, instead of opening them again by name, which those
  phones refuse to an app without storage permission.
* **Building the Android app's game from a Windows PC** (`--android`)
  stopped with `relocation R_AARCH64_ABS64 cannot be used against symbol
  ...; recompile with -fPIC` in 0.2.0.
* **Graphics cards whose driver has neither shader interlock nor
  raster-order attachment access** (the log's `Framebuffer reads:` line
  says "no, no": Qualcomm's own Adreno driver, older AMD Radeon such as
  the R5 APUs) leave effects that blend with the picture to the card's
  own blender, or read a copy of the picture, as ss-delta 0.5.2 does
  against blocks in its smoke and fog
  ([ss-delta #17](https://github.com/vita-recomps/ss-delta/issues/17)).
  Other cards draw exactly as before. `[debug] shader_blend` turns it off.

### New

* **The log lists every graphics card** Vulkan offers the game, and
  `[debug] gpu` picks one by its number there (for a laptop that starts
  on the wrong one).

## 0.2.0 (2026-11-24)

What ss-delta 0.4 and 0.5 have, apart from multiplayer, which this game
doesn't have, and ss-delta's fixes to its own game
([plan](docs/03-plan.md), Phases 10 and 11).

### New

* **Android** (64-bit ARM with Vulkan; made for Snapdragon handhelds such
  as the AYN Thor): an APK whose setup screen builds the game on the
  device from your dump, in about 8 minutes on a Snapdragon 8 Gen 2, or a
  PC that has built the game copies it over (`--android`). Turnip offered
  on Adreno; on-screen controls for phones, with a **CROUCH** button that
  holds R. **Import a Vita save** on the icon's long-press menu (a folder
  or a .zip, through `--import-save`).
* **Language:** the game's English, French or Spanish text, and the
  system dialogs with it (**Language** on the settings menu's Game page,
  `[game] language`). The game itself follows the console's language only.
* **Mouse camera** on a PC: Tab or a middle click captures the cursor, and
  the mouse turns the camera exactly as far and as fast as it moves, in
  the field and in the hook's aim: the game's camera code takes the mouse
  itself (in the recompiled code, [D16](docs/decisions.md)), not through
  the stick's slow, speeding-up turn. Sensitivity and inverted vertical on
  the Mouse page.
* **Xbox button prompts:** A, B, X, Y, LB, RB, Menu and View instead of the
  PlayStation symbols in the game's prompts, its HUD and the pause menu's
  Basic Controls page (each language's), or whichever the connected
  gamepad has (**Button prompts**, `[game] button_labels`).
* **Cheats** on a Cheats page of the settings menu, all off, switched
  while the game runs: infinite health, infinite ninja tools and items,
  one-hit kills, maximum money and maximum stats.
* **Skip intro logos** (off by default): from the loading screen straight
  to the opening movie, which Start skips.
* **rePatch mods,** kept beside the game in `fs/ux0/rePatch/` and read in
  place of its loose files (**Mods (rePatch)**). Add-ons and mods can be
  added after the build, in seconds, without building again.
* **RecompLauncher:** each release carries a `recomplauncher.json`.
* **Building without internet:** `--download-only <folder>` saves what the
  first build downloads (the firmware; `--for` adds other platforms'
  compilers and adb), and a build then takes it from that folder
  (`--offline <folder>`, the importer's "Downloaded files" row, or a folder
  named `offline` in the game's folder). Firmware PUPs you already have
  work too, whatever their names. See
  [INSTALLING](docs/INSTALLING.md#without-internet).
* **The cursor hides by itself** when the mouse has been still for 3
  seconds, and at once when you use a key or a gamepad; moving the mouse
  shows it again (**Hide idle cursor** on the Mouse page, `[mouse]
  hide_cursor`).
* From ss-delta's front end and kit: an Exit page in the settings menu,
  laptops with two GPUs use the faster one, the setup's log in
  `shinobido2/setup.log`, decrypted dumps laid out as `ux0`, and the
  Windows setup works from a temp folder whose path has a space.

### Changed

From ss-delta 0.5.1's setup (its D32):

* **The compiler comes with the release; no Microsoft licence.** The
  game's code is compiled with zig on Windows too, as on Linux and macOS,
  and each release carries it: the first build downloads only the PS Vita
  firmware (about 180 MB; Windows downloaded 650 MB before), and there is
  no licence to accept. `--accept-microsoft-license` is still accepted
  and does nothing. The release download is about 90 MB larger.
* **Fallback downloads:** when Sony's server (or ziglang.org) doesn't
  answer, the setup takes the same files from the Wayback Machine's
  copies, checked by SHA-256.
* **RecompLauncher: no second build for nothing.** Run again with the same
  release and the same dump, the setup ends at once ("Already built"); a
  new release or another dump still builds, and `--rebuild` builds
  anyway.

### Fixed

* **Skip intro logos at 60 fps hung on a black screen** before the title
  (found during 0.2.0's testing): the skip could race the game's own step
  past the first logo, so the opening movie never started. The skip now
  checks that the movie started and starts it again if not.

From ss-delta's setup
([ss-delta #13](https://github.com/vita-recomps/ss-delta/issues/13)):

* **Linux and the Steam Deck: the update in the same folder as the game
  could be left out.** A NoNpDrm dump's `app/` and `patch/` were installed
  in the order the file system lists them, and on Linux the update could
  come first and fail; the setup then stopped with "eboot.bin is not a
  build this port supports". The game is now always installed first, and
  the setup says when the update is missing ("the game's version 1.00").
* **Games copied straight off a Vita** carry the PSN account's own
  licence, usable only on that Vita. The setup now says so before its
  downloads, takes the NoNpDrm licence in the dump's `license/` folder in
  its place, and uses a licence given with a folder or `.zip` (it used to
  be ignored). See [INSTALLING](docs/INSTALLING.md#what-you-need), "From
  your own Vita".
* A folder whose game failed to install while something else in it
  installed counted as installed, and the setup stopped later without the
  reason.

## 0.1.0 (2026-11-18)

The first release: Windows, Linux (the Steam Deck among them) and macOS
on Apple Silicon, each built from the player's own dump on its first
start, natively, in its own folder.
