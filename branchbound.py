from assignment import *

def find_open(A):
    xs, ys, zs = set([0]), set([0]), set([0])
    for p in A.A:
        xs.add(p.x); ys.add(p.y); zs.add(p.z)
        xs.add(p.x+p.w); ys.add(p.y+p.l); zs.add(p.z+p.h)
    return itertools.product(xs, ys, zs)

def find_order_location(A, P):
    res = [ ]
    open = find_open(A)

    for p in P:
        wlh_tuples = itertools.permutations([p.w, p.l, p.h])
        for (cur, wlh) in itertools.product(open, wlh_tuples):
            p.set(cur, wlh)
            A.add(p)
            if not A.is_in_bounds(): continue
            if not A.has_intersect(): continue
            if not A.is_bottom_supported(): continue
            A.remove(p)
            value = 1 # compute in some better way
            res.append((value, p, cur, wlh))

    # return sorted based on best weights
    return res.sort(key=lambda x : x[0], reverse=True)

def branch_and_bound(A, P, u): # current assignment A, remaining P
    if len(P) == 0:
        return A, True

    # gets best options for next placement
    order = find_order_location(A, P)

    for (_, p, loc, wlh) in order:
        p.set(loc, wlh)
        A.add(p)
        if -1 < u: # this should be a fancier function
            A.remove(p)
            break
        A_res, res = branch_and_bound(A, P.remove(p), u)
        if res : return A_res, res
        A.remove(p)
        P.append(p)

    return -1, False

def branch_and_bound_pre(P, W, L, H):
    A = Assignment([], W, L, H)
    res, truth = branch_and_bound(A, P, 1)
    return res, truth, []