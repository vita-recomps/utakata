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
* → DLC: the add-on is found at boot, but its missions didn't appear on
  the board up to day 4. Moved to Phase 7's DLC item (done there): it needs play
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
Phase 1 (2026-10-13).

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
* ☑ **Scripts in Python** in `vita-recomp/tools`: `build-vita3k.py`
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
* ☑ ss-delta on the new front end: `ss-delta.exe` from this build, with
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
this repo configured and built from scratch in 9 min (after
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

## Phase 5 — Audio: NGS (M–L) ☑

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
* ☑ Reverb, `sceNgsModuleGetPreset` and the release fade on key-off,
  in the fork behind a per-game switch (`[audio] effects`, on for this
  game, off for ss-delta; owner's choice, 2026-10-14). The soak stays
  steady with them. In the scenes tested the game sends nothing to the
  reverb and asks for no fades, so they still need a scene that uses
  them (02-baseline). The EQ is left out: the game sets it flat.
* → Comparing against a Vita (a recording by the owner) for envelopes and
  reverb moved to "Later": the owner heard nothing wrong in a whole
  playthrough.

**Exit:** a long session (several missions, or an hour of combat) with no
SFX loss; envelope, reverb and EQ audible and plausible against hardware.
Met (2026-10-14): the whole story played with no sound loss; the effects
follow the game's requests (the EQ is flat in this game).

## Phase 6 — Rendering correctness (M) ☑

* ☑ Sweep every mission area and the castle/hub screens: covered by the
  owner's playthrough (2026-10-14, AMD, scale 2): every story mission to
  the ending and a DLC mission, no rendering issue seen. The owner judged
  a scripted sweep not worth doing after it. Saves after every mission are
  archived should one be needed.
* ☑ Cutscenes and FMV: the story movies and every story scene played in
  the playthrough; no stuck subtitles seen.
* ☑ Effects: blood, smoke, water, night lighting: seen in play, no issue.
* ☑ AMD and NVIDIA (ss-delta's two-reference rule, its D4 update 2). The
  fork's NVIDIA fixes come along, among them the USSE min/max NaN rule
  (patch 0039) behind SSD's white floor. PhyreEngine's fog and lighting
  may hit the same NaN path, so NVIDIA is checked early, not last.
  The owner played the NVIDIA package (`utakata-nvidia-5e9ddf2`) on the
  RTX 4090 PC (2026-10-15): the game works, no issues seen.

**Exit:** a visual sweep of all areas and cutscenes with no known
rendering bugs. Met: on AMD by the playthrough, on NVIDIA by the
owner's play on the RTX 4090 (2026-10-15).

## Phase 7 — PC features (M) ☑

* ☑ **Internal resolution**: Vita3K's multiplier. The game renders 3D at
  the full 960×544 (Phase 2); the playthrough ran at scale 2 (1920×1088)
  with no depth or effect issues, 57–60 fps at frame_rate 60.
* ☑ **Input**:
  * keyboard and gamepad bindings: the front end's [keyboard] and
    [gamepad]; the whole playthrough on a gamepad;
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
* ☑ **Saves**: `--import-save <folder|zip> [--slot N]` and `--export-save
  <folder> [--slot N]` for the ten slots (data0000-0009.bin, Vita3K's slot
  records). Checked: export of all slots, a Vita-style folder (data file
  only) into slot 5 and a zip into slot 6, both in the Load dialog, slot 5
  loads.
* ☑ **DLC**: the Mirror Spirits missions available (installed add-on +
  1.02), and checked in play. They are issued only after an ending, so
  this needs a cleared save. The owner started New Game+ on the cleared
  save and the DLC missions were in the list (2026-10-14). ☑ The first
  DLC mission loads and plays (02-baseline).
* ☑ **Texture shimmer** (seen by the owner in the tutorial field,
  2026-10-13: the ground grains and shimmers while the camera moves). In
  ss-delta the same look was the game's own (a real Vita shimmers too), from
  repeating textures shipped without mips (its 02-baseline, "Ground shimmer
  in motion"). Here:
  1. ☑ Confirmed on hardware (the owner, 2026-10-13): the tutorial
     shimmers exactly the same on a Vita. It is more visible on PC because
     the 960×544 image is blown up to a large screen.
  2. ☑ Find the cause with a sampler trace, as ss-delta did: 34 of the 70
     large textures in mission 1 are repeating UBC1/UBC3 without mips,
     sampled trilinear (02-baseline).
  3. Options, cheapest first:
     * a higher internal resolution, which supersamples and reduces
       shimmer even without mips; it costs GPU time;
     * Vita3K's anisotropic filtering, which only helps textures that have
       mips;
     * ☑ **mip chains built at upload** for mipless repeating textures:
       in the fork (`State::generate_mips`, Vulkan), `[display] mipmaps`.
       The owner (2026-10-14): the shimmer in motion is gone, so it is on
       by default (D8). In ss-delta it made no visible difference on the
       ST17 ground, so it is there but off.

  Post-process AA (FXAA/SMAA) does little for texture shimmer.
* ☑ **60 fps**, by ss-delta's method (its D16): find the frame pacing
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
  steps per frame. Fixed: event scenes after a load (no scene flag) run
  at 30 fps, everything else at 60; found from logged signals over four
  owner tests, confirmed end to end on the second-to-last mission
  (02-baseline). The final mission's scene is for the owner to confirm.
  The title, menus, hub and mission results run at 30 too (no script
  controller), so their 1/30 animations and timers keep their speed; the
  pause menu and HUD in a mission still animate twice as fast.

**Exit:** a full playthrough is possible on keyboard/controller at ≥ 2×
internal resolution, grappling hook included (native controls), at 60 fps or with 60 marked
unplanned. Met (2026-10-14): the owner's playthrough at scale 2 on a gamepad,
its last missions at 60. The texture shimmer, the last open item, is
smoothed by generated mipmaps (D8).

## Phase 8 — Compatibility pass (M) ☑

* ☑ A compatibility matrix ([06-compatibility](06-compatibility.md)):
  from the owner's playthrough and the test runs. No blocking entries; open
  (?) are other endings and difficulties, Kaede, the DLC missions played
  through and NVIDIA; Kaede works (owner); Network Jar is unplanned (D7).
* ☑ Native against JIT for timing-sensitive systems (Havok, AI) in one
  fight: differential runs at 30 and 60 fps, 0 mismatches (02-baseline).

**Exit:** the matrix has no blocking entries.

## Publishing (S, when the owner decides) ◐

[D6](decisions.md). Runs for each of the three repos (and ss-delta's,
**(ss-delta)**). It can happen before Phase 8; the only requirement is
that the repo builds from a fresh clone.

* ☑ Licences: MIT for this repo, ss-delta (its Vita3K patches stay GPL)
  and vita-recomp-kit; the fork GPL-2.0-or-later.
* ☑ History: our commits rewritten to the no-reply address in all four
  repos (fork: ours only). Scans: no D2 file types, no blobs over 1 MB, no
  personal email. The pre-rewrite copies were deleted (2026-10-15). Every
  working copy and submodule commits with the no-reply address.
* ☑ History scan of every commit: D2 file types, big blobs, zRIF-like
  base64, licence contents, personal paths and addresses
  (`tools/leak-scan.py`, run as the pre-push hook of every repo).
* ☑ Docs made public-ready (2026-10-13), in this repo and ss-delta:
  repo-relative paths, relative submodule URLs (`../vita3k`), READMEs with
  requirements, a build guide from a fresh clone, "bring your own dump"
  install steps and known issues. The owner's local details stay outside
  the repos, brought to Claude Code by a git-ignored `CLAUDE.local.md`.
* ☑ History scrubbed in this repo and ss-delta: no host name, local paths
  or user folders in any commit or message (`C:\...` project paths became
  `<utakata>`, `<ss-delta>`, `<git>`). The fork's and vita-recomp-kit's
  histories had nothing to scrub.
* ☑ Leak scan: vita-recomp-kit `tools/leak-scan.py`, a pre-push hook in
  every repo (game-data files, big files, licence strings, tokens, user
  folders, and the owner's private patterns kept outside the repos).
* ☑ Published on GitHub, org `vita-recomps`:
  * the fork (`Vita3K`, a fork of Vita3K/Vita3K, default branch `games`)
    and `vita-recomp-kit` (2026-10-13), both kept up to date since;
  * **ss-delta** (2026-10-15), its `master` as GitHub's `main`;
  * **utakata** (2026-10-15), after its README got a single status
    paragraph and a Features section, and the docs lost the private-server
    history.

  Each repo's whole history passed the leak scan.
* ☑ A fresh-clone check of each game repo:
  * ss-delta (2026-10-15): cloned into an empty folder, then built and
    installed from the owner's dump with its README alone (clone 13 min,
    build 9 min, install 16 min). The result ran on native code.
  * utakata (2026-10-15): an anonymous clone from GitHub, by its README
    alone (clone 5 min, build 11 min, update fetch and install 7 min). It
    reached the first mission with every module native.
* ☐ A GitHub Actions build of the fork and the recompiler tests (no game
  data needed).
* ☐ Release binaries only from a public tag of the fork.

**Exit:** the owner pushes to GitHub; a stranger can clone, build and
install from their own dump with the README alone.

## Shared work after Phase 1 (both games) ◐

ss-delta's remaining wishes, done once in the shared repos after Phase 1,
so both games get them. Not on this game's critical path; the owner orders
them against Phases 2–8.

* ☑ **Settings menu**: an in-app menu that edits the ini, built from the
  profile's settings list (Phase 1). It covers display (scale, frame rate),
  audio, input bindings and paths. Settings that need a restart say so.
  Done (2026-10-14, both games): F1 or Select held for a second opens it
  over the paused game; one page per section, built from the declarations;
  changes written to the ini line by line (comments and line endings kept)
  and live where the emulator allows (window, fullscreen, vsync, filter,
  volume, ss-delta's frame rate). Not in it yet: key bindings (rebinding
  needs key capture) and paths, which stay in the ini.
* ☑ **Mip chains for mipless textures** (a setting): generated at texture
  upload for repeating textures with one level, against ground shimmer in
  both games (Phase 7, "Texture shimmer").
* ☑ **Linux and macOS builds**: done in the shared repos by ss-delta
  (its Phases 11 and 12, 07-linux and 08-macos), taken by utakata in
  Phase 9 below. The original list:
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
* ☐ **A setup for players** ([D9](decisions.md)): a download from GitHub
  Releases that turns the player's own dump into a playable port without
  cloning or building, on Nebula's model (github.com/keepvaibin/nebula):
  * GitHub Actions builds the game's executable from a public tag of the
    fork (a build option for the single-game executables without Qt) and
    freezes the Python tools (install, ELF dump, recompile, packaging)
    into the setup; release checks refuse any file that looks like game
    data;
  * on the player's PC the setup installs the game, firmware (downloaded
    from Sony's servers, as Vita3K does) and add-ons, captures the modules
    in a short run, recompiles them and compiles them with a toolchain it
    downloads and pins by hash: `clang-cl`/`lld-link` (llvm-mingw) with
    Microsoft's C++ runtime and Windows SDK packages, under Microsoft's
    licence, so nothing of Microsoft's is redistributed;
  * the setup's screens could be the game's own first start (the overlay
    UI of the settings menu, a native file dialog), usable with a gamepad;
  * unsigned at first ("Run anyway"), with SHA-256 checksums and GitHub
    build attestations; SignPath's free signing for open source once the
    repos are public.

  ☑ Spike (2026-10-15): ss-delta's ten modules built with llvm-mingw
  20261006 (clang 23.1.3) as `clang-cl` and `lld-link`, against the MSVC
  runtime and Windows SDK on the dev PC, loaded by the MSVC-built
  `ss-delta.exe`:

  | | MSVC (cl) | clang-cl |
  |---|---|---|
  | compile, 10 modules, 6 jobs | 11.9 min | **2.7 min** |
  | `ssd_aot_eboot.dll` | 98.4 MB | 83.8 MB |
  | modules verified, quest fps | all, 56-58 | all, 56-58 |
  | differential, quest and fight | — | **15,608 calls, 0 mismatching** |

  What the toolchain needs: `clang-cl.exe` as a copy of `clang-23.exe`
  (llvm-mingw's `clang.exe` is a wrapper that reads a target from its
  name), `lld-link.exe` of `ld.lld.exe`, `llvm-lib.exe` of `llvm-ar.exe`,
  `--target x86_64-pc-windows-msvc` (llvm-mingw defaults to MinGW) and
  `-fuse-ld=lld`, no manifest tool. Linux and macOS setups reuse the same
  pipeline with a bundled or system clang. The 4x shorter compile also
  makes clang-cl worth offering for development builds.

  ☑ The toolchain without Visual Studio (2026-10-15, vita-recomp-kit
  `tools/toolchain.py`): llvm-mingw plus the MSVC 14.44 runtime and Windows
  SDK 10.0.26100 packages from Microsoft's Visual Studio manifest, every
  file pinned by SHA-256 in `tools/toolchain-windows.json`, fetched only
  with `--accept-microsoft-license`; 444 MB to download, ~930 MB unpacked
  (x64 desktop only). `build-recomp.py --toolchain <dir>` replaces CMake
  and Ninja with a Python driver (same flags, incremental). ss-delta's ten
  modules, nothing of Visual Studio on the path (every header and library
  read from the toolchain folder): 3.0 min with 6 jobs, all verified in a
  quest at 56-57 fps, differential 11,285 calls with 0 mismatching.

  ☑ The setup, first version (2026-10-15):
  * the fork's `VITA3K_GAMES_ONLY` (`build-vita3k.py --games-only`) builds
    the game executables without Qt, in 9 min;
  * the kit's `make-setup.py` lays out the setup (96 MB, 30 MB zipped):
    * Python's embeddable distribution with capstone and PyYAML, pinned
      to the development versions, since the recompiler's output depends on
      capstone's;
    * the kit;
    * the game's front end;
    * a release check that refuses anything that looks like game data;
  * `setup.bat` asks for the dump and needs Microsoft's licence accepted.
    It then downloads:
    * the firmware from Sony (`fetch-firmware.py`; both PUPs match our
      copies' SHA-256);
    * the toolchain, into `%LOCALAPPDATA%\vita-recomps`.

    Then it installs, captures, recompiles and compiles, and puts the VC++
    runtime DLLs beside the exe.

  Test: Shinobido 2 (game, 1.02, add-on), from a fresh unzip with no
  Python, Git or Visual Studio on the path. Results:
  * about 6 min to a playable folder;
  * generated code byte-identical to the development build's;
  * every loaded module verified and native in the first mission.

  ☑ The setup's window (2026-10-15, kit `setupgui.py`). It uses Tk from
  python.org's `tcltk.msi` and asks for:
  * the game, its update and add-ons, with their licences (a pkg's
    `work.bin` or `.rif` is found next to it);
  * the playable folder;
  * acceptance of Microsoft's licence.

  It shows the stages and output, then Play and Open folder. Tested end to
  end:
  * Shinobido 2 through the window;
  * an ss-delta setup from the console, which reached a quest at 56-58 fps
    with every module native.

  ◐ The GitHub Actions release. ss-delta's `.github/workflows/release.yml`
  (its D18) makes a draft release from a tag `v*`: setup zip, SHA-256 and
  build attestation; a manual run uploads the zip as an artifact.
  * The first manual run (2026-10-15, 24 min) built fine, but the runner's
    own OpenSSL 3 got linked and not shipped. Fixed in two places:
    * the fork's games-only builds always take the pinned prebuilt
      OpenSSL;
    * `make-setup.py` refuses a setup whose exe imports a DLL it doesn't
      carry.
  * The second run (20 min) made a setup that installed and played here
    from a fresh unzip: a quest at 56-58 fps, every module native.
  * The owner's test on a separate PC (2026-10-15) found two problems,
    both fixed:
    * the template exe in the setup's own folder was easy to start by
      mistake; it now sits in `kit\game\`, and the setup offers a desktop
      shortcut;
    * 47-50 fps on the RTX 4090, from surface sync reading back through
      video memory; fixed in the fork (ss-delta's 02-baseline).
  * utakata has the same workflow (`.github/workflows/release.yml`).
  * Next: a tag for each game's first draft release.

  ☐ A check on a separate PC without Visual Studio or the VC++ runtime
  (the owner).
* ☐ **Android**, now [Phase 11](#phase-11--android-targeting-the-ayn-thor-l-).
  The original note, written before ss-delta's Phase 14 built the game on
  the device itself: the port can't compile on a phone, so the APK is built on the player's PC from their own dump (the
  Android NDK's clang, ARM64) and sideloaded; a "Build for Android" step in
  the PC setup could do it. Needs the `dlopen` loader and the ARM64 check
  from the Linux and macOS work, an Android build of the single-game front
  end (Vita3K runs on Android; the fork keeps its `android/`), on-screen
  touch controls, and performance and GPU-driver testing. Test device:
  AYN Thor (Snapdragon 8 Gen 2, Adreno 740).

## Phase 9 — Linux, macOS and the 0.1.0 release (M) ◐

The owner asked for it on 2026-11-18: utakata on today's fork and kit,
with ss-delta's Linux and macOS builds, towards a 0.1.0 release on GitHub
with all three setups ([D10](decisions.md)).

* ☑ The submodules at fork `bc449f9a` and kit `2b39018` (ss-delta 0.3.0's);
  `shinobido2.exe` rebuilt on Windows and checked: the day-57 hub and the
  last mission's field on native code, 0 native-to-JIT calls.
* ☑ The game's own icon and version resource (fork, `tools/make-icon.py`);
  `fmt::join`'s header in `saves.cpp`, which g++ needed.
* ☑ `game.json`: the Linux and macOS READMEs
  (`docs/dist-readme-linux.txt`, `docs/dist-readme-macos.txt`).
* ☑ The release workflow with Windows, Linux and macOS jobs and one draft
  release, as ss-delta's.
* ☑ The Linux setup on the Steam Deck (2026-11-18): built in WSL 2's sniper
  SDK, run over SSH in console mode from the game pkg, the 1.02 patch pkg
  and the add-on (firmware and zig downloaded by a first attempt that
  failed for lack of a display over SSH): **7.8 min** to a playable folder
  of 1.35 GB with its desktop entry and icon (`<out>-work` keeps 1.4 GB).
  From a hub save, the first mission's field on native code: the five
  modules that load verified, 0 native-to-JIT calls, rendered as on
  Windows; 30.0 fps at the default settings, 60.0 fps (worst frame 17 ms)
  at `frame_rate = 60`, scale 1.
* ☑ The macOS setup on the M5 (2026-11-18): built on the Mac (the fork in
  1.6 min), run in console mode: **2.5 min** to a playable folder with
  `Shinobido 2 - Revenge of Zen.app` (firmware and zig already in the
  cache). The same mission natively: 30.0 fps by default, 60.0 fps (worst
  16.7 ms) at 60.
* ☑ The workflow run on GitHub (2026-11-18, run 44277535729, from a
  `release-0.1.0` branch): all three jobs passed (Linux 18 min, macOS 17,
  Windows 31).
  * ☑ Its macOS setup on the M5, from a quarantined tarball: 145 s, then
    the mission natively at 60.0 fps.
  * The Windows setup failed to download llvm-mingw:
    `CERTIFICATE_VERIFY_FAILED`. GitHub's release-asset servers chain to
    Let's Encrypt's Root YR, which this PC's Windows store didn't hold;
    Python trusts only the roots already there, while Windows' own TLS
    (System32 `curl.exe`) fetches a missing root and downloaded the file.
    Every Windows setup was exposed (ss-delta's too). Fixed in the kit
    (`0923a76`): on that error, `toolchain.py` downloads with `curl.exe`;
    the SHA-256 is checked as before.
  * ☑ Its Windows setup with that fix: 3.6 min to a playable folder (the
    MSVC packages already downloaded by the failed run), then
    `to-mission.py` to the first mission's field, every loaded module
    native, 0 native-to-JIT calls.
  * ☑ Its Linux setup on the Deck: 7.8 min, then the mission natively at
    60.0 fps.
* ☑ Tag `v0.1.0` (`141d87f`, 2026-11-18): run 44286462267 passed and made
  the draft release with the three setups (Windows zip 34 MB, Linux 88 MB,
  macOS 45 MB), their SHA-256 and build attestations. Held back, not
  published: ss-delta's 0.3.0 changed what a release is the same day.
* ☑ The release as the game's own folder, ss-delta's D22 ([D11](decisions.md)):
  fork `430e30af` and kit `8220643`, plus fork `3c62a496` (the game's save
  options in `--help`); the workflow makes
  `utakata-<version>-{windows.zip,linux.tar.gz,macos.tar.gz}`, each
  unpacking to `utakata/`; the three folder READMEs rewritten for the
  importer and the command line. `shinobido2.exe` built on Windows
  (games only) and `--help` checked.
* ☑ README with a banner (`docs/assets/banner.svg`, the icon's throwing
  star, texts pinned with `textLength`) and badges; `docs/INSTALLING.md`
  for players and `docs/BUILDING.md` (the build, install and tools
  sections moved out of the README).
* ☑ The workflow's three jobs on the new layout (run 44306621814, from
  `583d67b`; archives: Windows 34 MB, macOS 45 MB). Windows, unattended
  (`--dump` game + licence + 1.02 [+ add-on] `--accept-microsoft-license
  --build-only`):
  * a local layout of the same commit, downloads from a `--cache`: 181 s;
  * the workflow's archive, downloads fresh into `setup/downloads`: 261 s,
    3.3 GB at the peak, 1.4 GB after, `setup/` back to `kit` and `python`.

  Both then went with `--import-save` (hub-day1, slot 1) and
  `to-mission.py` to the first mission's field, every module native, 0
  native-to-JIT calls; nothing was written to `%APPDATA%\Vita3K` or
  elsewhere outside the folder. Linux and macOS archives not run on the
  Deck or the M5 for this layout (ss-delta's 0.3.0 checked the same kit
  and front end on both).
* ☑ `v0.1.0` tagged again on the new layout (`40b516a`, 2026-11-18; the
  first draft and tag deleted): run 44311171344 made the draft release
  with `utakata-v0.1.0-windows.zip` (33 MB), `-linux.tar.gz` (84 MB) and
  `-macos.tar.gz` (44 MB), their SHA-256 and build attestations. Its
  macOS job was cancelled the first time without starting (GitHub had
  no macOS arm64 runner free); re-running the failed jobs passed. The
  owner published it on 2026-11-18.
* ☐ The published Linux and macOS archives run on the Deck and the M5 to
  a mission (the Windows one was, from the workflow's earlier run of the
  same layout).

**Exit:** with their own dump, a player on each of the three platforms
gets from the 0.1.0 release to a mission on native code.

## Phase 10 — ss-delta's 0.4.0 features on the desktop (M) ◐

The owner asked on 2026-11-21: feature parity with ss-delta, apart from
multiplayer (this game has none). ss-delta's Phase 8 additions and the
fork's front end since `bbca8b81` (28 commits on `games`, up to
`36e098b3`; kit `fb2a5cb` → `dd07e72`). Most of the machinery is in the
shared front end already; what is new here is each feature's game side
(addresses, textures, the camera) and its tests. Findings in
[01-research](01-research.md#ss-deltas-040-features-phase-10-2026-11-21-local),
tests in [02-baseline](02-baseline.md#ss-deltas-040-features-phase-10-2026-11-21).

* ☑ **10a Today's fork and kit** (2026-11-21). Submodules to fork
  `36e098b3` and kit `dd07e72` (then `f7f6f91`, ss-delta 0.4.1's
  Windows setup fix); `shinobido2.exe` rebuilt, `to-mission.py` to the
  first mission's field, every loaded module verified, 0 native-to-JIT
  calls. What came without game work:
  * the settings menu's Exit page; the discrete-GPU exports (laptops with
    two GPUs, ss-delta issue #4);
  * add-ons and mods after the build (`--dump=<file>`): a mod alone
    installed in 1 s from a release folder of this commit; NoNpDrm dumps
    laid out as ux0; the setup's `--progress` and `setup.log`;
  * the input pipe's `memdump:`, `memwrite:` and `mouse:` steps, used for
    10e and 10f.
  * ☐ Not checked here: the settings menu over this game's Load and Save
    dialogs (Vita3K's overlay input queue, fixed in ss-delta).

  ☑ As ss-delta has it: `recomplauncher.json` in every release
  ([D13](decisions.md); inputs: the game, the 1.02 update, the add-on and
  a mod), stamped by the workflow (`tools/stamp-recomplauncher.py`);
  `CHANGELOG.md`; release notes in `.github/release-notes/<tag>.md` when
  there is one. A release folder laid out from this commit built from the
  dump in 3.1 min and played to the mission natively.
* ☑ **10b Language** (2026-11-21): `[game] language` (`english`,
  `french`, `spanish`), on the settings menu's Game page, read at start.
  The US data has French and Spanish text: menus, hub, briefings, the
  Basic Controls picture and the system dialogs follow; mission names stay
  English.
* ☑ **10c rePatch mods** (2026-11-21): `[game] repatch`, "Mods
  (rePatch)". A hand-made mod (Spike's logo movie as Acquire's) was read
  in place of the game's file, installed both with `--install-content` and
  through a release's `--dump=`. It only overrides loose files
  (`RomImage/...`, the stream packs, the movies), not members of
  `volume.dat`. No Shinobido 2 mod is known; an undub needs the JP
  release's voice packs (see Later).
* ☑ **10d Skip the intro logos** (2026-11-21): `[game] skip_intro`, off
  by default. The opening scene's state machine is moved from the Bandai
  Namco picture to the opening movie (data only): the four logos are
  skipped, the movie starts at about 26 s instead of 46, and Start skips
  it as on the Vita. The boot's loading screen (about 22 s) stays.
* ☑ **10e Mouse camera** (2026-11-21): `[mouse]`, PC only. The game's
  right stick is on or off (past 77 steps of 127: 120°/s left and right,
  60°/s up and down) and speeds up over half a second, so a pulsed stick
  hardly turned it. The shared mouse camera gained a second mode
  (fork `75df4aa8`): the game gives its camera's angles (the world matrix
  at application `+0xc0`) and the stick is held until the camera has
  turned as far as the mouse asked. Through the pipe: turns of 1–90°
  within about a frame's turn, both axes, diagonals, the pitch's limits.
  * ☐ Played with a real mouse by the owner; the hook's aim (R + Circle)
    and the game's own Y/X-axis camera options with it.
* ☑ **10f Cheats** (2026-11-21): `[cheats]`, a Cheats page, all off,
  switched while the game runs, data only: Infinite health, Infinite
  ninja tools (tools and items given back), One-hit kills (every other
  character's health kept at 1), Max money (9,999,999), Max stats (both
  characters, Apollo's values). From the game's record at `0x8153b530`
  (laid out as the save) and, in a mission, the player and the character
  list, each checked before it is written. Checked through memory in the
  first mission.
  * ☐ Playtest by the owner: One-hit kills in fights and on a boss, a
    whole mission with the others, a save and reload, the mission rank.
  * ☐ Candidates not done: enemies never alert, no mission timer (whether
    the game keeps such values is unknown).
* ☑ **10g Xbox button labels** (2026-11-21): `[game] button_labels`
  (`playstation`, `xbox`, `auto`). The textures were collected as the game
  uploads them (`UTAKATA_TEXTURE_DUMP`, development); the game keeps its
  pictures upside down, so the shared labels gained `flip_y`, and white
  letters for symbols on discs of their own colour (fork `55248dcb`;
  ss-delta's table unchanged). Redrawn: the UI font's page of button
  glyphs (the prompts in text, START and SELECT, L and R), the HUD
  atlas's symbols and the Basic Controls picture in all three languages.
  * ☐ Not found yet: the tutorial's and help screens' pictures, and any
    context prompt in a mission (a dump during the owner's play would
    show them).
  * ☐ Playtest by the owner (prompts, Controls page, `auto` with a pad).

**Exit:** each feature above in the settings menu (rePatch, language,
skip intro, button labels, mouse, cheats), checked on Windows and played
by the owner; the Linux and macOS builds checked to a mission. No
release before Phase 11: both ship together as v0.2.0 (the owner,
2026-11-21). Open: the owner's playtest, Linux and macOS.

**The owner's playtest, for later** (the owner, 2026-11-21: "I will test
this later"; before v0.2.0 is tagged). On Windows, `shinobido2.exe` of
this phase:

* ☑ Mouse camera with a real mouse (Tab or a middle click): turning,
  looking up and down, the hook's aim (R + Circle), the game's own Y/X
  camera options, the Mouse page's sensitivity and inversion. The owner,
  2026-11-24: it works but "feels very sluggish", and "after looking up
  and quickly down the camera keeps going up then stops then goes down".
  Fixed through the eboot's overrides ([D16](decisions.md)): the camera
  code takes the mouse itself, exact and unlimited, in the field and the
  hook's aim (01-research, "Mouse camera"). ☐ The owner's feel of it.
* ☑ Cheats: One-hit kills in fights and on a boss; a whole mission with
  the others on; a save and reload; the mission rank with cheats on.
* ☑ Xbox button prompts: `xbox`, and `auto` with a real pad (the
  prompts, START/SELECT, L/R, the HUD, the Basic Controls page); any
  picture still showing PlayStation symbols (the tutorial, help screens,
  mission prompts) noted, with `UTAKATA_TEXTURE_DUMP` set if possible.
* ☑ The settings menu (Select held or F1) over the game's Load and Save
  dialogs: does it still respond?
* ☑ Language (French, Spanish) and Skip intro logos, in normal play.
  Everything above "works properly" (the owner, 2026-11-24), apart from
  the mouse camera's feel. Found in testing the fix: Skip intro logos at
  60 fps hung on black every boot (a race with the game's step past the
  first logo, 01-research "Boot logos"); fixed, the skip checks that the
  opening movie started.
* ☑ Android, on the Thor (Phase 11): the APK from the release (or a
  test build), the setup screen from the dump, a mission with the
  built-in controls; the on-screen controls and CROUCH on the
  touchscreen. The owner, 2026-11-23, with the release-signed APK:
  "tested it on the thor including the touch controls, all is good".

## Phase 11 — Android, targeting the AYN Thor (L) ◐

ss-delta's Phase 14 built the shared pieces: the single-game APK
(`game-frontend/android/`, parameterised by `-Pgame`), the modules built
with zig for Android (its D25), the on-device build with Python, capstone
and zig in the APK (its D27), Turnip on Adreno, on-screen controls and
the release workflow's `android` job. Research in ss-delta's
`09-android.md`. What is left is this game's side, recorded as
[D14](decisions.md) (the owner, 2026-11-21: proceed with Android). Tests
in [02-baseline](02-baseline.md#android-on-the-ayn-thor-phase-11-2026-11-21).

* ☑ **11a The APK on the JIT** (2026-11-21): `libshinobido2.so` from
  `add_game` on `ANDROID` (NDK r29 in WSL, 68 MB stripped), Gradle with
  `-Pgame=shinobido2`, `io.github.vitarecomps.shinobido2`, "Shinobido 2".
  On the Thor, from the test folder's `fs/` pushed over adb: logos →
  title → hub → first mission at 30 fps on Qualcomm's driver; the
  built-in controls as a gamepad. No icon of the game's own (game data,
  D2): the system's default, as ss-delta's.
* ☑ **11b Native code on Android** (2026-11-21): the seven modules with
  zig, from a release folder (`setup.py --android`, 6.4 min with the
  copy); the first mission on NativeCPU with 0 native-to-JIT calls, 30
  fps, on Turnip T23.
  * ☑ The kit's dynarmic comparison tests on the device (2026-11-22,
    regenerated by the current kit, built with the NDK against the APK's
    dynarmic): 17,083 instruction and 623 function tests over the seven
    modules, **0 failing**, in 6 min.
  * ☑ The differential mode on the device: the JIT with native code
    stopped at its first boundary on arm64 (dynarmic's arm64 backend
    asserts on a host call's empty arguments; fixed in the fork,
    `886b5884`). Then in the first mission's combat with a restart:
    **28,144 calls checked, 0 mismatching**, 99.9–100% native. Checking
    every call of one function (`810f054c`, which a first sampled run had
    flagged) found it differing on arm64 only (the PC: 2,472 calls, 0):
    one word below the stack pointer, a register the random-range helper
    saves, a tiny denormal float in its last bits; every live result
    agrees. Which side rounds that intermediate differently is a
    **hypothesis** (02-baseline). Android takes the debug environment
    from `debug.vitarecomps.env` or `debug-env.txt` (fork `a8fc1101`).
* ☑ **11c Rendering and sound on the Adreno**: Turnip T23 offered and
  used as on ss-delta. In the first mission's field Qualcomm's driver and
  Turnip draw the same picture.
  * ☑ Rendering against Windows on both drivers (2026-11-22, 02-baseline):
    six saves from the day-1 hub to New Game+, the hub and the board's
    first mission in each (the town at night, the forest, the castle
    grounds): the same picture on Windows, Qualcomm's driver and Turnip,
    and 30 fps on both drivers. The game doesn't need Turnip as far as
    the sweep reached (smoke and blood effects, story scenes and movies
    not covered). The offer stays (ss-delta's text says fog draws black
    rectangles: not so here); a text of this game's own is the owner's
    call.
  * ☑ Frame rate at 60 and at scale 2 (2026-11-22): 60 fps at scale 2
    holds 59.9–60.0 in the town and the forest with Turnip, no frame over
    16.7 ms, no throttling over a minute's play; scale 2 draws sharper,
    with no artefacts. The defaults stay 30 fps and scale 1 (as on
    ss-delta: battery). Battery draw per mode is 11f's.
  * ☑ `sfx-soak.py`'s mission restarts on the device (2026-11-22): 12
    cycles of combat and Restart Mission, the sound effects steady in
    every cycle (−33.6 to −37.2 dB). A phone's sound can't be recorded
    over adb, so the fork logs each port's loudness when asked
    (`VITA3K_AUDIO_LEVELS=1`, on Android `adb shell setprop
    debug.vitarecomps.audio_levels 1`; fork `8e8289ff`).
* ◐ **11d Input on a handheld and a phone** (2026-11-21): the on-screen
  controls with a **CROUCH** latch beside R (R held: crouch, sneak, cling;
  the shared latch now sits beside the shoulder it holds), checked on the
  Thor with the controls switched on over its gamepad. Holding Select
  opens the settings menu (the game's own Select action opens under it).
  * ☑ The right trigger's frame read-back on the device (2026-11-22): a
    solid eye in the forest mission, the log's `caution: eye at 896,
    258`, the camera turned to the guard; a finger held on the eye does
    the same. A translucent eye (fading) isn't matched, on any platform.
  * ☑ The on-screen controls on the Thor's touchscreen, in the owner's
    playtest (2026-11-23).
  * ☐ A phone without a gamepad, and a finger on an eye under the face
    buttons: the Thor's built-in pad hides the controls while it is
    connected, so this needs a phone.
* ☑ **11e The setup on the device and from a PC** (2026-11-21): the
  setup screen takes this game's pkgs with their licences (game,
  1.02, add-on) as they are; on the Thor, Build to Play in about 7½ min
  (5.4 to compile), the modules byte-identical to the PC's; an update
  rebuilds in 5.3 min without the dump and keeps the saves
  (`game.json` `android_build_minutes` = 8 for the screen's estimate,
  a new shared key). The PC route (`setup.py --android`) works too.
  * ☑ The settings menu over the Load dialog on Android (2026-11-22):
    drawn over it, the D-pad moves in the menu only, Circle closes it and
    the dialog goes on (the Save dialog is the same overlay).
  * ☑ A Vita save brought to the device (2026-11-22): **Import a Vita
    save** on the icon's long-press menu (fork `07bfa876`, both games):
    a folder (copied into the cache) or a .zip, through the game's own
    `--import-save` as a front-end step; the saves it replaces go to
    `save-backups/`. On the Thor a .zip and a folder each imported into
    slot 7, and the save loaded (day 26 at the hub).
* ☑ **11f Release**: the workflow's `android` job feeding every
  archive (`.github/workflows/release.yml`, as ss-delta's), signed with
  the vita-recomps release key.
  * ☑ The release key's secrets on this repository (set by the owner,
    2026-11-22), then a manual run on GitHub (run 45028508098, `e1a0d14`:
    all four jobs passed in 40 min, the APK 11 min). The APK verifies (v2)
    with the release key's certificate (SHA-256 `80dcf71e…7a7e75`), as
    `io.github.vitarecomps.shinobido2`, versionCode 9, with the build
    tools inside; the Windows archive's `setup/android/shinobido2.apk` is
    the same file.
  * ☑ INSTALLING's Android section and the README (2026-11-22).
  * ☑ Power and AYN's performance modes (2026-11-22, on the charger with
    the battery full, the first mission, the camera turning, brightness
    164): the home screen 2.06 W; Standard 30 fps 1× **2.39 W**, 60 fps
    1× 2.54 W, 60 fps 2× 3.36 W; High Performance 60 fps 2× 3.32 W (the
    same: the GPU at 615 MHz instead of 401, less busy). Every mode at
    its full rate; the battery at 24–25 °C.
  * ☑ The Thor on a release-signed app (2026-11-22): the debug apps
    removed (their test saves kept on the PC), this commit's APK signed
    with the vita-recomps key (versionCode 10: v0.2.0's 200 updates it in
    place), the dump picked on the device, built in 5.2 min, the first
    mission on NativeCPU at 30 fps. Left with no save, the add-on
    installed, and the Turnip offer unanswered for the owner.
  * ☑ The owner's playtest on the Thor (2026-11-23, the list under
    Phase 10): all good, the touch controls too.
  * ☑ ss-delta's setup fixes for its issue #13 (2026-11-23, fork
    `c43094b3`, kit `36a902e`): a NoNpDrm folder's `app/` installs before
    its `patch/` (Linux could list the update first, leaving the game at
    1.00), a Vita's own account licence is named before the downloads and
    a NoNpDrm `.rif` in `license/` replaces it. `game.json`
    `eboot_sha256_other` names 1.00's eboot (`27354474…`), so the setup
    says the update is missing. The fork's `SceKernelModel` change
    (`sceKernelGetModel` now 0x10000) doesn't reach this game: neither the
    eboot nor its firmware modules import `sceKernelGetModel` or
    `...ForCDialog`.
  * ☑ ss-delta 0.5.1's front end and setup (2026-11-24, fork `1a78ad86`,
    kit `38cb384`; [D15](decisions.md)): zig on Windows too, carried in
    the release (no Microsoft licence; the first build downloads only
    the firmware); mirrors for every download and a weekly link check
    (`links.yml`); `--offline`, `--download-only`, `--for`; "Already
    built" for a re-run with the same parts and `--rebuild`
    (`recomplauncher.json`: `prepare.done`, no `timeout`, no licence
    option); the idle cursor hides (`[mouse] hide_cursor`, on the Mouse
    page). The rest of the range is ss-delta's own game code (Spirits'
    offerings, Sortiara, its eboot overrides) or a debugging switch
    (`VITA3K_NO_ORDERED_FB_READS`). Checked in a Windows release folder:
    built from the pkgs with the firmware from `--offline` in 5.0 min
    with no download; the same run again "Already built" in 0.5 s (an
    empty `--dump=` among the arguments ignored); then `--import-save`
    and the first mission's field, 100% native, 0 native-to-JIT calls;
    `--write-ini` has `hide_cursor`. Linux and macOS not run for this
    range (ss-delta 0.5.1 checked the same kit and front end on the Deck
    and the M5).
  * ☑ Tag `v0.2.0` (`e84a178`, 2026-11-24): run 45404163515 passed (all
    four jobs, 75 min) and made the draft release with its notes,
    `utakata-v0.2.0-windows.zip` (234 MB), `-linux.tar.gz` (275 MB),
    `-macos.tar.gz` (231 MB) and `-android.apk` (100 MB), their SHA-256
    and build attestations. The PC archives carry the APK and zig. Held
    as a draft for the owner's desktop playtest (Phase 10).
  * ☑ The playtest's mouse camera fixed ([D16](decisions.md), fork `471fee41` on the
    fork's branch `utakata-0.2` (on `1a78ad86`; the same change is on `games` as
    `8d839f4b`, after ss-delta's untested renderer commits), `overrides/eboot.json`)
    and Skip intro logos
    at 60 fps (2026-11-24). A release folder of this commit built the game
    with zig from the pkgs, the overrides applied (the log: "eboot feature
    mouse_camera"). Its run to a mission was cut short: another session was
    driving `ss-delta.exe` through the same input pipe name
    (`v3kdrive`), so the drivers' presses went to whichever game held it.
  * ☐ `v0.2.0` tagged again with these (the first draft and tag deleted).

**Exit:** with a Thor and their own dump, and no PC, a player gets from
the release's APK to a mission on native code (☑ with a debug APK,
2026-11-21; ☑ with a release-signed one, 2026-11-22); with a PC, the
`setup.py --android` route works too (☑).
Then v0.2.0, with Phase 10.

## Later (deferred)

* Other regions (EU PCSB00049, JP PCSG00019): the same profile with another
  title ID; regenerate per eboot. ss-delta supports both its regions
  (its D19). Needs the owner's EU or JP dump. The EU game may have more
  text languages for 10b (**hypothesis**).
* An undub (a rePatch mod with the JP release's voice packs at the US
  paths): needs a JP dump and a check that the packs hold the same lines
  in the same order. No such mod is known.
* iOS and iPadOS, after ss-delta's Phase 15 (not started there).
* Modding: loose-file overrides, if the engine has them (unknown), and
  FADEBABE repacking; `tools/fadebabe.py` names and kinds 2–5
  decompression (from Phase 2).
* Sound against a Vita recording (envelopes, reverb), from Phase 5; and
  the final mission's scene between its bosses at 60 fps (the owner
  confirmed the second-to-last mission's).

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
