import utils.symbolParser as symbolParser
import utils.preprocesser as preprocesser
import os
import re

def find_smt2_pairs(directory : str, symbol_table : set) -> list:
    """
    parse a directory to get path constraint and effect pairs.
    returns a list of pairs, (fst, snd).
    Especially note that snd is a string that holds the actual content
    """
    # Regular expression to match files like pathX.smt2 and valueX.smt2
    path_pattern = re.compile(r'path(\d+)\.smt2')
    value_pattern = re.compile(r'value(\d+)\.smt2')

    # Dictionary to store the pairs
    pairs = {}

    # List all files in the directory
    for filename in os.listdir(directory):
        path_match = path_pattern.match(filename)
        value_match = value_pattern.match(filename)
        
        if path_match:
            num = path_match.group(1)
            if num in pairs:
                pairs[num]['path'] = filename
            else:
                pairs[num] = {'path': filename}

        elif value_match:
            num = value_match.group(1)
            if num in pairs:
                pairs[num]['value'] = filename
            else:
                pairs[num] = {'value': filename}

    # Only keep pairs where both path and value are found
    complete_pairs = [(v['path'], v['value']) for k, v in pairs.items() if 'path' in v and 'value' in v]
    
    # registry the symbol_table
    res_pairs = []
    for path, value in complete_pairs:
        fst = os.path.join(directory, path)
        snd = os.path.join(directory, value)
        script = preprocesser.convert_smt2_file(snd)
        res_pairs.append((fst, script))

        for symbol in symbolParser.parse_symbol_file(fst):
            symbol_table.add(symbol)
        for symbol in symbolParser.parse_symbol_str(script):
            symbol_table.add(symbol)
    return res_pairs