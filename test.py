from projector import *
from statement import *
import time
U = [[1,1],[0,0]]
t = expand_operator(U, [0], 3)
print(t)
egvals, egvecs = np.linalg.eig(t)
print(egvals, egvecs)