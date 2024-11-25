"""
This script just declares EVERYTHING before we play with assertions.
So the assertions are assumed not containing declarations, otherwise
z3 may report an error indicating that a variable is declared multiple times.
It seems to be silly. Hopes to find a better approach.
"""

from z3 import *
from utils.directoryParser import find_smt2_pairs
from checker.equivalenceChecker import check_path_equivalence

BitArraySort = ArraySort(BitVecSort(32), BitVecSort(8))

# maps symbols to BitArraySort, which plays a role as "decls" in parse_smt2_file
# see docs of parse_smt2_string

def check_path_conflict(s : Solver, O, A, B, M) -> bool:
    """
    Return 0 if the paths are conflict free, otherwise return a bit mask
    representing the conflict type.
    """
    eqOA = check_path_equivalence(s, O, A)
    eqOB = check_path_equivalence(s, O, B)
    eqAM = check_path_equivalence(s, A, M)
    eqBM = check_path_equivalence(s, B, M)
    
    assertion1 = And(Not(eqOA), Not(eqAM))
    assertion2 = And(Not(eqOB), Not(eqBM))
    assertion3 = And(Not(eqAM), Not(eqBM))
    
    res = 0
    if s.check(assertion1) == sat: res |= 1
    if s.check(assertion2) == sat: res |= 2
    if s.check(assertion3) == sat: res |= 4
    return res

def check_merge_conflict_free(dirO : str, dirA : str, dirB : str, dirM : str) -> bool:

    sym = set()
    pO = find_smt2_pairs(dirO, sym)
    pA = find_smt2_pairs(dirA, sym)
    pB = find_smt2_pairs(dirB, sym)
    pM = find_smt2_pairs(dirM, sym)

    print(f"Found {len(pO)} paths for program O")
    print(f"Found {len(pA)} paths for program A")
    print(f"Found {len(pB)} paths for program B")
    print(f"Found {len(pM)} paths for program M")

    declarations = {}
    for s in sym:
        declarations[s] = Const(s, BitArraySort)

    isConflictFree = True

    solver = Solver(logFile="z3_solver.log")

    for pathO, valueO in pO:
        solver.push()
        constraintO = parse_smt2_file(pathO, decls=declarations)
        solver.add(constraintO)
        for pathA, valueA in pA:
            solver.push()
            constraintA = parse_smt2_file(pathA, decls=declarations)
            solver.add(constraintA)
            if solver.check() == unsat:
                solver.pop()
                continue
            for pathB, valueB in pB:
                solver.push()
                constraintB = parse_smt2_file(pathB, decls=declarations)
                solver.add(constraintB)
                if solver.check() == unsat:
                    solver.pop()
                    continue
                for pathM, valueM in pM:
                    solver.push()
                    constraintM = parse_smt2_file(pathM, decls=declarations)
                    solver.add(constraintM)
                    if solver.check() == unsat:
                        solver.pop()
                        continue
                    effectO = And(parse_smt2_string(valueO, decls=declarations))
                    effectA = And(parse_smt2_string(valueA, decls=declarations))
                    effectB = And(parse_smt2_string(valueB, decls=declarations))
                    effectM = And(parse_smt2_string(valueM, decls=declarations))

                    if check_path_conflict(solver, effectO, effectA, effectB, effectM):
                        isConflictFree = False
                        break

                    solver.pop()
                if not isConflictFree: break
                solver.pop()
            if not isConflictFree: break
            solver.pop()
        if not isConflictFree: break
        solver.pop()
    return isConflictFree