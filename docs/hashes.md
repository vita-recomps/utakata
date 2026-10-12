# Input hashes (SHA-256)

The port targets **1.02** ([D3](decisions.md)). 1.00 rows are the owner's
dump, kept for the record.

| File | SHA-256 |
|---|---|
| `rom/Shinobido 2 Revenge of Zen.rar` | `c3ef4d08890a4f73e2e689edd042491e6d5f29994468fba52b605ed61870ab45` |
| game pkg `UP0700-PCSE00015_00-APP0000000000000` (1.00) | `7ab35fa8ad79110c0427acfc24dd0f50e95d569241701b3ec9c7f8c57a43acde` |
| DLC pkg `UP0700-PCSE00015_00-DLC001X000000000` | `f68ab35e33bd863e1e335498de0fb83639d9575f28477ec3dbb01f5b6e5a7fb2` |
| update pkg `UP0700-PCSE00015_00-APP0000000000000-A0102-V0100-be30a8f6…-PE.pkg` (1.02, 21,421,968 bytes; Sony's SHA-1 `fdece2d56c4dd74ac0193c5f0e1926b294bb00fd` over all but the last 32 bytes) | `660fc24e712e3d0e91ebffab23960a4c3347395901bc34293ace9b703f7bcbae` |
| `eboot.bin` 1.02 (SELF, installed) | `943a04c05234d1c8a0f1bdd694d3f715d01b643bc5361543366526909e8f4a7b` |
| `eboot.bin` 1.00 | `27354474e5811ba2d539bebf34363bcaa1093c3ec872fa76bcf10ecaa20f31e7` |
| `sce_module/libc.suprx` 1.02 | `65d6fe7216d3a3b8711ee6dc369ae52fc93af926e75c16d78711aa4e34f0959f` |
| `sce_module/libc.suprx` 1.00 | `51eede7c860ea4be9ba94cbe2a9ff79eb4eeb6ca8d873c05dc28e462871ffc94` |
| `sce_module/libfios2.suprx` 1.02 | `f0734f575bc60d52221ba73c7c67d485a317414d8fa2e5636feed88ea408664a` |
| `sce_module/libfios2.suprx` 1.00 | `e75cd7dbe51a93adc94bd07c567d2aa9c449f509ea7b6439a4ef84201abcbb16` |
| `sce_module/libult.suprx` 1.02 (unused) | `39749ed2f3f444e83cdb3d800bf1ab508c31929fa5bb8bdf039b2f038f734191` |
| `sce_module/libult.suprx` 1.00 (unused) | `2b9adb01d64e647af6aa14ad47717bccf0e44fc75846e628fded7342d8067881` |
| `volume.dat` (unchanged by 1.02) | `9306b0a3e8613134a5167e12daa3b55d07667e31dae653ee0d797e089d048a35` |
| `patch.dat` (1.02) | `7559d40e977643fdec60ff2d14ccf85e726bbd4e6a56d82c917a8c56e9a44cd4` |
| `StreamPackDLC.dat` (1.02) | `bf697af21080dc0a3ec483b454b430834262a3767d8fe592459326c8cb8b8970` |
| firmware `PSVUPDAT.PUP` 3.74 (shared with ss-delta) | `6ef6dc8da6db026f28647713e473486d770087a605c52a8d751bfca7478386cf` |
| firmware `PSP2UPDAT.PUP` (shared with ss-delta) | `f372d306a7f2711125bea29aa75cbcb1eb19724e9648478fba07b8d655b37344` |

Dumped ELFs (decrypted, relocated by Vita3K at the addresses in
[01-research](01-research.md#recompiler-probe-local)):

| ELF | SHA-256 |
|---|---|
| `eboot.elf` **1.02**, module `Ninja2PSP2_US`, NID `0xF4A4F7C3` | `e2f8c640d196e2e44f888a46573f17a0e4ac2dae815c87882e0b95be19099102` |
| `eboot.elf` 1.00, NID `0xA56EE5A6` | `7826a49a9212faeaddb582b2e28ce9a6c4b36992c00cd32d76ef9d27aea757e0` |
| `libc.elf` (at `0x80323000`; identical for 1.00 and 1.02) | `50c69179e68d81de85a5522751764cc6cece823ab559192ff0a6e3ea32f2467c` |
| `libfios2.elf` (at `0x80362000`; identical for 1.00 and 1.02) | `fd69021b6ac385e57ce8e162d786ca80c93f4cb1eefb3c906a954581940b0351` |

Recompiler code hash: 1.02 `0116ae436dadcb24`; 1.00 `5d169059e3b239dd`.

Pins: ss-delta `107fd85`; its Vita3K fork `1f100891` (branch `ss-delta`).
