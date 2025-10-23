This is a 3-way merge checker that finds latent subtle **semantic merge conflicts** that are:
1. not syntactic merge conflicts. Otherwise, it should be detected by existing 3-way diffing tools (e.g. `diff3`).
2. not able to be catched by compiler. Some auto-merged programs could not pass compiler or build process, thus would be fixed by developer.
3. real **semantic bugs** that is rare but difficult to discover. 

It also tries to produce a "semantic-correct" merge results if semantic merge conflicts is detected and the fix is available.

Currently this tool only targets on simple C program pairs. It leverages the [KLEE symbolic executor](https://github.com/klee/klee) and the [Z3 theorem prover](https://github.com/Z3Prover/z3) to
analyze programs involved formally. 

