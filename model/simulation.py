import sys
import argparse
from pyomo.opt import SolverFactory

from model import *
from util import *


def run_opt(input_opt):

    #print "Creating instance..."
    abs_model = create_abs_opt()
    instance = abs_model.create_instance(input_opt)
    opt = SolverFactory("ipopt")

    #print "Solving..."
    results = opt.solve(instance, options={'tol': 0.01})
    instance.solutions.store_to(results)
    return instance


def run_approx(input_approx):

    #print "Creating instance..."
    abs_model = create_abs_approx()
    instance = abs_model.create_instance(input_approx)
    opt = SolverFactory("ipopt")

    #print "Solving..."
    results = opt.solve(instance)
    instance.solutions.store_to(results)
    return instance


def run_greedy(input_greedy):

    #print "Creating instance..."
    abs_model = create_abs_greedy()
    instance = abs_model.create_instance(input_greedy)
    opt = SolverFactory("ipopt")

    #print "Solving..."
    results = opt.solve(instance)
    instance.solutions.store_to(results)
    return instance


def run_greedy_perf(input_perf):

    #print "Creating instance..."
    abs_model = create_abs_greedy_perf()
    instance = abs_model.create_instance(input_perf)
    opt = SolverFactory("ipopt")

    #print "Solving..."
    results = opt.solve(instance)
    instance.solutions.store_to(results)
    return instance


def run_greedy_operation(input_operation):

    #print "Creating instance..."
    abs_model = create_abs_greedy_operation()
    instance = abs_model.create_instance(input_operation)
    opt = SolverFactory("ipopt")

    #print "Solving..."
    results = opt.solve(instance)
    instance.solutions.store_to(results)
    return instance


def run_greedy_static(input_static):

    #print "Creating instance..."
    abs_model = create_abs_greedy_static()
    instance = abs_model.create_instance(input_static)
    opt = SolverFactory("ipopt")

    #print "Solving..."
    results = opt.solve(instance)
    instance.solutions.store_to(results)
    return instance


def main(file_d, file_loc, is_gen, solution, alpha, beta, eps1, eps2):

    ni = 15
    nt = 60
    nj = 0

    mat_a = []
    mat_b = []
    mat_c = []

    mat_d = read_mat_d(file_d)
    mat_loc = read_mat_loc(file_loc)
    nj = len(mat_loc)

    mat_lbd = []
    mat_cap = []

    if is_gen:
        mat_a = gen_mat_a(ni, nt)
        mat_b = gen_mat_b(ni)
        mat_c = gen_mat_c(ni)

        mat_lbd = gen_mat_lbd(nj, is_gen)
        mat_cap = gen_mat_cap(ni, mat_lbd, mat_loc)

        return

    else:
        mat_a = read_mat_a("./data/a.dat")
        mat_b = read_mat_b("./data/b.dat")
        mat_c = read_mat_b("./data/c.dat")

        mat_lbd = read_mat_lbd("./data/lbd.dat")
        mat_cap = read_mat_cap("./data/cap.dat")

    if solution == "opt" or solution == "all":
        input_opt = "./data/opt.dat"
        gen_input_opt(input_opt, ni, nj, nt, mat_a, mat_b, mat_c, mat_d, mat_loc, mat_lbd, mat_cap, alpha, beta)
        instance = run_opt(input_opt)

        #for t in range(nt):
            #print "Resource allocated: {}".format(
            #    sum(sum(instance.x[i + 1, j + 1, t + 1].value for j in range(nj)) for i in range(ni)))
            #print "Resource needed: {}".format(sum(mat_lbd[j] for j in range(nj)))

        print "The optimal objective value is: {}".format(instance.OBJ())

    if solution == "approx" or solution == "all":

        obj_approx = 0
        stat_approx = 0
        dync_approx = 0
        mat_pre = [[0 for j in range(nj)] for i in range(ni)]

        for t in range(nt):

            #print "Starting iteration {}...".format(t + 1)

            input_approx = "./data/approx_{}.dat".format(t + 1)
            gen_input_approx(input_approx, t + 1, ni, nj, nt, mat_a, mat_b, mat_c, mat_d,
                         mat_loc, mat_lbd, mat_cap, mat_pre, alpha, beta, eps1, eps2)
            instance = run_approx(input_approx)

            stat_approx += alpha * sum(sum(
                                mat_a[i][t] * instance.x[i + 1, j + 1].value
                            for j in range(nj)) for i in range(ni))
            stat_approx += alpha * sum(sum(
                                mat_d[i][mat_loc[j][t]] * instance.x[i + 1, j + 1].value
                            for j in range(nj)) for i in range(ni))



            if t != 0:
                for i in range(ni):
                    load_cur = sum(instance.x[i + 1, j + 1].value for j in range(nj))
                    load_pre = sum(mat_pre[i][j] for j in range(nj))
                    dync_approx += beta * mat_c[i] * (abs(load_cur - load_pre) + load_cur - load_pre) / 2

                dync_approx += beta * sum(sum(
                        mat_b[i] * (abs(instance.x[i + 1, j + 1].value - mat_pre[i][j])
                                + (instance.x[i + 1, j + 1].value - mat_pre[i][j]))/2
                        for j in range(nj)) for i in range(ni))

            #print "Resource allocated: {}".format(
            #    sum(sum(instance.x[i + 1, j + 1].value for j in range(nj)) for i in range(ni)))
            #print "Resource needed: {}".format(sum(mat_lbd[j] for j in range(nj)))

            for i in range(ni):
                for j in range(nj):
                    mat_pre[i][j] = instance.x[i + 1, j + 1].value

        print "The approximated static cost is: {}".format(stat_approx)
        print "The approximated dynamic cost is: {}".format(dync_approx)
        print "The approximited objective value is: {}".format(stat_approx + dync_approx)


    if solution == "greedy" or solution == "all":

        obj_greedy = 0
        stat_greedy = 0
        dync_greedy = 0
        mat_pre = [[0 for j in range(nj)] for i in range(ni)]

        for t in range(nt):

            #print "Starting iteration {}...".format(t + 1)

            input_greedy = "./data/greedy_{}.dat".format(t + 1)
            gen_input_greedy(input_greedy, t + 1, ni, nj, nt, mat_a, mat_b, mat_c, mat_d,
                         mat_loc, mat_lbd, mat_cap, mat_pre, alpha, beta)
            instance = run_greedy(input_greedy)
            # obj_greedy += instance.OBJ()


            stat_greedy += alpha * sum(sum(
                mat_a[i][t] * instance.x[i + 1, j + 1].value
                for j in range(nj)) for i in range(ni))
            stat_greedy += alpha * sum(sum(
                mat_d[i][mat_loc[j][t]] * instance.x[i + 1, j + 1].value
                for j in range(nj)) for i in range(ni))

            if t != 0:
                for i in range(ni):
                    load_cur = sum(instance.x[i + 1, j + 1].value for j in range(nj))
                    load_pre = sum(mat_pre[i][j] for j in range(nj))
                    dync_greedy += beta * mat_c[i] * (abs(load_cur - load_pre) + load_cur - load_pre) / 2

                dync_greedy += beta * sum(sum(
                    mat_b[i] * (abs(instance.x[i + 1, j + 1].value - mat_pre[i][j])
                            + (instance.x[i + 1, j + 1].value - mat_pre[i][j])) / 2
                    for j in range(nj)) for i in range(ni))

            #print "Resource allocated: {}".format(
            #    sum(sum(instance.x[i + 1, j + 1].value for j in range(nj)) for i in range(ni)))
            #print "Resource needed: {}".format(sum(mat_lbd[j] for j in range(nj)))


            for i in range(ni):
                for j in range(nj):
                    mat_pre[i][j] = instance.x[i + 1, j + 1].value

        print "The greedy static cost is: {}".format(stat_greedy)
        print "The greedy dynamic cost is: {}".format(dync_greedy)
        print "The greedy objective value is: {}".format(stat_greedy + dync_greedy)



    if solution == "perf" or solution == "all":

        obj_perf = 0
        mat_pre = [[0 for j in range(nj)] for i in range(ni)]

        for t in range(nt):

            #print "Starting iteration {}...".format(t + 1)

            input_perf = "./data/perf_{}.dat".format(t + 1)
            gen_input_greedy(input_perf, t + 1, ni, nj, nt, mat_a, mat_b, mat_c, mat_d,
                             mat_loc, mat_lbd, mat_cap, mat_pre, alpha, beta)
            instance = run_greedy_perf(input_perf)

            obj_perf += alpha * sum(sum(
                mat_a[i][t] * instance.x[i + 1, j + 1].value
                for j in range(nj)) for i in range(ni))
            obj_perf += alpha * sum(sum(
                mat_d[i][mat_loc[j][t]] * instance.x[i + 1, j + 1].value
                for j in range(nj)) for i in range(ni))

            if t != 0:
                for i in range(ni):
                    load_cur = sum(instance.x[i + 1, j + 1].value for j in range(nj))
                    load_pre = sum(mat_pre[i][j] for j in range(nj))
                    obj_perf += beta * mat_c[i] * (abs(load_cur - load_pre) + load_cur - load_pre) / 2

                obj_perf += beta * sum(sum(
                    mat_b[i] * (abs(instance.x[i + 1, j + 1].value - mat_pre[i][j])
                                + (instance.x[i + 1, j + 1].value - mat_pre[i][j])) / 2
                    for j in range(nj)) for i in range(ni))

            #print "Resource allocated: {}".format(
            #    sum(sum(instance.x[i + 1, j + 1].value for j in range(nj)) for i in range(ni)))
            #print "Resource needed: {}".format(sum(mat_lbd[j] for j in range(nj)))

            for i in range(ni):
                for j in range(nj):
                    mat_pre[i][j] = instance.x[i + 1, j + 1].value

        print "The greedy perf objective value is: {}".format(obj_perf)

    if solution == "operation" or solution == "all":

        obj_operation = 0
        mat_pre = [[0 for j in range(nj)] for i in range(ni)]

        for t in range(nt):

            #print "Starting iteration {}...".format(t + 1)

            input_operation = "./data/operation_{}.dat".format(t + 1)
            gen_input_greedy(input_operation, t + 1, ni, nj, nt, mat_a, mat_b, mat_c, mat_d,
                             mat_loc, mat_lbd, mat_cap, mat_pre, alpha, beta)
            instance = run_greedy_operation(input_operation)

            obj_operation += alpha * sum(sum(
                mat_a[i][t] * instance.x[i + 1, j + 1].value
                for j in range(nj)) for i in range(ni))
            obj_operation += alpha * sum(sum(
                mat_d[i][mat_loc[j][t]] * instance.x[i + 1, j + 1].value
                for j in range(nj)) for i in range(ni))

            if t != 0:
                for i in range(ni):
                    load_cur = sum(instance.x[i + 1, j + 1].value for j in range(nj))
                    load_pre = sum(mat_pre[i][j] for j in range(nj))
                    obj_operation += beta * mat_c[i] * (abs(load_cur - load_pre) + load_cur - load_pre) / 2

                obj_operation += beta * sum(sum(
                    mat_b[i] * (abs(instance.x[i + 1, j + 1].value - mat_pre[i][j])
                                + (instance.x[i + 1, j + 1].value - mat_pre[i][j])) / 2
                    for j in range(nj)) for i in range(ni))

            #print "Resource allocated: {}".format(
            #    sum(sum(instance.x[i + 1, j + 1].value for j in range(nj)) for i in range(ni)))
            #print "Resource needed: {}".format(sum(mat_lbd[j] for j in range(nj)))

            for i in range(ni):
                for j in range(nj):
                    mat_pre[i][j] = instance.x[i + 1, j + 1].value

        print "The greedy operation objective value is: {}".format(obj_operation)


    if solution == "static" or solution == "all":

        obj_static = 0
        mat_pre = [[0 for j in range(nj)] for i in range(ni)]

        for t in range(nt):

            #print "Starting iteration {}...".format(t + 1)

            input_static = "./data/static_{}.dat".format(t + 1)
            gen_input_greedy(input_static, t + 1, ni, nj, nt, mat_a, mat_b, mat_c, mat_d,
                             mat_loc, mat_lbd, mat_cap, mat_pre, alpha, beta)
            instance = run_greedy_static(input_static)

            obj_static += alpha * sum(sum(
                mat_a[i][t] * instance.x[i + 1, j + 1].value
                for j in range(nj)) for i in range(ni))
            obj_static += alpha * sum(sum(
                mat_d[i][mat_loc[j][t]] * instance.x[i + 1, j + 1].value
                for j in range(nj)) for i in range(ni))

            if t != 0:
                for i in range(ni):
                    load_cur = sum(instance.x[i + 1, j + 1].value for j in range(nj))
                    load_pre = sum(mat_pre[i][j] for j in range(nj))
                    obj_static += beta * mat_c[i] * (abs(load_cur - load_pre) + load_cur - load_pre) / 2

                obj_static += beta * sum(sum(
                    mat_b[i] * (abs(instance.x[i + 1, j + 1].value - mat_pre[i][j])
                                + (instance.x[i + 1, j + 1].value - mat_pre[i][j])) / 2
                    for j in range(nj)) for i in range(ni))

            #print "Resource allocated: {}".format(
            #    sum(sum(instance.x[i + 1, j + 1].value for j in range(nj)) for i in range(ni)))
            #print "Resource needed: {}".format(sum(mat_lbd[j] for j in range(nj)))

            for i in range(ni):
                for j in range(nj):
                    mat_pre[i][j] = instance.x[i + 1, j + 1].value

        print "The greedy static objective value is: {}".format(obj_static)




if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="ICDCS-2017-Exp")
    parser.add_argument('-d', "--distance", help='distrance matrix file',
                        default="../station/roma_metro_dist.dat")
    parser.add_argument('-l', "--location", help='location matrix file',
                        default="../trajectory/roma_taxi_2014021215_loc.dat")
    parser.add_argument('-g', "--generate", help='generate new data: 0:no 1:powerlaw 2:normal 3:uniform', default=0)
    parser.add_argument('-s', "--solution", help='choose solution', default="")
    parser.add_argument('-a', "--alpha", type=float, help='alpha', default=1.0)
    parser.add_argument('-b', "--beta", type=float, help='beta', default=1.0)
    parser.add_argument('-e', "--epsilon", type=float, help='epsilon', default=0.1)

    args = parser.parse_args()


    main(args.distance, args.location, args.generate, args.solution,
         args.alpha, args.beta, args.epsilon, args.epsilon)
