def backtrack(M, n, m, A, B):
    C = []
    valC = M[n][m]
    i, j = n, m 
    
    while i > 0 and j > 0:
        if A[i - 1] == B[j - 1]:
            # not in the set/taken
            C.append(A[i-1])
            i -= 1
            j -= 1
        elif M[i - 1][j] >= M[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return C

