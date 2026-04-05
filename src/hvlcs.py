import backtrack

import sys

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Expect: python src/hvlcs.py <file_name.in> <file_name.out>")
        sys.exit()

    file = open(f'data/{sys.argv[1]}', 'r')

    alphabet_size = int(file.readline())

    alphabet = {}

    for i in range(alphabet_size):
        xK,vK = file.readline().split()
        alphabet[xK] = int(vK)
    
    A = list(file.readline().rstrip('\n'))
    B = list(file.readline().rstrip('\n'))

    n = len(A)
    m = len(B)

    M = [[None] * (m + 1) for i in range(n + 1)]


    # base cases
    for i in range(0, n + 1):
        M[i][0] = 0

    for j in range(0, m + 1):
        M[0][j] = 0

    # recurrence relation/equation
    for i in range(1, n + 1):
        for j in range(1, m + 1):

            a = A[i - 1]
            b = B[j - 1]

            if a == b:
                M[i][j] = alphabet[a] + M[i-1][j-1]
            else: 
                M[i][j] = max(M[i-1][j], M[i][j-1])

    #backtracking
    C = backtrack.backtrack(M, n, m, A, B)
    file.close()
    file = open(f'data/{sys.argv[2]}', 'w')
    file.write(str(M[n][m]) + "\n")
    for i in range(len(C)):
        file.write(str(C[i]))