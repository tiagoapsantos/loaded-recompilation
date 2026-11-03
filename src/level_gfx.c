#include "loaded_level_gfx.h"

static uint32_t read_le32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

int loaded_level_gfx_parse(LoadedLevelGfx *out, const uint8_t *data, size_t size)
{
    static const unsigned pointer_indices[] = {0,1,2,4,5,6,7,8,9};
    LoadedLevelGfx view;
    size_t i, table;
    if (!out || !data || size < 40) return 0;
    view.bytes = data; view.size = size;
    for (i = 0; i < 10; ++i) view.header[i] = read_le32(data + i * 4);
    for (i = 0; i < sizeof(pointer_indices) / sizeof(pointer_indices[0]); ++i)
        if ((size_t)view.header[pointer_indices[i]] >= size) return 0;
    table = (size_t)view.header[2];
    if ((size_t)view.header[3] > (size - table) / 4) return 0;
    for (i = 0; i < (size_t)view.header[3]; ++i)
        if ((size_t)read_le32(data + table + i * 4) >= size) return 0;
    *out = view;
    return 1;
}

int loaded_level_gfx_address(const LoadedLevelGfx *view, size_t index,
                             uint32_t ps1_base, uint32_t *out_address)
{
    uint32_t offset;
    if (!view || !view->bytes || !out_address || index >= (size_t)view->header[3]) return 0;
    offset = read_le32(view->bytes + (size_t)view->header[2] + index * 4);
    *out_address = ps1_base + offset;
    return 1;
}

int loaded_level_gfx_record(const LoadedLevelGfx *view, size_t index,
                            uint32_t out_words[4])
{
    size_t begin, end, pos, i;
    uint32_t words[4];
    if (!view || !view->bytes || !out_words) return 0;
    begin = (size_t)view->header[4]; end = (size_t)view->header[5];
    if (begin > end || end > view->size || (end - begin) % 16 != 0 ||
        index >= (end - begin) / 16) return 0;
    pos = begin + index * 16;
    for (i = 0; i < 4; ++i) words[i] = read_le32(view->bytes + pos + i * 4);
    if ((size_t)words[2] >= view->size) return 0;
    for (i = 0; i < 4; ++i) out_words[i] = words[i];
    return 1;
}
