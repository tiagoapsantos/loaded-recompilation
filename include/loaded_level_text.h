#ifndef LOADED_LEVEL_TEXT_H
#define LOADED_LEVEL_TEXT_H

#include <stddef.h>
#include <stdint.h>

/* A borrowed view: the input buffer must remain alive while the view is used. */
typedef struct {
    const uint8_t *bytes;
    size_t size;
    uint32_t offsets[16];
    uint32_t entry_count;
} LoadedLevelText;

/* Validates the outer structure observed in the supplied disc's level files.
   Does not parse unknown sections or interpret PS1 rendering semantics. */
int loaded_level_text_parse(LoadedLevelText *out, const uint8_t *data, size_t size);

/* Produce the 16 addresses used by the observed MIPS relocation loop.
   Addition wraps modulo 2^32 like a PS1 register. The input is not modified.
   This models only that loop, not the rest of the game's initialization. */
int loaded_level_text_addresses(const LoadedLevelText *view, uint32_t ps1_base,
                                uint32_t out_addresses[16]);

#endif
