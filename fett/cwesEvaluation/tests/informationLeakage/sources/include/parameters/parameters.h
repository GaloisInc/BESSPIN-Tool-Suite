#define NDOMAINS 1
#define STORE_SIZE 2

#define PAD "___"
#define SECRET_TEXT "#!SECRET#!"
#define SECRET_PATTERN PAD SECRET_TEXT PAD
#define NOT_SECRET     PAD "BG" PAD
#define PATTERN_SIZE (2*sizeof(PAD) + sizeof(SECRET_TEXT) - 2)

#define __IEX_GEN__STATIC_SECRET__
#define __IEX_GEN__ARRAYS__
