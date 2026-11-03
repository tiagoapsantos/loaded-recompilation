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
