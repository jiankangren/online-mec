from __future__ import division
from pyomo.environ import *

model = AbstractModel()


# Parameters for timeslot, cloud, and user
model.t = Param(within=NonNegativeIntegers)
model.i = Param(within=NonNegativeIntegers)
model.j = Param(within=NonNegativeIntegers)

# Index sets
model.T = RangeSet(0, model.t)
model.I = RangeSet(1, model.i)
model.J = RangeSet(1, model.j)

# Coefficients and right-hand-side data
model.a = Param(model.I, model.T)               # Operational price
model.c = Param(model.I)                        # Reconfiguration price
model.d = Param(model.I, model.J, model.T)      # Delay price
model.b = Param(model.I)                        # Migration price

model.lbd = Param(model.J)                      # User workload
model.cap = Param(model.I)                      # Cloud capacity

# Variable: workload from user j on cloud i at time t
model.x = Var(model.I, model.J, model.T, domain=NonNegativeReals, initialize=0)

# Objective expression
def obj_expr(model):

    # Operational cost
    cost_op = sum(sum(sum(
        model.a[i,t] * model.x[i,j,t]
        for j in model.J) for i in model.I) for t in model.T)

    # Reconfiguration cost
    cost_rc = 0
    for t in model.T:
        if t == 0:
            continue
        for i in model.I:
            cur_load = sum(model.x[i,j,t] for j in model.J)
            pre_load = sum(model.x[i,j,t-1] for j in model.J)
            inc_load = cur_load - pre_load
            cost_rc += model.c[i] * (abs(inc_load) + inc_load) / 2

    # Delay penalty cost
    cost_dl = summation(model.d, model.x)

    # Migration cost
    cost_mg = 0
    for t in model.T:
        # No migration in timeslots 0 and 1
        if t <= 1:
            continue
        for i in model.I:
            for j in model.J:
                mg_load = model.x[i,j,t] - model.x[i,j,t-1]
                cost_mg += model.b[i] * (abs(mg_load) + mg_load) / 2

    # return cost_op + cost_rc + cost_dl + cost_mg
    return cost_op + cost_rc + cost_dl + cost_mg

model.OBJ = Objective(rule=obj_expr)


def cov_const_rule(model, j, t):
    if t == 0:
        return sum(model.x[i,j,t] for i in model.I) == 0
    return sum(model.x[i,j,t] for i in model.I) >= model.lbd[j]


def cap_const_rule(model, i, t):
    if t == 0:
        return sum(model.x[i,j,t] for j in model.J) == 0
    return sum(model.x[i,j,t] for j in model.J) <= model.cap[i]



# Constraints
model.CovConst = Constraint(model.J, model.T, rule=cov_const_rule)
model.CapConst = Constraint(model.I, model.T, rule=cap_const_rule)













