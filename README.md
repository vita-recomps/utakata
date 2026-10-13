# utakata

A native PC port of **Shinobido 2: Revenge of Zen** (PS Vita, US PCSE00015)
by static recompilation, built from the player's own dump. Utakata is the
land the game is set in. It is a sibling of ss-delta (Soul Sacrifice
Delta), whose recompiler, Vita3K fork and tools it shares.

Licence: MIT ([LICENSE](LICENSE)). The Vita3K fork it builds on
(`third_party/vita3k`) is GPL-2.0-or-later.

> This repository contains *no* game data, *no* firmware and *no* code
> derived from the game. Everything is regenerated locally from the user's
> own dump ([D2](docs/decisions.md)). It lives on the owner's private
> Forgejo; publishing on GitHub follows ([D6](docs/decisions.md)).

## Status

Phase 0 (research, decryption, baseline) is done:

* the PSN pkg, the DLC and update **1.02** (the target,
  [D3](docs/decisions.md)) are installed through Vita3K's `--pkg/--zrif`;
* decrypted ELFs are dumped;
* the game runs in ss-delta's Vita3K fork into gameplay at 30 fps;
* ss-delta's recompiler translates the whole 1.02 eboot unchanged (0
  unsupported instructions).

The sound-effects dropout is reproduced: it comes at about the sixth
mission load of a session. Next is Phase 1, which moves the shared toolchain
into three publishable repos: the Vita3K fork, the recompiler, and one repo
per game ([D4](docs/decisions.md)). The known hard problem is audio:
Vita3K's NGS loses sound effects after a few missions. See the
[plan](docs/03-plan.md).

## Documentation

| Doc | Contents |
|---|---|
| [01-research](docs/01-research.md) | the dump, the FADEBABE archives, the 1.00 eboot measured, prior work, differences from ss-delta |
| [02-baseline](docs/02-baseline.md) | how the game behaves in the ss-delta fork today, and how to re-run it |
| [03-plan](docs/03-plan.md) | phases, exit criteria, risks |
| [decisions](docs/decisions.md) | decision log |
| [hashes](docs/hashes.md) | input hashes and pins |

## Tools

This game's own:

| Script | What |
|---|---|
| `tools/fadebabe.py` | Acquire's FADEBABE archives: stats, table listing, raw members |

The shared toolchain is a submodule, `third_party/recomp` (D4; its README
lists everything): the recompiler (`recomp/recompile.py`), `velf.py`,
`inventory.py`, `imix.py`, `v3kdrive.py`, `sfo.py`, and, from this
project, `mkzrif.py` (zRIF from a `work.bin`), `fetch-update.py` (a
title's update from Sony's update server), `proccap` (records one
process's audio) and `wavstats.py` (loudness over time). The Vita3K fork
is the other submodule, `third_party/vita3k`. Clone with
`git clone --recurse-submodules`.

Python dependencies: `pyyaml`, `capstone` (as ss-delta).
