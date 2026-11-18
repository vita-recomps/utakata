utakata: Shinobido 2: Revenge of Zen (US, PCSE00015, 1.02) on PC.

Start shinobido2.exe. The first time, it builds the game from your own dump: a
window asks for it (a folder, .zip or .vpk of the game with its 1.02 update, or
the PSN .pkg files with their licence; the Mirror Spirits add-on is optional),
downloads the PS Vita firmware from Sony and a compiler (about 650 MB; accept
Microsoft's licence for the C++ runtime and Windows SDK it uses), installs the
game and compiles its code on this PC, which takes a few minutes. Play then
starts the game, and from then on shinobido2.exe goes straight to it. Windows
may warn the first time ("More info", "Run anyway"): shinobido2.exe isn't
signed.

Everything stays in this folder: the game (fs), its code compiled for this PC
(ssd_aot_*.dll), settings (shinobido2.ini), saves, logs and the shader cache.
The downloads are deleted once the game is built; delete the folder and the
game is gone. Nothing of the game leaves your PC.

Command line (shinobido2.exe --help lists it all): --install opens the
importer again (another dump, the add-on); --dump <file> builds without the
window (add --accept-microsoft-license); --fullscreen or --windowed; --set
section.key=value sets any setting of shinobido2.ini for one run; --game
<folder> plays the game in another folder.

Settings: press F1, or hold Select (Back/View) on a gamepad for a second, to
open the settings menu over the paused game (Up/Down choose, Left/Right or
Cross change, L1/R1 or Q/E switch pages, Circle, Esc or F1 close). Window
size, fullscreen, vsync, filter and volume change at once; the rest are
marked * and take effect the next time the game starts. The menu writes
shinobido2.ini, which can also be edited by hand (key bindings and paths
are there only); read when the game starts:
- [display] scale (internal resolution, 2 = 1920x1088), window, fullscreen
  (F11 or Alt+Enter while playing), vsync, filter, and frame_rate: 30 as on
  the Vita, or 60. At 60, missions run at 60; the title, menus, hub and
  mission results stay at 30, and so do the scenes that follow a loading
  screen, as their animation would run twice as fast. The pause menu and
  the HUD in a mission animate twice as fast at 60.
- [display] mipmaps: smooths textures that shimmer in motion (the ground,
  walls), as the game ships some without mip levels; on by default (false:
  as on the Vita).
- [audio] volume, and effects: the reverb and fade-outs the game asks for
  (false: the plain sound of earlier builds).
- [keyboard], [gamepad]: bindings.
- [touch]: keys and buttons that hold a finger on the touchscreen. caution
  (F, right trigger) touches the topmost caution eye in a mission, which
  turns the camera to that enemy. The mouse is the touchscreens: left
  button front, right button rear.
F12 saves a screenshot to shinobido2\screenshots.

Saves (ten slots, 0-9) can be copied in and out, with the game closed:
  shinobido2.exe --import-save <folder or zip> [--slot N]
  shinobido2.exe --export-save <folder> [--slot N]
A save decrypted on a Vita (VitaShell, Apollo) has data0000.bin to
data0009.bin, one per slot. Without --slot every file goes to its own slot;
with it, one save goes to slot N. The saves as they were go to
shinobido2\save-backups first.

Built from Vita3K (https://github.com/Vita3K/Vita3K) under the GNU GPL
version 2. The game files, and the ssd_aot_*.dll files here, are derived
from your own copy of the game: do not share them.
