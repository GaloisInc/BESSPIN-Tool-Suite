#ifndef _SRC_SAFE_STRSTR_H
#define _SRC_SAFE_STRSTR_H
#include <string.h>

/*
 * Find the first occurrence of find in s, where the search is limited to the
 * first slen characters of s.
 */
char* safe_strstr(const char *s, const char *find, size_t slen);
#endif
