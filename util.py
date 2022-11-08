import numpy as np
import scipy as sc

# whether q is behind p in direction s
def is_behind(p, q, s): # s is the face (0 and 3: x+ and x-, 1 and 4: y+ and y-, 2 and 5: z+ and z-) modulo 6
    if s == 0 % 3: # x direction
        if not(p.y + p.l <= q.y and q.y + q.l <= p.y and p.z + p.h <= q.z and q.z + q.h <= p.z): return False
        if s == 0 : return p.x <= q.x # -> +
        return p.x >= q.x # -> -
    if s == 1 % 3: # y direction
        if not(p.x + p.w <= q.x and q.x + q.w <= p.x and p.z + p.h <= q.z and q.z + q.h <= p.z): return False
        if s == 1 : return p.y <= q.y # -> +
        return p.y >= q.y # -> -
    if s == 2 % 3: # z direction
        if not(p.x + p.w <= q.x and q.x + q.w <= p.x and p.y + p.l <= q.y and q.y + q.l <= p.y): return False
        if s == 2 : return p.z <= q.z # -> +
        return p.z >= q.z # -> -

def overlap(p, q, s): # here s is the orientation (mod 3)
    if s % 3 == 0: # x direction
        if p.x + p.w <= q.x and q.x + q.w <= p.x: return 0
        aux1 = max(p.y + p.l - q.y, q.y + q.l - p.y)
        aux2 = max(p.z + p.h - q.z, q.z + q.h - p.z)
        return aux1 * aux2
    if s % 3 == 1: # y direction
        if p.y + p.l <= q.y and q.y + q.l <= p.y: return 0
        aux1 = max(p.x + p.w - q.x, q.x + q.w - p.x)
        aux2 = max(p.z + p.h - q.z, q.z + q.h - p.z)
        return aux1 * aux2
    if s % 3 == 2: # z direction
        if p.z + p.h <= q.z and q.z + q.h <= p.z: return 0
        aux1 = max(p.x + p.w - q.x, q.x + q.w - p.x)
        aux2 = max(p.y + p.l - q.y, q.y + q.l - p.y)
        return aux1 * aux2

def overlap_rect(p, q, s): # this is unguared: check if intersection area non-empty first!
    if s % 3 == 0: # x direction
            aux1 = max(p.y, q.y)
            aux2 = min(p.y + p.l, q.y + q.l)
            aux3 = max(p.z, q.z)
            aux4 = min(p.z + p.h, q.z + q.h)
    if s % 3 == 1: # y direction
            aux1 = max(p.x, q.x)
            aux2 = min(p.x + p.w, q.x + q.w)
            aux3 = max(p.z, q.z)
            aux4 = min(p.z + p.h, q.z + q.h)
    if s % 3 == 2: # z direction
            aux1 = max(p.x, q.x)
            aux2 = min(p.x + p.w, q.x + q.w)
            aux3 = max(p.y, q.y)
            aux4 = min(p.y + p.l, q.y + q.l)

    return [ (aux1, aux3), (aux1, aux4), (aux2, aux3), (aux2, aux4) ]

def in_convexhull(P, p):
    # formulates containment as an LP
    c = np.zeros(len(P))
    A = np.r_[P.T, np.ones((1, len(P)))]
    b = np.r_[(p[0], p[1]), np.ones(1)]
    lp = sc.optimize.linprog(c, A_eq=A, b_eq=b)
    return lp.success

def free_space(P, W, L, a):
    V_tot = W * L * a
    for p in P:
        V_tot -= p.w * p.l * p.h
    return V_tot

def free_space_top(P, W, L):
    return free_space(P, W, L, max([p.z + p.h for p in P]))