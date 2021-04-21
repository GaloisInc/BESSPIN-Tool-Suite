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
"""
import pandas as pd
import re
from hashlib import md5
from datetime import date

specs_filename = "can_specification.csv"
ids_filename = "component_ids.csv"

# Calculate hash to distinguish versions
specs_md5 = md5()
with open(specs_filename, "r") as f:
    specs_md5.update(b"{f.read()}")

ids_md5 = md5()
with open(ids_filename, "r") as f:
    specs_md5.update(b"{f.read()}")

# date and file info
today = date.today()

outfilename_py: str = "../cyberphyslib/cyberphyslib/canlib/canspecs.py"
file_header_py: str = f"""\"\"\"Cyberphys CAN Frames Specification
Project: SSITH CyberPhysical Demonstrator
Name: {outfilename_py}
Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
Michal Podhradsky <mpodhradsky@galois.com>
Date: {today.strftime("%d %B %Y")}
This file was created by BESSPIN-Tool-Suite/besspin/cyberPhys/canlib/make_can_spec.py
Version hash: {specs_md5.hexdigest()}
\"\"\"\n\n"""

outfilename_ids_py: str = "../cyberphyslib/cyberphyslib/canlib/componentids.py"
file_header_ids_py: str = f"""\"\"\"Cyberphys Component IDs
Project: SSITH CyberPhysical Demonstrator
Name: {outfilename_py}
Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
Michal Podhradsky <mpodhradsky@galois.com>
Date: {today.strftime("%d %B %Y")}
This file was created by BESSPIN-Tool-Suite/besspin/cyberPhys/canlib/make_can_spec.py
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
* This file was created by BESSPIN-Tool-Suite/besspin/cyberPhys/canlib/make_can_spec.py
* Version hash: {specs_md5.hexdigest()}
*/\n\n"""

outfilename_ids_h: str = "lib/componentids.h"
file_header_ids_h: str = f"""/*
* Cyberphys Cyberphys Component IDs
* Project: SSITH CyberPhysical Demonstrator
* Name: {outfilename_py}
* Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
* Michal Podhradsky <mpodhradsky@galois.com>
* Date: {today.strftime("%d %B %Y")}
* This file was created by BESSPIN-Tool-Suite/besspin/cyberPhys/canlib/make_can_spec.py
* Version hash: {specs_md5.hexdigest()}
*/\n\n"""


# Open specs
specdf = pd.read_csv(specs_filename, keep_default_na=False)
# Open IDs
component_ids = pd.read_csv(ids_filename, keep_default_na=False)

def produce_can_py(can_entry):
    """generate code for a can info entry (row of csv file)"""
    cid = can_entry["CAN ID"]
    units =  can_entry["Units"]
    units = units if isinstance(units, str) else "<N/A>"
    fname =  can_entry["Field Name"]
    fdescr: str = str(can_entry["Field Description"])
    fdescr = fdescr if isinstance(fdescr, str) else "<N/A>"
    canformat_raw = can_entry["Format"].split('|')
    canformat = '"!'
    for entry in canformat_raw:
        entry = entry.strip()
        if entry == "uint8_t":
            f = "B"
        elif entry == "int8_t":
            f = "b"
        elif entry == "uint16_t":
            f = "H"
        elif entry == "int16_t":
            f = "h"
        elif entry == "uint32_t":
            f = "I"
        elif entry == "int32_t":
            f = "i"
        elif entry == "float":
            f = "f"
        canformat = canformat + f + '"'

    var_name =  "CAN_ID_" + fname.upper().replace(" -", "").replace(" ", "_")
    format_name = "CAN_FORMAT_" + fname.upper().replace(" -", "").replace(" ", "_")
    return f"# Name: {fname}\n"\
           f"# Units: {units}\n"\
           f"# Type: {can_entry['Format']}\n"\
           f"# Description: {' '.join(fdescr.splitlines())}\n"\
           f"{var_name}: int = {cid}\n"\
           f"{format_name}: str = {canformat}\n\n"

def produce_ids_py(entry):
    """generate code for a ID info entry (row of csv file)"""
    component_name = entry["Component"]
    component_id = entry["ID"]
    return f"{component_name} = {component_id}\n" 


def produce_can_h(can_entry):
    """generate code for a can info entry (row of csv file)"""
    field_name = can_entry["Field Name"].lower()
    can_id = can_entry["CAN ID"]
    py_str = "\n"
    py_str += f"// {can_entry['Field Name']}\n"
    py_str += f"// Type: {can_entry['Format']}\n"
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
        py_str += "//\n"
        py_str += '// ' + can_entry['Field Description'].replace('\n','\n//\t') + "\n"
    py_str += f"#define CAN_ID_{field_name.upper()} {can_id}\n"
    py_str += f"#define BYTE_LENGTH_{field_name.upper()} {can_entry['Byte Length']}\n"
    if can_entry['PGN'] != '':
        py_str += f"#define PGN_{field_name.upper()} {can_entry['PGN']}\n"
    return py_str

def produce_ids_h(entry):
    """generate code for a ID info entry (row of csv file)"""
    component_id = entry["ID"]
    component_name = entry["Component"]
    return f"#define {component_name} {component_id}\n"

# 
# Python implementation
#
with open(outfilename_py, 'w') as f:
    f.write(file_header_py)
    for _, row in specdf.iterrows():
        f.write(produce_can_py(row))

with open(outfilename_ids_py, 'w') as f:
    f.write(file_header_ids_py)
    for _, row in component_ids.iterrows():
        f.write(produce_ids_py(row))

# 
# C implementation
#
with open(outfilename_h, "w") as f:
    f.write(file_header_h)
    f.write("#ifndef CANSPECS_H\n")
    f.write("#define CANSPECS_H\n")
    for _, row in specdf.iterrows():
        f.write(produce_can_h(row))
    f.write("\n#endif\n")

with open(outfilename_ids_h, "w") as f:
    f.write(file_header_ids_h)
    f.write("#ifndef COMPONENT_IDS_H\n")
    f.write("#define COMPONENT_IDS_H\n")
    for _, row in component_ids.iterrows():
        f.write(produce_ids_h(row))
    f.write("\n#endif\n")


print("Generating CANlib done!")
