utakata: Shinobido 2: Revenge of Zen (US, PCSE00015, 1.02) on macOS
(13.3 or newer, Apple Silicon).

"Shinobido 2 - Revenge of Zen.app" in this folder is the game: double-click
it, or keep it in the Dock. macOS refuses it the first time, as it does
anything downloaded that isn't signed by a registered Apple developer: click
Done, open System Settings > Privacy & Security, scroll down to "Shinobido 2 -
Revenge of Zen was blocked" and click Open Anyway (once).

The first time, it builds the game from your own dump: a window asks for it (a
folder, .zip or .vpk of the game with its 1.02 update, or the PSN .pkg files
with their licence; the Mirror Spirits add-on is optional), downloads the PS
Vita firmware from Sony and a compiler (zig, about 240 MB in all), installs
the game and compiles its code on this Mac, which takes a few minutes. Play
then starts the game, and from then on the app goes straight to it.

Everything stays in this folder: the game (fs), its code compiled for this Mac
(ssd_aot_*.dylib), settings (shinobido2.ini), saves, logs and the shader
cache. The downloads are deleted once the game is built; delete the folder and
the game is gone (apart from the copy in Applications, if you let the importer
make one). Keep the app and the files next to it together; the folder itself
can move. Graphics go through MoltenVK (Vulkan over Metal, inside the app).

Command line (in Terminal: "Shinobido 2 - Revenge of
Zen.app/Contents/MacOS/shinobido2" --help lists it all): --install opens the
importer again (another dump, the add-on); --dump <file> builds without the
window; --fullscreen or --windowed; --set section.key=value sets any setting
of shinobido2.ini for one run; --game <folder> plays the game in another
folder.

Settings: press F1, or hold Select (the View button) on a gamepad for a
second, to open the settings menu over the paused game (Up/Down choose,
Left/Right or Cross change, L1/R1 or Q/E switch pages, Circle, Esc or F1
close). Window size, fullscreen, vsync, filter and volume change at once;
the rest are marked * and take effect the next time the game starts. On a
Mac keyboard the F keys need fn held, unless they are set as standard
function keys (System Settings, Keyboard). The menu writes shinobido2.ini,
which can also be edited by hand (key bindings and paths are there only);
read when the game starts:
- [display] scale (internal resolution, 2 = 1920x1088), window, fullscreen
  (F11 or Option+Return while playing), vsync, filter, and frame_rate: 30
  as on the Vita, or 60. At 60, missions run at 60; the title, menus, hub
  and mission results stay at 30, and so do the scenes that follow a
  loading screen, as their animation would run twice as fast. The pause
  menu and the HUD in a mission animate twice as fast at 60.
- [display] mipmaps: smooths textures that shimmer in motion (the ground,
  walls), as the game ships some without mip levels; on by default (false:
  as on the Vita).
- [audio] volume, and effects: the reverb and fade-outs the game asks for
  (false: the plain sound of earlier builds).
- [keyboard], [gamepad]: bindings.
- [touch]: keys and buttons that hold a finger on the touchscreen. caution
  (F, right trigger) touches the topmost caution eye in a mission, which
  turns the camera to that enemy. The mouse or trackpad is the
  touchscreens: click for the front, right-click (two fingers) for the
  rear.
F12 saves a screenshot to shinobido2/screenshots.

In fullscreen, started from its app, the game runs in macOS's Game Mode (the
controller icon in the menu bar): background work waits, and Bluetooth
controllers answer faster.

Saves (ten slots, 0-9) are in the Vita file system
(ux0/user/00/savedata/PCSE00015) and can be copied in and out, with the
game closed, in Terminal, in this folder:
  "Shinobido 2 - Revenge of Zen.app/Contents/MacOS/shinobido2" --import-save <folder or zip> [--slot N]
  "Shinobido 2 - Revenge of Zen.app/Contents/MacOS/shinobido2" --export-save <folder> [--slot N]
A save decrypted on a Vita (VitaShell, Apollo) has data0000.bin to
data0009.bin, one per slot; saves from the Windows or Linux port are the
same files. Without --slot every file goes to its own slot; with it, one
save goes to slot N. The saves as they were go to shinobido2/save-backups
first.

Built from Vita3K (https://github.com/Vita3K/Vita3K) under the GNU GPL
version 2. The game files, and the ssd_aot_*.dylib files here, are derived
from your own copy of the game: do not share them.
