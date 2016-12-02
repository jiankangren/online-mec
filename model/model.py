from __future__ import division
from pyomo.environ import *



def create_abs_opt():

    model = AbstractModel()


    # Parameters for timeslot, cloud, and user
    model.t = Param(within=NonNegativeIntegers)
    model.i = Param(within=NonNegativeIntegers)
    model.j = Param(within=NonNegativeIntegers)

    model.alpha = Param(within=NonNegativeReals)
    model.beta = Param(within=NonNegativeReals)

    # Index sets
    model.T = RangeSet(1, model.t)
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
    model.y = Var(model.I, model.J, model.T, domain=NonNegativeReals, initialize=0)
    model.z = Var(model.I, model.T, domain=NonNegativeReals, initialize=0)

    # Objective expression
    def obj_expr(model):

        # Operational cost
        cost_op = sum(sum(sum(
            model.a[i,t] * model.x[i,j,t]
            for j in model.J) for i in model.I) for t in model.T)

        # Reconfiguration cost
        cost_rc = 0
        for t in model.T:
            if t == 1:
                continue
            for i in model.I:
                cost_rc += model.c[i] * model.z[i,t]

        # Delay penalty cost
        cost_dl = summation(model.d, model.x)

        # Migration cost
        cost_mg = 0
        for t in model.T:
            if t == 1:
                continue
            for i in model.I:
                for j in model.J:
                    cost_mg += model.b[i] * model.y[i,j,t]

        # return cost_op + cost_rc + cost_dl + cost_mg
        return (cost_op + cost_dl) * model.alpha + (cost_rc + cost_mg) * model.beta

    model.OBJ = Objective(rule=obj_expr)

    def cov_const_rule(model, j, t):
        return sum(model.x[i,j,t] for i in model.I) == model.lbd[j]

    def cap_const_rule(model, i, t):
        return sum(model.x[i,j,t] for j in model.J) <= model.cap[i]

    def mgr_const_rule(model, i, t):
        if t == 1:
            return model.z[i,t] >= sum(model.x[i,j,t] for j in model.J)
        else:
            return model.z[i,t] >= sum(model.x[i,j,t] for j in model.J) - sum(model.x[i,j,t-1] for j in model.J)

    def rcf_const_cule(model, i, j, t):
        if t == 1:
            return model.y[i,j,t] >= model.x[i,j,t]
        else:
            return model.y[i,j,t] >= model.x[i,j,t] - model.x[i,j,t-1]

    # Constraints
    model.CovConst = Constraint(model.J, model.T, rule=cov_const_rule)
    model.CapConst = Constraint(model.I, model.T, rule=cap_const_rule)
    model.MgrConst = Constraint(model.I, model.T, rule=mgr_const_rule)
    model.RcfConst = Constraint(model.I, model.J, model.T, rule=rcf_const_cule)

    return model


def create_abs_approx():

    model = AbstractModel()

    # Parameters cloud, and user
    model.i = Param(within=NonNegativeIntegers)
    model.j = Param(within=NonNegativeIntegers)

    model.alpha = Param(within=NonNegativeReals)
    model.beta = Param(within=NonNegativeReals)

    # Index sets
    model.I = RangeSet(1, model.i)
    model.J = RangeSet(1, model.j)

    # Coefficients and right-hand-side data
    model.a = Param(model.I)  # Operational price
    model.c = Param(model.I)  # Reconfiguration price
    model.d = Param(model.I, model.J)  # Delay price
    model.b = Param(model.I)  # Migration price

    # Regularization paramters
    model.eps1 = Param(within=NonNegativeReals)
    model.eps2 = Param(within=NonNegativeReals)
    model.pre = Param(model.I, model.J)

    model.lbd = Param(model.J)  # User workload
    model.cap = Param(model.I)  # Cloud capacity

    # Variable: workload from user j on cloud i at time t
    model.x = Var(model.I, model.J, domain=NonNegativeReals, initialize=0)

    # Objective expression
    def obj_expr(model):

        # Operational cost
        cost_op = sum(sum(
            model.a[i] * model.x[i, j]
            for j in model.J) for i in model.I)

        # Reconfiguration cost
        cost_rc = 0
        for i in model.I:
            cur_load = sum(model.x[i, j] for j in model.J)
            pre_load = sum(model.pre[i, j] for j in model.J)
            cost_rc += model.c[i] / log(1 + model.cap[i] / model.eps1) * \
                       (
                           (cur_load + model.eps1) *
                           log((cur_load + model.eps1) / (pre_load + model.eps1)) -
                           cur_load
                       )

        # Delay penalty cost
        cost_dl = summation(model.d, model.x)

        # Migration cost
        cost_mg = 0
        for i in model.I:
            for j in model.J:
                cost_mg += model.b[i] / log(1 + model.cap[i] / model.eps2) * \
                           (
                               (model.x[i, j] + model.eps2) *
                               log((model.x[i, j] + model.eps2) / (model.pre[i, j] + model.eps2)) -
                               model.x[i, j]
                           )

        # return cost_op + cost_rc + cost_dl + cost_mg
        return (cost_op + cost_dl) * model.alpha + (cost_rc + cost_mg) * model.beta

    model.OBJ = Objective(rule=obj_expr)

    def cov_const_rule(model, j):
        return sum(model.x[i, j] for i in model.I) == model.lbd[j]

    def cap_const_rule(model, i):
        return sum(model.x[i, j] for j in model.J) <= model.cap[i]

    # Constraints
    model.CovConst = Constraint(model.J, rule=cov_const_rule)
    model.CapConst = Constraint(model.I, rule=cap_const_rule)

    return model


def create_abs_greedy():

    model = AbstractModel()

    # Parameters cloud, and user
    model.i = Param(within=NonNegativeIntegers)
    model.j = Param(within=NonNegativeIntegers)

    model.alpha = Param(within=NonNegativeReals)
    model.beta = Param(within=NonNegativeReals)

    # Index sets
    model.I = RangeSet(1, model.i)
    model.J = RangeSet(1, model.j)

    # Coefficients and right-hand-side data
    model.a = Param(model.I)  # Operational price
    model.c = Param(model.I)  # Reconfiguration price
    model.d = Param(model.I, model.J)  # Delay price
    model.b = Param(model.I)  # Migration price

    # Previous solution
    model.pre = Param(model.I, model.J)

    model.lbd = Param(model.J)  # User workload
    model.cap = Param(model.I)  # Cloud capacity

    # Variable: workload from user j on cloud i at time t
    model.x = Var(model.I, model.J, domain=NonNegativeReals, initialize=0)
    model.y = Var(model.I, model.J, domain=NonNegativeReals, initialize=0)
    model.z = Var(model.I, domain=NonNegativeReals, initialize=0)

    # Objective expression
    def obj_expr(model):

        # Operational cost
        cost_op = sum(sum(
            model.a[i] * model.x[i, j]
            for j in model.J) for i in model.I)

        # Reconfiguration cost
        cost_rc = 0
        for i in model.I:
            cost_rc += model.c[i] * model.z[i]

        # Delay penalty cost
        cost_dl = summation(model.d, model.x)

        # Migration cost
        cost_mg = 0
        for i in model.I:
            for j in model.J:
                cost_mg += model.b[i] * model.y[i, j]

        # return cost_op + cost_rc + cost_dl + cost_mg
        return (cost_op + cost_dl) * model.alpha + (cost_rc + cost_mg) * model.beta

    model.OBJ = Objective(rule=obj_expr)

    def cov_const_rule(model, j):
        return sum(model.x[i, j] for i in model.I) == model.lbd[j]

    def cap_const_rule(model, i):
        return sum(model.x[i, j] for j in model.J) <= model.cap[i]

    def mgr_const_rule(model, i):
        return model.z[i] >= sum(model.x[i, j] for j in model.J) - sum(model.pre[i, j] for j in model.J)

    def rcf_const_cule(model, i, j):
        return model.y[i, j] >= model.x[i, j] - model.pre[i, j]

    # Constraints
    model.CovConst = Constraint(model.J, rule=cov_const_rule)
    model.CapConst = Constraint(model.I, rule=cap_const_rule)
    model.MgrConst = Constraint(model.I, rule=mgr_const_rule)
    model.RcfConst = Constraint(model.I, model.J, rule=rcf_const_cule)

    return model


def create_abs_greedy_perf():

    model = AbstractModel()

    # Parameters cloud, and user
    model.i = Param(within=NonNegativeIntegers)
    model.j = Param(within=NonNegativeIntegers)

    model.alpha = Param(within=NonNegativeReals)
    model.beta = Param(within=NonNegativeReals)

    # Index sets
    model.I = RangeSet(1, model.i)
    model.J = RangeSet(1, model.j)

    # Coefficients and right-hand-side data
    model.a = Param(model.I)  # Operational price
    model.c = Param(model.I)  # Reconfiguration price
    model.d = Param(model.I, model.J)  # Delay price
    model.b = Param(model.I)  # Migration price

    # Previous solution
    model.pre = Param(model.I, model.J)

    model.lbd = Param(model.J)  # User workload
    model.cap = Param(model.I)  # Cloud capacity

    # Variable: workload from user j on cloud i at time t
    model.x = Var(model.I, model.J, domain=NonNegativeReals, initialize=0)
    model.y = Var(model.I, model.J, domain=NonNegativeReals, initialize=0)
    model.z = Var(model.I, domain=NonNegativeReals, initialize=0)

    # Objective expression
    def obj_expr(model):

        # Operational cost
        cost_op = sum(sum(
            model.a[i] * model.x[i, j]
            for j in model.J) for i in model.I)

        # Reconfiguration cost
        cost_rc = 0
        for i in model.I:
            cost_rc += model.c[i] * model.z[i]

        # Delay penalty cost
        cost_dl = summation(model.d, model.x)

        # Migration cost
        cost_mg = 0
        for i in model.I:
            for j in model.J:
                cost_mg += model.b[i] * model.y[i, j]

        # return cost_op + cost_rc + cost_dl + cost_mg
        return (cost_dl) * model.alpha

    model.OBJ = Objective(rule=obj_expr)

    def cov_const_rule(model, j):
        return sum(model.x[i, j] for i in model.I) == model.lbd[j]

    def cap_const_rule(model, i):
        return sum(model.x[i, j] for j in model.J) <= model.cap[i]

    def mgr_const_rule(model, i):
        return model.z[i] >= sum(model.x[i, j] for j in model.J) - sum(model.pre[i, j] for j in model.J)

    def rcf_const_cule(model, i, j):
        return model.y[i, j] >= model.x[i, j] - model.pre[i, j]

    # Constraints
    model.CovConst = Constraint(model.J, rule=cov_const_rule)
    model.CapConst = Constraint(model.I, rule=cap_const_rule)
    model.MgrConst = Constraint(model.I, rule=mgr_const_rule)
    model.RcfConst = Constraint(model.I, model.J, rule=rcf_const_cule)

    return model


def create_abs_greedy_operation():

    model = AbstractModel()

    # Parameters cloud, and user
    model.i = Param(within=NonNegativeIntegers)
    model.j = Param(within=NonNegativeIntegers)

    model.alpha = Param(within=NonNegativeReals)
    model.beta = Param(within=NonNegativeReals)

    # Index sets
    model.I = RangeSet(1, model.i)
    model.J = RangeSet(1, model.j)

    # Coefficients and right-hand-side data
    model.a = Param(model.I)  # Operational price
    model.c = Param(model.I)  # Reconfiguration price
    model.d = Param(model.I, model.J)  # Delay price
    model.b = Param(model.I)  # Migration price

    # Previous solution
    model.pre = Param(model.I, model.J)

    model.lbd = Param(model.J)  # User workload
    model.cap = Param(model.I)  # Cloud capacity

    # Variable: workload from user j on cloud i at time t
    model.x = Var(model.I, model.J, domain=NonNegativeReals, initialize=0)
    model.y = Var(model.I, model.J, domain=NonNegativeReals, initialize=0)
    model.z = Var(model.I, domain=NonNegativeReals, initialize=0)

    # Objective expression
    def obj_expr(model):

        # Operational cost
        cost_op = sum(sum(
            model.a[i] * model.x[i, j]
            for j in model.J) for i in model.I)

        # Reconfiguration cost
        cost_rc = 0
        for i in model.I:
            cost_rc += model.c[i] * model.z[i]

        # Delay penalty cost
        cost_dl = summation(model.d, model.x)

        # Migration cost
        cost_mg = 0
        for i in model.I:
            for j in model.J:
                cost_mg += model.b[i] * model.y[i, j]

        # return cost_op + cost_rc + cost_dl + cost_mg
        return (cost_op) * model.alpha

    model.OBJ = Objective(rule=obj_expr)

    def cov_const_rule(model, j):
        return sum(model.x[i, j] for i in model.I) == model.lbd[j]

    def cap_const_rule(model, i):
        return sum(model.x[i, j] for j in model.J) <= model.cap[i]

    def mgr_const_rule(model, i):
        return model.z[i] >= sum(model.x[i, j] for j in model.J) - sum(model.pre[i, j] for j in model.J)

    def rcf_const_cule(model, i, j):
        return model.y[i, j] >= model.x[i, j] - model.pre[i, j]

    # Constraints
    model.CovConst = Constraint(model.J, rule=cov_const_rule)
    model.CapConst = Constraint(model.I, rule=cap_const_rule)
    model.MgrConst = Constraint(model.I, rule=mgr_const_rule)
    model.RcfConst = Constraint(model.I, model.J, rule=rcf_const_cule)

    return model


def create_abs_greedy_static():

    model = AbstractModel()

    # Parameters cloud, and user
    model.i = Param(within=NonNegativeIntegers)
    model.j = Param(within=NonNegativeIntegers)

    model.alpha = Param(within=NonNegativeReals)
    model.beta = Param(within=NonNegativeReals)

    # Index sets
    model.I = RangeSet(1, model.i)
    model.J = RangeSet(1, model.j)

    # Coefficients and right-hand-side data
    model.a = Param(model.I)  # Operational price
    model.c = Param(model.I)  # Reconfiguration price
    model.d = Param(model.I, model.J)  # Delay price
    model.b = Param(model.I)  # Migration price

    # Previous solution
    model.pre = Param(model.I, model.J)

    model.lbd = Param(model.J)  # User workload
    model.cap = Param(model.I)  # Cloud capacity

    # Variable: workload from user j on cloud i at time t
    model.x = Var(model.I, model.J, domain=NonNegativeReals, initialize=0)
    model.y = Var(model.I, model.J, domain=NonNegativeReals, initialize=0)
    model.z = Var(model.I, domain=NonNegativeReals, initialize=0)

    # Objective expression
    def obj_expr(model):

        # Operational cost
        cost_op = sum(sum(
            model.a[i] * model.x[i, j]
            for j in model.J) for i in model.I)

        # Reconfiguration cost
        cost_rc = 0
        for i in model.I:
            cost_rc += model.c[i] * model.z[i]

        # Delay penalty cost
        cost_dl = summation(model.d, model.x)

        # Migration cost
        cost_mg = 0
        for i in model.I:
            for j in model.J:
                cost_mg += model.b[i] * model.y[i, j]

        # return cost_op + cost_rc + cost_dl + cost_mg
        return (cost_op + cost_dl) * model.alpha

    model.OBJ = Objective(rule=obj_expr)

    def cov_const_rule(model, j):
        return sum(model.x[i, j] for i in model.I) == model.lbd[j]

    def cap_const_rule(model, i):
        return sum(model.x[i, j] for j in model.J) <= model.cap[i]

    def mgr_const_rule(model, i):
        return model.z[i] >= sum(model.x[i, j] for j in model.J) - sum(model.pre[i, j] for j in model.J)

    def rcf_const_cule(model, i, j):
        return model.y[i, j] >= model.x[i, j] - model.pre[i, j]

    # Constraints
    model.CovConst = Constraint(model.J, rule=cov_const_rule)
    model.CapConst = Constraint(model.I, rule=cap_const_rule)
    model.MgrConst = Constraint(model.I, rule=mgr_const_rule)
    model.RcfConst = Constraint(model.I, model.J, rule=rcf_const_cule)

    return model