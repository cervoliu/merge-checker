"""
This script just declares EVERYTHING before we play with assertions.
So the assertions are assumed not containing declarations, otherwise
z3 may report an error indicating that a variable is declared multiple times.
It seems to be silly. Hopes to find a better approach.
"""

from z3 import *
from utils.directoryParser import find_smt2_pairs

BitArraySort = ArraySort(BitVecSort(32), BitVecSort(8))

# maps symbols to BitArraySort, which plays a role as "decls" in parse_smt2_file
# see docs of parse_smt2_string

def check_path_equivalence(s : Solver, P, Q) -> bool:
    neg_equiv = Or(And(P, Not(Q)), And(Not(P), Q))
    return s.check(neg_equiv) == unsat

def check_program_equivalence(dirA : str, dirB : str) -> bool:

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

            if check_path_equivalence(solver, effectA, effectB) == False:
                print(f"Paths {pathA} and {pathB} are not equivalent")
                isEquivalent = False
                break
            solver.pop()
        if not isEquivalent: break
        solver.pop()
    return isEquivalent