import os
from checker.equivalenceChecker import check_program_equivalence
from checker.summaryGenerator import get_merge_summary
import getEdits
import shutil

def handle_trivial():
    # handle trivial cases
    if check_program_equivalence(f"{tmp}/A", f"{tmp}/B", verbose=False):
        shutil.copyfile(sourceA_path, os.path.join(source_dir_path, "merge.c"))
        print("A and B are semantically equivalent, simply adopt either")
        exit(0)
    if check_program_equivalence(f"{tmp}/A", f"{tmp}/O", verbose=False):
        shutil.copyfile(sourceB_path, os.path.join(source_dir_path, "merge.c"))
        print("A and O are semantically equivalent, simply adopt B")
        exit(0)
    if check_program_equivalence(f"{tmp}/B", f"{tmp}/O", verbose=False):
        shutil.copyfile(sourceA_path, os.path.join(source_dir_path, "merge.c"))
        print("B and O are semantically equivalent, simply adopt A")
        exit(0)

if __name__ == "__main__":

    clang_path = "~/.local/llvm-13/bin/clang"
    
    klee_source_path = "~/klee/klee_fork"
    klee_build_path = "~/klee/klee_build"

    klee_include_path = klee_source_path + "/include"
    klee_exe_path = klee_build_path + "/bin/klee"

    source_dir_path = None
    source_dir_path = "~/merge-benchmark/klee/unsafe/4"
    if source_dir_path is None:
        raise ValueError("Source directory path is not set")
    source_dir_path = os.path.expanduser(source_dir_path)
    
    sourceO_path = source_dir_path + "/O.c"
    sourceA_path = source_dir_path + "/A.c"
    sourceB_path = source_dir_path + "/B.c"
    
    if not os.path.isfile(sourceO_path):
        raise FileNotFoundError(f"Source file O not found: {sourceO_path}")
    if not os.path.isfile(sourceA_path):
        raise FileNotFoundError(f"Source file A not found: {sourceA_path}")
    if not os.path.isfile(sourceB_path):
        raise FileNotFoundError(f"Source file B not found: {sourceB_path}")
    
    shared, edits_A, edits_O, edits_B = getEdits.compute_shared_and_edits(sourceA_path, sourceO_path, sourceB_path)

    tmp = "tmp"

    # clean tmp directory
    os.system(f"rm -r {tmp}")
    os.makedirs(tmp)
        
    # compile source

    compile_args = f"-I {klee_include_path} -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone"
    os.system(f"{clang_path} {compile_args} {sourceO_path} -o {tmp}/O.bc")
    os.system(f"{clang_path} {compile_args} {sourceA_path} -o {tmp}/A.bc")
    os.system(f"{clang_path} {compile_args} {sourceB_path} -o {tmp}/B.bc")

    # run klee on bitcode
    klee_constraint_solving_options = "--solver-backend=z3 --use-query-log=solver:kquery "
    klee_debugging_options = " "
    klee_execution_tree_options = "--write-exec-tree --write-sym-paths "
    klee_expression_options = " "
    klee_external_call_policy_options = " "
    klee_linking_options = " "
    klee_memory_management_options = " "
    klee_test_case_options = "--write-no-tests "

    klee_options = (
        klee_constraint_solving_options
        + klee_debugging_options
        + klee_execution_tree_options
        + klee_expression_options
        + klee_external_call_policy_options
        + klee_linking_options
        + klee_memory_management_options
        + klee_test_case_options
    )

    program_args = ""
    redirect_output = " > /dev/null 2>&1"

    os.system(f"{klee_exe_path} {klee_options} --output-dir={tmp}/O {tmp}/O.bc {program_args} {redirect_output}")
    os.system(f"{klee_exe_path} {klee_options} --output-dir={tmp}/A {tmp}/A.bc {program_args} {redirect_output}")
    os.system(f"{klee_exe_path} {klee_options} --output-dir={tmp}/B {tmp}/B.bc {program_args} {redirect_output}")

    handle_trivial()

    record = get_merge_summary(f"{tmp}/O", f"{tmp}/A", f"{tmp}/B")
    print(record)

    edits_M = [[] for i in range(len(edits_A))]

    for i in range(len(record)):
        with open(f"{tmp}/{record[i]}/coveredline{i+1}.txt", "r") as f:
            coveredline = [int(line.strip()) for line in f]
            if record[i] == 'A':
                for j in range(len(edits_A)):
                    flag = False
                    for line_no in range(edits_A[j][1], edits_A[j][2]):
                        if line_no + 1 in coveredline: # line_no is 0-indexed, coveredline is 1-indexed
                            flag = True
                            break
                    if flag:
                        edits_M[j] = edits_A[j][0]
            elif record[i] == 'B':
                for j in range(len(edits_B)):
                    flag = False
                    for line_no in range(edits_B[j][1], edits_B[j][2]):
                        if line_no + 1 in coveredline: # line_no is 0-indexed, coveredline is 1-indexed
                            flag = True
                            break
                    if flag:
                        edits_M[j] = edits_B[j][0]
    
    merged = getEdits.apply(edits_M, shared)

    with open(os.path.join(source_dir_path, "merge.c"), "w") as f:
        for line in merged:
            f.write(line)
        print("merged file saved")