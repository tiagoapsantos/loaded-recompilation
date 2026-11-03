#include "loaded_level_gfx.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    FILE *in;
    unsigned char *data;
    long length;
    LoadedLevelGfx view;
    uint32_t value, record[4];
    size_t i, zeros=0, records;
    if (argc != 2) { fprintf(stderr, "Usage: loaded-gfx-info <level GFX.BIN>\n"); return 2; }
    in=fopen(argv[1],"rb");
    if (!in) { fprintf(stderr,"Cannot open input.\n"); return 2; }
    if (fseek(in,0,SEEK_END) || (length=ftell(in))<0 || fseek(in,0,SEEK_SET)) {
        fprintf(stderr,"Cannot determine input size.\n"); fclose(in); return 2;
    }
    data=(unsigned char *)malloc(length>0?(size_t)length:1);
    if (!data) { fclose(in); return 2; }
    if (fread(data,1,(size_t)length,in)!=(size_t)length) {
        fprintf(stderr,"Cannot read input.\n"); fclose(in); free(data); return 2;
    }
    fclose(in);
    if (!loaded_level_gfx_parse(&view,data,(size_t)length)) {
        fprintf(stderr,"Invalid or unsupported level GFX file.\n"); free(data); return 1;
    }
    for (i=0; i<view.header[3]; ++i) {
        if (!loaded_level_gfx_address(&view,i,0,&value)) { free(data); return 1; }
        if (value==0) ++zeros;
    }
    if (view.header[5] < view.header[4] || (view.header[5]-view.header[4]) % 16u) {
        fprintf(stderr,"Invalid record range.\n"); free(data); return 1;
    }
    records=(view.header[5]-view.header[4])/16u;
    for (i=0; i<records; ++i) {
        if (!loaded_level_gfx_record(&view,i,record)) {
            fprintf(stderr,"Invalid record.\n"); free(data); return 1;
        }
    }
    printf("size=%zu table_offset=%u entries=%u zero_entries=%zu records=%zu\n",
           view.size,view.header[2],view.header[3],zeros,records);
    free(data); return 0;
}
