import os
from checker.conflictChecker import check_merge_conflict_free

if __name__ == "__main__":

    clang_path = "~/.local/llvm-13/bin/clang"

    merger_path = "~/merger/merger"
    
    klee_source_path = "~/klee/klee_fork"
    klee_build_path = "~/klee/klee_build"

    klee_include_path = klee_source_path + "/include"
    klee_exe_path = klee_build_path + "/bin/klee"

    source_dir_path = None

    if source_dir_path is None:
        raise ValueError("Source directory path is not set")
    
    sourceO_path = source_dir_path + "/O.c"
    sourceA_path = source_dir_path + "/A.c"
    sourceB_path = source_dir_path + "/B.c"
    sourceM_path = source_dir_path + "/M.c"
    
    if not os.path.isfile(os.path.expanduser(sourceO_path)):
        raise FileNotFoundError(f"Source file O not found: {sourceO_path}")
    if not os.path.isfile(os.path.expanduser(sourceA_path)):
        raise FileNotFoundError(f"Source file A not found: {sourceA_path}")
    if not os.path.isfile(os.path.expanduser(sourceB_path)):
        raise FileNotFoundError(f"Source file B not found: {sourceB_path}")
    if not os.path.isfile(os.path.expanduser(sourceM_path)):
        raise FileNotFoundError(f"Source file M not found: {sourceM_path}")

    tmp = "tmp"

    # clean tmp directory
    os.system(f"rm -r {tmp}")
    os.makedirs(tmp)
        
    # compile source

    compile_args = f"-I {klee_include_path} -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone"
    os.system(f"{clang_path} {compile_args} {sourceO_path} -o {tmp}/O.bc")
    os.system(f"{clang_path} {compile_args} {sourceA_path} -o {tmp}/A.bc")
    os.system(f"{clang_path} {compile_args} {sourceB_path} -o {tmp}/B.bc")
    os.system(f"{clang_path} {compile_args} {sourceM_path} -o {tmp}/M.bc")

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
    os.system(f"{klee_exe_path} {klee_options} --output-dir={tmp}/M {tmp}/M.bc {program_args} {redirect_output}")

    # check merge conflict
    print("safe" if check_merge_conflict_free(f"{tmp}/O", f"{tmp}/A", f"{tmp}/B", f"{tmp}/M") else "unsafe")