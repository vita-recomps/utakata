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

## Phase 1 — Shared repos, fork branch and front end (M) ☑

Steps marked **(ss-delta)** change the ss-delta repo; the owner OKed
Phase 1 (2026-10-13). The repos were in local stand-in hubs until they
moved to the owner's private remote (D4, D6).

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
* ☑ **Submodules**: this repo and ss-delta both have `third_party/vita3k`
  (branch `games`) and `third_party/recomp` (`main`).
* ☑ **Fork**: branch `shinobido-2` from `4704fc6c`, built here in 12 min
  (`build/vita3k`).
* ◐ **Scripts in Python** in `vita-recomp/tools`: `build-vita3k.py`
  (MSVC found with vswhere, Qt found in its default folder), `install-game.py`,
  `make-dist.py`, read from the project's `game.json`. ss-delta's old
  PowerShell build/install/dist scripts are gone; its map sweep and RTX
  4090 package stay PowerShell (SSD-specific, used rarely).
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
  touched. After ss-delta's switch, its own rebuilt exe went from Stage
  Select into a quest (ST01A): loading screen at 30, field at 56–58 fps
  on native code.
* ☑ ss-delta switched to the submodules and the Python scripts, docs
  updated, its D17 **(ss-delta)**; its `master` is at the switch, pushed
  to its hub.
* ☑ One integration branch, `games`, builds both exes; both game repos
  track it **(ss-delta)**.

**Exit:** a fresh clone of this repo with `--recurse-submodules` builds
`shinobido2.exe`, which installs the game from the owner's pkg files, boots
1.02 on the JIT to gameplay at 30 fps, and is driven by `v3kdrive.py`.
ss-delta still builds and plays (title → a quest), so the shared changes
broke nothing.
**Met** (2026-10-13): a `--recurse-submodules` clone of
this repo's hub configured and built from scratch in 9 min (after
two fixes to `build-vita3k.py` it found: Boost's bootstrap and Qt), and its
`shinobido2.exe` booted to the title at 30 fps. `dist/shinobido2-test`
(installed from the pkg files) played a mission. ss-delta played a quest.
Left open: the map sweep and RTX 4090 package stay PowerShell (ss-delta's).

## Phase 2 — Inventory and game knowledge (S) ☑

Results: [01-research, Game knowledge](01-research.md#game-knowledge-phase-2-2026-10-13).
Tools: `tools/xref.py` (disassembly with names, strings, callers over the
inventory), `tools/untranslatable.py` (what the recompiler leaves to the
fallback CPU, and why), `tools/to-mission.py` (boot → hub save → mission field).

* ☑ Inventory of 1.02's eboot, libc and libfios2: all exidx entries
  classified, 0 unreached bytes, every indirect branch listed.
* ☑ The 2 "untranslatable" eboot functions: half-precision conversions
  (`vcvtb.f16.f32`, `vcvt.f32.f16` NEON) the recompiler doesn't translate
  yet (to add before Phase 4). libpvf's 2 forms are unreached data.
* ☑ Located (addresses in 01-research):
  * main loop and frame pacing: one value, the application's frame rate
    (`[app+8]`, set to 30 by `main`), drives both the period and the
    vblank minimum;
  * render targets: a single 960×544 target and surface, so the 3D is at
    the full native resolution;
  * the NGS voice manager, which frees a stopped voice only when the
    envelope (module 4) reports its release done: the leading lead for
    the SFX dropout (Phase 5);
  * touch: front (port 0) and rear (port 1) reads in PhyreEngine's input
    update;
  * the DLC check (a key string compared with the add-on's file);
  * the Near / Network Jar calls (one thread).
* ☑ No debug or mission-select entry point is left: late-game tests use
  saves (R9).
* → `tools/fadebabe.py` names and kinds 2–5: deferred to "Later" (the port
  doesn't need it).

**Exit:** met (2026-10-13).

## Phase 3 — Native code in the fork (M) ☑

ss-delta's Phases 3–5 at once, since the recompiler already covered almost
every form. Results: [02-baseline, Native code](02-baseline.md#native-code-phase-3-2026-10-13).

* ☑ Recompiler: the half-precision conversions it lacked (VFP
  `vcvtb/vcvtt.f16.f32`, NEON `vcvt` f32↔f16), so all 16,974 eboot
  functions translate; and register jumps the inventory resolved to a
  function entry (libc's `memmove` → `memcpy`, `bx ip`) become tail calls
  instead of escapes (37 escapes on boot before, 0 after).
* ☑ eboot, libc and libfios2 generated at their load addresses (their
  dumps are already relocated) and built into `ssd_aot_*.dll` in 3.4 min
  with 6 jobs (new `tools/build-recomp.py` in vita-recomp-kit; the eboot
  DLL is 33 MB).
* ☑ Comparison suites against dynarmic: eboot 5,711 instruction tests
  (553 forms, the new ones included) and 300 function tests; libc 2,733 and
  107; libfios2 1,900 and 40: **0 failing**.
* ☑ JIT as fallback: boot → hub → mission → combat → *Restart Mission* →
  combat. 99.5–99.7% of guest instructions native, **0 escapes**, **0 JIT
  instructions inside the three modules**; the rest is firmware code
  (`libscemp4`, the video player: Phase 4). Differential mode
  (`SSD_AOT_DIFF=2000`): 50,727 calls checked, **0 mismatching**.
* ☑ Rendering and speed as on the JIT: 30 fps in combat (no checker).
* → Havok physics native against JIT at a scale (ss-delta R1): the
  differential run covered gameplay with physics (0 mismatches); a
  dedicated long fight moves to Phase 8's native-vs-JIT item.
* New tool: `tools/to-mission.py` reaches the field by recognising each
  screen (references in `build/screens/`) instead of fixed waits, which
  the title's attract movie broke.

**Exit:** met (2026-10-13).

## Phase 4 — Standalone, no JIT (S) ☑

Results: [02-baseline, No JIT](02-baseline.md#no-jit-phase-4-2026-10-13).

* ☑ Firmware modules recompiled at this game's addresses: sysmodule,
  libSceFt2, libpvf, libscemp4 (all functions; libpvf's 2 unsupported
  forms are unreached data). Comparison tests: 6,754 instruction and 174
  function tests, 0 failing. They must be generated from ELFs named
  `<module>.elf` (the runtime matches modules by that name to hold and
  release their places).
* ☑ Fork: a recompiled module's place is held again when it unloads
  (`aot_restore_reservation`). libscemp4 loads and unloads for every
  movie; without this, a later load could land elsewhere, as one did at
  `0x80650000` in the 2-hour Phase 0 run, and its native code couldn't run.
* ☑ NativeCPU is the default (`jit = false`); `shinobido2.exe` built
  without dynarmic (`build-vita3k.py --no-jit`, 8.4 min).
* ☑ Install flow end to end: `install-game.py --no-jit` from the pkg files,
  the 1.02 pkg, the add-on and the PUPs into `dist/<name>/` in 6 minutes
  (install, ELF dump, recompile 7 modules, compile, package with the
  no-JIT exe); `game.json` lists the modules.
* ☑ Offline stubs: the NP, trophy, net, HTTP/SSL and Near modules are
  Vita3K's HLE; no errors in any run, including the 2-hour Phase 0 session
  with six Near load/unload cycles. Opening the Network Jar in play is
  left to Phase 8's matrix.

**Exit:** met (2026-10-13). The no-JIT install played New Game → intro
cutscene → tutorial lessons, and the first mission with combat and a
restart: 30–31 fps, 100% native, 0 escapes, no "no native code".

## Phase 5 — Audio: NGS (M–L) ◐

The one known blocking bug. It is Vita3K's, so the fix is upstreamable.
Results: [02-baseline, SFX dropout fixed](02-baseline.md#the-sfx-dropout-cause-and-fix-phase-5-2026-10-14).

* ☑ **Cause found** (the Phase 2 suspect, confirmed by measurement): the
  game's sound manager (`0x8122d870`) frees a voice it keyed off only when
  `sceNgsVoiceGetStateData(voice, 4 = envelope)` reports the release done
  (`nReleasing == 1`, height 0). Vita3K's envelope had no state and read
  zeros, so every such voice stayed taken: one more per mission load,
  until the sound-effect voices ran out.
* ☑ **Fixed in the fork** (`fe8659d0`): the envelope keeps
  `SceNgsEnvelopeStates`, reports the release finished when Vita3K ends
  the voice, and applies the envelope's gain while the voice plays. Over 3
  mission restarts the game re-polled ended voices 71,000 times without
  the fix and 2 times with it; sound-effect loudness is unchanged.
* ☑ Repro tooling: `tools/sfx-soak.py` (combat, *Restart Mission*,
  loudness per cycle). Restarting mission 1 alone leaks one voice per
  load but did not empty the pool in 12 loads; Phase 0's dropout came
  in mission 2, which uses more voices.
* ☑ **Owner's playtest** (2026-10-14, the no-JIT install with the fix):
  all tutorials and several missions in one session, a new save after
  every mission; no audio loss, glitches or other issues seen. Second
  session (same day, with the caution binding): to day 16 of the story
  (~40%, 1:45 played, all ten save slots used), still no issues. Then the
  whole story to the ending the same day (Easy, 5:04, clear count 1), the
  last part at 60 fps: no audio loss, glitches or crashes. Saves after
  every mission are archived (four batches, the cleared save included).
* ◐ Reverb, `sceNgsModuleGetPreset` and the release fade on key-off,
  in the fork behind a per-game switch (`[audio] effects`, on for this
  game, off for ss-delta; owner's choice, 2026-10-14). The soak stays
  steady with them. In the scenes tested the game sends nothing to the
  reverb and asks for no fades, so they still need a scene that uses
  them (02-baseline). The EQ is left out: the game sets it flat.
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
  * ☑ **rear touch**: not needed. The game itself aims the grappling
    hook with R + Circle held and the left stick (owner, 2026-10-14);
  * front touch: the caution-icon lock-on and any menu touches, as keys
    (ss-delta's held-finger bindings). ☑ Caution (owner's request,
    2026-10-14): `caution_key = F`, `caution_gamepad = righttrigger`. The
    eyes move (one per nearby enemy, stacked on the right, in four
    colours), so when the binding goes down the front end reads one frame
    back, finds the topmost eye by its frame (a new front-end feature:
    touch bindings with a moving target), and holds the finger there.
    Checked in the field: the camera turns to the enemy while F is held;
    the owner confirmed the right trigger works in play (2026-10-14).
* ☐ **Saves**: import/export of Vita saves (ss-delta's `--import-save`,
  with this game's ten slots).
* ☐ **DLC**: the Mirror Spirits missions available (installed add-on +
  1.02), and checked in play. They are issued only after an ending, so
  this needs a cleared save.
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
* ◐ **60 fps**, by ss-delta's method (its D16): find the frame pacing
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

  Done (2026-10-14): `[display] frame_rate = 60` (default 30). Logic
  steps by time, or by a fixed step the hook turns into 1/60; mission 1
  plays at the right speed, movies at theirs, loads and a restart work
  (02-baseline). The rate can't drop to 30 for loading screens (the run
  loop reads it once). Known: HUD and menu animations and the results
  screen's timers step by a literal 1/30 and run twice as fast. Next:
  the owner tries 60 in play, including a mission's end.

  Owner's play at 60 (2026-10-14, to the ending): gameplay right, UI at
  twice the speed as expected, and **two mid-mission story cutscenes ran
  at twice the speed** while their audio stayed at normal speed. The
  cutscenes before and after missions were right. No movie file played
  mid-mission (the log), so these are real-time scenes whose animation
  steps per frame (**hypothesis**). Next: find which missions, reproduce
  from the archived saves, find their step.

**Exit:** a full playthrough is possible on keyboard/controller at ≥ 2×
internal resolution, grappling hook included (native controls), at 60 fps or with 60 marked
unplanned.

## Phase 8 — Compatibility pass (M) ☐

* ☐ A compatibility matrix (`docs/06-compatibility.md`, to be started): story
  missions, faction missions, Harakiri Engine missions, DLC missions,
  every ending, letters, items, Network Jar (offline), options, saves.
* ☐ Native against JIT for timing-sensitive systems (Havok, AI) in one
  fight.

**Exit:** the matrix has no blocking entries.

## Publishing (S, when the owner decides) ◐

[D6](decisions.md). Runs for each of the three repos (and ss-delta's,
**(ss-delta)**). It can happen before Phase 8; the only requirement is
that the repo builds from a fresh clone.

* ☑ Licences: MIT for this repo, ss-delta (its Vita3K patches stay GPL)
  and vita-recomp-kit; the fork GPL-2.0-or-later.
* ☑ A private remote as `origin` for all four repos, private notes in a
  separate repo (D6 update).
* ◐ History: our commits rewritten to the no-reply address in all four
  repos (fork: ours only), pushed to the private remote. Scans so far: no D2 file
  types, no blobs over 1 MB, no personal email (the three gmail hits in
  ss-delta are the Vita3K-Plus author's public attributions). The
  `leak-scan.py` hook is still to write.
* ☐ History scan of every commit: D2 file types, blobs over a few MB,
  zRIF-like base64, `work.bin`/`.rif` contents, personal paths and
  addresses. A script (`tools/leak-scan.py`), also usable as a pre-commit
  hook. Rewrite the history if anything is found, before the first push.
* ☑ Docs made public-ready (2026-10-13), in this repo and ss-delta:
  repo-relative paths, relative submodule URLs (`../vita3k`), READMEs with
  requirements, a build guide from a fresh clone, "bring your own dump"
  install steps and known issues. The owner's local details moved to the
  private notes, imported through a git-ignored `CLAUDE.local.md`.
* ☑ History scrubbed in this repo and ss-delta: no host name, local paths
  or user folders in any commit or message (`C:\...` project paths became
  `<utakata>`, `<ss-delta>`, `<git>`); force-pushed to the private remote.
  The fork's and vita-recomp-kit's histories had nothing to scrub. One old
  doc line still quotes the former placeholder email (a reserved
  `home.arpa` address, nothing personal).
* ☑ Leak scan: vita-recomp-kit `tools/leak-scan.py`, a pre-push hook in
  every repo (game-data files, big files, licence strings, tokens, user
  folders, and the owner's private patterns kept outside the repos).
* ☑ Published on GitHub (2026-10-13), org `vita-recomps`: the fork
  (`Vita3K`, a fork of Vita3K/Vita3K, default branch `games`) and
  `vita-recomp-kit`. The game repos (utakata, ss-delta) are not pushed
  yet; their relative submodule URLs will resolve there unchanged.
* ☐ A GitHub Actions build of the fork and the recompiler tests (no game
  data needed).
* ☐ Release binaries only from a public tag of the fork.

**Exit:** the owner pushes to GitHub; a stranger can clone, build and
install from their own dump with the README alone.

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
  FADEBABE repacking; `tools/fadebabe.py` names and kinds 2–5
  decompression (from Phase 2).

---

## Risk register

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | NGS audio: SFX dropout, missing envelope/reverb/EQ | unplayable without sound effects | Phase 5; NGS tracing; hardware recording; the fix is upstreamable |
| R2 | 1.00 vs 1.02 | wasted work if we start on 1.00 | **closed**: 1.02 installed and measured in Phase 0 (D3); the recompiler's code hash rejects a mismatched DLL anyway |
| R3 | ~~Rear-touch aiming has no natural PC control~~ | — | Closed: the game aims the hook with R + Circle and the left stick |
| R4 | Havok + NEON correctness (13.6% FP/SIMD) | physics desync | ss-delta's NEON layer and dynarmic tests already pass for these forms; differential runs |
| R5 | PhyreEngine render-to-texture and readback | effects wrong at higher scale | surface sync on (ss-delta D4 update 4); Phase 6 sweep at scale 1 and 2 |
| R6 | Shared toolchain changes break ss-delta | regressions in the finished port | D4: shared patches tested on both games; ss-delta's quick check in Phase 1's exit |
| R7 | Frame-locked logic | no 60 fps | Mostly not: logic steps by time (02-baseline); HUD/menu animations and result timers at 1/30 run fast at 60 |
| R8 | GPL (Vita3K) | runtime can't be relicensed | the fork's source is published with any binary (D6); the recompiler has no Vita3K code |
| R9 | No debug menu found | slow testing of late content | saves per chapter; Vita save import |
| R10 | Game data or personal data in a pushed history | can't be taken back once public | D2; the history scan before the first push (Publishing); the scan as a pre-commit hook |
| R11 | Extracting the shared repos disturbs the finished ss-delta | regressions, lost history | `git filter-repo` keeps history; ss-delta's quick check after each step; the owner OKs each step; ss-delta is finished (2026-10-13), so nothing else moves under it |
