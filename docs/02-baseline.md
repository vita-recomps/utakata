# 02 — Baseline: how the game behaves today

## First run: ss-delta's fork through a shim (2026-10-12)

**Setup.** No fork branch exists for this game yet. `ss-delta.exe` boots
PCSA00152 only, so the run uses a copy of it with a shim file system:

* `build/ssd-shim/`: `ss-delta.exe` (ss-delta fork `1f100891`,
  RelWithDebInfo, with dynarmic) plus its DLLs, `data/` and
  `shaders-builtin/`. Its own `ss-delta.ini`: `vita_fs =
  <utakata>/build/shimfs`, `[recompiled] enabled = false` (everything
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
* Machine: the mini PC (Radeon 760M), Windows 11.

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

## How to re-run

```
python -I <ss-delta>\tools\v3kdrive.py build/ssd-shim start
python -I <ss-delta>\tools\v3kdrive.py build/ssd-shim run "wait 30000,start,wait 3500,hold:down:250,wait 1200,cross,..." build/baseline/fps.csv
python -I <ss-delta>\tools\v3kdrive.py build/ssd-shim close
```

The window title still says "Soul Sacrifice Delta" (it is the shim's exe).
Screenshots go to `build/baseline/` and are never committed.
