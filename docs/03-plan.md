# 03 — Plan

Same rules as ss-delta. Every phase has an **exit criterion**, and a phase
is done when that criterion is met, not when its tasks are ticked.

Sizes are relative effort: S = a session or two, M = several sessions,
L = many sessions. For scale, ss-delta went from Phase 0 to a playable
native port in four days, and this game reuses all of that work.

Status key: ☐ not started · ◐ in progress · ☑ done

The approach is ss-delta's ([D1](decisions.md)), and the toolchain is
shared with it ([D4](decisions.md)):

* recompile the game's Thumb-2 code to C++ ahead of time with ss-delta's
  recompiler;
* run it in ss-delta's Vita3K fork, which supplies the HLE, GXM, the
  renderer and the shader translator;
* end on NativeCPU, with no JIT, in a single-game executable.

The work that is new compared with ss-delta is **audio (NGS)**, **rear
touch** and the **pkg install path**.

---

## Phase 0 — Workspace, decryption, baseline (S) ☑

* ☑ Research snapshot ([01-research](01-research.md)): imports,
  instruction mix, inventory and a recompiler probe of 1.00; prior work;
  Vita3K's known bugs.
* ☑ PSN pkg + `work.bin` installed into a portable Vita3K (`--pkg/--zrif`,
  `third_party/recomp/tools/mkzrif.py`); DLC installed; firmware 3.74.
* ☑ ELFs decrypted and relocated via a dump run of the ss-delta fork
  ([D5](decisions.md) shim).
* ☑ Baseline ([02-baseline](02-baseline.md)): logos, FMV, title, menus,
  New Game and the tutorial field at 30 fps on the JIT, rendered correctly.
* ☑ **Update 1.02** ([D3](decisions.md)): fetched (`third_party/recomp/tools/fetch-update.py`)
  and installed; ELFs dumped; `velf`/`imix`/inventory/recompile probe
  re-run (16,972 functions, 0 unsupported); hashes recorded; boots to the
  first in-engine cutscene at 30 fps, and the add-on is found at boot.
* ◐ DLC: the add-on is found at boot, but its missions didn't appear on
  the board up to day 4. Moved to Phase 7's DLC item: it needs play
  further into the story, or Phase 2's look at the DLC check in the code.
* ☑ Repository: branch `main`, first commit `393f883` (docs and tools
  only). The commit identity is the owner's GitHub no-reply address
  ([D6](decisions.md)), set in this repo's local git config.
* ☑ Audio baseline ([02-baseline](02-baseline.md#audio-baseline-the-sfx-dropout-reproduced-2026-10-13)):
  dropout reproduced. Sound effects went silent at the 6th mission load of
  a session (95 min in), and stayed silent through new missions and a
  reload. Dialogue still played, and a new process brought them back. 30
  min of constant combat before that didn't trigger it. The log shows
  nothing at that moment. Tools: `third_party/recomp/tools/proccap` (per-process recording),
  `third_party/recomp/tools/wavstats.py`.
* ☑ Cross-check against upstream Vita3K on this machine
  ([02-baseline](02-baseline.md#upstream-vita3k-on-this-machine-2026-10-13)):
  OpenGL and Vulkan both boot, load a save and render a mission correctly
  at 30 fps. Unlike with Soul Sacrifice, upstream Vulkan doesn't crash
  here.
* → The RTX 4090 run moves to Phase 6's AMD/NVIDIA item. It needs the
  owner's other PC, and ss-delta's package flow is generalised in Phase 1.

**Exit:** the 1.02 game boots to gameplay in our fork, with ELFs, hashes,
the measurements and a recorded SFX-dropout repro. **Met** (2026-10-13).

## Phase 1 — Shared repos, fork branch and front end (M) ◐

Steps marked **(ss-delta)** change `<ss-delta>`; the owner OKed Phase 1
(2026-10-13). The hub repos are in `<git>\` until publishing (D4, D6).

* ☑ **Recompiler repo** `vita-recomp` (D4 item 2), extracted from a copy
  of ss-delta's history (`git filter-repo`; ss-delta itself untouched):
  `recomp/` and the game-agnostic tools, plus this project's `mkzrif.py`,
  `fetch-update.py`, `proccap`, `wavstats.py`. `GENERATED_DIR`,
  `VITA3K_SRC`/`VITA3K_BUILD` and the DLL prefix (`RECOMP_DLL_PREFIX`,
  default `ssd_aot_`) are parameters; `imix.py` reads the segment and
  exidx from the ELF; `v3kdrive.py` picks the front end in the folder.
  Checked: the 1.02 eboot recompiles to the same code hash
  (`0116ae436dadcb24`), `imix` matches the hand-patched copy for this
  game and the old one for SSD, and CMake with ss-delta's paths gives the
  same `build.ninja`. Not yet run: the dynarmic suites on both games
  (Phase 3).
* ◐ **Submodules**: this repo has `third_party/vita3k` and
  `third_party/recomp`. ss-delta's switch is still to do **(ss-delta)**.
* ☑ **Fork**: branch `shinobido-2` from `4704fc6c`, built here in 12 min
  (`build/vita3k`).
* ◐ **Scripts in Python** in `vita-recomp/tools`: `build-vita3k.py`
  (MSVC found with vswhere), `install-game.py`, `make-dist.py`, read from
  the project's `game.json`. ss-delta's map sweep and RTX 4090 package
  stay PowerShell until ss-delta switches.
* ☑ **Front end generalised** (fork `4a2d068c`): `vita3k/game-frontend/`
  (the shared frontend, a library; `Profile` with hooks) and
  `vita3k/games/<id>/` (one small exe per game). Everything particular to
  Soul Sacrifice is in its profile: frame-rate control, `boot_config.ini`
  and the depth-UV fix, the add-on unlock, save import/export, Ad Hoc
  Play and the `adhoc_matching` dump preload. The settings file is
  declared as data (`IniLayout`/`SettingSpec`); `ss-delta.ini`'s default
  text is byte-identical to before. `shinobido2.exe` has the shared
  settings only. Its saves layout and import come with Phase 7.
* ☑ **Install path for PSN pkgs**: `--install <pkg> --license
  <work.bin|rif>` (or `--zrif`); the patch uses the game's installed
  licence. `install-game.py` installed firmware, game, 1.02 and the DLC
  into a fresh `dist/shinobido2-test/` in 18 s, and checked the eboot is
  1.02.
* ☑ `--dump-elfs` loads only what the game loads: `shinobido2.exe`'s dump
  is byte-identical to the shim's, without `adhoc_matching`.
* ☑ Tools take a game: `v3kdrive.py` (auto-detects `shinobido2.exe`),
  `install-game.py`/`make-dist.py` (`game.json`). New front-end flag
  `--write-ini <file>` replaces ss-delta's `ssdelta_ini.py`.
* ☑ **D5 shim retired**: `dist/shinobido2-test/shinobido2.exe` loaded the
  `hub-day1` save and played a mission at 30 fps (moved, swung), driven
  by the shared `v3kdrive.py`.
* ◐ ss-delta on the new front end: `ss-delta.exe` from this build, with
  ss-delta's recompiled modules, booted to the title, loaded a save into
  the hub on NativeCPU (all 10 modules placed where expected), 57 fps at
  scale 2, its hooks active (add-ons, `boot_config`, 60 fps). Run on a
  junction file system with a copy of the saves, so the owner's weren't
  touched. A quest (loading screen at 60) is still to check.
* ☐ ss-delta switches to the submodules and the Python scripts, its docs
  follow **(ss-delta)**.
* ☐ Merge `shinobido-2` into one integration branch that builds both exes
  **(ss-delta)**.

**Exit:** a fresh clone of this repo with `--recurse-submodules` builds
`shinobido2.exe`, which installs the game from the owner's pkg files, boots
1.02 on the JIT to gameplay at 30 fps, and is driven by `v3kdrive.py`.
ss-delta still builds and plays (title → a quest), so the shared changes
broke nothing.

## Phase 2 — Inventory and game knowledge (S) ☐

* ☐ Inventory of 1.02's eboot, libc and libfios2 (`tools/inventory.py`):
  every indirect branch resolved or listed.
* ☐ Explain the 2 "untranslatable" eboot functions and libpvf's 2
  unsupported forms at this load address.
* ☐ Locate:
  * the main loop and frame pacing (vblank wait, frame timer) for the 60 fps
    study;
  * the render-target creation sites (internal 3D resolution);
  * the NGS voice manager (how the game allocates and frees voices);
  * the `SceTouch` call sites (front/rear, which regions);
  * the DLC check (`DLCVersion000.txt`);
  * the Near / Network Jar calls.
* ☐ A debug or mission-select entry point for testing, if one is left in
  the retail eboot. Otherwise, a test save per chapter.
* ☐ `tools/fadebabe.py`: list and extract `volume.dat` and the StreamPacks
  (names, kinds 2–5 decompression). This is for debugging and mods; the
  port doesn't need it.

**Exit:** 100% of exidx entries classified; the frame loop, render targets,
NGS use and touch sites have addresses in 01-research.

## Phase 3 — Native code in the fork (M) ☐

ss-delta's Phases 3–5 at once, since the recompiler already covers every
form.

* ☐ Generate eboot, libc and libfios2 for their load addresses
  (`--load-base`, ss-delta D8) and build `*_aot_<module>.dll` (61 + 5
  buckets, ~210 MB of C++).
* ☐ The dynarmic comparison suites (`recomp/run-tests.ps1`) for this game's
  modules: every form, plus whole leaf functions. 0 failing.
* ☐ Run with the JIT as fallback: counters (`SSD_AOT_COUNT`), then the
  differential mode (`SSD_AOT_DIFF`) through title, tutorial and a mission.
* ☐ Check Havok physics native against JIT (ss-delta R1), as ss-delta did
  in its boss-fight timing.

**Exit:** a full mission with **0 JIT instructions** in the eboot, libc and
libfios2, and a clean differential log.

## Phase 4 — Standalone, no JIT (S) ☐

* ☐ Firmware modules recompiled from this install's dumps at this game's
  addresses: sysmodule, libSceFt2, libpvf, libscemp4 (ss-delta D11).
* ☐ NativeCPU by default; a build without dynarmic.
* ☐ The install flow end to end from the owner's pkg files and PUPs into
  `dist/<name>/`.
* ☐ Offline stubs checked: NP, trophies, HTTP/SSL, Near (Network Jar
  reports no gifts), CommonDialog network checks.

**Exit:** `shinobido2.exe` built without dynarmic, installed from the
owner's pkg, plays the tutorial and the first mission at 30 fps with 0 JIT
instructions.

## Phase 5 — Audio: NGS (M–L) ☐

The one known blocking bug. It is Vita3K's, so the fix is upstreamable.

* ☐ Reproduce the SFX dropout deterministically. Start from Phase 0's
  repro: the `hub-day1` save, then *Restart Mission* every ~90 s; it
  died at about the 6th mission load. Count the loads it takes, and check
  whether loads alone (no combat) are enough.
* ☐ Trace NGS: voices created, played, released and their states over time.
  Find what leaks. The code reading
  ([01-research](01-research.md#vita3ks-ngs-and-this-game-code-reading-2026-10-13))
  rules out the envelope holding voices and ranks a stale pause flag, an
  end-of-data race, the SFX buss leaving the queue, and a game-side wait on
  state Vita3K fills differently. The log list is there too.
* ☐ Fix the cause, then implement what the game uses that Vita3K lacks,
  for sound quality: the **envelope** (attack/release instead of hard
  cuts), **reverb**, **equalizer**, and `sceNgsModuleGetPreset`.
* ☐ Compare against a Vita (a recording by the owner) for envelopes and
  reverb in a few known scenes.

**Exit:** a long session (several missions, or an hour of combat) with no
SFX loss; envelope, reverb and EQ audible and plausible against hardware.

## Phase 6 — Rendering correctness (M) ☐

* ☐ Sweep every mission area and the castle/hub screens (ss-delta's
  `map-sweep.ps1` pattern, through saves or a mission select).
* ☐ Cutscenes and FMV: the four story movies, subtitles, and the "subtitles
  stick after skipping a cutscene" report.
* ☐ Effects: blood, smoke, water, night lighting.
* ☐ AMD and NVIDIA (ss-delta's two-reference rule, its D4 update 2). The
  fork's NVIDIA fixes come along, among them the USSE min/max NaN rule
  (patch 0039) behind SSD's white floor. PhyreEngine's fog and lighting
  may hit the same NaN path, so NVIDIA is checked early, not last.

**Exit:** a visual sweep of all areas and cutscenes with no known
rendering bugs.

## Phase 7 — PC features (M) ☐

* ☐ **Internal resolution**: Vita3K's multiplier; first find the game's own
  3D resolution (Phase 2) and check depth-reading effects at scale 2.
* ☐ **Input**:
  * keyboard and gamepad bindings;
  * **rear touch**: map grappling-hook aiming and first-person aim to the
    right stick or the mouse. This depends on what Phase 2 finds the game
    reads: an absolute point, a drag, or a hold;
  * front touch: the caution-icon lock-on and any menu touches, as keys
    (ss-delta's held-finger bindings).
* ☐ **Saves**: import/export of Vita saves (ss-delta's `--import-save`,
  with this game's ten slots).
* ☐ **DLC**: the Mirror Spirits missions available (installed add-on +
  1.02), and checked in play.
* ☐ **Texture shimmer** (seen by the owner in the tutorial field,
  2026-10-13: the ground grains and shimmers while the camera moves). In
  ss-delta the same look was the game's own (a real Vita shimmers too), from
  repeating textures shipped without mips (its 02-baseline, "Ground shimmer
  in motion"). Here:
  1. ☑ Confirmed on hardware (the owner, 2026-10-13): the tutorial
     shimmers exactly the same on a Vita. It is more visible on PC because
     the 960×544 image is blown up to a large screen.
  2. Find the cause with a sampler trace, as ss-delta did: mip levels, wrap
     mode, filters and LOD bias of the ground textures.
  3. Options, cheapest first:
     * a higher internal resolution, which supersamples and reduces
       shimmer even without mips; it costs GPU time;
     * Vita3K's anisotropic filtering, which only helps textures that have
       mips;
     * **mip chains built at upload** for mipless repeating textures.
       ss-delta proposed this but never built it, so it is shared work for
       both games ("Shared work after Phase 1"). It is an enhancement that
       changes the look, so it is a setting.

  Post-process AA (FXAA/SMAA) does little for texture shimmer.
* ☐ **60 fps**, by ss-delta's method (its D16): find the frame pacing
  (frame timer period, vblank flip threshold) and change it as data in
  guest memory from the profile's frame-rate hook, so no game code is
  patched and native code stays on. Then check:
  * that game logic steps by the measured frame time (movement, combat,
    Havok, AI, cutscene timing at 60 against 30);
  * every screen that may depend on the frame time (ss-delta's loading
    screen hung at 60 and stays at 30): loading, FMV, mission start and
    end, menus.

  If logic is frame-locked, 60 needs a game rewrite: mark it unplanned, as
  ss-delta's D16 allowed for.

**Exit:** a full playthrough is possible on keyboard/controller at ≥ 2×
internal resolution, grappling hook included, at 60 fps or with 60 marked
unplanned.

## Phase 8 — Compatibility pass (M) ☐

* ☐ A compatibility matrix (`docs/06-compatibility.md`, to be started): story
  missions, faction missions, Harakiri Engine missions, DLC missions,
  every ending, letters, items, Network Jar (offline), options, saves.
* ☐ Native against JIT for timing-sensitive systems (Havok, AI) in one
  fight.

**Exit:** the matrix has no blocking entries.

## Publishing (S, when the owner decides) ☐

[D6](decisions.md). Runs for each of the three repos (and ss-delta's,
**(ss-delta)**). It can happen before Phase 8; the only requirement is
that the repo builds from a fresh clone.

* ☐ Licences chosen and added (fork: GPL-2.0-or-later with Vita3K's
  notices; recompiler and game repos: owner's choice).
* ☐ History scan of every commit: D2 file types, blobs over a few MB,
  zRIF-like base64, `work.bin`/`.rif` contents, personal paths and
  addresses. A script (`tools/leak-scan.py`), also usable as a pre-commit
  hook. Rewrite the history if anything is found, before the first push.
* ☐ Docs made public-ready: repo-relative paths, a build guide from a fresh
  clone, "bring your own dump" install steps, known issues.
* ☐ A GitHub Actions build of the fork and the recompiler tests (no game
  data needed).
* ☐ Release binaries only from a public tag of the fork.

**Exit:** the owner pushes; a stranger can clone, build and install from
their own dump with the README alone.

## Shared work after Phase 1 (both games) ☐

ss-delta's remaining wishes, done once in the shared repos after Phase 1,
so both games get them. Not on this game's critical path; the owner orders
them against Phases 2–8.

* ☐ **Settings menu**: an in-app menu that edits the ini, built from the
  profile's settings list (Phase 1). It covers display (scale, frame rate),
  audio, input bindings and paths. Settings that need a restart say so.
* ☐ **Mip chains for mipless textures** (a setting): generated at texture
  upload for repeating textures with one level, against ground shimmer in
  both games (Phase 7, "Texture shimmer").
* ☐ **Linux and macOS builds**:
  * the AOT loader: `dlopen` beside `LoadLibrary` (it is Windows-only
    today);
  * the recompiler's CMake: `.so`/`.dylib` instead of DLLs, GCC/Clang
    instead of MSVC, and the generated C++ checked on both;
  * macOS on Apple Silicon: an ARM64 host. The recompiler's runtime has
    no x86 intrinsics, but the generated code's speed there is
    unmeasured;
  * Vulkan through MoltenVK on macOS (Vita3K's own path);
  * the scripts, already in Python after Phase 1;
  * Steam Deck as a Linux target.

## Later (deferred)

* Other regions (EU PCSB00049, JP PCSG00019): the same profile with another
  title ID; regenerate per eboot.
* Modding: loose-file overrides, if the engine has them (unknown), and
  FADEBABE repacking.

---

## Risk register

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | NGS audio: SFX dropout, missing envelope/reverb/EQ | unplayable without sound effects | Phase 5; NGS tracing; hardware recording; the fix is upstreamable |
| R2 | 1.00 vs 1.02 | wasted work if we start on 1.00 | **closed**: 1.02 installed and measured in Phase 0 (D3); the recompiler's code hash rejects a mismatched DLL anyway |
| R3 | Rear-touch aiming has no natural PC control | grappling hook awkward | Phase 2 finds the semantics first; right stick or mouse; playtest |
| R4 | Havok + NEON correctness (13.6% FP/SIMD) | physics desync | ss-delta's NEON layer and dynarmic tests already pass for these forms; differential runs |
| R5 | PhyreEngine render-to-texture and readback | effects wrong at higher scale | surface sync on (ss-delta D4 update 4); Phase 6 sweep at scale 1 and 2 |
| R6 | Shared toolchain changes break ss-delta | regressions in the finished port | D4: shared patches tested on both games; ss-delta's quick check in Phase 1's exit |
| R7 | Frame-locked logic | no 60 fps | ss-delta D16's method (data-only change, loading screens at 30); otherwise 60 is marked unplanned |
| R8 | GPL (Vita3K) | runtime can't be relicensed | the fork's source is published with any binary (D6); the recompiler has no Vita3K code |
| R9 | No debug menu found | slow testing of late content | saves per chapter; Vita save import |
| R10 | Game data or personal data in a pushed history | can't be taken back once public | D2; the history scan before the first push (Publishing); the scan as a pre-commit hook |
| R11 | Extracting the shared repos disturbs the finished ss-delta | regressions, lost history | `git filter-repo` keeps history; ss-delta's quick check after each step; the owner OKs each step; ss-delta is finished (2026-10-13), so nothing else moves under it |
