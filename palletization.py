import sys
#import pathlib
#import gurobipy as gp
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
ITER_MAX = 100000

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

def greedy_01(P, W, L, H):
    Q = sorted(P, key=lambda p: p.w * p.l * p.h, reverse=True) # volume decreasing
    queue = [ ]
    for p in Q:
        queue.append(p)
    A = Assignment(Q, W, L, H)
    open = [ (0, 0, 0) ] # points of interest
    iter = 0
    while len(queue) > 0 and iter < ITER_MAX:
        p = queue.pop(0)
        w, l, h = p.w, p.l, p.h
        wlh_tuples = itertools.permutations([w, l, h])
        has_place = False
        for (cur, wlh) in itertools.product(open, wlh_tuples):
            p.set(cur, wlh)
            if p.x + p.w > W or p.y + p.l > L or p.z + p.h > H : continue
            if p.has_intersect_set(Q[:iter]): continue

            open.remove(cur)
            open.extend([ (p.x + p.w, p.y, p.z), (p.x, p.y + p.l, p.z), (p.x, p.y, p.z + p.h) ])
            has_place = True
            break

        if not has_place: queue.append(p)
        iter += 1

    if iter >= ITER_MAX:
        print("ERROR: Maximum iterations exceeded {l} boxes remaining".format(l=len(queue)))
        for p in queue:
            print(p)

    return A, iter < ITER_MAX



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
            A, truth = greedy_01(P, W, L, H)
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
    # print("Assignment is eps-bottom-stable: {t}".format(t=A.is_bottom_supported()))
    # print("Assignment is eps-bottom-side-stable: {t}".format(t=A.is_bottom_side_supported()))
    # print("Assignment is delta-F-S-push-tolerant: {t}".format(t=A.is_F_S_push_tolerant([0,1,3,4], 1, DLT))) # force 1N
    # print("Assignment is a-acceleration-tolerant: {t}".format(t=A.is_a_acceleration_tolerant(1))) # acceleration 1m/ss

    make_figure(A.A, W, L, H)

if __name__ == "__main__":
    main()