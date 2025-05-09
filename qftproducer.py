import numpy as np

n = 20

def assign(i):
    return 'q'+str(i)+' = 0'

def UROT(k):
    m = np.exp(2j*np.pi/2**k)
    if np.abs(m.real) < 1e-10:
        if m.imag > 0:
            return 'UROT'+str(k)+' = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,0+'+str(m.imag)+'j]]'
        if m.imag < 0:
            return 'UROT'+str(k)+' = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,0-'+str(-m.imag)+'j]]'
    if np.abs(m.imag) < 1e-10:
        return 'UROT'+str(k)+' = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,'+str(m.real)+']]'
    if m.imag > 0:
        return 'UROT'+str(k)+' = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,'+str(m.real)+'+'+str(m.imag)+'j]]' 
    if m.imag < 0:
        return 'UROT'+str(k)+' = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,'+str(m.real)+'-'+str(-m.imag)+'j]]'
    if m.imag == 0:
        return 'UROT'+str(k)+' = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,'+str(m.real)+']]'
    

with open('qft.txt','w') as f:
    for i in range(1,n+1):
        f.write(assign(i))
        f.write('\n')
    f.write('H = [[0.7071067, 0.7071067], [0.7071067, -0.7071067]]\n')
    for i in range(2,n+1):
        f.write(UROT(i))
        f.write('\n')
    for i in range(1,n+1):
        f.write('q'+str(i)+'*=H\n')
        for j in range(2, n +2-i):
            f.write('q'+str(i+j-1)+',q'+str(i)+'*=UROT'+str(j)+'\n')
            
    