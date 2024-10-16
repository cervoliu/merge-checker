import os
from checker.equivalenceChecker import check_program_equivalence

if __name__ == "__main__":

    clang_path = "~/.local/llvm-13/bin/clang"
    
    klee_source_path = "~/klee/klee_fork"
    klee_build_path = "~/klee/klee_build"

    klee_include_path = klee_source_path + "/include"
    klee_exe_path = klee_build_path + "/bin/klee"

    sourceA_path, sourceB_path = None, None
    # sourceA_path = "~/klee/klee_fork/examples/equivalence_check/2/A/A.c"
    # sourceB_path = "~/klee/klee_fork/examples/equivalence_check/2/B/B.c"
    sourceA_path = "/home/lyd24/benchmarks/CLEVER/divide/Eq/newV.c"
    sourceB_path = "/home/lyd24/benchmarks/CLEVER/divide/Eq/oldV.c"
    if sourceA_path is None:
        sourceA_path = input("Enter the path to the first source file: ")
    if sourceB_path is None:
        sourceB_path = input("Enter the path to the second source file: ")

    if not os.path.isfile(os.path.expanduser(sourceA_path)):
        raise FileNotFoundError(f"Source file A not found: {sourceA_path}")
    if not os.path.isfile(os.path.expanduser(sourceB_path)):
        raise FileNotFoundError(f"Source file B not found: {sourceB_path}")

    tmp = "tmp"

    # clean tmp directory
    os.system(f"rm -r {tmp}")
    os.makedirs(tmp)
        
    # compile source

    compile_args = f"-I {klee_include_path} -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone"
    os.system(f"{clang_path} {compile_args} {sourceA_path} -o {tmp}/A.bc")
    os.system(f"{clang_path} {compile_args} {sourceB_path} -o {tmp}/B.bc")

    # run klee on bitcode
    klee_options = f"-posix-runtime"
    program_options = f""
    os.system(f"{klee_exe_path} {klee_options} --output-dir={tmp}/A {tmp}/A.bc {program_options}")
    os.system(f"{klee_exe_path} {klee_options} --output-dir={tmp}/B {tmp}/B.bc {program_options}")

    # check equivalence
    print("Equivalence" if check_program_equivalence(f"{tmp}/A", f"{tmp}/B") else "Not Equivalent")