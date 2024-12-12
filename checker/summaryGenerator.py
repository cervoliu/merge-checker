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

def get_merge_summary(dirO : str, dirA : str, dirB : str):

    sym = set()
    pO = find_smt2_pairs(dirO, sym)
    pA = find_smt2_pairs(dirA, sym)
    pB = find_smt2_pairs(dirB, sym)

    print(f"Found {len(pO)} paths for program O")
    print(f"Found {len(pA)} paths for program A")
    print(f"Found {len(pB)} paths for program B")

    declarations = {}
    for s in sym:
        declarations[s] = Const(s, BitArraySort)

    summary = []
    solver = Solver(logFile="get_merge_summary.log")
    record = []

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
                pc = And(And(constraintO), And(constraintA), And(constraintB))
                pc = simplify(pc)
                # print(pc)
                effectO = simplify(And(parse_smt2_string(valueO, decls=declarations)))
                effectA = simplify(And(parse_smt2_string(valueA, decls=declarations)))
                effectB = simplify(And(parse_smt2_string(valueB, decls=declarations)))

                eqOA =  check_path_equivalence(solver, effectO, effectA)
                eqOB =  check_path_equivalence(solver, effectO, effectB)
                eqAB =  check_path_equivalence(solver, effectA, effectB)

                if not eqOA and not eqOB and not eqAB:
                    print("Intrinsic semantic conflict. No merge possible")
                    exit(0)
                if eqOA:
                    record.append('B')
                    summary.append(And(pc, effectB))
                elif eqOB or eqAB:
                    record.append('A')
                    summary.append(And(pc, effectA))

                solver.pop()
            solver.pop()
        solver.pop()
    return record