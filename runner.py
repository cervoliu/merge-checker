import os
from equivalence_checker import check_equivalence

if __name__ == "__main__":

    clang_path = "~/.local/llvm-13/bin/clang"
    
    klee_source_path = "~/klee/klee_fork"
    klee_build_path = "~/klee/klee_build"

    klee_include_path = klee_source_path + "/include"
    klee_exe_path = klee_build_path + "/bin/klee"

    sourceA_path = "~/klee/klee_fork/examples/equivalence_check/2/A/A.c"
    sourceB_path = "~/klee/klee_fork/examples/equivalence_check/2/B/B.c"

    tmp = "tmp"

    # clean tmp directory
    os.system(f"rm -r {tmp}")
    os.makedirs(tmp)
        
    # compile source

    compile_params = f"-I {klee_include_path} -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone"
    os.system(f"{clang_path} {compile_params} {sourceA_path} -o {tmp}/A.bc")
    os.system(f"{clang_path} {compile_params} {sourceB_path} -o {tmp}/B.bc")

    # run klee on bitcode
    klee_options = f"-posix-runtime"
    program_options = f""
    os.system(f"{klee_exe_path} {klee_options} --output-dir={tmp}/A {tmp}/A.bc {program_options}")
    os.system(f"{klee_exe_path} {klee_options} --output-dir={tmp}/B {tmp}/B.bc {program_options}")

    # check equivalence
    print("Equivalence" if check_equivalence(f"{tmp}/A", f"{tmp}/B") else "Not Equivalent")