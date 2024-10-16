# The purpose of this script is to convert a customized SMTLIB2-like format
# to a standard SMTLIB2 format. The customized format is used to represent 
# the output of a symbolic execution engine, which includes the variable name, 
# declaration, and value expression in a structured manner. 
# The script reads the input file line by line, extracts the relevant information, 
# and writes the equivalent SMTLIB2 format to the output file.

import re

def convert_smt2_file(input_file=None, output_file=None):
    result = []
    current_var_name = None
    current_values = []
    
    with open(input_file, 'r') as infile:
        for line in infile:
            # Look for the variable name indicated by "; name:"
            var_match = re.match(r";\s*(\w+):", line)
            if var_match:
                if current_var_name:
                    # Process the previous variable's section
                    result.append(write_section(current_var_name, current_values))
                
                # Start a new section
                current_var_name = var_match.group(1)
                current_values = []
                result.append(line.strip())  # Add the comment line
                continue
            
            # Capture the value expression under each numbered comment
            value_match = re.match(r";\s+\d+", line)
            if value_match:
                current_values.append(next(infile).strip())  # Grab the following line (expression)

        # Process the last variable section
        if current_var_name:
            result.append(write_section(current_var_name, current_values))

    # Optionally write to output file or return as string
    if output_file:
        with open(output_file, 'w') as outfile:
            outfile.write("\n".join(result) + "\n")
    else:
        return "\n".join(result)


def write_section(var_name, value_exprs):
    section = []
    
    # # Declare the dummy variable
    # dummy_var_decl = f"(declare-fun {var_name}_p () (Array (_ BitVec 32) (_ BitVec 8) ))"
    # section.append(f"(declare-fun {var_name} () (Array (_ BitVec 32) (_ BitVec 8) ))")
    # section.append(dummy_var_decl)
    
    # Generate a separate assertion per byte
    for idx, value_expr in enumerate(value_exprs):
        dummy_select = f"(select {var_name}_p (_ bv{idx} 32))"
        assertion = f"(assert (= {dummy_select} {value_expr}))"
        section.append(assertion)
    
    return "\n".join(section) + "\n"