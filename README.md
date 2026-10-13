# shinobido-2

A personal research project: a native PC port of **Shinobido 2: Revenge of
Zen** (PS Vita, US PCSE00015) by static recompilation, built from the
owner's own dump. It is a sibling of `<ss-delta>` (Soul Sacrifice Delta),
whose recompiler, Vita3K fork and tools it reuses.

> This repository contains *no* game data, *no* firmware and *no* code
> derived from the game. Everything is regenerated locally from the user's
> own dump ([D2](docs/decisions.md)). It is not published yet; it is kept
> ready to be, after a cleanup pass ([D6](docs/decisions.md)).

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

| Script | What |
|---|---|
| `tools/mkzrif.py` | zRIF (base64) from a `work.bin`, for Vita3K's `--pkg ... --zrif` |
| `tools/fadebabe.py` | Acquire's FADEBABE archives: stats, table listing, raw members |
| `tools/fetch-update.py` | lists a title's update on Sony's update server, and downloads and checks it |
| `tools/proccap/proccap.cpp` | records what one process plays to a WAV (Windows process loopback), optionally turned down so nothing is heard; build with MSVC (see the file) |
| `tools/wavstats.py` | loudness of a recording over time: RMS, peak and sound onsets per window |

Until Phase 1 moves them into a shared repo (D4), ss-delta's tools are
used from `<ss-delta>\tools` and `<ss-delta>\recomp`: `velf.py`, `inventory.py`, `imix.py` (needs this ELF's
segment offset `0x1000` and, for 1.02, exidx `0x813dfc14`), `v3kdrive.py`, `sfo.py`
and `recomp/recompile.py`.

Python dependencies: `pyyaml`, `capstone` (as ss-delta).
