import numpy as np


n = 2**6 # number of qubits
# mat = np.eye(n, dtype=np.int64)

mat = np.zeros((n, n), dtype=np.int64)
for i in range(2**5):
    mat[i, (i-1) % (2**5)] = 1
    mat[i+2**5, (i+1) % (2**5)+2**5] = 1
with open ('mat.txt', 'w') as f:
    f.write('[')
    for i in range(n-1):
        f.write('[')
        f.write(f"{mat[i,0]}")
        for j in range(1, n):
            f.write(f",{mat[i,j]}")
        f.write('],')
        f.write("\n")
    f.write('[')
    f.write(f"{mat[n-1,0]}")
    for j in range(1, n):
        f.write(f",{mat[n-1,j]}")
    f.write(']')
    f.write(']') 
        