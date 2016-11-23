from __future__ import division
from pyomo.environ import *

model = AbstractModel()


# Parameters cloud, and user
model.i = Param(within=NonNegativeIntegers)
model.j = Param(within=NonNegativeIntegers)

# Index sets
model.I = RangeSet(1, model.i)
model.J = RangeSet(1, model.j)

# Coefficients and right-hand-side data
model.a = Param(model.I)                        # Operational price
model.c = Param(model.I)                        # Reconfiguration price
model.d = Param(model.I, model.J)               # Delay price
model.b = Param(model.I)                        # Migration price

# Regularization paramters
model.eps1 = Param(within=NonNegativeReals)
model.eps2 = Param(within=NonNegativeReals)
model.pre = Param(model.I, model.J)


model.lbd = Param(model.J)                      # User workload
model.cap = Param(model.I)                      # Cloud capacity

# Variable: workload from user j on cloud i at time t
model.x = Var(model.I, model.J, domain=NonNegativeReals, initialize=0)

# Objective expression
def obj_expr(model):

    # Operational cost
    cost_op = sum(sum(
        model.a[i] * model.x[i,j]
        for j in model.J) for i in model.I)

    # Reconfiguration cost
    cost_rc = 0
    for i in model.I:
        cur = sum(model.x[i,j] for j in model.J)
        pre = sum(model.pre[i,j] for j in model.J)
        cost_rc += model.c[i] / log (1 + model.cap[i]/model.eps1) * \
                   (
                       (cur + model.eps1) *
                       log((cur + model.eps1)/(pre + model.eps1)) -
                       cur
                   )

    # Delay penalty cost
    cost_dl = summation(model.d, model.x)

    # Migration cost
    cost_mg = 0
    for i in model.I:
        for j in model.J:
            cost_mg += model.b[i] / log(1 + model.lbd[j]/model.eps2) * \
                       (
                           (model.x[i,j] + model.eps2) *
                           log((model.x[i,j] + model.eps2)/(model.pre[i,j] + model.eps2)) -
                           model.x[i,j]
                       )

    # return cost_op + cost_rc + cost_dl + cost_mg
    return cost_op + cost_rc + cost_dl + cost_mg

model.OBJ = Objective(rule=obj_expr)

def cov_const_rule(model, j):
    return sum(model.x[i,j] for i in model.I) >= model.lbd[j]


def cap_const_rule(model, i):
    return sum(model.x[i,j] for j in model.J) <= model.cap[i]




# Constraints
model.CovConst = Constraint(model.J, rule=cov_const_rule)
model.CapConst = Constraint(model.I, rule=cap_const_rule)