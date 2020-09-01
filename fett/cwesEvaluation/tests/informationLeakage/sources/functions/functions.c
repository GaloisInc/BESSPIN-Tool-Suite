#include "types.h"
#include "functions.h"
struct function_result* mark_private(struct smessage *msg);
struct function_result* direct(struct smessage *msg);
struct function_result* declassify(struct smessage *msg);
struct function_result* classify(struct smessage *msg);
struct function_result* login(struct smessage *msg);
struct function_result* set_env(struct smessage *msg);
struct function_result* search(struct smessage *msg);
struct function_result* errorf(struct smessage *msg);
struct function_result* sysconfig(struct smessage *msg);
struct function_result* count(struct smessage *msg);
struct function_result* broadcast(struct smessage *msg);
struct function_rec function_tab[] =
	{
		{ "mark_private", mark_private },
		{ "direct", direct },
		{ "declassify", declassify },
		{ "classify", classify },
		{ "login", login },
		{ "set_env", set_env },
		{ "search", search },
		{ "errorf", errorf },
		{ "sysconfig", sysconfig },
		{ "count", count },
		{ "broadcast", broadcast },
	};
size_t n_functions = sizeof function_tab/sizeof function_tab[0];
