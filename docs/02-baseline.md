# 02 — Baseline: how the game behaves today

## First run: ss-delta's fork through a shim (2026-10-12)

**Setup.** No fork branch exists for this game yet. `ss-delta.exe` boots
PCSA00152 only, so the run uses a copy of it with a shim file system:

* `build/ssd-shim/`: `ss-delta.exe` (ss-delta fork `1f100891`,
  RelWithDebInfo, with dynarmic) plus its DLLs, `data/` and
  `shaders-builtin/`. Its own `ss-delta.ini`: `vita_fs =
  <repo>/build/shimfs`, `[recompiled] enabled = false` (everything
  on the JIT), scale 1, volume 0.
* `build/shimfs/`: junctions to `extracted/vita3k/fs/{os0,sa0,vs0}` and
  `ux0/{addcont,license}`, and `ux0/app/PCSA00152` → our
  `ux0/app/PCSE00015`. `ux0/user/` is a real folder, so the saves stay in
  the shim.
* The game reports its own title ID (`PCSE00015`) from `param.sfo`. ELF
  dumps and saves use it.
* ss-delta's game-specific code does nothing here: the `boot_config.ini`
  override finds no file, and the add-on unlock finds no `quest_param.csv`.
  Both only log a warning.
* Fixed settings, as ss-delta (D4 update 4): Vulkan, `high-accuracy`,
  surface sync on, `memory-mapping: double-buffer`, offline mode.
* Machine: the AMD Radeon 760M test PC, Windows 11.

**ELF dump** (`--dump-elfs 45`): bootimage, sysmodule, libc, libfios2,
libSceFt2, libpvf and libscemp4 come out decrypted and relocated
([01-research](01-research.md#recompiler-probe-local)). This replaces an
external SELF decryptor, as in ss-delta D11.

**Driven run** (`tools/v3kdrive.py` from ss-delta, input pipe, no focus):

| Point | Result |
|---|---|
| Boot | Acquire and Spike logo movies play (`libscemp4` LLE, H.264 through SceVideodec) |
| Title | "Press START button", correct, **30 fps** |
| Main menu | New Game / Continue. The cursor wraps; cross confirms, circle backs out. Continue with no save opens the system's Load dialog ("There is no saved data") as a Vita3K overlay, which `frame:` captures do not show (use `shot:`) |
| New Game | Select Difficulty / Options, then the intro: a painted map scene, text panels |
| Tutorial field | **Gameplay reached.** Player model, lighting, HUD (map, objective list) correct. Move, jump and crouch tick their objectives. **30 fps** (36 samples: 30–31) |

Rendering: no visible errors in title, menus, intro or the tutorial field.
Not yet seen: cutscene FMV with subtitles, combat, effects, other maps.

**Log, whole session:**

* NGS (audio): `Game is using unimplemented reverb audio module`, `...
  envelope ...`, `... equalizer ...`, `Unimplemented sceNgsModuleGetPreset`.
  The likely root of the known SFX dropout ([01-research](01-research.md)).
  Audio was muted for this run, so nothing was heard.
* Saves: the game probes `savedata0:/SlotParam_0.bin` … `SlotParam_9.bin`
  (ten slots). The `SlotParam_N.bin` naming is the same as Soul
  Sacrifice's.
* One `ksceKernelAllocMemBlock` NO_MEMORY at boot (firmware side), and one
  `_sceKernelWaitThreadEnd` on an unknown thread at the end. Neither had a
  visible effect.
* Stubs hit: `sceAppUtilInit`, `sceCommonDialogSetConfigParam`,
  `sceNpTrophyCreateHandle`, the codec engine memory calls, three FIOS
  overlay calls, `sceKernelGetCpuId`. No crash.
* Trophies: `TROPUSR.DAT` missing (no trophy data set up). Harmless.

**Not yet measured:**

* audio heard, and the SFX dropout reproduced (needs 2–3 missions, or the
  "sprint over corpses" shortcut from compat #1193);
* the upstream Vita3K release on this machine (OpenGL and Vulkan; ss-delta
  found upstream Vulkan crashing on the 760M);
* an RTX 4090 run;
* per-thread CPU time, thread count;
* ~~update 1.02~~ (below).

## Update 1.02 through the same shim (2026-10-12)

1.02 installed over 1.00 ([01-research](01-research.md#update-102-local)).
The shim's junction follows it, so nothing in `build/ssd-shim` changed.

* **ELF dump:** the eboot differs (see [hashes](hashes.md)); bootimage,
  sysmodule, libc, libfios2, libSceFt2, libpvf and libscemp4 are
  byte-identical to the 1.00 run, at the same addresses. Only
  `adhoc_matching` (loaded by ss-delta's dump code, not by the game) moved
  from `0x805D9000` to `0x805DA000`.
* **Driven run:** logos → title → menu (New Game / Continue) → New Game →
  intro map → the first in-engine cutscene, all rendered correctly, **30
  fps** (samples 28–31; the 28s are during loads). The title showed up
  later than the 1.00 script expects: still in the logo movie at 30 s, the
  title by about 40 s. Use `wait 40000` before the first `start`.
* **Log:** at boot the game opens `app0:/patch.dat`,
  `app0:/RomImage/PSP2/US/Sound/StreamPack/StreamPackDLC.dat` and
  `addcont0:/DLC001X000000000/RomImage/DLC/DLCVersion000.txt`, with no
  errors: the add-on is found. Otherwise the same warnings as 1.00 (the
  NGS reverb/envelope/equalizer modules, `sceNgsModuleGetPreset`, the same
  stubs, one firmware-side `NO_MEMORY`).
* **Not yet checked:** that the DLC missions show up in the game (needs
  play to the mission board).

## Audio baseline: the SFX dropout reproduced (2026-10-13)

**Setup.** The shim as above, 1.02, `[audio] volume = 100`. In-game: Easy,
Music Volume 0 (so the recording holds sound effects and voices only),
SFX 100. The game's output was recorded with `third_party/recomp/tools/proccap`: Windows
process loopback, only this process, with its session turned down to −80 dB
so nothing was heard. The recording is scaled back up. Loudness per
window came from `third_party/recomp/tools/wavstats.py`. Input came from `v3kdrive.py`
scripts: swings (Square ×3), dashes (Circle + stick), jumps (Cross).

**Run 1 (one process, 2 h 04 min):**

| Time into the run | What | Sound effects |
|---|---|---|
| 0–8 min | boot, menus, intro, tutorial lessons | yes |
| 8–38 min | stress loop in the tutorial field: ~400 swings, dashes and jumps a minute | **yes, steady** (−27 to −29 dB RMS, peaks −3 dB, ~600 onsets/min) |
| 38–77 min | the loop's presses ran past the tutorial's end into the hub menus (not intended) | menu sounds only |
| 77–84 min | save; mission 1 "Request for Help" loaded, restarted once, ended | yes |
| 86–95 min | mission 2 "Kill Kinokuniya": load, then *Restart Mission* after each ~90 s cycle | yes after the load and the 1st restart |
| **95 min** | **2nd restart in mission 2 (about the 6th mission load of the session)** | **gone, for good** |
| 95–124 min | 10 more cycles; three 20 s probes (swings, dashes, jumps): in the same mission, in a new mission (after giving up and a new day), and after *Back to Title* + loading the save | **exact digital silence** (−100 dB) in every probe |
| | cutscene after a failed mission | **dialogue audible** (−30 dB) |
| | the "Mission Failed" sting | silent |

**Run 2 (new process, same save):** the first mission's probe has sound
effects again (−27 dB, peaks −3 dB).

**What this shows:**

* Reproduced: sound effects stop and stay stopped while voice playback
  goes on, as in every Vita3K report.
* The loss is **sudden, and it came at a mission load**, not during
  combat. 30 minutes of constant swings in the tutorial didn't trigger it.
  **Hypothesis:** each mission load (or restart) leaks something in the SFX
  path, and after about six the SFX path dies. That fits "after 2–3
  missions" (each mission has loads and retries) better than a per-sound
  leak. The "faster when sprinting over corpses" report is not explained
  yet.
* Nothing saved is involved: Back to Title and reloading don't help, and
  a new process does.
* The log has nothing at the moment of the loss (no NGS warning or error;
  Vita3K logs each NGS error once, and the only NGS lines are the first-use
  warnings at boot). Phase 5 needs the instrumentation listed in
  [01-research](01-research.md#vita3ks-ngs-and-this-game-code-reading-2026-10-13).
* The dropout came 6 loads into the session. To get there quickly, load
  the `hub-day1` save, start a mission and use *Restart Mission* (pause →
  top item → Yes) every ~90 s, probing in between.

**Files** (git-ignored): `build/audio/run1.wav`, `run2.wav` (the
recordings), `chunks.log` (each step's start offset in the recording),
`run1-vita3k.log`, the `cycle.sh` and `probe.sh` scripts and their
screenshots, `build/saves/hub-day1/` (a save at the hub, day 1, after the
tutorial: `SlotParam_0.bin`, `data0000.bin`).

**Driving pitfalls seen:** `v3kdrive.py` children outlive a stopped
background shell and keep pressing buttons (see CLAUDE.md). The menus
react slowly: give each press 3 s or more, and check with screenshots.

## Native code (Phase 3, 2026-10-13)

`shinobido2.exe` (fork `games` + render-target logging), `[recompiled]
enabled = true, jit = true`, with `ssd_aot_eboot.dll`, `ssd_aot_libc.dll`
and `ssd_aot_libfios2.dll` in `dist/shinobido2-test`. Driven by
`tools/to-mission.py` and v3kdrive, counters from `SSD_AOT_COUNT=1
SSD_AOT_STATS=<file>`.

| Run | Native share | Escapes | JIT inside the 3 modules | Differential | fps |
|---|---|---|---|---|---|
| boot → mission → combat (first build) | 99.4% | 87 → 9,406 (libc `memcpy`, through `memmove`'s `bx ip`) | 0 | — | 30 |
| same, after the tail-call fix | 99.4–99.5% | **0** | **0** | — | **30** (112 samples 30, 41 at 31) |
| boot → mission → combat → *Restart Mission* → combat, `SSD_AOT_DIFF=2000` | 99.7% | 0 | 0 | 50,727 calls, **0 mismatching**, 1,341 skipped (HLE calls, atomics) | 11–31 (the checker's shadow runs) |

* The rest of the JIT time is the firmware's MP4 player
  (`libscemp4`, reached through SceMp4 stubs) and other firmware code,
  all for Phase 4.
* `SSD_AOT_DIFF=100` slows the game to 4–5 fps and turned the screen red
  and dark (the shadow runs' undo racing other threads, as ss-delta saw at
  20); use sparse intervals.
* Rendering matched the JIT build in every screenshot (field, mission
  start, combat, restart).

## No JIT (Phase 4, 2026-10-13)

`dist/utakata-p4`, installed by `install-game.py --no-jit` from the pkg
files (game, 1.02, add-on) and the PUPs: `shinobido2.exe` without dynarmic,
seven recompiled modules (eboot, libc, libfios2, sysmodule, libSceFt2,
libpvf, libscemp4), `jit = false`.

| Run | fps | Native | Escapes | Stops |
|---|---|---|---|---|
| boot → New Game → intro cutscene → tutorial (move, jump, crouch, dash) | 30–31 | 100% (1.6 G instructions, JIT 0) | 0 | none |
| hub save → first mission → combat → *Restart Mission* | 30–31 (199 × 30, 74 × 31) | 100% (2.1 G, JIT 0) | 0 | none |

* libscemp4 (the movie player) loaded three times by the first mission,
  each time at `0x805B4000`, where its native code expects it.
* Before the firmware modules were generated from `<module>.elf` names,
  their places were held but never released, so they loaded elsewhere and
  the game stopped at once with "no native code" in sysmodule.

## The SFX dropout: cause and fix (Phase 5, 2026-10-14)

No-JIT install (`dist/utakata-p4`), sound recorded by `tools/sfx-soak.py`
(3–12 cycles of 30 s combat + *Restart Mission* in the first mission).

| Build | Cycles | SFX loudness per cycle | Polls of voices Vita3K had ended |
|---|---|---|---|
| fork before the envelope fix | 12 | −27 to −28 dB, steady | (not counted) |
| before the fix, with a temporary counter | 3 | −26 to −27 dB | **71,000** (every frame, never freed) |
| with the fix (`fe8659d0`) | 3 | −27 to −28 dB | **2** (freed at once) |

* A first counter (distinct ended voices still polled) rose by exactly one
  per mission load before the fix: the leak is one voice per load in
  mission 1. Twelve loads did not exhaust the pool there; Phase 0's
  dropout came in mission 2, after about six loads in total.
* The envelope gain changed no measured loudness.
* **Memory** (`tools/memwatch.ps1`, every 15 s for 30 min over four game
  sessions): the game's private memory 1.2–1.6 GB and flat within each
  session (1,599 → 1,602 MB over 12 restarts), handles flat; free RAM never
  below 4.9 GB. No leak in the game. Windows Defender peaked at ~1 GB while
  scanning build and test output.

## Caution binding (Phase 7, 2026-10-14)

The `caution` touch binding (F, right trigger) puts its finger on the
topmost caution eye. When it goes down, the front end reads back one frame
and slides a 150-point template of the eye's frame (wings, rim and pupil,
taken where white and red eyes over five backgrounds agree) down x = 896;
the first y scoring under 30 (mean difference per channel) is the eye.

| Screenshots | Score |
|---|---|
| 12 with an eye (white, red, one fading in, one over a bright wall) | 4.9–20.7 |
| 104 without (field, combat, menus, cutscenes, system pictures) | 43 and up |

In the field (no-JIT build, scale 2), after fighting until an eye showed,
holding F logged `caution: eye at 896, 258` and turned the camera to the
enemy; it turned back on release. With no eye shown it logged
`no eye on screen` and touched nothing. Yellow and purple eyes were not
in the samples; they share the frame (**hypothesis**: they match the
same way). `v3kdrive.py` cannot press F for the game (front-end keys need
the window focused), so this check focused the window by hand.

## Upstream Vita3K on this machine (2026-10-13)

The stock release in `extracted/vita3k` (`v0.2.1 4152-38bce160`, the
build ss-delta compared against), 1.02, the `hub-day1` save, scale 1:

| Renderer | Boot → title → hub (save loaded) | Mission field ("Request for Help") |
|---|---|---|
| OpenGL | correct | **correct, 30 fps** (samples 30–31) |
| Vulkan | correct | **correct, 30 fps** (27–32, mostly 30) |

* Unlike Soul Sacrifice Delta, upstream Vulkan **doesn't crash** on the
  Radeon 760M with this game. So upstream is a usable reference on both
  renderers here, which helps Phase 6 (renderer differences against our
  fork).
* No visible difference from the fork in these scenes.
* Not run: the RTX 4090 (it needs the owner's other PC; see the plan).

**DLC check, so far:** the hub up to day 4 lists only story missions, and
the day-1 letters are regular ones. The Mirror Spirits missions didn't
appear yet; they may unlock later in the story (**hypothesis**). The
add-on itself is found at boot.

## How to re-run

```
python -I third_party/recomp/tools/v3kdrive.py build/ssd-shim start
python -I third_party/recomp/tools/v3kdrive.py build/ssd-shim run "wait 30000,start,wait 3500,hold:down:250,wait 1200,cross,..." build/baseline/fps.csv
python -I third_party/recomp/tools/v3kdrive.py build/ssd-shim close
```

The window title still says "Soul Sacrifice Delta" (it is the shim's exe).
Screenshots go to `build/baseline/` and are never committed.
