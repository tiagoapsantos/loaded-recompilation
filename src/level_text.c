#include "loaded_level_text.h"

static uint32_t read_le32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

int loaded_level_text_parse(LoadedLevelText *out, const uint8_t *data, size_t size)
{
    LoadedLevelText view;
    size_t i;
    if (!out || !data || size < 68) return 0;
    view.bytes = data;
    view.size = size;
    for (i = 0; i < 16; ++i) {
        view.offsets[i] = read_le32(data + i * 4);
        if (view.offsets[i] < 68 || view.offsets[i] >= size) return 0;
    }
    view.entry_count = read_le32(data + 64);
    if (view.offsets[0] != 68 || view.offsets[1] - view.offsets[0] != 0x40000u)
        return 0;
    if (view.offsets[2] < view.offsets[1] ||
        (uint64_t)(view.offsets[2] - view.offsets[1]) != (uint64_t)view.entry_count * 32u)
        return 0;
    *out = view;
    return 1;
}

int loaded_level_text_addresses(const LoadedLevelText *view, uint32_t ps1_base,
                                uint32_t out_addresses[16])
{
    size_t i;
    if (!view || !out_addresses) return 0;
    for (i = 0; i < 16; ++i)
        out_addresses[i] = ps1_base + view->offsets[i];
    return 1;
}
