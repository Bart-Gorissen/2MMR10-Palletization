import itertools
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
from greedy import *
from branchbound import *
from levels import *

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



##################
# MAIN FUNCTIONS #
##################

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print("ERROR: expected one argument, but got {c}.".format(c=len(args)))
        return -1

    mode = "greedy_01"
    # w_func = lambda x, y: 1  # constant weight -> counting
    w_func = lambda A, p: (A.H - (p.z + p.h)) # lower top = better
    figure = True
    hist_dots = True

    while len(args) > 1:
        cur = args[0]
        args.remove(cur)

        if cur == "greedy_01":
            mode = "greedy_01"
            continue
        if cur == "greedy_02":
            mode = "greedy_02"
            continue
        if cur == "greedy_03":
            mode = "greedy_03"
            continue
        elif cur == "bb":
            mode = "bb"
            continue
        elif cur[:12] == "lambda A, p:":
            w_func = eval(cur)
            continue
        elif cur == "no_dots":
            hist_dots = False
            continue
        elif cur == "no_vis":
            figure = False
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
    elif mode == "greedy_03":
        A, truth, hist = greedy_03(P, W, L, H, w_func)
    elif mode == "bb":
        A, truth, hist = branch_and_bound_pre(P, W, L, H)
    else:
        print("ERROR: mode {m} not supported".format(m=mode))
        return -1

    print("Found ordered assignment:")
    for p in A.A:
        print(p.to_string())
    print("")
    if len(A.A) != len(P):
        print("Missing {n} items".format(n=len(P) - len(A.A)))
        for p in P:
            if p not in A.A: print(p)

    print("\nProperties:")
    print("Algorithm completed: {t}".format(t=truth))
    print("Assignment fits in bounds: {t}".format(t=A.is_in_bounds()))
    print("Assignment has no overlap: {t}".format(t=not A.has_intersect()))
    print("Assignment is eps-bottom-stable: {t}".format(t=A.is_bottom_supported()))
    print("Assignment is eps-bottom-side-stable: {t}".format(t=A.is_bottom_side_supported()))
    # print("Assignment is delta-F-S-push-tolerant: {t}".format(t=A.is_F_S_push_tolerant([0,1,3,4], 1, DLT))) # force 1N
    # print("Assignment is a-acceleration-tolerant: {t}".format(t=A.is_a_acceleration_tolerant(1))) # acceleration 1m/ss

    if figure:
        if hist_dots: make_figure(A.A, hist, W, L, H)
        else: make_figure(A.A, [], W, L, H)

if __name__ == "__main__":
    main()