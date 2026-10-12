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

## Phase 0 — Workspace, decryption, baseline (S) ◐

* ☑ Research snapshot ([01-research](01-research.md)): imports,
  instruction mix, inventory and a recompiler probe of 1.00; prior work;
  Vita3K's known bugs.
* ☑ PSN pkg + `work.bin` installed into a portable Vita3K (`--pkg/--zrif`,
  `tools/mkzrif.py`); DLC installed; firmware 3.74.
* ☑ ELFs decrypted and relocated via a dump run of the ss-delta fork
  ([D5](decisions.md) shim).
* ☑ Baseline ([02-baseline](02-baseline.md)): logos, FMV, title, menus,
  New Game and the tutorial field at 30 fps on the JIT, rendered correctly.
* ☑ **Update 1.02** ([D3](decisions.md)): fetched (`tools/fetch-update.py`)
  and installed; ELFs dumped; `velf`/`imix`/inventory/recompile probe
  re-run (16,972 functions, 0 unsupported); hashes recorded; boots to the
  first in-engine cutscene at 30 fps, and the add-on is found at boot.
* ☐ Check the DLC missions appear in play (mission board, after the
  tutorial).
* ◐ Repository: `git init` done; `git status` shows only docs, tools,
  README, CLAUDE.md and `.gitignore`. The first commit waits for the
  owner.
* ☐ Audio baseline: run with sound on and reproduce the SFX dropout (2–3
  missions, or sprinting over corpses). Record how long it takes and what
  the NGS log says when it happens.
* ☐ Cross-checks: the upstream Vita3K release (OpenGL and Vulkan) on this
  machine, and an RTX 4090 run (reuse ss-delta's `pkg4090` flow).

**Exit:** the 1.02 game boots to gameplay in our fork, with ELFs, hashes,
the measurements and a recorded SFX-dropout repro.

## Phase 1 — Shared repos, fork branch and front end (M) ☐

Steps marked **(ss-delta)** change `<ss-delta>` and wait for the owner's
OK at the time ([D4](decisions.md)).

* ☐ **Recompiler repo** (D4 item 2) **(ss-delta)**: extract `recomp/` and
  the game-agnostic tools with their history (`git filter-repo`), add
  `mkzrif.py` and `fetch-update.py`. Parameterise what is SSD-specific:
  `SSD_ROOT`/`GENERATED_DIR`, the `ssd_aot_` DLL prefix and `SSD_AOT*`
  env names (keeping the old ones working for ss-delta), `imix.py`'s
  segment offset and exidx (read from the ELF), `v3kdrive.py`'s exe and
  window name. The dynarmic suites pass on both games' forms.
* ☐ **Submodules**: this repo gets `third_party/recomp` and
  `third_party/vita3k`; ss-delta switches its nested clone and `recomp/` to
  the same submodules **(ss-delta)**.
* ☐ **Fork**: a `shinobido-2` branch from the `ss-delta` tip (`1f100891`).
  Build both exes with `build-vita3k.ps1` (ss-delta's, with paths as
  parameters).
* ☐ Generalise `vita3k/ss-delta/` into a per-game front end:
  * a game profile with title ID, window name, exe name, icon and ini
    defaults;
  * hooks for game-specific features;
  * `shinobido2.exe` with `shinobido2.ini`, its own config and log folder,
    keyboard and gamepad bindings, and the saves layout (`SlotParam_N.bin`
    plus data).
* ☐ Install path for PSN pkgs: `--install-pkg <pkg> --work-bin <file>`
  (zRIF made in code, as `tools/mkzrif.py` does), then the 1.02 patch pkg
  (with the game's licence) and the DLC pkg. Fetching the patch stays an
  explicit step (`fetch-update.py`, or a front-end flag that says what it
  downloads). ss-delta keeps its zip path.
* ☐ `--dump-elfs` loads only what this game loads. ss-delta's ad hoc
  matching preload becomes a ss-delta hook.
* ☐ Tools: `v3kdrive.py` takes the exe/window name as a parameter;
  `install-game.ps1` and `make-dist.ps1` take a game profile.
* ☐ Retire the D5 shim.
* ☐ Merge `shinobido-2` into one integration branch that builds both exes
  **(ss-delta)**, once ss-delta's quick check passes on it.

**Exit:** a fresh clone of this repo with `--recurse-submodules` builds
`shinobido2.exe`, which installs the game from the owner's pkg files, boots
1.02 on the JIT to the tutorial at 30 fps, and is driven by `v3kdrive.py`.
ss-delta still builds and passes its quick check (title → field), so the
shared changes broke nothing.

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

* ☐ Reproduce the SFX dropout deterministically, if possible with a saved
  game in a combat area and a scripted loop.
* ☐ Trace NGS: voices created, played, released and their states over time.
  Find what leaks: voices that never end, a voice limit, a callback never
  fired, or the game's own pool.
* ☐ Implement what the game uses that Vita3K lacks: the **envelope** module
  (the leading suspect: a voice whose envelope never ends is never
  released, **hypothesis**), **reverb**, **equalizer**, and
  `sceNgsModuleGetPreset`.
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
* ☐ AMD and NVIDIA (ss-delta's two-reference rule, its D4 update 2).

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
* ☐ **60 fps study** (optional, as in ss-delta): the frame timer and flip
  threshold, and whether game logic is frame-locked.

**Exit:** a full playthrough is possible on keyboard/controller at ≥ 2×
internal resolution, grappling hook included.

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

## Later (deferred)

* Other regions (EU PCSB00049, JP PCSG00019): the same profile with another
  title ID; regenerate per eboot.
* Modding: loose-file overrides, if the engine has them (unknown), and
  FADEBABE repacking.
* Linux / Steam Deck (shared with ss-delta).

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
| R7 | Frame-locked logic | no 60 fps | optional study only |
| R8 | GPL (Vita3K) | runtime can't be relicensed | the fork's source is published with any binary (D6); the recompiler has no Vita3K code |
| R9 | No debug menu found | slow testing of late content | saves per chapter; Vita save import |
| R10 | Game data or personal data in a pushed history | can't be taken back once public | D2; the history scan before the first push (Publishing); the scan as a pre-commit hook |
| R11 | Extracting the shared repos disturbs the finished ss-delta | regressions, lost history | `git filter-repo` keeps history; ss-delta's quick check after each step; the owner OKs each step |
