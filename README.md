# Loaded recompilation research

An early-stage, independent reverse-engineering project investigating the PlayStation game *Loaded* and the work required for a potential native Windows port. There is currently **no playable Windows build** or reconstructed game source.

## Current work

- Disc extraction and inventory of game files and CD audio.
- Analysis containers for the main MIPS executable and its dynamically loaded overlays.
- Research tools for inspecting level texture containers and generating experimental texture-sheet previews.

This repository contains research tools and documentation only. It does **not** contain the game, disc images, extracted assets, disassembly, or generated previews. You must supply your own game files. This project is not affiliated with the game's creators or rights holders.

## Requirements

Python 3 is required. The texture preview tool also requires Pillow. The scripts operate on locally supplied disc images or files and write analysis artifacts locally. Their assumptions are based on the specific disc examined during this project; other versions may differ.

## Tools

- `tools/extract_disc.py`: extract ISO 9660 files from a raw Mode 2 disc image and write an inventory. Preserve the original image; audio tracks and Form 2 sectors require special handling.
- `tools/extract_audio.py`: split CUE audio tracks into raw sector files.
- `tools/psxexe_to_elf.py`, `tools/overlay_to_elf.py`, and `tools/combined_elf.py`: create analysis-only MIPS ELF containers. These are not Windows executables or complete runtime snapshots.
- `tools/disasm_mips.py` and `tools/inventory_exe.py`: limited static inspection; results are heuristic and may include false positives.
- `tools/asset_catalog.py`: inventory level and player files on the supplied disc.
- `tools/extract_level_text.py`: split a known level TEXT container into byte-preserving sections.
- `tools/inspect_level_gfx.py`: inspect observed level graphics offset tables.
- `tools/preview_level_texture.py`: render an experimental single-palette texture-sheet preview. Palette selection, transparency and blending do not yet match the game.

Each script supports `--help`. Generated data belongs in the ignored `disc/` and `analysis/` folders. Avoid uploading copyrighted game contents or generated game imagery.

## Status

This is exploratory work. A native Windows version would require extensive additional analysis, code reconstruction, platform implementation, and testing.



## Native asset reader

The C library in `src/level_text.c` validates the observed outer TEXT container, and `loaded-text-info` reports its key offsets. This is a research utility and first native building block, not game code or a Windows game. It was compiled with MSVC and checked against all 15 supplied level TEXT files and an invalid input. The parser borrows its input buffer and does not interpret the unknown sections.

Build with CMake and a C compiler:

```powershell
cmake -S . -B build
cmake --build build --config Release
build/Release/loaded-text-info.exe disc/LEVELS/L1TEXT.BIN
```

The supplied PlayStation disc was started manually in DuckStation 0.1-12442 and reached the title screen. The emulator reported 60 FPS at the time of inspection. This verifies an emulated boot only; the memory observations and a native Windows build remain unverified.

`loaded-text-preview` is a native C utility that writes a 1024x512 PPM texture-sheet preview from a local level TEXT file. It uses a single selected 16-color palette and renders opaque RGB; it does not reproduce per-texture palette selection or PS1 transparency. For example:

```powershell
build/Release/loaded-text-preview.exe disc/LEVELS/L1TEXT.BIN 0 analysis/L1-preview.ppm
```

The MSVC build was compared pixel-for-pixel against the Python preview for two palettes in each of the 15 supplied levels; invalid palette selections were also rejected.

The 60 FPS report was a single observation at the title screen, not a gameplay benchmark or evidence of a constant 60 FPS on original hardware. Gameplay performance, emulator settings, and timing remain to be tested, including during heavy action.

Performance target: 60 distinct rendered frames per second during demanding gameplay, without changing game speed. See [performance validation](docs/performance.md). This remains an unverified target until a native build exists and is benchmarked.

`tools/analyze_frame_times.py` summarizes captured frame timestamps and identifies frame-time spikes. See [performance validation](docs/performance.md) for its CSV format and limitations.

The native TEXT library also models the observed 16-entry PS1 address-relocation loop: `loaded_level_text_addresses` computes the addresses from a validated file view and a supplied emulated base, using 32-bit wraparound. It does not modify the source or implement the remaining initialization code. A C test checks representative values, wraparound and invalid arguments; run it with `ctest --test-dir build -C Release` after building with CMake.

`loaded-gfx-info` and `loaded_level_gfx` inspect the observed level GFX header and its nested offset table. They preserve the source bytes and model 32-bit base addition for entries, including zero offsets. The native reader was compared with the Python inspector across all 15 supplied level GFX files and tested with malformed tables. This does not yet decode geometry or render levels.

The GFX routine also walks 16-byte records between the file-relative offsets in header words 4 and 5, adding the file base to the third 32-bit word in each record. `loaded_level_gfx_record` exposes those four raw words with bounds checks. The range and embedded offsets were checked across all 15 supplied levels. The meaning of the fields and the data they reference is not yet established; runtime confirmation remains pending.

An experimental local build of PSXRecomp has parsed the main executable and generated unvalidated C. See [the experiment notes](docs/recompiler-experiment.md) for limitations, the concrete false-positive candidate, and upstream licensing. No game-derived output is included in this repository.

A disc-specific first-pass seed list has been generated locally. Strict code generation completed but reported a nonconvergent control-flow pass and possible dispatch misses; the generated code has not been linked or executed. See [experiment notes](docs/recompiler-experiment.md).

An experimental Windows executable linking the generated main-executable code has been built locally. A bounded headless test reached BIOS execution, but did not confirm the game's entry point or title screen. It is not a playable release; see [experiment notes](docs/recompiler-experiment.md).

A debug-enabled headless run has since confirmed that the main executable bytes are present in guest memory and that 256-byte samples of two startup overlays match the supplied disc files at their expected address. This does not yet establish a correct title screen, playable game, or 60 FPS.
