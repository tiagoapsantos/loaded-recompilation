#include "loaded_level_text.h"
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <limits.h>

static unsigned expand5(unsigned value) { return (value << 3) | (value >> 2); }

int main(int argc, char **argv)
{
    FILE *in, *out;
    long length, palette;
    char *end;
    unsigned char *data;
    unsigned char colors[16][3];
    LoadedLevelText view;
    size_t i;
    if (argc != 4) {
        fprintf(stderr, "Usage: loaded-text-preview <level TEXT.BIN> <palette index> <output.ppm>\n");
        return 2;
    }
    errno = 0;
    palette = strtol(argv[2], &end, 10);
    if (errno || end == argv[2] || *end || palette < 0 || palette > INT_MAX) {
        fprintf(stderr, "Invalid palette index.\n"); return 2;
    }
    in = fopen(argv[1], "rb");
    if (!in) { fprintf(stderr, "Cannot open input file.\n"); return 2; }
    if (fseek(in, 0, SEEK_END) || (length = ftell(in)) < 0 || fseek(in, 0, SEEK_SET)) {
        fprintf(stderr, "Cannot determine input size.\n"); fclose(in); return 2;
    }
    data = (unsigned char *)malloc(length > 0 ? (size_t)length : 1);
    if (!data) { fprintf(stderr, "Allocation failed.\n"); fclose(in); return 2; }
    if (fread(data, 1, (size_t)length, in) != (size_t)length) {
        fprintf(stderr, "Cannot read input file.\n"); fclose(in); free(data); return 2;
    }
    fclose(in);
    if (!loaded_level_text_parse(&view, data, (size_t)length) ||
        (unsigned long)palette >= view.entry_count) {
        fprintf(stderr, "Invalid input or palette out of range.\n"); free(data); return 1;
    }
    for (i = 0; i < 16; ++i) {
        size_t pos = (size_t)view.offsets[1] + (size_t)palette * 32 + i * 2;
        unsigned color = (unsigned)data[pos] | ((unsigned)data[pos+1] << 8);
        colors[i][0] = (unsigned char)expand5(color & 31u);
        colors[i][1] = (unsigned char)expand5((color >> 5) & 31u);
        colors[i][2] = (unsigned char)expand5((color >> 10) & 31u);
    }
    out = fopen(argv[3], "wb");
    if (!out) { fprintf(stderr, "Cannot open output file.\n"); free(data); return 2; }
    if (fprintf(out, "P6\n1024 512\n255\n") < 0) {
        fprintf(stderr, "Write failed.\n"); fclose(out); free(data); return 2;
    }
    for (i = 0; i < 0x40000u; ++i) {
        unsigned byte = data[(size_t)view.offsets[0] + i];
        if (fwrite(colors[byte & 15u], 1, 3, out) != 3 ||
            fwrite(colors[byte >> 4], 1, 3, out) != 3) {
            fprintf(stderr, "Write failed.\n"); fclose(out); free(data); return 2;
        }
    }
    if (fclose(out)) { fprintf(stderr, "Write failed.\n"); free(data); return 2; }
    free(data);
    return 0;
}
