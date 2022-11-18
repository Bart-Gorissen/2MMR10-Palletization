import random

import numpy as np
import scipy as sc

from conf import *

# whether q is behind p in direction s
def is_behind(p, q, s): # s is the face (0 and 3: x+ and x-, 1 and 4: y+ and y-, 2 and 5: z+ and z-) modulo 6
    if s % 3 == 0: # x direction
        if not(p.y + p.l <= q.y and q.y + q.l <= p.y and p.z + p.h <= q.z and q.z + q.h <= p.z): return False
        if s == 0 : return p.x <= q.x # -> +
        return p.x >= q.x # -> -
    if s % 3 == 1: # y direction
        if not(p.x + p.w <= q.x and q.x + q.w <= p.x and p.z + p.h <= q.z and q.z + q.h <= p.z): return False
        if s == 1 : return p.y <= q.y # -> +
        return p.y >= q.y # -> -
    if s % 3 == 2: # z direction
        if p.x + p.w <= q.x or q.x + q.w <= p.x or p.y + p.l <= q.y or q.y + q.l <= p.y: return False
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

def overlap_rect(p, q, s, zeta=ZETA): # this is unguared: check if intersection area non-empty first! zeta in [0,1]
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

    # now looking at square in x,y coordinates
    # zeta = 1 : standard
    # zeta = 0 : single line
    len_x_2 = (aux2 - aux1) / 2
    len_y_2 = (aux4 - aux3) / 2
    xlow = aux1 + ((1-zeta)* len_x_2)
    ylow = aux3 + ((1-zeta)* len_y_2)
    xhi = aux2 + ((zeta-1) * len_x_2)
    yhi = aux4 + ((zeta-1) * len_y_2)

    return [ (xlow, ylow), (xlow, yhi), (xhi, ylow), (xhi, yhi) ]

def in_convexhull(P, p):
    # formulates containment as an LP
    if len(P) < 1: return False
    c = np.zeros(len(P))
    A = np.r_[P.T, np.ones((1, len(P)))]
    b = np.r_[(p[0], p[1]), np.ones(1)]
    lp = sc.optimize.linprog(c, A_eq=A, b_eq=b)
    return lp.success

def compute_space(P, W, L, H):
    V_use = 0
    top_max = P[0].z + P[0].h
    for p in P:
        top_max = max(top_max, p.z + p.h)
        V_use += p.w * p.l * p.h

    return W*L*H, W*L*top_max, V_use

def free_space(P, W, L, a):
    V_tot = W * L * a
    for p in P:
        V_tot -= p.w * p.l * p.h
    return V_tot

def free_space_top(P, W, L):
    return free_space(P, W, L, max([p.z + p.h for p in P]))

def get_order(P, f, reverse=True):
    aux = [ p for p in P ]
    aux.sort(key=f, reverse=reverse)
    return [ aux.index(p) for p in P ]


def sort_points(P, method):
    if method == "none":
        return P
    if method == "rand":
        random.shuffle(P)
        return P
    if method == "volume":
        return sorted(P, key=lambda p: p.w * p.l * p.h, reverse=True)  # volume decreasing
    if method == "side":
        return sorted(P, key=lambda p: max(p.w, p.l, p.h), reverse=True) # longest side decreasing
    if method == "sidevol":
        aux1 = get_order(P, f=lambda p: p.w * p.l * p.h, reverse=True) # volume decreasing
        aux2 = get_order(P, f=lambda p: max(p.w, p.l, p.h), reverse=True)  # longest side decreasing
        return sorted(P, key=lambda p: aux1[P.index(p)] + aux2[P.index(p)], reverse=False) # combination

    print("ERROR: Invalid sorting method {s}".format(s=method))
