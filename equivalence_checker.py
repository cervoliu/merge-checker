"""
This script just declares EVERYTHING before we play with assertions.
It seems to be silly. Hopes to find a better approach.

"""

from z3 import *
import symbolParser
import preprocesser
import os
import re

BitArraySort = ArraySort(BitVecSort(32), BitVecSort(8))

# maps symbols to BitArraySort, which plays a role as "decls" in parse_smt2_file
# see docs of parse_smt2_string

def find_smt2_pairs(directory, symbol_table):
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

def check_formula_equivalence(s : Solver, P : AstVector, Q : AstVector) -> bool:
    neg_equiv = Or(And(P, Not(Q)), And(Not(P), Q))
    return s.check(neg_equiv) == unsat

def check_equivalence(dirA : str, dirB : str) -> bool:

    sym = set()
    pA, pB = find_smt2_pairs(dirA, sym), find_smt2_pairs(dirB, sym)

    print(f"Found {len(pA)} paths for program A")
    print(f"Found {len(pB)} paths for program B")

    declarations = {}
    for s in sym:
        declarations[s] = Const(s, BitArraySort)

    isEquivalent = True

    solver = Solver(logFile="z3_solver.log")

    for pathA, valueA in pA:
        solver.push()
        constraintA = parse_smt2_file(pathA, decls=declarations)
        solver.add(constraintA)
        for pathB, valueB in pB:
            solver.push()
            constraintB = parse_smt2_file(pathB, decls=declarations)
            solver.add(constraintB)
            if solver.check() == unsat:
                solver.pop()
                continue
            
            effectA = And(parse_smt2_string(valueA, decls=declarations))
            effectB = And(parse_smt2_string(valueB, decls=declarations))

            if check_formula_equivalence(solver, effectA, effectB) == False:
                print(f"Paths {pathA} and {pathB} are not equivalent")
                isEquivalent = False
                break
            solver.pop()
        if not isEquivalent: break
        solver.pop()
    return isEquivalent