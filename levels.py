#import gurobipy as gp

from assignment import *

# def gen_level_height(P, W, L, H):
#     A = Assignment([], W, L, H)
#
#     Q = [ p for p in P if p.w <= H or p.l <= H or p.h <= H ]
#     VQ = [ p.w * p.l * p.h for p in Q ]
#     n = len(Q)
#
#     m = gp.Model("compact")
#
#     # bottom-left coordinates
#     x = m.addVars(range(n), vtype=gp.GRB.CONTINUOUS, lb=0, ub=W, name="x")
#     y = m.addVars(range(n), vtype=gp.GRB.CONTINUOUS, lb=0, ub=L, name="y")
#     z = m.addVars(range(n), vtype=gp.GRB.CONTINUOUS, lb=0, ub=H, name="z")
#
#     # dimensions
#     w = m.addVars(range(n), vtype=gp.GRB.CONTINUOUS, lb=0, ub=W, name="w")
#     l = m.addVars(range(n), vtype=gp.GRB.CONTINUOUS, lb=0, ub=L, name="l")
#     h = m.addVars(range(n), vtype=gp.GRB.CONTINUOUS, lb=0, ub=H, name="h")
#
#     # used
#     b = m.addVars(range(n), vtype=gp.GRB.BINARY, name="b")
#
#     # each box should keep its dimensions
#
#
#     # each box should be in the pallet
#     m.addConstrs(gp.quicksum(x[i] + w[i] <= W) for i in range(n))
#     m.addConstrs(gp.quicksum(y[i] + l[i] <= L) for i in range(n))
#     m.addConstrs(gp.quicksum(z[i] + h[i] <= H) for i in range(n))
#
#     # boxes should not intersect
#     m.addConstrOr([x1, x3, x4] )
#
#
#     # we maximize the total volume packed
#     m.setObjective(gp.quicksum(b[i] * VQ[i] for i in range(n)), sense=gp.GRB.MINIMIZE)
#
#     # require that a and b satisfy the inequalities for all x in X
#     m.addConstrs(
#         gp.quicksum(a[i, j] * X[l][j] for j in range(n)) <= b[i]
#         for i, l in itertools.product(range(K), range(len(X)))
#     )
#
#     # separation of points in Y (optional)
#     m.addConstrs(
#         gp.quicksum(a[i, j] * Y[l][j] for j in range(n)) >= b[i] + eps - ((1 - s[i, l]) * M)
#         for i, l in itertools.product(range(K), range(len(Y)))
#     )
#
#     # can only separate for active inequalities
#     m.addConstrs(
#         s[i, l] <= u[i]
#         for i, l in itertools.product(range(K), range(len(Y)))
#     )
#
#     # separate for each y in Y with at least one inequality
#     m.addConstrs(
#         gp.quicksum(s[i, l] for i in range(K)) >= 1
#         for l in range(len(Y))
#     )
#
#     m.optimize()
#
#     # min empty space
#     # s.t. all fit
