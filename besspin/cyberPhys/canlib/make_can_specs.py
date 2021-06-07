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
from datetime import date

class CanlibTemplate:
    can_format_dict = {
        "uint8_t": "B",
        "int8_t": "b",
        "uint16_t": "H",
        "int16_t": "h",
        "uint32_t": "I",
        "int32_t": "i",
        "float": "f",
        }
    
    # date and file info
    today = date.today()
    
    def produce_can(self, can_entry):
        pass

    def produce_ids(self, entry):
        pass

    def generate_specs(self, specs):
        with open(self.outfilename, 'w') as f:
            f.write(self.file_header)
            for _, row in specs.iterrows():
                f.write(self.produce_can(row))

    def generate_ids(self, component_ids):
        with open(self.outfilename_ids, 'w') as f:
            f.write(self.file_header_ids)
            for _, row in component_ids.iterrows():
                f.write(self.produce_ids(row))

    def generate_code(self, specs_filename, ids_filename):
        # Open specs
        specs = pd.read_csv(specs_filename, keep_default_na=False)
        self.generate_specs(specs)
        # Open IDs
        component_ids = pd.read_csv(ids_filename, keep_default_na=False)
        self.generate_ids(component_ids)
        print(f"<{self.__class__.__name__}> Generating done!")


class CanlibPy(CanlibTemplate):
    outfilename: str = "../cyberphyslib/cyberphyslib/canlib/canspecs.py"
    file_header: str = f"""\"\"\"Cyberphys CAN Frames Specification
Project: SSITH CyberPhysical Demonstrator
Name: {outfilename}
Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
Michal Podhradsky <mpodhradsky@galois.com>
Date: {CanlibTemplate.today.strftime("%d %B %Y")}
This file was created by BESSPIN-Tool-Suite/besspin/cyberPhys/canlib/make_can_spec.py
\"\"\"\n\n"""

    outfilename_ids: str = "../cyberphyslib/cyberphyslib/canlib/componentids.py"
    file_header_ids: str = f"""\"\"\"Cyberphys Component IDs
Project: SSITH CyberPhysical Demonstrator
Name: {outfilename_ids}
Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
Michal Podhradsky <mpodhradsky@galois.com>
Date: {CanlibTemplate.today.strftime("%d %B %Y")}
This file was created by BESSPIN-Tool-Suite/besspin/cyberPhys/canlib/make_can_spec.py
\"\"\"\n\n"""

    def produce_can(self, can_entry):
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
            val = self.can_format_dict[entry]
            canformat += val
        canformat += "\""

        var_name =  "CAN_ID_" + fname.upper().replace(" -", "").replace(" ", "_")
        format_name = "CAN_FORMAT_" + fname.upper().replace(" -", "").replace(" ", "_")
        return f"# Name: {fname}\n"\
            f"# Units: {units}\n"\
            f"# Type: {can_entry['Format']}\n"\
            f"# Description: {' '.join(fdescr.splitlines())}\n"\
            f"{var_name}: int = {cid}\n"\
            f"{format_name}: str = {canformat}\n\n"

    def produce_ids(self, entry):
        """generate code for a ID info entry (row of csv file)"""
        component_name = entry["Component"]
        component_id = entry["ID"]
        return f"{component_name} = {component_id}\n" 


class CanlibC(CanlibTemplate):
    outfilename: str = "lib/canspecs.h"
    file_header: str = f"""/*
* Cyberphys CAN Frames Specification
* Project: SSITH CyberPhysical Demonstrator
* Name: {outfilename}
* Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
* Michal Podhradsky <mpodhradsky@galois.com>
* Date: {CanlibTemplate.today.strftime("%d %B %Y")}
* This file was created by BESSPIN-Tool-Suite/besspin/cyberPhys/canlib/make_can_spec.py
*/\n\n"""

    outfilename_ids: str = "lib/componentids.h"
    file_header_ids: str = f"""/*
* Cyberphys Cyberphys Component IDs
* Project: SSITH CyberPhysical Demonstrator
* Name: {outfilename_ids}
* Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
* Michal Podhradsky <mpodhradsky@galois.com>
* Date: {CanlibTemplate.today.strftime("%d %B %Y")}
* This file was created by BESSPIN-Tool-Suite/besspin/cyberPhys/canlib/make_can_spec.py
*/\n\n"""

    def produce_can(self, can_entry):
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

    def produce_ids(self, entry):
        """generate code for a ID info entry (row of csv file)"""
        component_id = entry["ID"]
        component_name = entry["Component"]
        return f"#define {component_name} {component_id}\n"

    def generate_specs(self, specs):
        with open(self.outfilename, "w") as f:
            f.write(self.file_header)
            f.write("#ifndef CANSPECS_H\n")
            f.write("#define CANSPECS_H\n")
            for _, row in specs.iterrows():
                f.write(self.produce_can(row))
            f.write("\n#endif\n")

    def generate_ids(self, component_ids):
        with open(self.outfilename_ids, "w") as f:
            f.write(self.file_header_ids)
            f.write("#ifndef COMPONENT_IDS_H\n")
            f.write("#define COMPONENT_IDS_H\n")
            for _, row in component_ids.iterrows():
                f.write(self.produce_ids(row))
            f.write("\n#endif\n")


class CanlibJs(CanlibTemplate):
    outfilename: str = "lib/canspecs.js"
    file_header: str = f"""/*
* Cyberphys CAN Frames Specification
* Project: SSITH CyberPhysical Demonstrator
* Name: {outfilename}
* Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
* Michal Podhradsky <mpodhradsky@galois.com>
* Date: {CanlibTemplate.today.strftime("%d %B %Y")}
* This file was created by BESSPIN-Tool-Suite/besspin/cyberPhys/canlib/make_can_spec.py
*/\n\n"""

    outfilename_ids: str = "lib/componentids.js"
    file_header_ids: str = f"""/*
* Cyberphys Cyberphys Component IDs
* Project: SSITH CyberPhysical Demonstrator
* Name: {outfilename_ids}
* Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
* Michal Podhradsky <mpodhradsky@galois.com>
* Date: {CanlibTemplate.today.strftime("%d %B %Y")}
* This file was created by BESSPIN-Tool-Suite/besspin/cyberPhys/canlib/make_can_spec.py
*/\n\n"""

    def produce_can(self, can_entry):
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
            val = self.can_format_dict[entry]
            canformat += val
        canformat += "\""

        var_name =  "CAN_ID_" + fname.upper().replace(" -", "").replace(" ", "_")
        return f"// Name: {fname}\n"\
            f"// Units: {units}\n"\
            f"// Type: {can_entry['Format']}\n"\
            f"// Description: {' '.join(fdescr.splitlines())}\n"\
            f"const {var_name} = {cid}\n\n"

    def produce_ids(self, entry):
        """generate code for a ID info entry (row of csv file)"""
        component_name = entry["Component"]
        component_id = entry["ID"]
        return f" const {component_name} = {component_id}\n" 


specs_filename = "can_specification.csv"
ids_filename = "component_ids.csv"

cl = CanlibPy()
cl.generate_code(specs_filename, ids_filename)

cl = CanlibC()
cl.generate_code(specs_filename, ids_filename)

cl = CanlibJs()
cl.generate_code(specs_filename, ids_filename)
