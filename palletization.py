import sys
#import pathlib
#import gurobipy as gp
import itertools
#import time
import numpy as np
import scipy as sc
import queue
import math
import functools

###############################################################################################
##### HEADER ####
###############################################################################################

# Group Members:
#
# Student 1: Bart Gorissen 1116922
# Student 2:
# Student 3:
# Student 4:
# Student 5:

###############################################################################################
### MAIN PART ###
###############################################################################################

####################
# GLOBAL VARIABLES #
####################

g = math.pi ** 2 # gravitational acceleration
static_coefficient = 1 # coefficient of static friction
EPS = 10 # error coefficient
DLT = 5 # reaching coefficient for pushing
CNT = 10 # default number of pallets
verbose = 1 # 0 : only result, 1 : +important steps, 2 : +debug



#######################################################
# CLASSES ON ITEMS, ASSIGNMENTS, AND COMMON FUNCTIONS #
#######################################################

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
    match s % 3:
        case 0: # x direction
            if p.x + p.w <= q.x: return 0
            if q.x + q.w <= p.x: return 0
            aux1 = max(p.y + p.l - q.y, q.y + q.l - p.y)
            aux2 = max(p.z + p.h - q.z, q.z + q.h - p.z)
            return aux1 * aux2
        case 1: # y direction
            if p.y + p.l <= q.y: return 0
            if q.y + q.l <= p.y: return 0
            aux1 = max(p.x + p.w - q.x, q.x + q.w - p.x)
            aux2 = max(p.z + p.h - q.z, q.z + q.h - p.z)
            return aux1 * aux2
        case 2: # z direction
            if p.z + p.h <= q.z: return 0
            if q.z + q.h <= p.z: return 0
            aux1 = max(p.x + p.w - q.x, q.x + q.w - p.x)
            aux2 = max(p.y + p.l - q.y, q.y + q.l - p.y)
            return aux1 * aux2

def overlap_rect(p, q, s): # this is unguared: check if intersection area non-empty first!
    match s % 3:
        case 1:
            aux1 = max(p.y, q.y)
            aux2 = min(p.y + p.l, q.y + q.l)
            aux3 = max(p.z, q.z)
            aux4 = min(p.z + p.h, q.z + q.h)
        case 2:
            aux1 = max(p.x, q.x)
            aux2 = min(p.x + p.w, q.x + q.w)
            aux3 = max(p.z, q.z)
            aux4 = min(p.z + p.h, q.z + q.h)
        case 3:
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

class Item:
    x, y, z = 0, 0, 0
    w, l, h = 0, 0, 0
    m, c = 1, (0, 0, 0)
    name = ""

    def __init__(self, name, w, l, h):
        self.name = name
        self.set((0, 0, 0), (w, l, h))

    def set(self, blc, wlh):
        self.x = blc[0]
        self.y = blc[1]
        self.z = blc[2]
        self.w = wlh[0]
        self.l = wlh[1]
        self.h = wlh[2]
        self.c = (self.x + (self.w / 2), self.y + (self.l / 2), self.z + (self.h / 2))

    def is_in_bounds(self, W, L, H):
        if self.x < 0: return False
        if self.y < 0: return False
        if self.z < 0: return False
        if self.x + self.w > W: return False
        if self.y + self.l > L: return False
        if self.z + self.h > H: return False
        return True

    def has_intersect(self, q):
        if self.x + self.w <= q.x: return False
        if q.x + q.w <= self.x: return False
        if self.y + self.l <= q.y: return False
        if q.y + q.l <= self.y: return False
        if self.z + self.h <= q.z: return False
        if q.z + q.h <= self.z: return False
        return True

    def has_intersect_set(self, Q):
        for q in Q:
            if self.has_intersect(q): return True
        return False

    def to_string(self):
        return "{n} x: {x} y: {y} z: {z} w: {w} l: {l} h: {h} V: {v}".format(n=self.name,
                                                                             x=self.x,y=self.y,z=self.z,
                                                                             w=self.w,l=self.l,h=self.h,
                                                                             v=self.w*self.l*self.h)

    def __repr__(self):
        return self.to_string()

@functools.total_ordering
class ItemQueueTask:
    def __init__(self, item, key, cnt):
        self.item = item
        self.key = key
        self.cnt = cnt

    def __repr__(self):
        return "Item {p}, key {k}, entry {c}".format(p=self.item,k=self.key,c=self.cnt)

    def __lt__(self, other):
        return (self.key, self.cnt) < (other.key, other.cnt)

    def __eq__(self, other):
        return (self.key, self.cnt) == (other.key, other.cnt)

class Assignment:
    W, L, H = 0, 0, 0 # dimensions of pallet
    A = [] # assignment (set of oriented and transposed items) where w, l, h determines orientation
    eps = EPS

    def __init__(self, A, W, L, H):
        self.A = A
        self.W = W
        self.L = L
        self.H = H

    def add(self, p):
        self.A.append(p)

    def get(self, i):
        return self.A[i]

    # Functions for validity of assignment
    def is_in_bounds(self):
        for p in self.A:
            if not p.is_in_bounds(self.W, self.L, self.H) : return False
        return True

    def has_intersect(self):
        for i in range(len(self.A)):
            if self.A[i].has_intersect_set(self.A[i+1:]): return True
        return False

    def supported_from(self, p):
        res = []
        tot = 0
        for q in self.A:
            if p == q: continue
            if p.z + p.h > q.z: continue # q is below p
            if p.z + p.h + self.eps < q.z: continue # q is more than distance eps away from p
            a = overlap(p, q, 2)
            if a > 0:
                res.append((q, a))
                tot += a

        return res, tot

    def supports(self, p):
        res = []
        tot = 0
        for q in self.A:
            if p == q: continue
            if q.z + q.h > p.z: continue  # q is above p
            if q.z + q.h + self.eps < p.z: continue # q is more than distance eps away from p
            a = overlap(p, q, 2)
            if a > 0:
                ol_rect = overlap_rect(p, q, 2)
                res.append((q, a, ol_rect))
                tot += a

        return res, tot

    # Functions for support + stability
    def bottom_support(self, p):
        S, _ = self.supports(p)
        T = [ ]
        for (q, a, ol_rect) in S:
            T.extend(ol_rect)
        if len(T) == 0: return False
        return in_convexhull(np.array(T), (p.c[0], p.c[1]))

    def side_support(self, p, s):
        res = [ ]
        for q in self.A:
            if s % 6 == 0 and 0 <= q.x + q.w - p.x <= self.eps: res.append(q)
            if s % 6 == 1 and 0 <= q.y + q.l - p.y <= self.eps: res.append(q)
            if s % 6 == 2 and 0 <= q.z + q.h - p.z <= self.eps: res.append(q)
            if s % 6 == 3 and 0 <= p.x + p.w - q.x <= self.eps: res.append(q)
            if s % 6 == 4 and 0 <= p.y + p.l - q.y <= self.eps: res.append(q)
            if s % 6 == 5 and 0 <= p.z + p.h - q.z <= self.eps: res.append(q)

        return len(res) > 0, res

    def side_support_set(self, p, S):
        res = [ [ ] for i in range(6) ]
        truth = True

        for s in S:
            aux1, aux2 = self.side_support(p, s)
            truth = truth and aux1
            res[s].extend(aux2)

        return truth, res

    def side_bottom_support(self, p, S):
        SB, _ = self.supports(p)
        _, SS = self.side_support_set(p, S)
        TB = []
        for (q, a, ol_rect) in SB:
            TB.extend(ol_rect)
        TS = [ ]
        for s in S:
            if s % 6 == 0: TS.extend(itertools.chain(*[[(q.x + q.w, q.y), (q.x + q.w, q.y + q.l)] for q in SS[s]]))
            if s % 6 == 1: TS.extend(itertools.chain(*[[(q.x, q.y + q.l), (q.x + q.w, q.y + q.l)] for q in SS[s]]))
            if s % 6 == 3: TS.extend(itertools.chain(*[[(q.x, q.y), (q.x, q.y + q.l)] for q in SS[s]]))
            if s % 6 == 4: TS.extend(itertools.chain(*[[(q.x, q.y), (q.x + q.w, q.y)] for q in SS[s]]))
            # we are not concerned with top and bottom faces

        T = TB
        T.extend(TS)
        return in_convexhull(np.array(T), (p.x, p.y))

    def is_bottom_supported(self):
        for p in self.A:
            if not self.bottom_support(p): return False
        return True

    def is_bottom_side_supported(self):
        for p in self.A:
            if not self.side_bottom_support(p, [0, 1, 3, 4]): return False
        return True

    # Functions for tolerance
    def box_cone(self, p, s): # note that a needs to be from A, not from P
        # naive implementation
        res = [ p ]
        size = 0
        while len(res) != size and len(res) < len(self.A):
            size = len(res)
            for q in self.A:
                if q in res: continue
                if is_behind(p, q, s): res.append(q)

        return res

    def support_mass(self, P):
        Q = queue.PriorityQueue()
        m = 0
        cnt = 0
        for p in P:
            Q.put(ItemQueueTask((p, 1), p.z + p.h, cnt))
            cnt += 1

        while not Q.empty():
            task = Q.get()
            (t, a) = task.item
            if not t in P: m += t.m * a

            T, a_tot = self.supported_from(t)

            for (s, a_s) in T:
                if s in P: continue
                Q.put(ItemQueueTask((s, a * (a_s / a_tot)), s.z + s.h, cnt))
                cnt += 1

        return m

    def is_F_push_tolerant(self, p, s, F):
        B = self.box_cone(p, s)
        m_1 = sum([b.m for b in B])
        m_2 = self.support_mass(B)
        N = g * (m_1 + m_2)
        return F <= static_coefficient * N

    def is_F_S_push_tolerant_sub(self, p, S, F):
        for s in S:
            if not self.is_F_push_tolerant(p, s, F): return False
        return True

    def is_F_S_push_tolerant(self, S, F, dlt):
        for p in self.A:
            Sp = [ ]
            for s in S:
                if s % 6 == 0 and p.x <= dlt : Sp.append(s)
                if s % 6 == 1 and p.y <= dlt: Sp.append(s)
                if s % 6 == 2 and p.z <= dlt: continue # Sp.append(s) : do not consider vertical
                if s % 6 == 3 and p.x + p.w <= self.W - dlt: Sp.append(s)
                if s % 6 == 4 and p.y + p.l <= self.L - dlt: Sp.append(s)
                if s % 6 == 5 and p.z + p.h <= self.H - dlt: continue # Sp.append(s) do not consider vertical

            if not self.is_F_S_push_tolerant_sub(p, Sp, F): return False
        return True

    def is_a_acceleration_tolerant_sub(self, p, a):
        m_2 = self.support_mass([p])
        N = g * (p.m + m_2)
        return p.m * a <= static_coefficient * N

    def is_a_acceleration_tolerant(self, a):
        for p in self.A:
            if not self.is_a_acceleration_tolerant_sub(p, a): return False
        return True

class MultiAssignment:
    MA = [ ]  # assignments, each corresponding to a pallet
    eps = EPS
    cnt = CNT

    def __init__(self, cnt):
        self.MA = [ [ ] for i in range(cnt)]

    # Functions for validity of assignment
    def is_in_bounds(self):
        for A in self.MA:
            if not A.is_in_bounds(): return False
        return True

    def has_intersect(self):
        for A in self.MA:
            if A.has_intersect(): return True
        return False

    # Functions for support + stability
    def is_bottom_supported(self):
        for A in self.MA:
            if not A.bottom_support(): return False
        return True

    def is_bottom_side_supported(self):
        for A in self.MA:
            if not A.side_bottom_support(): return False
        return True

    # Functions for tolerance
    def is_F_S_push_tolerant(self, S, F, dlt):
        for A in self.MA:
            if not A.is_F_S_push_tolerant(S, F, dlt): return False
        return True

    def is_a_acceleration_tolerant(self, a):
        for A in self.MA:
            if not A.is_a_acceleration_tolerant(a): return False
        return True



##########################
# OPTIMIZATION FUNCTIONS #
##########################

def greedy_01(P, W, L, H):
    Q = sorted(P, key=lambda p: p.w * p.l * p.h, reverse=True) # volume decreasing
    A = Assignment(Q, W, L, H)
    open = [ (0, 0, 0) ] # points of interest
    iter = 0
    for p in Q:
        w, l, h = p.w, p.l, p.h
        wlh_tuples = itertools.permutations([w, l, h])
        for (cur, wlh) in itertools.product(open, wlh_tuples):
            p.set(cur, wlh)
            if p.x + p.w > W or p.y + p.l > L or p.z + p.h > H : continue
            if p.has_intersect_set(Q[:iter]): continue

            open.remove(cur)
            open.extend([ (p.x + p.w, p.y, p.z), (p.x, p.y + p.l, p.z), (p.x, p.y, p.z + p.h) ])
            break
        iter += 1

    return A



##################
# MAIN FUNCTIONS #
##################

def read_instance(
    path                # specification of the file to be read
):
    file = open(path, 'r')
    lines = file.readlines()
    file.close()

    # read data-set
    P = [ ]

    for line_comma in lines[1:]:
        line = line_comma.split(",")
        name = str(line[0])
        width = int(line[1])
        length = int(line[2])
        height = int(line[3])
        P.append(Item(name,width,length,height))

    return P

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print("ERROR: expected one argument, but got {c}.".format(c=len(args)))
        return -1

    mode = "greedy_01"

    while len(args) > 1:
        cur = args[0]
        args.remove(cur)

        match cur:
            case "greedy_01":
                mode = "greedy_01"
                continue

            case other:
                print("ERROR: argument {a} not supported".format(a=cur))
                return -1

    path = args[0]
    P = read_instance(path)
    W, L, H = 800, 1200, 1500
    A = [ ]

    if verbose >= 1:
        print("Running on items:")
        for p in P:
            print(p.to_string())

    print("\nVerbose mode {v}\n".format(v=verbose))

    match mode:
        case "greedy_01":
            A = greedy_01(P, W, L, H)
        case other:
            print("ERROR: mode {m} not supported".format(m=mode))
            return -1

    print("Found ordered assignment:")
    for p in A.A:
        print(p.to_string())

    print("\nProperties:")
    print("Assignment fits in bounds: {t}".format(t=A.is_in_bounds()))
    print("Assignment has no overlap: {t}".format(t=not A.has_intersect()))
    print("Assignment is eps-bottom-stable: {t}".format(t=A.is_bottom_supported()))
    print("Assignment is eps-bottom-side-stable: {t}".format(t=A.is_bottom_side_supported()))
    print("Assignment is delta-F-S-push-tolerant: {t}".format(t=A.is_F_S_push_tolerant([0,1,3,4], 1, DLT))) # force 1N
    print("Assignment is a-acceleration-tolerant: {t}".format(t=A.is_a_acceleration_tolerant(1))) # acceleration 1m/ss

if __name__ == "__main__":
    main()