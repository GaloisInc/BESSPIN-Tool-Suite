#! /usr/bin/env python3
"""Cyberphys Can Info Generation Script
Project: SSITH CyberPhysical Demonstrator
Name: make_can_spec.py
Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>,
Michal Podhradsky <mpodhradsky@galois.com>
Date: 17 February 2021
Generates canlib.{py,h} from can_specification.csv
Use:
    ./make_canlib.py
    use the header/canlib files as needed
    Currently used:
      - canlib.h in C version of the canlib
      - canlib.py in:
        - SSITH-FETT-Target/fett/cyberPhys/canlib.py
        - SSITH-Cyberphys/scripts/cyberphys/canlib.py
"""
import pandas as pd
import re
from hashlib import md5
from datetime import date

specs_filename = "can_specification.csv"

# Calculate hash to distinguish versions
specs_md5 = md5()
with open(specs_filename, "r") as f:
    specs_md5.update(b"{f.read()}")

# date and file info
today = date.today()

outfilename_py: str = "python/canspecs.py"
file_header_py: str = f"""\"\"\"Cyberphys CAN Frames Specification
Project: SSITH CyberPhysical Demonstrator
Name: {outfilename_py}
Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
Michal Podhradsky <mpodhradsky@galois.com>
Date: {today.strftime("%d %B %Y")}
This file was created by SSITH-FETT-Target/fett/cyberPhys/canlib/make_can_spec.py
Version hash: {specs_md5.hexdigest()}
\"\"\"\n\n"""


outfilename_h: str = "lib/canspecs.h"
file_header_h: str = f"""/*
* Cyberphys CAN Frames Specification
* Project: SSITH CyberPhysical Demonstrator
* Name: {outfilename_py}
* Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
* Michal Podhradsky <mpodhradsky@galois.com>
* Date: {today.strftime("%d %B %Y")}
* This file was created by SSITH-FETT-Target/fett/cyberPhys/canlib/make_can_spec.py
* Version hash: {specs_md5.hexdigest()}
*/\n\n"""

# Open specs
specdf = pd.read_csv(specs_filename, keep_default_na=False)

def produce_can_py(can_entry):
    """generate code for a can info entry (row of csv file)"""
    cid = can_entry["CAN ID"]
    units =  can_entry["Units"]
    units = units if isinstance(units, str) else "<N/A>"
    fname =  can_entry["Field Name"]
    fdescr: str = str(can_entry["Field Description"])
    fdescr = fdescr if isinstance(fdescr, str) else "<N/A>"

    fvname = re.split("^(.*)\s\(.*\)$", fname)[1]
    var_name =  "CAN_ID_" + fvname.upper().replace(" -", "").replace(" ", "_")
    py_str = f"# Name: {fname} Units: {units}\n"\
             f"# Description: {' '.join(fdescr.splitlines())}\n"\
             f"{var_name}: int = {cid}\n\n"
    return py_str

def produce_can_h(can_entry):
    field_name = can_entry["Field Name"].split()[0].lower()
    can_id = can_entry["CAN ID"]
    py_str = "\n"
    py_str += f"// {can_entry['Field Name']}\n"
    py_str += f"// Sender: {can_entry['Sender']}\n"
    py_str += f"// Receiver: {can_entry['Receiver']}\n"
    if can_entry["Bounds/Range"] != '':
        py_str += f"// Bounds/Range: {can_entry['Bounds/Range']}\n"
    if can_entry["Units"] != '':
        py_str += f"// Units: {can_entry['Units']}\n"
    if can_entry["J1939?"] != '':
        py_str += f"// J1939 compatible: {can_entry['J1939?']}\n"
    else:
        py_str += f"// J1939 compatible: NO\n"
    if can_entry["Field Description"] != '':
        py_str += "// Description: \n"
        py_str += '//\t' + can_entry['Field Description'].replace('\n','\n//\t') + "\n"
    py_str += f"#define CAN_ID_{field_name.upper()} {can_id}\n"
    py_str += f"#define BYTE_LENGTH_{field_name.upper()} {can_entry['Byte Length']}\n"
    if can_entry['PGN'] != '':
        py_str += f"#define PGN_{field_name.upper()} {can_entry['PGN']}\n"
    return py_str

# write output file
with open(outfilename_py, 'w') as f:
    f.write(file_header_py)
    for _, row in specdf.iterrows():
        f.write(produce_can_py(row))

with open(outfilename_h, "w") as f:
    f.write(file_header_h)
    f.write("#ifndef CANSPECS_H\n")
    f.write("#define CANSPECS_H\n")
    for _, row in specdf.iterrows():
        f.write(produce_can_h(row))
    f.write("\n#endif\n")

print("Generating CANlib done!")