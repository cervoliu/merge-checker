import re

# Actually it's a hack here. only finds all symbols immediately following 'select'
# But that's enough for our special-formatted smt files.
select_pattern = r'\(select\s+([a-zA-Z_][a-zA-Z0-9_]*)'

def parse_symbol_str(script_content : str):
    return set(re.findall(select_pattern, script_content))
def parse_symbol_file(script_file):
    with open(script_file, 'r') as f:
        script_content = f.read()
    return set(re.findall(select_pattern, script_content))