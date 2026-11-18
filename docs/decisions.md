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
Amended by D12: a few screenshots for the README, in
`docs/assets/screenshots/`.

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
3. **One repo per game** (`ss-delta`, `utakata`, first called `shinobido-2`): docs, game-specific
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

**Needs the owner's OK at the time:** each change inside ss-delta
(extracting `recomp/`, the submodule switch, the merged branch). The names
of the new repos are the owner's choice.

**Done (Phase 1, 2026-10-13, owner's OK for Phase 1):**

* Four repos: `vita3k` (the fork), `vita-recomp-kit` (the shared
  toolchain; `vita-recomp` was its working name), `ss-delta` and `utakata`
  (`shinobido-2` was its working name).
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
PCSA00152 ([02-baseline](02-baseline.md)). Nothing in ss-delta is
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
  * docs: absolute local paths replaced by repo-relative ones; machine
    details kept only where they matter (GPU vendor and driver);
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

**Update (owner, 2026-10-13):**

* **GitHub on purpose.** Nothing goes to GitHub before the docs cleanup
  and the owner's go-ahead. `.gitmodules` uses relative URLs (`../vita3k`),
  which resolve next to wherever the superproject came from.
* **Nothing local in the repos** (owner, 2026-10-13): no host names,
  absolute paths, machine or user names, tokens, not even in history.
  They stay outside the repos; a git-ignored `CLAUDE.local.md` brings them
  to Claude Code. The history was scrubbed of them before the GitHub
  pass.
* **Licences:** MIT for `utakata`, `ss-delta` (except its
  `patches/vita3k/`, GPL like Vita3K) and `vita-recomp-kit`; the fork
  stays GPL-2.0-or-later.
* **History rewritten** before the first push: every commit of ours by
  the old local placeholder address now carries the GitHub no-reply address (fork:
  our 49 commits only, with `--refs ... ^master`, so upstream's commits,
  signatures and IDs are unchanged). Submodule pointers and commit IDs
  quoted in docs and messages were remapped to the new IDs. The old
  histories were deleted.

## D7 — Network Jar is unplanned (accepted, 2026-10-14)

**Context:** the Network Jar trades resources between players through PS
Vita "near" (SceNearUtil), which Vita3K only stubs. It needs another Vita
nearby and adds nothing to the story.

**Decision:** not implemented; the compatibility matrix lists it as
unplanned (the owner, 2026-10-14).

## D8 — Generated mipmaps on by default (accepted, 2026-10-14)

**Context:** half of the large repeating textures ship without mips and
shimmer in motion, on a Vita too (02-baseline). Building mip chains at
upload changes the look slightly.

**Decision:** `[display] mipmaps` is on by default in shinobido2.ini: the
owner found the shimmer gone and the look right. ss-delta has the same
setting, off, as it made no visible difference there.

## D9 — Players get a setup that compiles the port on their own machine (accepted, 2026-10-15)

**Context:** the owner wants players to get a playable port without
cloning or building. Two published projects show two ways: Nebula (Super
Mario Galaxy) ships a setup that compiles the game's recompiled code on the
player's PC; Yakumo (Monster Hunter Portable 3rd HD) ships releases with
the recompiled game code built in, which works on every platform, Android
included, but distributes code derived from the game's executable.

**Decision:**

* Nebula's model: nothing derived from the game is distributed, as D2
  says. The setup downloads a pinned compiler and builds the recompiled
  modules on the player's machine from their own dump.
* A release is a setup (vita-recomp-kit `make-setup.py`, 2026-10-15):
  * Python's embeddable distribution with Tk, capstone and PyYAML;
  * the kit's tools;
  * `shinobido2.exe`, built without Qt (the fork's `VITA3K_GAMES_ONLY`).

  On the player's PC it downloads the firmware from Sony and the compiler
  (llvm-mingw's clang-cl with Microsoft's C++ runtime and Windows SDK,
  under Microsoft's licence, which the player accepts). It then installs
  the dump, recompiles and compiles the modules, and lays out the playable
  folder. GitHub Actions builds the setup from a tag
  (`.github/workflows/release.yml`) into a draft release with its SHA-256
  and a build attestation, the same as ss-delta's (its D18).
* Releases are unsigned at first, with checksums and build attestations.
* Android is built the same way: on the player's PC, for their own device
  (plan, "Android").

**Rejected:** shipping recompiled game code in releases (Yakumo's way):
it makes every platform easy, but it distributes a derivative of the
game's code.


## D10 — Linux and macOS: ss-delta's native builds and setups, shared (accepted, 2026-11-18)

**Context:** the owner asked for utakata on Linux and macOS for a 0.1.0
release on GitHub. ss-delta did the work in the shared repos (its Phases
11 and 12, D20 and D21): the fork builds every single-game executable on
Linux (`<id>.x86_64`, in the Steam Runtime 3 SDK) and on Apple Silicon
(`<id>.arm64`, with MoltenVK), the recompiled modules load with `dlopen`,
and the kit's setup compiles them on the player's machine with zig.

**Decision:**

* utakata takes all of it unchanged: the same fork and kit, the same
  setups (`setup.sh` with a desktop entry and the game added to Steam;
  `setup.command` with an app in the playable folder, Game Mode, no
  notarization), and a release workflow with three jobs, as ss-delta's.
  Nothing game-specific was needed beyond `game.json`'s Linux and macOS
  READMEs.
* The executable gets its own icon (fork `games/shinobido2/`): a throwing
  star drawn by `tools/make-icon.py`, no game artwork, as ss-delta's
  delta. The Linux desktop entry and the macOS app take theirs from it;
  the window still shows the game's `icon0.png` on Windows and Linux.
* The first release with all three setups is **0.1.0**.

**Rejected:** a Windows release only, with Linux players on Proton: the
setup would have to compile under Wine (ss-delta's 07-linux), and macOS
would have nothing.


## D11 — One program per platform, a portable folder: ss-delta's D22 for 0.1.0 (accepted, 2026-11-18)

**Context:** ss-delta changed what a release is (its D22, 0.3.0), after an
open letter from RecompLauncher's lead asking recomp ports for one
executable, everything in its folder, a tarball and a flag for everything.
The work is in the shared fork (`430e30af`) and kit (`8220643`). utakata's
0.1.0 had been tagged as a draft with the old layout (a setup that built a
separate playable folder) and not yet published.

**Decision:**

* utakata follows D22 unchanged: the release is the game's folder,
  `utakata`, in `utakata-<version>-{windows.zip, linux.tar.gz,
  macos.tar.gz}`. The one thing to start is `shinobido2.exe`,
  `shinobido2.x86_64` or `Shinobido 2 - Revenge of Zen.app`; not built yet,
  it opens the importer in `setup/`, which builds the game in that folder
  and hands back to it. Everything stays in the folder; the VC++ runtime
  ships beside `shinobido2.exe`; the command line is the front end's
  (`--game`, `--install`, `--dump`, `--set`, `--help`, ...).
* The game's own options (`--import-save`, `--export-save`, `--slot`,
  `--quiet`) are listed by `--help` (fork `games/shinobido2/`,
  `profile.usage`).
* 0.1.0 is tagged again on the new layout; the earlier draft and its tag
  are deleted, as nobody downloaded them.

**Rejected:** publishing the first 0.1.0 draft and moving to D22 in a
0.2.0: players would have had to move their saves between layouts once
for nothing.


## D12 — Screenshots of the game in the README (accepted, 2026-11-18)

**Context:** the owner asked for screenshots in the README: the main menu
and a few from missions. D2 kept every screenshot of the game out of git.

**Decision:**

* A few screenshots for the README are committed, in
  `docs/assets/screenshots/`: JPEGs at 1280×725, taken from the port
  (`shinobido2.exe` at scale 2, from the release workflow's archive) with
  `v3kdrive.py`'s `frame:` and `record:`, from copies of the owner's
  saves: the main menu, the first mission, a fight and the opening scene
  of the second-to-last mission. The README links them under
  "Screenshots".
* The pre-push leak scan blocks images as game data; a clone lets these
  through with `git config leakscan.allow 'docs/assets/screenshots/*.jpg
  docs/assets/screenshots/*.png'` (kit `fb2a5cb`; a clone's setting, never
  pushed). ss-delta's clone has the same, for screenshots it may add.
* Everything else D2 lists stays out, including any other screenshot
  (references for `tools/to-mission.py`, test captures: `build/`).
* The README's note says the repository holds no game data *apart from
  these screenshots*; the releases still hold none.

**Rejected:** hosting the pictures outside the repository (release assets):
the owner chose committing them.
