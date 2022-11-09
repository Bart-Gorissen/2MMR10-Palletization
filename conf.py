####################
# GLOBAL VARIABLES #
####################

# margins and coefficients
EPS = 10 # error coefficient for tilted boxes
DLT = 5 # reaching coefficient for pushingstatic_coefficient = 1
ZETA = 0.75 # convex hull margin 0: tight line, 1: full hull on overlap

# default values
CNT = 10 # default number of pallets

# physical values
g = 3.14 ** 2 # gravitational acceleration
static_coefficient = 1 # coefficient of static friction

# program operation
verbose = 1 # 0 : only result, 1 : +important steps, 2 : +debug
ITER_MAX = 100 # maximum number of algorithm iterations
