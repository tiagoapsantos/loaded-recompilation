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

#endif
