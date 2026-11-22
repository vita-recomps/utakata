# Changelog

The changes in each release of utakata. The downloads and each release's
full notes are on the [releases page](https://github.com/vita-recomps/utakata/releases);
[INSTALLING](docs/INSTALLING.md#updating) explains how to update.

## 0.2.0 (not released yet)

What ss-delta 0.4 has, apart from multiplayer, which this game doesn't
have ([plan](docs/03-plan.md), Phases 10 and 11).

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
  the mouse turns the camera as far as it moves, up to the game's own
  speed (120° a second sideways, 60 up and down). Sensitivity and inverted
  vertical on the Mouse page.
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
* From ss-delta's front end and kit: an Exit page in the settings menu,
  laptops with two GPUs use the faster one, the setup's log in
  `shinobido2/setup.log`, decrypted dumps laid out as `ux0`, and the
  Windows setup works from a temp folder whose path has a space.

## 0.1.0 (2026-11-18)

The first release: Windows, Linux (the Steam Deck among them) and macOS
on Apple Silicon, each built from the player's own dump on its first
start, natively, in its own folder.
