import itertools
import sys
import os
#import pathlib
#import gurobipy as gp
#import itertools
import time
#import numpy as np
#import math

#from conf import *
#from util import *
#from item import *
#from assignment import *
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
        if len(line) > 4:
            P[-1].x = int(line[4])
            P[-1].y = int(line[5])
            P[-1].z = int(line[6])

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
    sort_method = "volume"
    lvl_fixed = True
    lvl_max = "total"
    lvl_support = False
    greedy_backup = False
    hist_only = False
    validate = False

    while len(args) > 1:
        cur = args[0]
        args.remove(cur)

        if cur == "greedy_01" or cur == "greedy_02" or cur == "greedy_03":
            mode = cur
        elif cur == "bb":
            mode = "bb"
        elif cur == "level_01" or cur == "level_02" or cur == "level_03":
            mode = cur
        elif cur[:5] == "sort:":
            sort_method = cur[5:]
        elif cur[:12] == "lambda A, p:":
            w_func = eval(cur)
        elif cur == "weight_const":
            w_func = const_1
        elif cur == "flat":
            w_func = flat
        elif cur == "weight_top":
            w_func = low_top
        elif cur == "weight_center":
            w_func = far_center
        elif cur == "weight_center_flat":
            w_func = far_center_flat
        elif cur == "weight_center_top":
            w_func = far_center_low_top
        elif cur == "flat_top":
            w_func = flat_low_top
        elif cur == "weight_center_flat_top":
            w_func = far_center_flat_low_top
        elif cur == "custom":
            w_func = custom
        elif cur == "total" or cur == "density":
            lvl_max = cur
        elif cur == "twoqueue":
            greedy_backup = True
        elif cur == "onequeue":
            greedy_backup = False
        elif cur == "support":
            lvl_support = True
        elif cur == "freeform":
            lvl_support = False
        elif cur == "fix_p":
            lvl_fixed = True
        elif cur == "loose_p":
            lvl_fixed = False
        elif cur == "no_dots":
            hist_dots = False
        elif cur == "no_vis":
            figure = False
        elif cur == "histo":
            hist_only = True
        elif cur == "validate":
            validate = True
        else:
            print("ERROR: argument {a} not supported".format(a=cur))
            return -1

    path = args[0]
    P = read_instance(path)
    W, L, H = 800, 1200, 1500
    A = [ ]

    if hist_only:
        make_histo(P, os.path.basename(path).split('/')[-1])
        return 1

    if verbose >= 1:
        print("Running on items:")
        for p in P:
            print(p.to_string())

    print("\nVerbose mode {v}\n".format(v=verbose))

    time_start = time.time()

    if not validate:
        if mode == "greedy_01" or mode == "greedy_02" or mode == "greedy_03":
            A, truth, hist = greedy(P, W, L, H, method=sort_method, algo=mode, w=w_func, backup=greedy_backup)
        elif mode == "bb":
            A, truth, hist = branch_and_bound_pre(P, W, L, H)
        elif mode == "level_01" or mode == "level_02" or mode == "level_03":
            A, truth, hist = levels(P, W, L, H, fixed=lvl_fixed, method=mode, max_obj=lvl_max, sort=sort_method, support=lvl_support)
        else:
            print("ERROR: mode {m} not supported".format(m=mode))
            return -1
    else:
        A, truth, hist = Assignment(P, W, L, H), True, [ ]

    time_end = time.time()

    print("Found ordered assignment:")
    for p in A.A:
        print(p.to_string())
    print("")
    if len(A.A) != len(P):
        print("Missing {n} items".format(n=len(P) - len(A.A)))
        for p in P:
            if p not in A.A: print(p)

    V_tot, V_eff, V_use = compute_space(A.A, W, L, H)
    V_item_total = 0
    for p in P: V_item_total += p.w * p.l * p.h

    print("\nProperties:")
    print("Time: {t} seconds".format(t=round(time_end-time_start,3)))
    print("Total volume used {use} / {tot} ({per_1}%)".format(use=V_use, tot=V_tot, per_1=round(V_use*100/V_tot,3)))
    if V_eff > 0: print("Effective volume used {use} / {tot} ({per_1}%)".format(use=V_use, tot=V_eff, per_1=round(V_use*100/ V_eff, 3)))
    if V_eff == 0: print("Effective volume used {use} / {tot} ({per_1}%)".format(use=V_use, tot=V_eff, per_1=100))
    print("Item volume used {use} / {tot} ({per_1}%)".format(use=V_use, tot=V_item_total, per_1=round(V_use * 100 / V_item_total, 3)))
    print("Algorithm completed: {t}".format(t=truth))
    print("Assignment fits in bounds: {t}".format(t=A.is_in_bounds()))
    print("Assignment has no overlap: {t}".format(t=not A.has_intersect()))
    print("Assignment is eps-bottom-stable: {t}".format(t=A.is_bottom_supported()))
    print("Assignment is eps-bottom-side-stable: {t}".format(t=A.is_bottom_side_supported()))
    # print("Assignment is delta-F-S-push-tolerant: {t}".format(t=A.is_F_S_push_tolerant([0,1,3,4], 10, DLT))) # force 1N
    # print("Assignment is a-acceleration-tolerant: {t}".format(t=A.is_a_acceleration_tolerant(1))) # acceleration 1m/ss

    if figure:
        if hist_dots: make_figure(A.A, hist, W, L, H)
        else: make_figure(A.A, [], W, L, H)

if __name__ == "__main__":
    main()