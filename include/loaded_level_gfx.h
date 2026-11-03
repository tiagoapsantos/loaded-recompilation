#ifndef LOADED_LEVEL_GFX_H
#define LOADED_LEVEL_GFX_H
#include <stddef.h>
#include <stdint.h>

/* Borrowed view: the supplied buffer must outlive this structure. */
typedef struct {
    const uint8_t *bytes;
    size_t size;
    uint32_t header[10];
} LoadedLevelGfx;

/* Read only the outer fields observed in the supplied disc. */
int loaded_level_gfx_parse(LoadedLevelGfx *out, const uint8_t *data, size_t size);
/* Model the observed 32-bit base addition, including for zero offsets.
   Return 0 if the index is invalid; no source data is modified. */
int loaded_level_gfx_address(const LoadedLevelGfx *view, size_t index,
                             uint32_t ps1_base, uint32_t *out_address);
/* Read four raw words from one observed 16-byte record bounded by header
   offsets 4 and 5. Returns 0 for invalid ranges, index or embedded offset. */
int loaded_level_gfx_record(const LoadedLevelGfx *view, size_t index,
                            uint32_t out_words[4]);
#endif
