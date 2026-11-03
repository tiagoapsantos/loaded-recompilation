#include "loaded_level_text.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    FILE *file;
    long length;
    unsigned char *data;
    LoadedLevelText view;
    int valid;
    if (argc != 2) {
        fprintf(stderr, "Usage: loaded-text-info <level TEXT.BIN>\n");
        return 2;
    }
    file = fopen(argv[1], "rb");
    if (!file) { fprintf(stderr, "Cannot open input file.\n"); return 2; }
    if (fseek(file, 0, SEEK_END) || (length = ftell(file)) < 0 || fseek(file, 0, SEEK_SET)) {
        fprintf(stderr, "Cannot determine input size.\n"); fclose(file); return 2;
    }
    data = (unsigned char *)malloc(length > 0 ? (size_t)length : 1);
    if (!data) { fprintf(stderr, "Allocation failed.\n"); fclose(file); return 2; }
    if (fread(data, 1, (size_t)length, file) != (size_t)length) {
        fprintf(stderr, "Cannot read input file.\n"); fclose(file); free(data); return 2;
    }
    fclose(file);
    valid = loaded_level_text_parse(&view, data, (size_t)length);
    if (!valid) fprintf(stderr, "Invalid or unsupported level TEXT file.\n");
    else printf("size=%zu block_offset=%u block_size=%u table_offset=%u entries=%u\n",
                view.size, view.offsets[0], view.offsets[1]-view.offsets[0],
                view.offsets[1], view.entry_count);
    free(data);
    return valid ? 0 : 1;
}
