
"""

A Python implementation of De Boor's algorithm, used for evaluating Bezier splines.

This algorithm is highly stable, but slow for complex splines.

This algorithm was converted into Python using source code and documentation available
from here:

    http://www.cs.mtu.edu/~shene/COURSES/cs3621/NOTES/

"""

def get_k(U, u):
    for i in range(len(U)-1):
        if U[i] <= u and U[i+1] > u:
            return i
            
        if U[len(U)-2] == u:
            return len(U)-2
            
    raise Exception("Bounding interval for knot not found.")

def get_multiplicity(U, u, i):

    multiplicity = 0
    
    for i in range(i+1,len(U)):
        if U[i] == u:
            multiplicity += 1
        else:
            break
            
    for i in range(i-1,0,-1):
        if U[i] == u:
            multiplicity += 1
        else:
            break
        
    return multiplicity

def deboor(_P, U, u, p):
    k = get_k(U, u)
    s = get_multiplicity(U, u, k)
    
    if u != U[k]:
        h = p
    else:
        h = p - s
    
    P = []
    for _p in _P:
        P.append([_p])
    
    for r in range(1, h+1):
        for i in range(k-p+r, k-s+1):
            a = (u - U[i]) / (U[i+p-r+1] - U[i])
            
            # Each point is a tuple
            x = (1 - a) * P[i-1][r-1][0] + a * P[i][r-1][0]
            y = (1 - a) * P[i-1][r-1][1] + a * P[i][r-1][1]
            
            P[i].append((x,y))
            
    return P[k-s][p-s]
