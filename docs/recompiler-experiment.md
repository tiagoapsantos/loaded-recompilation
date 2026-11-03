# PSXRecomp experiment

This is an initial, local experiment, not a working game port.

- Framework: [RetroPortingToolKit/psxrecomp](https://github.com/RetroPortingToolKit/psxrecomp), revision `c1f5cafd4102daa57b7342bec7c432aaca8981ce`.
- The upstream project declares PolyForm Noncommercial 1.0.0; review its license and dependencies before any reuse or distribution.
- Built its `psxrecomp-game` target on Windows using MSVC and CMake, with CHD support and tests disabled. This establishes that the tool builds here; it is not a test of the framework's complete runtime.
- Pointed it at the supplied `SLUS_000.76` and upstream BIOS profile. It read the expected PS-X EXE entry `0x800114e4`, load address `0x80010000`, and size `0x47000`, then produced local C and a dispatch table. The tool reported 931 dispatch entries. It generated files even with `--inspect`; choose the output path deliberately.
- The generated files contain translated game code and are excluded from this repository along with the disc and framework checkout. Do not publish generated output without resolving rights and licenses.
- Its analysis identified a function at `0x80010000`, which our earlier inspection identified as string data. This is a concrete false-positive candidate: the output needs tighter code/data boundaries and validation. Generated C is neither a verified decompilation nor proof that the game compiles or runs.
- Loaded streams `FRONT.BIN` and `GAME.BIN` over the same address (`0x80056f38`). Upstream documents overlay support, but compatibility with this game and the correctness of any overlay handling are untested.
- No runtime or executable game was built, no gameplay was tested through this framework, and no 60 FPS claim can be made. The next technical milestone is to build a minimal runtime/project, refine code boundaries and compare boot/overlay behavior with the original.

The tool's own platform and build instructions are in the upstream repository. Do not assume arbitrary new versions have the same CLI behavior or compatibility.

## Disc probe and strict generation

The upstream `probe_disc.py` identified `SLUS-00076`, 30 tracks and entry `0x800114e4`, and generated a local game configuration plus 267 first-pass entry/JAL seeds. Running `psxrecomp-game` with those seeds and `--strict` completed and produced 80 C shards and 931 dispatch entries. These are analysis/generation counts, not proof of valid functions or coverage. The output remains local and ignored.

The generation log reported that the mid-function split pre-pass **did not converge after 256 passes** and warned of possible dispatch misses, plus out-of-function control-flow warnings. The resulting program has not been linked to a runtime or run. The seed list is heuristic and overlays are still unverified. This result does not establish bootability, compatibility or frame rate; resolve and test these warnings as the build proceeds. Local paths: `build/loaded-probe/game.toml`, `build/loaded-probe/seeds.txt`, `build/loaded-probe/generation.log`, and `build/loaded-probe/generated/`.

## First Windows link and bounded boot smoke test

Built the standalone framework runtime and an experimental Windows executable with the generated Loaded main-executable C linked into it. The runtime was configured for OpenBIOS, software renderer testing, no launcher UI, no netplay and no rewind. This required SDL3, libwebp and zlib, plus local MSVC compatibility changes in the ignored framework checkout: static storage on two local constexpr flags; `/experimental:c11atomics` for C sources that need it; and C11 atomic load/store for one OpenGL renderer flag. CMake regeneration was suppressed to work around a duplicate Ninja phony output; changes to build inputs require an explicit reconfigure. These local framework changes have not been reviewed upstream or validated across platforms.

A 20-second headless smoke test loaded the `SLUS-00076` config, detected an NTSC-U disc, selected the bundled OpenBIOS and logged that execution started at `0xBFC00000`. The process was stopped after the time limit. The available log did not show that the game executable, a game overlay, the title screen or gameplay was reached. It also reported no bundled TCC overlay toolchain and fallback to an interpreter for overlay gaps. The runtime's reported overlay-region floor was `0x80057000`, while static analysis places Loaded's shared overlay base at `0x80056f38`; the 200-byte overlap needs investigation before assuming overlay compatibility.

Local artifacts include `build/loaded-native/Loaded___experimental.exe`, the project/config in `build/loaded-probe/`, and the configure, build and smoke-test logs in that directory. They are ignored and not distributed. This experimental executable is **not a playable port** and has not been benchmarked for 60 FPS. The earlier code-generation nonconvergence and control-flow warnings remain unresolved.

## Debug-server memory observations

A new build with PSX_DEBUG_TOOLS enabled answered local debug requests during a bounded headless run. At approximately 3 seconds, 16 bytes at the main entry address `0x800114e4` matched the original executable; 256 bytes at `0x80056f38` matched the beginning of `FRONT/INTRPLAY.BIN`. At approximately 10 and 20 seconds, 256 bytes at that same overlay address matched `FRONT/STREAM.BIN`. One register sample reported PC `0x800575d0` while STREAM was resident. The process was intentionally stopped after 20 seconds.

These observations demonstrate that the experimental runtime loaded the main executable bytes and changed at least those overlay bytes during startup. They do not prove that an entire overlay matches, that the front-end or gameplay is correct, that the title screen was reached, or that the code is fully recompiled. The debug build still reported that overlay gaps may use an interpreter. Frame counters in this headless experiment are not a gameplay FPS benchmark. Tests used OpenBIOS, a software renderer, and the previously documented local MSVC compatibility changes.

## First front-end and movement smoke test

Using the debug-enabled experimental Windows executable with OpenBIOS, software rendering, no audio, and automated Start/Cross input, a bounded headless test reached a recognizable main menu and then a one-player level. A 256-byte memory sample at the shared overlay address matched `FRONT/FRONT.BIN` at the menu and later matched `LOADED/GAME.BIN`. In a separate bounded run, a held Right input produced a visible change in the player's position and camera view. Screenshots and game-derived files remain local.

This is a limited smoke test, not proof of full gameplay compatibility: enemies, combat, progression, save/load, audio, and other levels have not been tested. The runtime indicated it may interpret overlay gaps; it is not evidence that all game code is statically recompiled. Headless frame counters are not a 60 FPS measurement, and the build is not ready for release. The earlier control-flow warnings and overlay boundary concern remain open.

## Longer input smoke test

A further bounded headless software-renderer run advanced from the first level's starting area after repeated directional/action inputs. Captured images show the character and camera in a different location and a visible bright effect. This indicates input and rendering progressed beyond the starting image; the test did not establish which action produced the effect, verify combat or enemy behavior, or test audio (headless audio was disabled).

As a diagnostic observation, the debug frame counter rose from 2525 at approximately 40 seconds to 2642 at 50 seconds and 2707 at 55 seconds. Those wall-clock snapshots suggest that this particular debug-enabled, software-rendered run with 4x internal-resolution settings was not maintaining a 60-per-second counter during that interval. This is not a controlled gameplay FPS benchmark: the run was headless, the meaning of the counter needs confirmation, and no comparable baseline or display-frame capture was collected. The 60 FPS performance target remains unverified.

## Captured overlay compilation check

A diagnostic run recorded 31 local capture-history files during earlier startup/gameplay tests. One 4,100-byte captured region at `0x8005c000` was passed to upstream `compile_overlays.py --check` with the local TinyCC toolchain and the experimental game's configuration. The tool reported one successful temporary shard build, three function definitions, and no unsupported-instruction TODOs in that shard. The check deleted its temporary output.

This verifies that this one captured region can be translated and compiled in isolation. It does **not** establish that the shard would load, match the correct runtime cache identity, execute correctly, cover other overlays, or improve frame rate. No generated game code or cache is included in the repository. The upstream project uses a noncommercial license; review its terms before distribution.
