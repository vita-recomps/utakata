# Compatibility

What has been played or checked on the native, no-JIT build (`dist/utakata`),
and what not yet. ✓ works, ◐ partly checked, ? not checked, ✗ broken.
Sources: the owner's playthrough (2026-10-14, Easy, AMD Radeon 760M,
scale 2, a gamepad; the last missions at 60 fps) and the test runs in
[02-baseline](02-baseline.md).

| Area | State | Notes |
|---|---|---|
| Boot, logos, opening movie, title | ✓ | 30 and 60 fps |
| New Game, difficulty, tutorials (Training) | ✓ | all tutorials, owner |
| Hub (Asuka Village): Missions, Arrow Message, Information, Tool Shelf, Options, Save/Load | ✓ | owner, every visit |
| Story missions to the ending | ✓ | all of them, one route (5:04, day 57); saves after each |
| Boss fights and their scenes | ✓ | at 60: intros and outros right, scenes after a load at 30 |
| Endings | ◐ | one ending seen; the story asks "repay my debts, or follow my revenge", so others may exist (**hypothesis**) |
| New Game+ | ✓ | from the cleared save; keeps money; Kaede playable |
| DLC (Mirror Spirits) missions | ◐ | listed after an ending; the first loads and plays; not played through |
| Playing as Kaede | ✓ | New Game+, the owner (2026-10-14) |
| Other difficulties (Normal, Hard) | ? | Easy only |
| Caution eye (front touch) | ✓ | F / right trigger, any eye colour |
| Grappling hook | ✓ | the game's own R + Circle aiming |
| Rear-touch actions | ? | none needed in the playthrough |
| Movies (SceMp4) | ✓ | logos, opening, story; the module reloads in place each time |
| Sound: music, voices, effects | ✓ | no loss over the whole story (Phase 5 fix) |
| Reverb, fade-outs | ◐ | in the fork; no scene seen that uses them |
| Saves: save, load, ten slots | ✓ | owner, four batches archived |
| Saves: `--import-save` / `--export-save` | ✓ | folder, zip, one slot or all |
| Trophies | ◐ | earned in the test install (a pop-up shown) |
| Network Jar (Near) | unplanned | needs PS Vita "near" between players, only shares resources ([D7](decisions.md)) |
| 60 fps | ✓ | missions at 60; menus, hub, results and post-load scenes at 30 |
| Generated mipmaps | ✓ | on by default: the shimmer in motion is gone (the owner) ([D8](decisions.md)) |
| NVIDIA GPUs | ? | the fork carries ss-delta's NVIDIA fixes; untested here |
| Native code against the JIT | ✓ | 0 mismatches in ~79,000 sampled calls |

## Native code against the JIT

Differential runs (the JIT re-running sampled native calls) in mission 1's
combat with a restart: 35,790 calls at 30 fps and 43,062 at 60, **none
mismatching** ([02-baseline](02-baseline.md), "Native against JIT").
