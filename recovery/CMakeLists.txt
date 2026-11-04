cmake_minimum_required(VERSION 3.20)
project(LoadedExperimental C CXX)
set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 17)
set(PSXRECOMP_ROOT "E:/Recompille/third_party/psxrecomp")
include("${PSXRECOMP_ROOT}/runtime/runtime.cmake")
psxrecomp_add_game_runtime(loaded-runtime
    PRELOADED_MODS_DIR "NONE"
    WINDOW_TITLE "Loaded - experimental"
    DEFAULT_GAME_CONFIG_PATH "game.toml"
    MAX_PLAYERS 2
    GEN_MARKER "generated/SLUS_000.76_dispatch.c"
    GEN_FULL_GLOB "generated/SLUS_000.76_full_*.c"
)
