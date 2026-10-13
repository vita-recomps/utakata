# Decisions

Irreversible or expensive choices, newest last. Ones marked **proposed** wait
for the owner.

## D1 — The ss-delta approach: AOT-recompiled code in a Vita3K fork, then native code alone (proposed, 2026-10-12)

**Context:** [01-research](01-research.md). The ss-delta toolchain
(recompiler, AOT runtime, NativeCPU, single-game front end) is proven on
Soul Sacrifice Delta and translates this game's eboot unchanged. Vita3K
runs the game to gameplay at 30 fps.

**Decision:**

* Reuse ss-delta's design end to end: ss-delta D1 (hybrid with dynarmic as
  fallback and oracle), D6 (Python generator, C++ runtime), D7 (DLLs at JIT
  block boundaries), D8 (relocatable modules generated at their load
  addresses), D10 (a single-game executable in the fork), D11 (NativeCPU,
  firmware modules recompiled), D12 (shaders compiled in the background).
* D9 (fibers) does not apply: the game uses no ULT.

**Consequences:** the runtime is GPL-2.0-or-later (Vita3K), as for ss-delta.

## D2 — Nothing derived from the dump or firmware is committed (carried over from ss-delta D2, 2026-10-12)

**Decision:** none of the following go into git: extracted or decrypted
files, pkgs, licences (`work.bin`, `.rif`, zRIFs), ELFs, generated C++,
analysis databases, screenshots or logs of the game, firmware. Hashes,
addresses, names and notes are fine. `.gitignore` enforces the file types.

## D3 — Target the US 1.02 update (accepted, 2026-10-12)

**Context:** the owner's dump is 1.00 (PCSE00015). The final US update,
1.02, is still on Sony's update server. Its notes say it adds DLC support
and "downloadable content missions" ([01-research](01-research.md#versions-and-regions)).

**Decision (owner, 2026-10-12):**

* 1.02 is fetched from Sony's update server (`third_party/recomp/tools/fetch-update.py`) and
  installed over 1.00 with the game's zRIF.
* It is the only analysis and port target. Its eboot's module NID
  (`0xF4A4F7C3`) and hashes are in [hashes](hashes.md).
* 1.00 stays as the record of the dump (`extracted/app-1.00-PCSE00015/`,
  `extracted/elf-1.00/`).

**Why:** it is the final version, and without it the Mirror Spirits DLC
probably unlocks nothing.

**Result:** the 1.02 eboot is 0.6% larger, adds two imports and recompiles
just like 1.00; libc and libfios2 are unchanged
([01-research](01-research.md#update-102-local)). Installing the patch from
the user's files is part of the front end's install path (Phase 1).

## D4 — Share the toolchain with ss-delta through three publishable repos (accepted, 2026-10-12)

**Context:** almost everything that makes ss-delta work is game-agnostic.
The recompiler (`recomp/`) and the AOT runtime in the fork have no title ID,
module name or address in their logic. Game-specific code is confined to:

* `vita3k/ss-delta/` in the fork;
* `install-game.ps1`, `make-dist.ps1`, `v3kdrive.py`'s window name;
* `recomp/CMakeLists.txt`'s `SSD_ROOT` and `ssd_aot_` names, `imix.py`'s
  segment offset and exidx;
* SSD's asset tools.

The owner intends to publish both projects on GitHub ([D6](#d6--publish-the-working-repos-after-a-cleanup-accepted-as-direction-2026-10-12)),
so the sharing has to work for someone who clones from GitHub, not only on
this machine.

**Decision:** three kinds of repo, each pinned by commit:

1. **The Vita3K fork**, to be published as a GitHub fork of
   `Vita3K/Vita3K`. It holds the generic Vita3K fixes, the AOT/NativeCPU
   runtime and the **shared single-game front end** with one profile per
   game (title ID, window and exe name, icon, ini defaults, hooks for
   game-specific features). It builds `ss-delta.exe` and `shinobido2.exe`.
   * End state: **one integration branch for both games**, so each fix
     reaches both and each game repo pins a commit of the same branch.
   * Until the owner OKs changes on ss-delta's side, this game's work goes
     on a `shinobido-2` branch from the `ss-delta` tip (`4704fc6c`, patch
     0042). It is merged once ss-delta's quick check (title → field) passes
     on it.
   * Update (2026-10-13): the owner considers ss-delta done (NVIDIA fixed,
     60 fps), apart from Linux/macOS builds and a settings menu. Both are
     shared-toolchain work and come after this restructuring, so they are
     built once for both games (plan, "Shared work after Phase 1").
2. **The recompiler and shared tools**, extracted from ss-delta in Phase 1
   with their history: `recomp/` (generator, runtime headers, CMake,
   dynarmic tests) and the game-agnostic tools (`velf.py`, `inventory.py`,
   `imix.py`, `v3kdrive.py`, `sfo.py`, and this repo's `mkzrif.py` and
   `fetch-update.py`). Hard-coded game values become parameters.
3. **One repo per game** (`ss-delta`, `shinobido-2`): docs, game-specific
   tools and scripts, with 1 and 2 as git submodules (`third_party/vita3k`,
   `third_party/recomp`).

Locally each game repo has its own submodule checkouts, so the two games
build independently. Disk space is not a constraint.

**Rejected:**

* A per-game public release repo exported one-way from private research
  repos (owner, 2026-10-12): maintaining two sets of repos is more awkward
  in the long run than cleaning up the working ones.
* Using ss-delta's tools by absolute path (the earlier proposal): it can't
  be cloned from GitHub.
* A full copy of ss-delta's recomp and fork into this repo: two copies of
  ~40 patches and of the NEON layer would drift. Fixes found here (for
  example libpvf's forms) would not reach ss-delta.
* Starting from upstream Vita3K: it would redo Phases 1–6 of ss-delta for
  nothing.

**Needs the owner's OK at the time:** each change inside `<ss-delta>`
(extracting `recomp/`, the submodule switch, the merged branch). The names
of the new repos are the owner's choice.

**Done (Phase 1, 2026-10-13, owner's OK for Phase 1):**

* Hubs (bare repos, stand-ins for GitHub until publishing) in `<git>\`:
  `vita3k.git` (the fork), `vita-recomp.git` (the shared toolchain),
  `ss-delta.git` and `shinobido-2.git`. `vita-recomp` is a working name;
  renaming before publishing is cheap.
* The fork's integration branch is **`games`**: ss-delta's branch plus the
  shared single-game frontend (`vita3k/game-frontend/`, one exe per game
  in `vita3k/games/<id>/`). Both game repos track it. The old `ss-delta`
  and `shinobido-2` branches stay as history.
* `vita-recomp` (history extracted from ss-delta) holds the recompiler,
  the analysis and driving tools, and the Python build, install and
  packaging scripts, which read each game's `game.json`.
* ss-delta switched on 2026-10-13 (its D17): both submodules, its
  PowerShell build/install/dist scripts replaced, checked from Stage
  Select into a quest on native code with the 60 fps loading-screen
  switch.

## D5 — Phase 0 runs through a shim of `ss-delta.exe` (accepted as a stopgap, 2026-10-12)

**Context:** an ELF dump and a baseline were needed before any fork work.

**Decision:** a copy of `ss-delta.exe` in `build/ssd-shim/`, JIT only, with
its own ini and a junction file system that presents PCSE00015 as
PCSA00152 ([02-baseline](02-baseline.md)). Nothing in `<ss-delta>` is
changed.

**Consequences:** it is retired by Phase 1's `shinobido2.exe`. Results from
it are valid for the JIT path only.

## D6 — Publish the working repos after a cleanup (accepted as direction, 2026-10-12)

**Context:** the owner may publish both projects on GitHub later, and
prefers publishing the cleaned-up working repos to keeping separate release
repos.

**Decision:**

* The repos named in [D4](#d4--share-the-toolchain-with-ss-delta-through-three-publishable-repos-accepted-2026-10-12)
  are written from now on as if public. D2 is unchanged: no game data,
  firmware, licences or generated code, ever. Every user builds from their
  own dump.
* **Licences:**
  * the fork stays GPL-2.0-or-later with Vita3K's notices, and every
    published binary must be buildable from a public tag;
  * the recompiler repo and the game repos take a licence of the owner's
    choice. The recompiler contains no Vita3K code (its tests link
    dynarmic, which is 0BSD), so a permissive licence is possible;
  * generated C++ and recompiled DLLs are derived from the game and are
    never distributed.
* **Before the first push of any repo**, a cleanup pass (plan,
  "Publishing"):
  * scan the whole history, not only the tip, for D2 file types, large
    blobs, zRIF-like base64, `work.bin`/`.rif` contents and personal data.
    Rewrite the history (only before the first push) if anything is found;
  * docs: absolute local paths (`<ss-delta>`, `<user>\…`) replaced by
    repo-relative ones; machine details kept only where they matter (GPU
    vendor and driver);
  * the commit identity checked: commits carry the author name and email
    configured when they are made (ss-delta's use a local placeholder
    address).
* Timing is the owner's call. Nothing is pushed without it.

**Consequences:**

* The README's "private and non-distributed" becomes "contains no game
  data; bring your own dump". Risk R8 changes from "moot" to "met by
  publishing the fork's source".
* Install paths must work for strangers: the front end installs from the
  user's own pkg/zip, `work.bin` and PUPs, and fetches nothing behind their
  back (the update is fetched by an explicit command).
