#!/usr/bin/python3
import pandas as pd

specs_filename = "can_specification.csv"
specdf = pd.read_csv(specs_filename, keep_default_na=False)

header_filename = "lib/canlib.h"
with open(header_filename, "w") as f: 
    f.write("#ifndef CANLIB_H\n") 
    f.write("#define CANLIB_H\n") 
    for _, row in specdf.iterrows():
        field_name = row["Field Name"].split()[0].lower()
        field_type = row["Field Name"].split()[1].replace('(','').replace(')','')
        can_id = row["CAN ID"]
        f.write("\n")
        f.write(f"// {row['Field Name']}, {row['Required by Hardware']}\n")
        if row["Bounds/Range"] != '':
            f.write(f"// Bounds/Range: {row['Bounds/Range']}\n")
        if row["Units"] != '':
            f.write(f"// Units: {row['Units']}\n")
        if row["J1939?"] != '':
            f.write(f"// J1939 compatible: {row['J1939?']}\n")
        else:
            f.write(f"// J1939 compatible: NO\n")
        if row["Field Description"] != '':
            f.write("// Description: \n")
            f.write('//\t' + row['Field Description'].replace('\n','\n//\t') + "\n")
        f.write(f"#define CAN_ID_{field_name.upper()} {can_id}\n")
        f.write(f"#define BYTE_LENGTH_{field_name.upper()} {row['Byte Length']}\n")
        if row['PGN'] != '':
            f.write(f"#define PGN_{field_name.upper()} {row['PGN']}\n")
        if row['SPN'] != '':
            f.write(f"#define SPN_{field_name.upper()} {row['SPN']}\n")

    f.write("\n#endif")
    
