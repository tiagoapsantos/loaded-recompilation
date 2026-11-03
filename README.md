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


