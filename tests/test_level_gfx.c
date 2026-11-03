#include "loaded_level_gfx.h"
#include <stdio.h>
#include <string.h>

static void put32(unsigned char *p, uint32_t x)
{
    p[0]=(unsigned char)x; p[1]=(unsigned char)(x>>8);
    p[2]=(unsigned char)(x>>16); p[3]=(unsigned char)(x>>24);
}
int main(void)
{
    unsigned char data[64] = {0}, original[64];
    LoadedLevelGfx view;
    uint32_t address;
    put32(data+8,40); put32(data+12,2); put32(data+40,0); put32(data+44,60);
    memcpy(original,data,sizeof(data));
    if (!loaded_level_gfx_parse(&view,data,sizeof(data))) return 1;
    if (!loaded_level_gfx_address(&view,0,0x80107b98u,&address) || address!=0x80107b98u) return 2;
    if (!loaded_level_gfx_address(&view,1,0xfffffff0u,&address) || address!=0x2cu) return 3;
    if (loaded_level_gfx_address(&view,2,0,&address)) return 4;
    if (memcmp(data,original,sizeof(data))) return 5;
    put32(data+44,64);
    if (loaded_level_gfx_parse(&view,data,sizeof(data))) return 6;
    put32(data+8,63);
    if (loaded_level_gfx_parse(&view,data,sizeof(data))) return 7;
    puts("Zero offset, wrap, bounds, malformed tables and input preservation verified");
    return 0;
}
