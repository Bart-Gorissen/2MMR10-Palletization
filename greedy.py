from conf import *
from assignment import *
# from item import *

def greedy_01(P, W, L, H): # base version
    queue = [ ]
    for p in P:
        queue.append(p)
    A = Assignment([ ], W, L, H)
    open = [ (0, 0, 0) ] # points of interest
    open_history = open
    iter = 0
    while len(queue) > 0 and iter < ITER_MAX:
        p = queue.pop(0)
        wlh_tuples = itertools.permutations([p.w, p.l, p.h])
        has_place = False
        for (cur, wlh) in itertools.product(open, wlh_tuples):
            p.set(cur, wlh)
            if p.x + p.w > W or p.y + p.l > L or p.z + p.h > H: continue
            if p.has_intersect_set(A.A): continue
            if not A.bottom_support(p): continue

            open.remove(cur)
            open_new = [ (p.x + p.w, p.y, p.z), (p.x, p.y + p.l, p.z), (p.x, p.y, p.z + p.h) ]
            open_history.extend(open_new)
            open.extend(open_new)
            has_place = True
            break

        if has_place: A.add(p)
        if not has_place: queue.append(p)
        iter += 1

    if iter >= ITER_MAX:
        print("ERROR: Maximum iterations exceeded {l} boxes remaining".format(l=len(queue)))
        for p in queue:
            print(p)

    return A, iter < ITER_MAX, open_history

def count_placement(A, open, p):
    cnt = 0
    for (cur, wlh) in itertools.product(open, itertools.permutations([p.w, p.l, p.h])):
        p.set(cur, wlh)
        if p.x + p.w > A.W or p.y + p.l > A.L or p.z + p.h > A.H: continue
        if p.has_intersect_set(A.A): continue
        # if not A.bottom_support(p): continue
        cnt += 1
    return cnt

def greedy_02(P, W, L, H): # counting ahead one iteration
    queue = [ ]
    for p in P:
        queue.append(p)
    A = Assignment([ ], W, L, H)
    open = [ (0, 0, 0) ] # points of interest
    open_history = open
    iter = 0

    while len(queue) > 0 and iter < ITER_MAX:
        p = queue.pop(0)
        wlh_tuples = itertools.permutations([p.w, p.l, p.h])
        has_place = False

        cnt_max = -1
        best_cur, best_wlh = -1, -1
        for (cur, wlh) in itertools.product(open, wlh_tuples):
            p.set(cur, wlh)
            if p.x + p.w > A.W or p.y + p.l > A.L or p.z + p.h > A.H: continue
            if p.has_intersect_set(A.A): continue
            if not A.bottom_support(p): continue

            pos_new = [ (p.x + p.w, p.y, p.z), (p.x, p.y + p.l, p.z), (p.x, p.y, p.z + p.h) ]
            pos_open = open+pos_new
            pos_open.remove(cur)
            has_place = True

            if len(queue) == 0:
                best_cur, best_wlh = cur, wlh
                break

            q = queue[0]
            A.add(p)
            cnt = count_placement(A, pos_open, q)
            A.remove(p)
            if cnt > cnt_max: cnt_max, best_cur, best_wlh = cnt, cur, wlh

        if has_place:
            p.set(best_cur, best_wlh)
            A.add(p)
            open.remove(best_cur)
            open_new = [ (p.x + p.w, p.y, p.z), (p.x, p.y + p.l, p.z), (p.x, p.y, p.z + p.h) ]
            open_history.extend(open_new)
            open.extend(open_new)
        else:
            queue.append(p)

        iter += 1

    if iter >= ITER_MAX:
        print("ERROR: Maximum iterations exceeded {l} boxes remaining".format(l=len(queue)))
        for p in queue:
            print(p)

    return A, iter < ITER_MAX, open_history

def count_placement_weighted(A, open, p, w): # counting using weight function w
    weight = 0
    for (cur, wlh) in itertools.product(open, itertools.permutations([p.w, p.l, p.h])):
        p.set(cur, wlh)
        if p.x + p.w > A.W or p.y + p.l > A.L or p.z + p.h > A.H: continue
        if p.has_intersect_set(A.A): continue
        # if not A.bottom_support(p): continue
        weight += w(A,p)
    return weight

def greedy_03(P, W, L, H, w):
    queue = [ ]
    for p in P:
        queue.append(p)
    A = Assignment([ ], W, L, H)
    open = [ (0, 0, 0) ] # points of interest
    open_history = open
    iter = 0

    while len(queue) > 0 and iter < ITER_MAX:
        p = queue.pop(0)
        wlh_tuples = itertools.permutations([p.w, p.l, p.h])
        has_place = False

        cnt_max = -1
        best_cur, best_wlh = -1, -1
        for (cur, wlh) in itertools.product(open, wlh_tuples):
            p.set(cur, wlh)
            if p.x + p.w > A.W or p.y + p.l > A.L or p.z + p.h > A.H: continue
            if p.has_intersect_set(A.A): continue
            if not A.bottom_support(p): continue

            pos_new = [ (p.x + p.w, p.y, p.z), (p.x, p.y + p.l, p.z), (p.x, p.y, p.z + p.h) ]
            pos_open = open+pos_new
            pos_open.remove(cur)
            has_place = True

            if len(queue) == 0:
                best_cur, best_wlh = cur, wlh
                break

            q = queue[0]
            A.add(p)
            cnt = count_placement_weighted(A, pos_open, q, w)
            A.remove(p)
            if cnt > cnt_max: cnt_max, best_cur, best_wlh = cnt, cur, wlh

        if has_place:
            p.set(best_cur, best_wlh)
            A.add(p)
            open.remove(best_cur)
            open_new = [ (p.x + p.w, p.y, p.z), (p.x, p.y + p.l, p.z), (p.x, p.y, p.z + p.h) ]
            open_history.extend(open_new)
            open.extend(open_new)
        else:
            queue.append(p)

        iter += 1

    if iter >= ITER_MAX:
        print("ERROR: Maximum iterations exceeded {l} boxes remaining".format(l=len(queue)))
        for p in queue:
            print(p)

    return A, iter < ITER_MAX, open_history


# WEIGHT FUNCTIONS
def const_1(A, p):
    return 1

def low_top(A, p):
    return A.H - (p.z + p.h)

def far_center(A, p):
    return abs(A.W/2 - p.x) + abs(A.L/2 - p.y)

def far_center_low_top(A, p):
    return far_center(A, p) + low_top(A, p)

def custom(A, p):
    return 1


# GENERAL GREEDY WRAPPER

def greedy(P, W, L, H, method="volume", algo="greedy_01", w=const_1):
    Q = sort_points(P, method)
    if algo == "greedy_01":
        return greedy_01(Q, W, L, H)
    if algo == "greedy_02":
        return greedy_02(Q, W, L, H)
    if algo == "greedy_03":
        return greedy_03(Q, W, L, H, w)

def sort_points(P, method):
    if method == "volume":
        return sorted(P, key=lambda p: p.w * p.l * p.h, reverse=True)  # volume decreasing

    print("ERROR: Invalid sorting method {s}".format(s=method))

