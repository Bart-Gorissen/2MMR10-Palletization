import itertools

import gurobipy as gp

from util import *
from assignment import *

# post-processing for applying gravity
def post_collapse_gen(A, s):
    stable = False
    while not stable:
        stable = True

        for p in A.A:
            if A.bottom_support(p): continue
            if s % 6 == 0: max_move = A.W - p.x
            if s % 6 == 1: max_move = A.L - p.y
            if s % 6 == 2: max_move = A.H - p.z
            if s % 6 == 3: max_move = p.x
            if s % 6 == 4: max_move = p.y
            if s % 6 == 5: max_move = p.z
            for q in A.A:
                if p == q: continue
                if not is_behind(p, q, s): continue
                if s % 6 == 0: aux = q.x - (p.x + p.w)
                if s % 6 == 1: aux = q.y - (p.y + p.l)
                if s % 6 == 2: aux = q.z - (p.z + p.h)
                if s % 6 == 3: aux = p.x - (q.x + q.w)
                if s % 6 == 4: aux = p.y - (q.y + q.l)
                if s % 6 == 5: aux = p.z - (q.z + q.h)

                max_move = min(max_move, aux)
            if max_move > 0:
                stable = False
                if s % 6 == 0: p.x += max_move
                if s % 6 == 1: p.y += max_move
                if s % 6 == 2: p.z += max_move
                if s % 6 == 3: p.x -= max_move
                if s % 6 == 4: p.y -= max_move
                if s % 6 == 5: p.z -= max_move

# post processing for gravity in z- direction
def post_collapse(A):
    stable = False
    while not stable:
        stable = True

        for p in A.A:
            if A.bottom_support(p): continue
            max_move = p.z
            for q in A.A:
                if p == q: continue
                if not is_behind(p, q, 5): continue
                max_move = min(max_move, p.z - (q.z + q.h))
            if max_move > 0:
                stable = True
                p.z -= max_move

# construct IP model and run
# P : set of items
# W, L, H : level dimensions
# max_obj : whether to optimize total volume placed or density of layer
# p : box to force include in layer
# fix_to_p : max height does not exceed that of p
# support : forces strong eps-bottom-support (for the layer)
def run_model(P, W, L, H, p=-1, max_obj="total", fix_to_p=False, support=False):
    n = len(P)
    VP = [p.w * p.l * p.h for p in P]

    m = gp.Model("layer_gen")
    m.setParam("OutputFlag", 0)

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
    if support:
        supp = m.addVars(itertools.product(range(n), range(n)), vtype=gp.GRB.BINARY, name="supp")
        supp_floor = m.addVars(range(n), vtype=gp.GRB.BINARY, name="floor_supp")

    # indicators
    t = m.addVars(range(n), vtype=gp.GRB.BINARY, name="t")
    dim_var = m.addVars(itertools.product(range(n), range(9)), vtype=gp.GRB.BINARY, name="dim_var")
    dim_var_or = m.addVars(itertools.product(range(n), range(3)), vtype=gp.GRB.BINARY, name="dim_var_or")
    int_var = m.addVars(itertools.product(range(n), range(6)), vtype=gp.GRB.BINARY, name="int_var")

    # indicator for validity
    m.addConstrs((b[i] == 1) >> (t[i] == 1) for i in range(n))

    # each box should keep its dimensions
    m.addConstrs((dim_var[i, 0] == 1) >> (w[i] == P[i].w) for i in range(n))
    m.addConstrs((dim_var[i, 1] == 1) >> (l[i] == P[i].w) for i in range(n))
    m.addConstrs((dim_var[i, 2] == 1) >> (h[i] == P[i].w) for i in range(n))
    m.addConstrs((dim_var[i, 3] == 1) >> (w[i] == P[i].l) for i in range(n))
    m.addConstrs((dim_var[i, 4] == 1) >> (l[i] == P[i].l) for i in range(n))
    m.addConstrs((dim_var[i, 5] == 1) >> (h[i] == P[i].l) for i in range(n))
    m.addConstrs((dim_var[i, 6] == 1) >> (w[i] == P[i].h) for i in range(n))
    m.addConstrs((dim_var[i, 7] == 1) >> (l[i] == P[i].h) for i in range(n))
    m.addConstrs((dim_var[i, 8] == 1) >> (h[i] == P[i].h) for i in range(n))

    m.addConstrs(dim_var_or[i, 0] == gp.or_(dim_var[i, 0], dim_var[i, 1], dim_var[i, 2]) for i in range(n))
    m.addConstrs(dim_var_or[i, 1] == gp.or_(dim_var[i, 3], dim_var[i, 4], dim_var[i, 5]) for i in range(n))
    m.addConstrs(dim_var_or[i, 2] == gp.or_(dim_var[i, 6], dim_var[i, 7], dim_var[i, 8]) for i in range(n))

    m.addConstrs(t[i] == gp.and_(dim_var_or[i, 0], dim_var_or[i, 1], dim_var_or[i, 2]) for i in range(n))

    # each box should be in the pallet
    m.addConstrs(x[i] + w[i] <= W for i in range(n))
    m.addConstrs(y[i] + l[i] <= L for i in range(n))
    m.addConstrs(z[i] + h[i] <= H for i in range(n))

    # boxes should not intersect
    m.addConstrs((int_var[i, 0] == 1) >> (x[i] + w[i] <= x[j]) for i, j in itertools.combinations(range(n), 2))
    m.addConstrs((int_var[i, 1] == 1) >> (x[j] + w[j] <= x[i]) for i, j in itertools.combinations(range(n), 2))
    m.addConstrs((int_var[i, 2] == 1) >> (y[i] + l[i] <= y[j]) for i, j in itertools.combinations(range(n), 2))
    m.addConstrs((int_var[i, 3] == 1) >> (y[j] + l[j] <= y[i]) for i, j in itertools.combinations(range(n), 2))
    m.addConstrs((int_var[i, 4] == 1) >> (z[i] + h[i] <= z[j]) for i, j in itertools.combinations(range(n), 2))
    m.addConstrs((int_var[i, 5] == 1) >> (z[j] + h[j] <= z[i]) for i, j in itertools.combinations(range(n), 2))

    m.addConstrs(t[i] == gp.or_(int_var[i, 0], int_var[i, 1], int_var[i, 2],
                                int_var[i, 3], int_var[i, 4], int_var[i, 5]) for i in range(n))

    # strong support
    if support:
        m.addConstrs(supp[i, i] == 0 for i in range(n)) # no box supports itself
        m.addConstrs(supp[i, j] <= b[i] for i, j in itertools.product(range(n), range(n))) # only active boxes can support
        m.addConstrs(gp.quicksum(supp[i, j] for i in range(n) if i != j) + supp_floor[j] >= b[j] for j in range(n)) # every active box is supported by one other box (or floor)

        # contained along x
        m.addConstrs((supp[i, j] == 1) >> (x[i] + ((1 - ZETA) * w[i]) <= x[j] + (w[j] / 2)) for i, j in
                     itertools.product(range(n), range(n))) # c_grav (middle) contained along x
        m.addConstrs((supp[i, j] == 1) >> (x[j] + (w[j] / 2) <= x[i] + (ZETA * w[i])) for i, j in
                     itertools.product(range(n), range(n)))  # c_grav (middle) contained along x

        # contained along y
        m.addConstrs((supp[i, j] == 1) >> (y[i] + ((1 - ZETA) * l[i]) <= y[j] + (l[j] / 2)) for i, j in
                    itertools.product(range(n), range(n)))  # c_grav (middle) contained along y
        m.addConstrs((supp[i, j] == 1) >> (y[j] + (l[j] / 2) <= y[i] + (ZETA * l[i])) for i, j in
                     itertools.product(range(n), range(n)))  # c_grav (middle) contained along y

        # close in z
        m.addConstrs((supp[i, j] == 1) >> (z[i] + h[i] <= z[j]) for i, j in
                     itertools.product(range(n), range(n))) # supporting box is below supported box
        m.addConstrs((supp[i, j] == 1) >> (z[i] + h[i] + EPS >= z[j]) for i, j in
                      itertools.product(range(n), range(n)))  # supporting box is close below supported box
        m.addConstrs((supp_floor[j] == 1) >> (EPS >= z[j]) for j in range(n)) # box is close to the floor

    if p != -1: m.addConstr(b[P.index(p)] == 1) # require that p is in the level
    if fix_to_p: m.addConstrs(z[i] + h[i] <= h[P.index(p)] for i in range(n)) # require that p determines level height

    # we maximize the total volume packed (this unfortunately does not bound the height directly...
    m.setObjective(gp.quicksum(b[i] * VP[i] for i in range(n)), sense=gp.GRB.MAXIMIZE)

    # run model (stop after max(time first solution, time_cutoff)
    oldSolutionLimit = m.Params.SolutionLimit
    m.Params.SolutionLimit = 1
    m.optimize()
    m.Params.TimeLimit = time_cutoff - m.getAttr(gp.GRB.Attr.Runtime)
    m.Params.SolutionLimit = oldSolutionLimit - m.Params.SolutionLimit
    m.optimize()

    status = m.getAttr("status")
    if status == 3 or status == 4:
        return -1, False, -1

    # collect assignment
    A = Assignment([], W, L, H)

    for i in range(n):
        if b[i].X == 1 :
            P[i].set((round(x[i].X), round(y[i].X), round(z[i].X)), (round(w[i].X), round(l[i].X), round(h[i].X)))
            A.add(P[i])

    # post_collapse_gen(A, 5)
    # post_collapse_gen(A, 3)
    # post_collapse_gen(A, 4)
    valid = A.is_in_bounds() and (not A.has_intersect()) and A.is_bottom_supported()

    if max_obj == "total": res = m.objVal
    elif max_obj == "density":
        h = max([ p.z + p.h for p in A.A ])
        if h == 0 : h = H
        res = m.objVal / (W * L * h)

    return A, valid, res

# tries to construct best layer (tries a layer for all dimensions and chooses best)
# P : set of items
# W, L: pallet dimensions
# max_obj : whether to optimize total volume placed or density of layer
# support : forces strong eps-bottom-support (for the layer)
def get_best_level_01(P, W, L, max_obj="total", support=False): # fixes height first
    levels = []
    Pdims = set()
    for p in P: Pdims.update([p.w, p.l, p.h])
    if verbose >= 2: print("Generating {p} layers".format(p=len(Pdims)))

    for h in Pdims:
        A, valid, obj = run_model(P, W, L, h, p=-1, max_obj=max_obj, support=support)
        if verbose >= 2: print("Finished layer {h}".format(h=h))
        if valid: levels.append((p, obj, h))

    levels.sort(key=lambda x: x[1], reverse=True)
    return levels[0]

# tries to construct best layer (tries for each item and dimension a layer (possibly with fixed item) and chooses best)
# P : set of items
# W, L: pallet dimensions
# fixed : whether to fix the item for which we generate the layer
# max_obj : whether to optimize total volume placed or density of layer
# support : forces strong eps-bottom-support (for the layer)
def get_best_level_02(P, W, L, fixed=True, max_obj="total", support=False): # fixes box first
    levels = []

    if verbose >= 2: print("Generating {p} layers".format(p=len(P)*3))
    for p in P:
        for h in [p.w, p.l, p.h]:
            if not fixed: A, valid, obj = run_model(P, W, L, h, p=-1, max_obj=max_obj, support=support)
            else: A, valid, obj = run_model(P, W, L, h, p=p, max_obj=max_obj, support=support)
            if verbose >= 2: print("Finished layer {h}".format(h=h))
            if valid: levels.append((p, obj, h))

    levels.sort(key=lambda x: x[1], reverse=True)
    return levels[0]

# tries to construct best layer, heuristically chooses an item to fix in the level
# P : set of items
# W, L: pallet dimensions
# fixed : whether to fix the height of the layer to the fixed item (for which we generate the layer)
# max_obj : whether to optimize total volume placed or density of layer
# sort : how to choose item for next layer
# support : forces strong eps-bottom-support (for the layer)
def get_best_level_03(P, W, L, fixed=True, max_obj="total", sort="volume", support=False): # fixes highest volume box, fixed controls whether p determines height level
    p = sort_points(P, method=sort)[0]
    # if len(P) > 10:
    h = max(p.w, p.l, p.h)
    # else:
    #     h = max([ max(p.w, p.l, p.h) for p in P ])
    A, valid, obj = run_model(P, W, L, h, p=p, max_obj=max_obj, fix_to_p=fixed, support=support)

    if not valid: print("ERROR: Generated invalid layer with expected feasible solution")

    return A, h, obj


# tries to construct best layer (tries for each item and dimension a layer (possibly with fixed item) and chooses best)
# P : set of items
# W, L, H: pallet dimensions
# fixed : depends on method (see above functions) level_01 nothing, level_02 fix p to layer, level_03 fix layer height to p
# method : which function to use for level generation
# max_obj : whether to optimize total volume placed or density of layer
# sort : how to choose best item (only for level_03)
# support : forces strong eps-bottom-support (for the layer)
def levels(P, W, L, H, fixed=True, method="level_01", max_obj="total", sort="volume", support=False):
    queue = [ ]
    for p in P: queue.append(p)
    A_full = Assignment([], W, L, H)
    cur_height = 0

    while len(queue) > 0:
        # get best layer constructors
        if method == "level_01": (p, obj, h) = get_best_level_01(queue, W, L, max_obj=max_obj, support=support)
        elif method == "level_02": (p, obj, h) = get_best_level_02(queue, W, L, fixed=fixed, max_obj=max_obj, support=support)
        elif method =="level_03": A, h, obj = get_best_level_03(queue, W, L, fixed=fixed, max_obj=max_obj, sort=sort, support=support)

        # construct best layer
        if (not fixed) or method == "level_01": A, _, obj = run_model(queue, W, L, h, p=-1, max_obj=max_obj, support=support)
        elif method == "level_02": A, _, obj = run_model(queue, W, L, h, p=p, max_obj=max_obj, support=support)

        # raise layer to correct height and add layer to assignment, remove from remaining
        if verbose >= 2: print("Found layer with objective {v}:".format(v=obj))
        h = max([ p.z + p.h for p in A.A ])
        for q in A.A:
            if verbose >= 3: print(q)
            q.z += cur_height
            A_full.add(q)
            queue.remove(q)
        cur_height += h

    # post_collapse_gen(A_full, 3)
    # post_collapse_gen(A_full, 4)
    # post_collapse_gen(A_full, 5)

    return A_full, True, []