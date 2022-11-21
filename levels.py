from assignment import *

def levels(P, W, L, H, fixed=True, method="level_01", max_obj="total", sort="volume", support=False):
    print("Error: method not implemented, switch to ``Layers'' branch")
    A = Assignment([], W, L, H)
    return A, False, []