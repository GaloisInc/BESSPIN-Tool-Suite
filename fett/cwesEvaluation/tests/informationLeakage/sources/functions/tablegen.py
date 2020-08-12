#!/usr/bin/env python3
import os
import glob

def write_prototypes(out, functions):
    def getstr(x):
        return f'struct function_result* {x}(struct smessage *msg);\n';
    for f in functions:
        out.write(getstr(f))

def write_struct(out, functions):
    for f in functions:
        out.write(f'\t\t{{ "{f}", {f} }},\n')

def main():
    funtab = open("functions.c", "w")
    files = [os.path.splitext(f)[0] for f in glob.glob("*.c")]
    def OK(x):
        return (x != "fdispatch") and (x != "functions")
    functions = list(filter(OK, files))
    funtab.write("#include \"types.h\"\n")
    funtab.write("#include \"functions.h\"\n")

    write_prototypes(funtab, functions)

    funtab.write("struct function_rec function_tab[] =\n")
    funtab.write("\t{\n")
    write_struct(funtab, functions)
    funtab.write("\t};\n")
    funtab.write("size_t n_functions = sizeof function_tab/sizeof function_tab[0];\n")


if __name__ == "__main__":
    main()

"""
struct function_result*
login(struct smessage *msg);

struct function_result*
sysconfig(struct smessage *msg);

struct function_rec function_tab[] =
    {
     { "login", login },
     { "sysconfig", sysconfig },
    };

size_t n_functions = sizeof function_tab/sizeof function_tab[0];
"""
