# 01 — Research: a PC port of Shinobido 2: Revenge of Zen (PS Vita)

Research snapshot from 2026-10-12. **Hypothesis** marks claims not checked
against the binary or Vita3K. Sources are marked:

* **[local]**: measured on our own dump in this session;
* **[ssd]**: carried over from the Soul Sacrifice Delta port (ss-delta),
  where the same tool or mechanism was proven;
* **[web]**: issue trackers, Sony's update servers, wikis (URLs inline).

## TL;DR

* **Much easier than Soul Sacrifice Delta, and most of the work is already
  done.**
  * The ss-delta recompiler translates the 1.02 eboot **unchanged**:
    16,972 functions, **0 unsupported instructions**, 2 functions left to
    the fallback, 211 MB of C++ in 48 s (1.00: 16,917 functions, the same
    result). libc, libfios2 and the firmware
    modules translate too (libpvf has 2 functions with unsupported forms at
    this load address).
  * ss-delta's inventory reads it completely in 10 s: 0 unreached bytes,
    every jump table resolved, no tail calls, no ARM-mode code.
  * The ss-delta Vita3K fork (JIT) runs it to gameplay at **30 fps** on
    Vulkan on the Radeon 760M, rendering correctly as far as we got (1.00:
    logos, FMV, title, menus, tutorial field; 1.02: the same up to the
    first in-engine cutscene).
* **It is about a third of Soul Sacrifice Delta's size:** 1.37 M
  instructions and 17.4 k functions, against 3.8 M and 34.6 k.
* **ss-delta's hardest runtime problem doesn't arise:** the game ships
  `libult.suprx` but neither imports nor loads it, so there are no user-level
  threads or fiber switches (ss-delta D9).
* **New problem: audio.** The game mixes through **SceNgs** (27 imports).
  Vita3K leaves NGS's envelope, equalizer and reverb modules unimplemented
  (warnings in our first run). Every Vita3K report of this game, on any
  version and region, says that **sound effects die after 2–3 missions**
  while voices and BGM continue. This is the one known blocking bug.
* **New input problem:** the rear touchpad aims the grappling hook and the
  first-person view [web]. It needs a PC mapping.
* **Engine:** Sony's **PhyreEngine** (`.phyre` assets, `.cgfx.GXM.phyre`
  shaders) with **Havok** physics [local]. Scripts are `.sol`/`.sx`.
* **Version:** the dump is **1.00**; the port targets **1.02**
  ([D3](decisions.md)), the final US update, fetched from Sony's update
  server with `third_party/recomp/tools/fetch-update.py` and installed. It adds DLC support and
  "downloadable content missions" [web]. Its eboot grew by 0.6% and adds
  only two imports (`sceAppUtilDrmOpen/Close`, the add-on mount); libc and
  libfios2 decrypt to the same code as 1.00 ([below](#update-102-local)).
* **Single-player only.** No ad hoc or online play. The online surface is
  trophies, the "Network Jar" (Near gifts) and HTTP/NP calls, all of which
  can be stubbed offline.

## What's in the dump [local]

Input: `rom/Shinobido 2 Revenge of Zen.rar` (1.04 GB, RAR5). It holds a PSN
**`.pkg` plus `work.bin`** for the game and for the DLC. This is a different
format from ss-delta's NoNpDrm zip.

| Item | Value |
|---|---|
| Game pkg | `UP0700-PCSE00015_00-APP0000000000000`, 1,086,050,096 bytes |
| DLC pkg | `UP0700-PCSE00015_00-DLC001X000000000`, "The Mirror Spirits", 102,400 bytes |
| `param.sfo` | `TITLE_ID PCSE00015`, `APP_VER 01.00`, `CATEGORY gd`, `c_date=20120105`, `PSP2_SYSTEM_VER 0x1060000` (firmware 1.06), `SAVEDATA_MAX_SIZE 0x1000` |
| Trophies | `NPWR03064_00` |

### Installing

* Vita3K's CLI installs a pkg with `--pkg <file> --zrif <base64>`. The zRIF
  is `work.bin` deflated with psvpfstools' 1 KB dictionary (window bits 10)
  and base64-encoded. `third_party/recomp/tools/mkzrif.py` makes it from `work.bin`; the
  dictionary is read from Vita3K's own `libzrif/src/keyflate.c`. Both
  licences decoded, both pkgs installed ("matched retail hmac").
* Firmware 3.74 is installed from the PUPs ss-delta already has (same
  hashes, [hashes](hashes.md)).
* ss-delta's `install-game.ps1` and `ss-delta.exe --install` take only zips,
  vpks and folders. The new front end needs the pkg + zRIF path (plan
  Phase 1).

### Layout of the installed game

| Path | What |
|---|---|
| `eboot.bin` | 2.43 MB SELF |
| `sce_module/` | `libc.suprx` (166 KB), `libfios2.suprx` (103 KB), `libult.suprx` (59 KB, **never loaded**) |
| `volume.dat` | **397 MB, the main archive** (`FADEBABE`, 5,481 entries) |
| `RomImage/General/Common/Movie/` | `logo_acquire.mp4`, `logo_spike.mp4` |
| `RomImage/General/US/Movie/` | 4 story FMVs (opening, Maya 02/07/08), 150 MB |
| `RomImage/PSP2/US/Sound/StreamPack/` | 6 `FADEBABE` stream packs: BGM (148 MB), CutInVoice, EventBGM, EventVoice, LetterVoice, VoiceSE (203 MB) |
| `sce_sys/manual/` | the digital manual (PNGs) |
| DLC `addcont/PCSE00015/DLC001X000000000/` | `RomImage/DLC/DLCVersion000.txt` (32 bytes, a key string) and nothing else |
| `patch.dat` (1.02) | 3.7 MB `FADEBABE`, 35 entries (kinds 0/2/4/5), opened at boot after `volume.dat` |
| `RomImage/PSP2/US/Sound/StreamPack/StreamPackDLC.dat` (1.02) | 9.6 MB `FADEBABE`, 256 raw entries: the DLC missions' audio (**hypothesis**) |

The same 32-byte key string is the first member of `volume.dat`
(`DLC\DLCVersion000.txt`). **Hypothesis:** the game unlocks the DLC
missions when the add-on's copy matches its own, and the missions
themselves come with update 1.02. 1.02 does open
`addcont0:/DLC001X000000000/RomImage/DLC/DLCVersion000.txt` at boot, with no
error [local]; that the missions appear is still to be checked in play.

### The FADEBABE archive [local, partly verified]

Acquire's container (all big-endian):

* Header: `u32 0xFADEBABE, count, count, data_start, total_size`. For
  `volume.dat` that is 5,481 entries, data from `0x20800`, total
  `0x17A83000`.
* From `0x14`: 24-byte entries `{hash, offset, size, kind, end, name_len}`.
  Data is aligned to `0x800`; `end - offset` is the stored size.
  * StreamPack files: all `kind 0` (raw), hashes sorted, stored = size.
    **Verified** on `StreamPackBGM.dat`.
  * `volume.dat` kinds: 4 (3,566 entries), 2 (1,208), 0 (683), 5 (16) and
    3 (8). The hashes are sorted in 13 runs, not globally (**hypothesis:**
    one run per group).
* **Compression of kinds 2–5 is not zlib** (raw, zlib and gzip all fail).
  The streams look like an LZ variant with literal runs.
* **File names:** plaintext names (`General\Common\AI\ActionSet\Akame.ass`
  ...) are in the data region, but not at `end`. Where they sit is open.
* The engine reads the archive itself, so the port does not need this
  format. A reader is wanted for debugging and mods (plan Phase 2,
  `tools/fadebabe.py` is the probe so far).
* Content seen in names and strings: AI action sets (`.asc`/`.ass`),
  scripts (`Script/*.sol`, `*.sx`), PhyreEngine assets (`*.dae.GXM.phyre`,
  `*.cgfx.GXM.phyre`, `*.fgen.GXM.phyre` fonts), `Camera/Pack/*.lst`.

### The 1.00 eboot (`Ninja2PSP2_US`)

Decrypted and relocated by a run of the ss-delta fork with `--dump-elfs`
(see [02-baseline](02-baseline.md)).

| Fact | Value |
|---|---|
| ELF type | `0xFE00` (fixed address), ARM |
| Module | **`Ninja2PSP2_US`**, version 0x101, module NID **`0xA56EE5A6`** |
| Segment 0 (RX) | `0x81000000`, filesz `0x45FF94` (4.4 MB code + rodata) |
| Segment 1 (RW) | `0x81460000`, filesz `0xB1D4C`, memsz `0x57F7D4` (5.5 MB, mostly BSS) |
| TLS | 0x10 bytes |
| `module_start` | `0x811BF924` |
| exidx | `0x813D8DEC–0x813FAC9C`: **17,366 entries** (16,919 Thumb functions, 446 import stubs, 1 end marker) |
| Imports | **32 libraries, 468 functions, 13 variables**; 36 without a name in vita-headers (SceMp4 19, SceNearUtil 17) |
| Middleware | **PhyreEngine** (path macros `<P>/<NL>/...`, `PhyreShader/`, `CPhyreTexture2D`), **Havok** physics (licence key string `...Physics.Acquire_Shinobido_NGP`, `Havok-3.0.0`/`3.1.0` version strings) |

**Import surface:**

| Group | Libraries (functions) |
|---|---|
| Graphics | SceGxm (100), SceDisplay (3), SceDisplayUser (1) |
| Kernel / OS | SceLibKernel (42), SceThreadmgr (21), SceSysmem (4), SceIofilemgr (5), SceSysmodule (3), SceAppUtil (6), SceCpu (1) |
| C runtime (bundled `libc.suprx`) | SceLibc (63 + 6 vars), SceLibm (12), SceLibstdcxx (11 + 7 vars) |
| File I/O (bundled `libfios2.suprx`) | SceFios2 (17) |
| **Audio** | **SceNgs (27)**, SceAudio (4), SceAudiodecUser (4) |
| Video | SceMp4 (19, firmware `libscemp4` as LLE), SceVideodecUser (9), SceCodecEngineUser (4). **Not** SceAvPlayer, unlike ss-delta |
| Input | SceCtrl (2), SceTouch (4), SceIme (6). No SceMotion, no SceCamera |
| UI | SceCommonDialog (38) |
| Online, to stub | SceNet (22), SceNetCtl (7), SceHttp (2), SceSsl (2), SceNpManager (2), SceNpTrophy (8), SceNpUtility (2), **SceNearUtil (17)** |

There is no SceUlt, SceFiber, SceNetAdhoc*, SceNpMatching2 or SceAvPlayer.

### Update 1.02 [local]

`python -I third_party/recomp/tools/fetch-update.py PCSE00015 <dir>` reads Sony's update XML
(the path's HMAC-SHA256 of `np_PCSE00015` under the well-known key), lists
1.02 only (21,421,968 bytes) and downloads it. The XML's `sha1sum` covers
the pkg minus its last 32 bytes. Installed with the game's own zRIF
(`Vita3K.exe --pkg ... --zrif ...`); Vita3K merges a patch into
`ux0/app/PCSE00015` (`APP_VER 01.02`, `CATEGORY gp`, `PSP2_DISP_VER
01.610`). The 1.00 install is kept as `extracted/app-1.00-PCSE00015/`.

| Fact | 1.00 | 1.02 |
|---|---|---|
| Module NID | `0xA56EE5A6` | **`0xF4A4F7C3`** |
| Segment 0 (RX) filesz | `0x45FF94` | `0x4673E4` (+29 KB) |
| Segment 1 (RW) | `0x81460000`, filesz `0xB1D4C`, memsz `0x57F7D4` | `0x81468000`, filesz `0xB1EEC`, memsz `0x58ED14` |
| `module_start` | `0x811BF924` | `0x811C66B0` |
| exidx | `0x813D8DEC–0x813FAC9C`, 17,366 entries | `0x813DFC14–0x81401C8C`, **17,423** entries |
| Thumb functions / import stubs | 16,919 / 446 | 16,974 / 448 |
| Imports | 468 functions | 470: **+ `sceAppUtilDrmOpen`, `sceAppUtilDrmClose`** (both implemented in Vita3K) |
| libc, libfios2 | | the `.suprx` files differ (re-signed), the decrypted ELFs are **byte-identical** to 1.00 |
| New files | | `patch.dat`, `StreamPackDLC.dat`; `volume.dat` unchanged |

Probes on 1.02 (same tools as below; `imix` needs `EXIDX 0x813dfc14`):

* imix: 1,375,874 instructions, 100% Thumb (the same one ARM function),
  FP/SIMD 186,738 (13.6%), NEON 73,426, `blx reg` 17,165, jump tables 453,
  `mrc` 902, IT 428, `bkpt` 40.
* inventory: 1,344,095 instructions decoded, **0 unreached bytes**, 453
  jump tables (none leaving their function), 17,202 indirect branches,
  10,934 address-taken functions, 0 tail calls.
* recompiler: **16,972 functions, 0 unsupported**, 2 untranslatable (as in
  1.00), 1,099,908 dead flag writes dropped, 81,587 resume points, 62
  buckets, 211 MB of C++ in 48 s. Code hash **`0116ae436dadcb24`**.

The tables below are for 1.00 and stay as the record of the dump; 1.02
differs from them by the amounts above.

### Instruction mix [local]

Linear Capstone sweep of every exidx function (`imix.py` from ss-delta,
with this ELF's segment offset and exidx address):

| Metric | Shinobido 2 1.00 | Soul Sacrifice Delta 1.30 [ssd] |
|---|---|---|
| Instructions | **1,366,261** | 3,799,876 |
| Thumb share | 100.00% (one 18-instruction ARM function) | 99.85% |
| Functions | 16,919 | 34,636 |
| FP/SIMD | 185,667 (**13.6%**) | 671,377 (17.7%) |
| NEON (rough) | 73,019 | ~243,600 |
| `vrecpe`/`vrsqrte` family | 2,901 | 11,777 |
| `blx reg` | 17,156 | 41,486 |
| `tbb`/`tbh` | 447 | 1,336 |
| `ldrex`/`strex` family | 374 | 1,578 |
| `mrc` | **902** | 74 |
| `IT` blocks | 426 | ~2,500 |
| `bkpt` | 40 | 146 |

`mrc` is twelve times as common as in ss-delta. **Hypothesis:** TLS reads
(TPIDRURO) in hot code, e.g. a PhyreEngine per-thread context. The
recompiler already handles them.

### Inventory [local]

`tools/inventory.py` from ss-delta, unchanged, 10 s:

* 16,919 code functions (Thumb), 446 import stubs; 1,334,705 instructions
  decoded; **0 unreached bytes**;
* 447 jump tables, none with targets outside their function;
* 17,193 indirect branches (8,650 + 8,543 `blx reg`), 10,931
  address-taken functions;
* 0 tail calls, 1 no-return call, 12 orphan code roots (decoded but not
  reached from a root);
* 3 mid-function Thumb pointers in data.

### Recompiler probe [local]

`recomp/recompile.py` from ss-delta, unchanged:

| Module | Functions | Instructions | Unsupported | Left to fallback | Buckets |
|---|---|---|---|---|---|
| eboot | 16,917 | 1,334,460 | 0 | 2 ("untranslatable") | 61 (209 MB C++) |
| libc | 1,190 | 66,006 | 0 | 0 | 3 |
| libfios2 | 522 | 38,614 | 0 | 0 | 2 |
| libSceFt2 | 772 | 90,197 | 0 | 0 | — |
| libpvf | 101 | 19,196 | **2 in 2 functions** | — | — |
| libscemp4 | 274 | 22,027 | 0 | 0 | — |
| sysmodule | 19 | 1,286 | 0 | 0 | — |

* 1,091,572 dead flag writes dropped; 81,079 resume points.
* The firmware modules are the same 3.74 binaries ss-delta recompiled, but
  they load at other addresses here. They must be generated for these
  addresses (ss-delta D8). libpvf's 2 unsupported forms didn't occur at
  ss-delta's address; to be checked (Phase 2).
* Load addresses in our run: bootimage `0x80013000`, sysmodule
  `0x8031E000`, libc `0x80323000`, libfios2 `0x80362000`, libSceFt2
  `0x80384000`, libpvf `0x803D5000`, libscemp4 `0x805B4000` (loaded three
  times, for each movie). `adhoc_matching` appears in the dumps only
  because ss-delta's `--dump-elfs` loads it; this game never does.

## Prior work [web]

Collected 2026-10-12.

### Versions and regions

| Region | Title ID | Latest | Notes |
|---|---|---|---|
| US | **PCSE00015** | **1.02** (21.4 MB, needs FW 3.57) | our dump is 1.00 |
| EU | PCSB00049 | 1.02 | |
| JP | PCSG00019 | 1.02 | 忍道2 散華 |
| Asia | PCSH00001 | 1.01 | never got 1.02 |

* Sony's update XML for PCSE00015 lists 1.02 as `alive`; a HEAD request on
  the pkg returned 200 (2026-10-12). Also in NoPayStation's
  `PSV_UPDATES.tsv`.
* US/EU 1.02 change notes
  ([changeinfo.xml](http://gs.ww.np.dl.playstation.net/ppkg/np/PCSE00015/PCSE00015_T2/0102/073a981b26463e17/changeinfo.xml)):
  DLC compatibility, Network Jar item counts, **"Added downloadable
  content missions"**, manual typo. JP 1.02 also fixes some events, sound,
  mission issuing and letter history.
* One DLC per region (Mirror Spirits / 鏡の化身, additional missions).
* Demos exist (US PCSE00076), not relevant.
* Release: JP 2011-12-17 (Vita launch), NA 2012-02-21, EU 2012-02-22.
  Developer Acquire; publisher Spike (JP), Namco Bandai (West). Delisted
  from PS Store in the West in 2016.

### Vita3K compatibility

| Issue | Version | Status | Notes |
|---|---|---|---|
| [compat #173](https://github.com/Vita3K/compatibility/issues/173) | US PCSE00015 | Playable | 2023 (build 3353, Vulkan, 1.00, 1080p): "completely playable" but **sword-slash and footstep SFX die after 2–3 missions**, voices and BGM continue; subtitles sometimes stick after skipping a cutscene. June 2026 (build 4056, Linux, RX 6600): "still exists" |
| [compat #1193](https://github.com/Vita3K/compatibility/issues/1193) | Asia PCSH00001 | Ingame | green band in the opening FMV (fixed by May 2026); **sounds stop over time, faster when sprinting over corpses** |
| [compat #2237](https://github.com/Vita3K/compatibility/issues/2237) | EU PCSB00049 | Playable | 2025 report: SFX vanish |
| [compat #217](https://github.com/Vita3K/compatibility/issues/217) | JP PCSG00019 | Playable | |
| [Vita3K #3896](https://github.com/Vita3K/Vita3K/issues/3896) | Android | closed | "SFX lost after ~30 min", no root cause |

No FPS figures reported. Every report is on Vulkan.

### Patches, mods, tools

* VitaGrafix has **no entry** for any region (the full patchlist was
  checked). No 60 fps patch, no cheats, no format work, no decomp or recomp.
* Related only by series: ShinobidoCustomMissionsPS2toPSP (Shinobido 1).

### Input and online [web]

* Front touch: e.g. the "Caution Icon" lock-on
  ([PS Blog](https://blog.playstation.com/?p=62724)).
* **Rear touch:** grappling-hook aiming
  ([Engadget](https://www.engadget.com/2012-02-16-snapshot-shinobido-2-revenge-of-zen-vita.html))
  and a first-person aim mode. No gyro, camera or AR reported.
* Single-player. Near item exchange through the Network Jar (交信壺); Near's
  servers are reduced or gone, so the port answers "no gifts" offline.

## How this game differs from Soul Sacrifice Delta

| | Soul Sacrifice Delta [ssd] | Shinobido 2 |
|---|---|---|
| Dump | NoNpDrm zip, 1.30 merged | PSN pkg + `work.bin`; 1.00 (1.02 separate) |
| Code | 3.8 M instructions, 34.6 k functions | 1.37 M, 16.9 k |
| Bundled modules run | libc, libfios2, **libult** (fibers) | libc, libfios2; libult shipped but unused |
| Firmware LLE | sysmodule, Ft2, pvf, mp4, **avplayer**, (adhoc matching) | sysmodule, Ft2, pvf, mp4 |
| Engine | in-house Marvelous engine, Havok 2013 | **PhyreEngine**, Havok |
| Audio | SceAudio + Audiodec, game's own mixer | **SceNgs** (Vita3K incomplete) |
| Video | SceAvPlayer | SceMp4 + SceVideodec |
| Touch | front only, one action (Black Rite) | front **and rear** (aiming) |
| Multiplayer | ad hoc (4 players) | none |
| Known Vita3K bugs | rendering (surface sync, Mind's Eye, AMD crash) | **SFX dropout**, subtitles sticking |
| Debug features | `BootSequence` debug menu in `config.ini` | none found yet |

## In-game facts [local]

Seen in the 1.02 runs (2026-10-13):

* **Options** (title → New Game → Options, and the pause menu): Music
  Volume (default 50), SFX Volume (100), Bloodshed, Y/X-axis camera,
  **Rear Touch Pad Control: Wide / Standard / Off**, Subtitles. Saving
  asks "Save these options?". Rear touch can be switched off by the
  player, so a PC mapping only has to cover what it does when on.
* **Difficulty:** Easy / Normal / Hard.
* **Controls** (pause → Controls): left stick move, right stick camera,
  Square normal attack, Triangle Chimatsuri Sappo (stealth kill) / pick up
  / carry, Circle dash / sheathe / draw, Cross jump, L focus / guard, R
  crouch / cling to wall, d-pad use tool, Select item management, Start
  pause. A "caution" eye sits at the right edge of the screen in the
  field, one per nearby enemy; touching it turns the camera to that enemy.
* **Tutorial:** movement (move, jump, crouch, dash, reach a point), then
  "Execute Chimatsuri Sappo". The pause menu has Restart Training,
  Training Details, Status, Controls, Options, Quit.

## Vita3K's NGS and this game (code reading, 2026-10-13)

From the fork's sources (`vita3k/modules/SceNgsUser/SceNgs.cpp`,
`vita3k/ngs/src/scheduler.cpp`, `player.cpp`, `atrac9.cpp`). Phase 5 has
to confirm all of it in a run.

* Of the game's 27 SceNgs imports, all are implemented except
  `sceNgsModuleGetPreset`, which returns success without writing the
  preset. The DSP of the envelope, reverb, EQ, mixer, generator,
  distortion and compressor modules does nothing.
* **The missing envelope can't hold voices** (this drops the earlier
  hypothesis). `sceNgsVoiceKeyOff` ends the voice inside the call (no
  release phase), and a module's `process()` can only end a voice, never
  keep it. The game imports no voice-info or finished-callback function.
  Side effects: key-off cuts sounds without a release tail; envelope state
  reads back as zeros.
* Ways voices could still be lost, all **hypotheses**:
  1. **Stale pause flag:** pausing an *available* voice sets `is_paused`,
     which kill and key-off don't clear. The next play makes it active but
     never queues it: silent, no callback, and later plays fail. Play
     errors are logged only once.
  2. **End-of-data race:** while the END_OF_DATA callback runs (locks
     released), the voice is still active, so a re-play from the callback
     or another thread fails. The exports also change voice state without
     the scheduler lock.
  3. **SFX buss voice drops out of the queue** (paused, killed or a failed
     re-play): every SFX goes silent at once while BGM and voices continue,
     which matches the reports.
  4. The game's own "voice done" test reads state that Vita3K fills
     differently (the player's `current_buffer` reset after the end,
     envelope state all zeros). **Now the leading lead**: the game's
     voice manager frees a stopped voice only on the envelope's state
     ([Game knowledge](#game-knowledge-phase-2-2026-10-13), Sound).
* What to log (needs instrumentation in the fork, Phase 5): every play,
  key-off, kill, pause, resume and GetStateData with voice, caller and
  result (every error, not once); module callbacks; per rack, every few
  seconds, voices active+queued, active+paused and available, and whether
  each buss voice is queued.

## Game knowledge (Phase 2, 2026-10-13)

From the 1.02 eboot with `tools/xref.py` (disassembly with import and
callee names, the strings and data a function builds, callers) over the
inventory. Addresses are the eboot's (1.02, loaded at `0x81000000`).

**Coverage.** The inventory classifies all 17,423 exidx entries (16,974
Thumb functions, 448 import stubs, 1 end marker) with 0 unreached bytes and
every indirect branch listed; libc (1,233 entries, 81 C++ landing pads) and
libfios2 (603) likewise. The recompiler leaves 2 eboot functions to the
fallback CPU, both for half-precision conversions it doesn't translate yet:
`0x811dc974` (10 × `vcvtb.f16.f32`) and `0x8134d0f8` (`vcvt.f32.f16 q0, d0`,
NEON). Those two forms are needed before Phase 4 (no JIT). libpvf's 2
"unsupported" forms (`stc`, `svc #0x46`) are data decoded as code after a
no-return call: traps never reached.

**Main loop and frame pacing.**
* `main` = `0x81000016`. It defaults the display to 960×544, takes a
  `-width=N` argument (height = N × 544/960, rounded), creates the
  application (`0x81148d20`), sets its **frame rate to 30**
  (`movs r0, #0x1e` at `0x810000d4`; `str r0, [app, #8]`; PhyreEngine's
  root constructor `0x8114a22c` defaults it to 60), then calls init and
  run through the vtable (`0x81449f10`; base class `0x81449fa8`).
* The run loop `0x8114d024` (vtable slot 4): period = 1 / `[app+8]`; it
  waits on `sceDisplayWaitVblankStartCB` until the period has passed and at
  least `60 / [app+8]` vblanks (`0x813168a8`, an unsigned divide) since the
  last frame, then runs one frame through the vtable. **One value,
  `[app+8]`, sets both the period and the vblank minimum**: the 60 fps
  study (Phase 7) starts there. Time base: `0x811cb902` (a double, minus
  the start time at `0x819b5b30`).
* Display: GXM display-queue callback `0x8114d28e` (`sceGxmPadHeartbeat`,
  `sceGxmDisplayQueueAddEntry`; 3 frame buffers, index at `+0xf8` of
  `*0x8146c2c0`); the flip callback `0x8114d250` sets the frame buffer and
  waits one vblank.

**Render targets.** The GXM setup `0x8114c906` creates the only render
target the game uses in play: **960×544** (height hard-coded; width from
init), 1 scene per frame, no MSAA, with one 960×544 colour surface (stride
1024). A run from boot into a mission field logged no other target or
surface (fork log lines `Render target`/`Color surface`). So the 3D draws
at the full native resolution in a single pass, and Vita3K's resolution
multiplier scales all of it (unlike Soul Sacrifice's 720×408 3D).
PhyreEngine's generic render-to-texture path (`0x811e0302`, `0x811e09a2`,
`0x811e3bb4`) exists but did not run there.

**Touch.** PhyreEngine's input update `0x811c4db6` reads the front panel
(port 0) when bit 0 of `[input+0x8ac]` is set and the rear panel (port 1)
when bit 1 is, up to 6 samples each (`sceTouchRead` at `0x811c4dee` and
`0x811c4ee6`), into buffers at `+0x1a0` and `+0x4ec`; setup in
`0x811c4b74` (panel info, sampling on). What the grappling hook does with
rear touches (point, drag or hold) is still to be seen at run time
(Phase 7).

**Sound (Acquire's `CAcqSound`: a stream thread and a mix thread).** All
NGS calls are in `0x8122b522`–`0x8122e8xx`:
* `0x8122b5bc` sets up the racks: ATRAC9 voices, a Template1 (normal
  player) voice, and master, mixer, reverb and compressor busses.
* Play: `0x8122dcfc`, `0x8122df4c`, `0x8122e174` (each Kill, set a module
  callback, Play). Stop: key-off in `0x8122ded0`, `0x8122e392`,
  `0x8122e460`. Pause/resume: `0x8122e528`/`0x8122e570`,
  `0x8122e5b8`/`0x8122e600`.
* The per-frame update `0x8122d870` (before `sceNgsSystemUpdate` and
  `sceAudioOutOutput`) keeps voices in 28-byte slots (table at
  `[mgr+0xf0]`: in use `+0xc`, owner `+0x10`, playing `+0x14`, timeout
  `+0x18`). For each voice on its **stopping list** it reads
  `sceNgsVoiceGetStateData(voice, 4, buf, 0x14)`, and only when
  `buf+0x10 == 1` and the level `buf+0` is 0 does it kill the voice and
  free the slot. **Module 4 is the envelope** in both voice types the game
  uses (ATRAC9 and the normal player, in Vita3K's definitions too).
  Vita3K's envelope has no state, so this reads zeros: a stopped voice is
  **never freed**, and once the pool is used up new sound effects can't
  start. **Hypothesis**, the leading one for the SFX dropout, to prove in
  Phase 5 by tracing the slots and stopping list.

**DLC.** Per the Japanese release notes ([famitsu](https://www.famitsu.com/news/201203/09011325.html),
[gamer.ne.jp](https://www.gamer.ne.jp/news/201203090043/)), the Mirror
Spirits missions (鏡の化身) are issued only in a save that has reached an
ending: that explains their absence on the board in Phase 0.
`0x8114a156` mounts the add-on (`sceAppUtilDrmOpen
("DLC001X000000000")`), reads 32 bytes of `RomImage/DLC/DLCVersion000.txt`
and compares them with a key string in the eboot (`0x8140abe8`); a match
sets the flag at `[obj+0x2b0]`. The installed add-on holds that key, so
the unlock succeeds; the missions' timing in the story is still unchecked.

**Caution eyes** (the lock-on icons on the right). One eye per nearby
enemy, stacked down the right edge (centres at x = 896 of 960, the first
at y = 258); touching one turns the camera to that enemy. The iris shows
the enemy's state (owner, 2026-10-14): white not engaged, yellow spotted,
red in combat, purple cautious; eyes of different colours can be stacked
together. The frame around the iris (silver wings, rim, pupil) is the same
in every state. The HUD manager (`*0x8146c308`) keeps its widgets in a
vector at `+0x10`. A static reading took widget id 4 for the eye stack
(count `[+0x4c]`, elements at `[+0x2c + 4i]`, touch test `0x8115849e` →
`0x8115f51c` → `0x8115dc1e`, lock-on `0x811587f6`), but at run time,
with eyes on screen, its count stayed 0 and its element positions 0, 0:
widget 4 is not the eye stack (**hypothesis**: the on-target cursors).
The touch binding therefore finds the eyes in the picture
([Caution binding](02-baseline.md#caution-binding)).

**Sound effects** (static reading of the 1.02 eboot, 2026-10-14, checked
at run time where noted). The racks (`0x8122b5bc`) hold Template1 and
ATRAC9 voices and reverb, mixer, two compressor and master busses; a
voice's output 0 goes to the mixer, output 1 to the reverb buss, then
compressor A, B and master. The reverb buss is filled only by
`sceNgsModuleGetPreset(sys, 0x5ce7, 0, info)` at `0x8122c17c`, where
`info` is the `SceNgsBufferInfo` that `sceNgsVoiceLockParams` filled
(not the parameters themselves). The send levels come from each sound's
object (`[obj+0x18]`, `[obj+0x1c]`, applied by `0x8122dc32` from
`0x8122fbca`); at run time every output-1 send was set to 0 in the
title, the hub and mission 1 (~400 settings). Stops with a fade
(`0x8122ded0`, `0x8122e392`) write the envelope's `uReleaseMsecs`
(params `+0x38`) and key off; none came in six mission-1 restarts of
combat. The EQ (`0x8122b522`) is un-bypassed with all four filters off,
so it changes nothing.

**Frame rate** (static reading, 2026-10-14; behaviour checked at 60).
The application (pointer at `0x8146c2b0`) is constructed with a frame
rate of 60 at `[app+8]`; `main` sets 30 (`0x810000d4`). The run loop
`0x8114d024` reads it once on entry for both the period and the minimum
vblanks and keeps them in registers, so it can't change per screen. It
stores the vcount at `[app+0x1d8]` on entry (zero before). The time module
`0x81054b6e` stores the step every update uses at `0x81468978`: the mean
of the last 8 frame times capped at `[0x81468998]`, or in fixed mode
(`[0x81538370] != 0`, set by `0x81054ee8`) `[0x81468998]` itself. App init
`0x8114a778` and some scene changes select fixed steps of 1/30 s. HUD and
menu animations (`0x8114e8ce`, ~40 widgets) and the results screen's
timers (`0x811773c2`) step by a literal 1/30.

**Scripted scenes** (memory dumps during a mission's opening scene and in
play, 2026-10-14; code read after). The script controller's scene start
(`0x81102c70`) calls `0x81104428`, which freezes the player and sets
`[0x815399f8]` (bit 1; 2 in the dumps); the scene end (`0x8110291e`) calls
`0x8110473c`, which restores the player and clears it (0 in the hub and in
play). `[0x8146acd8]` holds the scene's music track (-1 for none) and
`[0x8146acdc]` is set while a scene has lowered the music (`0x81110da6`
clears both at the start, `0x81110e38` at the end). The fixed step is not
a scene marker: it stayed on through a scene and the play after it
(save 56's mission), and scene starts only call the setter again. Some
scenes advance per frame apart from the step (**hypothesis**: the two
that ran at twice the speed at 60, below).

**Network Jar (Near).** All 17 SceNearUtil calls are in one function,
`0x811bc526` (the "near_sub_thr" thread); Vita3K serves them as stubs.

**Saves.** No save of this game is shared online (searched 2026-10-14:
English and Japanese sites, GameFAQs, Apollo). The Apollo save patches
for PCSE00015 ([bucanero](https://bucanero.github.io/apollo-patches/PSV/PCSE00015.html))
give offsets in `data0000.bin` for money (`0x1434`), level (`0x1444`), SP,
stamina, offence, defence and tool counts, but nothing for story
progress. New Game+ keeps level, items, money and techniques
([wiki FAQ](https://wikiwiki.jp/shinobido2/%E3%82%88%E3%81%8F%E3%81%82%E3%82%8B%E8%B3%AA%E5%95%8F)).

**No debug menu.** No developer menu, stage select or boot option is left:
the "mission select" strings are the normal board's labels and
"DebugPrint" a script command. Late-game tests need saves (risk R9).

## Open questions

1. ~~Does update 1.02 change the eboot much?~~ No: +55 functions, two new
   imports, same recompiler result ([Update 1.02](#update-102-local)).
2. What causes the SFX dropout? Not the envelope holding voices in
   Vita3K, but the game waiting for the envelope's state before freeing a
   stopped voice ([Game knowledge](#game-knowledge-phase-2-2026-10-13),
   Sound). **Confirmed and fixed in Phase 5** (fork `fe8659d0`).
   Reproduced ([02-baseline](02-baseline.md#audio-baseline-the-sfx-dropout-reproduced-2026-10-13)):
   it came at a mission load, not during combat, which points at
   something done per load (the SFX buss or rack set up again, voices
   paused or killed at unload; **hypothesis**).
3. What does the grappling hook do with rear touches? Ports and buffers
   are known (Phase 2); the gesture is for Phase 7.
4. ~~The 3D's internal resolution?~~ The full 960×544 (Phase 2).
5. Does game logic step by the measured frame time? The loop's rate is one
   value (`[app+8]`, Phase 2); the logic's time step is for Phase 7.
6. ~~A debug menu?~~ None (Phase 2).
7. FADEBABE compression and the name table (Phase 2, for tools only).
8. ~~The 2 "untranslatable" functions and libpvf's 2 forms?~~
   Half-precision conversions to add to the recompiler; libpvf's are
   unreached data (Phase 2).

## Workspace state

All of this is outside git ([D2](decisions.md)).

| Path | What |
|---|---|
| `rom/Shinobido 2 Revenge of Zen.rar` | input, read-only |
| `extracted/pkg/` | the rar unpacked: the two pkgs and their `work.bin` |
| `extracted/vita3k/` | portable Vita3K (the upstream release ss-delta uses), `pref-path` = `fs/`, firmware 3.74, game and DLC installed |
| `extracted/update-1.02/` | the 1.02 patch pkg from Sony's update server, and its install log |
| `extracted/app-1.00-PCSE00015/` | copy of the 1.00 install, before 1.02 was merged over it |
| `extracted/elf/` | decrypted, relocated ELFs of **1.02**: `eboot.elf`, `libc.elf`, `libfios2.elf`, `firmware/*.elf` |
| `extracted/elf-1.00/` | the same for 1.00 |
| `build/ssd-shim/` | Phase 0 stopgap: a copy of ss-delta's `ss-delta.exe` (JIT only, its own `ss-delta.ini`) |
| `build/shimfs/` | junctions over `extracted/vita3k/fs/`, with `ux0/app/PCSA00152` → our `PCSE00015`, so the shim boots this game |
| `generated/inventory/eboot/` | inventory CSVs |
| `generated/{eboot,libc,libfios2,fw_*}/` | probe output of the recompiler (eboot: 1.02; `eboot-1.00/` kept) |
| `build/probe-1.02/` | velf/imix output for both eboots |
