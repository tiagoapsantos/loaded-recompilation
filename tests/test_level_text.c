#include "loaded_level_text.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void put32(unsigned char *p, unsigned long x)
{
    p[0]=(unsigned char)x; p[1]=(unsigned char)(x>>8);
    p[2]=(unsigned char)(x>>16); p[3]=(unsigned char)(x>>24);
}
int main(void)
{
    const size_t size = 0x40044u + 32u + 1u;
    unsigned char *data = (unsigned char *)calloc(size, 1);
    LoadedLevelText view;
    uint32_t out[16];
    size_t i;
    if (!data) return 2;
    for (i=0; i<16; ++i) put32(data+i*4, 68);
    put32(data+4, 0x40044u); put32(data+8, 0x40064u); put32(data+64, 1);
    if (!loaded_level_text_parse(&view,data,size)) return 3;
    if (!loaded_level_text_addresses(&view,0x80107b98u,out)) return 4;
    if (out[0]!=0x80107bdcu || out[1]!=0x80147bdcu || out[2]!=0x80147bfcu) return 5;
    if (!loaded_level_text_addresses(&view,0xfffffff0u,out) || out[0]!=0x34u) return 6;
    if (loaded_level_text_addresses(NULL,0,out) || loaded_level_text_addresses(&view,0,NULL)) return 7;
    if (data[0]!=68 || data[4]!=0x44) return 8;
    free(data);
    puts("Relocation, 32-bit wrap, null checks and unchanged input verified");
    return 0;
}
