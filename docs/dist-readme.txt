shinobido2: Shinobido 2: Revenge of Zen (US, PCSE00015, 1.02) on PC.

This is a work in progress (see the project's docs/03-plan.md). The game runs
in a fork of Vita3K, on its JIT for now; the native-code modules come later.

shinobido2.exe runs the game installed in a Vita file system ([paths]
vita_fs in shinobido2.ini; default: the fs folder next to this file).

Settings are in shinobido2.ini: resolution, window, fullscreen (F11 or
Alt+Enter while playing), filter, volume, keyboard and gamepad bindings. The
mouse is the touchscreens: left button front, right button rear. F12 saves a
screenshot to shinobido2\screenshots.

Known problem: Vita3K's audio loses the sound effects after a few mission
loads in a session (voices and music go on). Restarting shinobido2.exe
brings them back.

Built from Vita3K (https://github.com/Vita3K/Vita3K) under the GNU GPL
version 2. The game files, and any ssd_aot_*.dll here, are derived from your
own copy of the game: do not share them.
