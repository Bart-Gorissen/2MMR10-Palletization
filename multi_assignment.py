EPS = 10
CNT = 2

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