import itertools
import queue

from util import *
from item import *

EPS = 10
static_coefficient = 1
g = 3.14 ** 2

class Assignment:
    W, L, H = 0, 0, 0 # dimensions of pallet
    A = [] # assignment (set of oriented and transposed items) where w, l, h determines orientation
    pallet = Item("pallet", W, L, 0)
    eps = EPS

    def __init__(self, A, W, L, H):
        self.A = A
        self.W = W
        self.L = L
        self.H = H
        self.pallet.w = W
        self.pallet.l = L

    def add(self, p):
        self.A.append(p)

    def remove(self, p):
        self.A.remove(p)

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

        for q in self.A + [self.pallet]:
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