utakata: Shinobido 2: Revenge of Zen (US, PCSE00015, 1.02) on Linux
(x86-64; Steam Deck).

Start shinobido2.x86_64 (from a file manager, or ./shinobido2.x86_64 in a
terminal; on a Steam Deck in desktop mode the first time). The first time, it
builds the game from your own dump: a window asks for it (a folder, .zip or
.vpk of the game with its 1.02 update, or the PSN .pkg files with their
licence; the Mirror Spirits add-on is optional), downloads the PS Vita
firmware from Sony and a compiler (zig, about 240 MB in all), installs the
game and compiles its code on this computer, which takes a few minutes (about
20 on a Steam Deck). Play then starts the game, and from then on
shinobido2.x86_64 goes straight to it. It needs Vulkan, glibc 2.30 or newer
and nothing else from the system.

Everything stays in this folder: the game (fs), its code compiled for this
computer (ssd_aot_*.so), settings (shinobido2.ini), saves, logs and the shader
cache. The downloads are deleted once the game is built; delete the folder and
the game is gone (apart from the menu entry and Steam entry, if you let the
importer add them). Nothing of the game leaves your computer.

Command line (./shinobido2.x86_64 --help lists it all): --install opens the
importer again (another dump, the add-on); --dump <file> builds without the
window; --add-to-steam adds the game to Steam; --fullscreen or --windowed;
--set section.key=value sets any setting of shinobido2.ini for one run; --game
<folder> plays the game in another folder.

Steam Deck: the importer adds the game to Steam as a non-Steam game (its "Add
the game to Steam" box; Steam must be running), so it starts from Game Mode. If
it didn't, run ./shinobido2.x86_64 --add-to-steam, or add shinobido2.desktop
from this folder with "Add a Non-Steam Game" (Steam, Games menu, in desktop
mode). No compatibility tool is needed: it is a Linux program, not a Windows
one. The Deck's controls are a gamepad to the game; the touchscreen is the
Vita's front touchscreen.

Settings: press F1, or hold Select (the View button) on a gamepad for a
second, to open the settings menu over the paused game (Up/Down choose,
Left/Right or Cross change, L1/R1 or Q/E switch pages, Circle, Esc or F1
close). Window size, fullscreen, vsync, filter and volume change at once;
the rest are marked * and take effect the next time the game starts. The
menu writes shinobido2.ini, which can also be edited by hand (key bindings
and paths are there only); read when the game starts:
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
F12 saves a screenshot to shinobido2/screenshots.

Saves (ten slots, 0-9) are in the Vita file system
(ux0/user/00/savedata/PCSE00015) and can be copied in and out, with the
game closed:
  ./shinobido2.x86_64 --import-save <folder or zip> [--slot N]
  ./shinobido2.x86_64 --export-save <folder> [--slot N]
A save decrypted on a Vita (VitaShell, Apollo) has data0000.bin to
data0009.bin, one per slot; saves from the Windows or macOS port are the
same files. Without --slot every file goes to its own slot; with it, one
save goes to slot N. The saves as they were go to shinobido2/save-backups
first.

Built from Vita3K (https://github.com/Vita3K/Vita3K) under the GNU GPL
version 2. The game files, and the ssd_aot_*.so files here, are derived
from your own copy of the game: do not share them.
