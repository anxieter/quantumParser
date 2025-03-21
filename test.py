from projector import *

H = np.array([[0.5, 0.5], [0.5, 0.5]])
P = np.array([[1, 0], [0, 0]])
# print(,supp(H))
print('join:',join(H, P))
print('intersect:',intersect(H, P))
print('sasaki:',sasaki_projection(P, H))