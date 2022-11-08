import itertools
import sys
#import pathlib
import gurobipy as gp
#import itertools
#import time
#import numpy as np
#import math

#from util import *
#from item import *
from assignment import *
from visualization import *

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

# g = math.pi ** 2 # gravitational acceleration
# static_coefficient = 1 # coefficient of static friction
# EPS = 10 # error coefficient
DLT = 5 # reaching coefficient for pushing
# CNT = 10 # default number of pallets
verbose = 1 # 0 : only result, 1 : +important steps, 2 : +debug
ITER_MAX = 100

#######################
# AUXILIARY FUNCTIONS #
#######################

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



##########################
# OPTIMIZATION FUNCTIONS #
##########################

##########
# GREEDY #
##########

def count_placement(A, open, p):
    cnt = 0
    A.add(p)
    for (cur, wlh) in itertools.product(open, itertools.permutations([p.w, p.l, p.h])):
        p.set(cur, wlh)
        if not  A.is_in_bounds(): continue
        if A.has_intersect(): continue
        #if not A.is_bottom_supported(): continue
        cnt += 1
    A.remove(p)
    return cnt

def greedy_02(P, W, L, H):
    queue = [ ]
    Q = sorted(P, key=lambda p: p.w * p.l * p.h, reverse=True) # volume decreasing, sorted on volume
    for p in Q:
        queue.append(p)
    A = Assignment([ ], W, L, H)
    open = [ (0, 0, 0) ] # points of interest
    open_history = open
    iter = 0

    while len(queue) > 0 and iter < ITER_MAX:
        p = queue.pop(0)
        wlh_tuples = itertools.permutations([p.w, p.l, p.h])
        A.add(p)
        has_place = False

        max = -1
        best_cur, best_wlh = -1, -1
        for (cur, wlh) in itertools.product(open, wlh_tuples):
            p.set(cur, wlh)
            if not A.is_in_bounds(): continue
            if A.has_intersect(): continue
            if not A.is_bottom_supported(): continue

            pos_new = [ (p.x + p.w, p.y, p.z), (p.x, p.y + p.l, p.z), (p.x, p.y, p.z + p.h) ]
            pos_open = open+pos_new
            pos_open.remove(cur)
            has_place = True

            if len(queue) == 0:
                best_cur, best_wlh = cur, wlh
                has_place = True
                break

            q = queue[0]
            cnt = count_placement(A, pos_open, q)
            if cnt > max: max, best_cur, best_wlh = cnt, cur, wlh

        if has_place:
            p.set(best_cur, best_wlh)
            open.remove(best_cur)
            open_new = [ (p.x + p.w, p.y, p.z), (p.x, p.y + p.l, p.z), (p.x, p.y, p.z + p.h) ]
            open_history.extend(open_new)
            open.extend(open_new)
        else:
            A.remove(p)
            queue.append(p)

        iter += 1

    if iter >= ITER_MAX:
        print("ERROR: Maximum iterations exceeded {l} boxes remaining".format(l=len(queue)))
        for p in queue:
            print(p)

    return A, iter < ITER_MAX, open_history

def greedy_01(P, W, L, H):
    Q = sorted(P, key=lambda p: p.w * p.l * p.h, reverse=True) # volume decreasing
    queue = [ ]
    for p in Q:
        queue.append(p)
    A = Assignment([ ], W, L, H)
    open = [ (0, 0, 0) ] # points of interest
    open_history = open
    iter = 0
    while len(queue) > 0 and iter < ITER_MAX:
        p = queue.pop(0)
        A.add(p)
        wlh_tuples = itertools.permutations([p.w, p.l, p.h])
        has_place = False
        for (cur, wlh) in itertools.product(open, wlh_tuples):
            p.set(cur, wlh)
            if not A.is_in_bounds(): continue
            if A.has_intersect(): continue
            if not A.is_bottom_supported(): continue

            open.remove(cur)
            open_new = [ (p.x + p.w, p.y, p.z), (p.x, p.y + p.l, p.z), (p.x, p.y, p.z + p.h) ]
            open_history.extend(open_new)
            open.extend(open_new)
            has_place = True
            break

        if not has_place: A.remove(p); queue.append(p)
        iter += 1

    if iter >= ITER_MAX:
        print("ERROR: Maximum iterations exceeded {l} boxes remaining".format(l=len(queue)))
        for p in queue:
            print(p)

    return A, iter < ITER_MAX, open_history

##################
# BRANCH & BOUND #
##################

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
    return res.sorted(key=lambda x : x[0], reversed=True)

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



####################
# LEVEL GENERATION #
####################

def gen_level_height(P, W, L, H):
    A = Assignment([], W, L, H)

    Q = [ p for p in P if p.w <= H or p.l <= H or p.h <= H ]
    VQ = [ p.w * p.l * p.h for p in Q ]
    n = len(Q)

    m = gp.Model("compact")

    # bottom-left coordinates
    x = m.addVars(range(n), vtype=gp.GRB.CONTINUOUS, lb=0, ub=W, name="x")
    y = m.addVars(range(n), vtype=gp.GRB.CONTINUOUS, lb=0, ub=L, name="y")
    z = m.addVars(range(n), vtype=gp.GRB.CONTINUOUS, lb=0, ub=H, name="z")

    # dimensions
    w = m.addVars(range(n), vtype=gp.GRB.CONTINUOUS, lb=0, ub=W, name="w")
    l = m.addVars(range(n), vtype=gp.GRB.CONTINUOUS, lb=0, ub=L, name="l")
    h = m.addVars(range(n), vtype=gp.GRB.CONTINUOUS, lb=0, ub=H, name="h")

    # used
    b = m.addVars(range(n), vtype=gp.GRB.BINARY, name="b")

    # each box should keep its dimensions


    # each box should be in the pallet
    m.addConstrs(gp.quicksum(x[i] + w[i] <= W) for i in range(n))
    m.addConstrs(gp.quicksum(y[i] + l[i] <= L) for i in range(n))
    m.addConstrs(gp.quicksum(z[i] + h[i] <= H) for i in range(n))

    # boxes should not intersect
    m.addConstrOr([x1, x3, x4] )


    # we maximize the total volume packed
    m.setObjective(gp.quicksum(b[i] * VQ[i] for i in range(n)), sense=gp.GRB.MINIMIZE)

    # require that a and b satisfy the inequalities for all x in X
    m.addConstrs(
        gp.quicksum(a[i, j] * X[l][j] for j in range(n)) <= b[i]
        for i, l in itertools.product(range(K), range(len(X)))
    )

    # separation of points in Y (optional)
    m.addConstrs(
        gp.quicksum(a[i, j] * Y[l][j] for j in range(n)) >= b[i] + eps - ((1 - s[i, l]) * M)
        for i, l in itertools.product(range(K), range(len(Y)))
    )

    # can only separate for active inequalities
    m.addConstrs(
        s[i, l] <= u[i]
        for i, l in itertools.product(range(K), range(len(Y)))
    )

    # separate for each y in Y with at least one inequality
    m.addConstrs(
        gp.quicksum(s[i, l] for i in range(K)) >= 1
        for l in range(len(Y))
    )

    m.optimize()

    # min empty space
    # s.t. all fit



##################
# MAIN FUNCTIONS #
##################

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print("ERROR: expected one argument, but got {c}.".format(c=len(args)))
        return -1

    mode = "greedy_01"

    while len(args) > 1:
        cur = args[0]
        args.remove(cur)

        if cur == "greedy_01":
            mode = "greedy_01"
            continue
        if cur == "greedy_02":
            mode = "greedy_02"
            continue
        elif cur == "bb":
            mode = "bb"
            continue
        else:
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

    if mode == "greedy_01":
        A, truth, hist = greedy_01(P, W, L, H)
    elif mode == "greedy_02":
        A, truth, hist = greedy_02(P, W, L, H)
    elif mode == "bb":
        A, truth, hist = branch_and_bound_pre(P, W, L, H)
    else:
        print("ERROR: mode {m} not supported".format(m=mode))
        return -1

    print("Found ordered assignment:")
    for p in A.A:
        print(p.to_string())

    print("\nProperties:")
    print("Algorithm completed: {t}".format(t=truth))
    print("Assignment fits in bounds: {t}".format(t=A.is_in_bounds()))
    print("Assignment has no overlap: {t}".format(t=not A.has_intersect()))
    print("Assignment is eps-bottom-stable: {t}".format(t=A.is_bottom_supported()))
    print("Assignment is eps-bottom-side-stable: {t}".format(t=A.is_bottom_side_supported()))
    # print("Assignment is delta-F-S-push-tolerant: {t}".format(t=A.is_F_S_push_tolerant([0,1,3,4], 1, DLT))) # force 1N
    # print("Assignment is a-acceleration-tolerant: {t}".format(t=A.is_a_acceleration_tolerant(1))) # acceleration 1m/ss

    make_figure(A.A, hist, W, L, H)

if __name__ == "__main__":
    main()