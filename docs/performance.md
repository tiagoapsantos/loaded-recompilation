# Performance goal and validation

The target for the prospective native Windows port is **60 distinct rendered frames per second in representative heavy gameplay**, without unintentionally changing game speed, input response, animation, or audio timing. This is a target, not a result: there is no playable native port or gameplay benchmark yet.

## Baseline

- Record the game/disc revision, emulator version, BIOS region, renderer, resolution, display refresh rate, CPU overclock, speed settings, and host hardware.
- Compare the same repeatable sequences, including idle/menu, traversal, and a demanding encounter with multiple enemies and explosions. Describe how to reproduce each scene.
- Start with normal emulation settings. Record game frame rate, video/presentation rate, emulation speed and frame times separately where available. Count distinct output frames when needed; output refresh alone is not proof of 60 unique game frames.
- Optionally compare modest emulator CPU overclocks in separate runs. Overclocking is a diagnostic experiment, not a guarantee of 60 FPS or a substitute for a native Windows port; check for changes in timing, audio and gameplay.

## Windows target

- Benchmark the same scenarios over repeatable runs. Capture frame-time traces and report average FPS, frame-time percentiles, and visible or measured hitches; state test duration and hardware.
- Define a concrete frame-time threshold and acceptable outlier budget once a runnable build and representative workloads exist. Avoid claiming 60 FPS stable based solely on a short average or a menu.
- Validate gameplay speed, physics, input, animation and audio independently when decoupling game updates from rendering. Compare against the original and check that increasing the render rate does not accelerate game logic.
- Keep original game assets local. Record benchmark results without publishing disc contents.
