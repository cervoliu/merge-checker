from typing import List, Tuple, Union

def tokenize_program(file_path: str) -> List[str]:
    """Read and tokenize a C program by lines."""
    with open(file_path, 'r') as f:
        return f.readlines()

def compute_lcs(seq1: List[str], seq2: List[str]) -> List[Union[str, None]]:
    """Compute the LCS of two sequences and returns mapping."""
    m, n = len(seq1), len(seq2)
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    map = []
    i, j = m, n
    while i > 0 and j > 0:
        if seq1[i - 1] == seq2[j - 1]:
            map.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    map.reverse()
    return map

def compute_shared_and_edits(fileA: str, fileO: str, fileB: str):
    """Main function to compute shared program and edits."""
    A, O, B = tokenize_program(fileA), tokenize_program(fileO), tokenize_program(fileB)
    mapAO = compute_lcs(A, O)
    mapOB = compute_lcs(O, B)
    map = []
    shared = []
    i, j = 0, 0
    while i < len(mapAO) and j < len(mapOB):
        if mapAO[i][1] == mapOB[j][0]:
            map.append((mapAO[i][0], mapAO[i][1], mapOB[j][1]))
            shared.append(O[mapAO[i][1]])
            i += 1
            j += 1
        else:
            if shared[-1] is not None: shared.append(None) # mark a hole
            if mapAO[i][1] < mapOB[j][0]:
                i += 1
            else:
                j += 1
    
    map.append((len(A), len(O), len(B)))
    edits_A, edits_O, edits_B = [], [], []
    holes = 0
    for idx in range(len(map) - 1):
        i1, j1, k1 = map[idx]
        i2, j2, k2 = map[idx + 1]
        
        # Check for holes
        if i2 != i1 + 1 or j2 != j1 + 1 or k2 != k1 + 1:
            holes += 1
            # Extract edits for the current hole
            edits_A.append((A[i1 + 1:i2], i1 + 1, i2))
            edits_O.append((O[j1 + 1:j2], j1 + 1, j2))
            edits_B.append((B[k1 + 1:k2], k1 + 1, k2))
    return shared, edits_A, edits_O, edits_B

def apply(edits: List[List[str]], program: List[str]) -> List[str]:
    """Apply edits to a program with holes."""
    result = []
    edit_idx = 0
    
    for line in program:
        if line is None:
            if edit_idx < len(edits):
                result.extend(edits[edit_idx])
                edit_idx += 1
        else:
            result.append(line)
    
    return result

# Example usage:
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python script.py <A.c> <O.c> <B.c>")
        sys.exit(1)
    
    fileA, fileO, fileB = sys.argv[1], sys.argv[2], sys.argv[3]
    compute_shared_and_edits(fileA, fileO, fileB)