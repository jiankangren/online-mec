import sys
import argparse
from pyomo.opt import SolverFactory

from model import *
from util import *


def run_opt(input_opt):

    print "Creating instance..."
    abs_model = create_abs_opt()
    instance = abs_model.create_instance(input_opt)
    opt = SolverFactory("ipopt")

    print "Solving..."
    results = opt.solve(instance, tee=True, options={'tol': 0.01})
    instance.solutions.store_to(results)
    return instance.OBJ()


def run_approx(input_approx):

    print "Creating instance..."
    abs_model = create_abs_approx()
    instance = abs_model.create_instance(input_approx)
    opt = SolverFactory("ipopt")

    print "Solving..."
    results = opt.solve(instance)
    instance.solutions.store_to(results)
    return instance


def run_greedy(input_greedy):

    print "Creating instance..."
    abs_model = create_abs_greedy()
    instance = abs_model.create_instance(input_greedy)
    opt = SolverFactory("ipopt")

    print "Solving..."
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

    else:
        mat_a = read_mat_a("./data/a.dat")
        mat_b = read_mat_b("./data/b.dat")
        mat_c = read_mat_b("./data/c.dat")

        mat_lbd = read_mat_lbd("./data/lbd.dat")
        mat_cap = read_mat_cap("./data/cap.dat")

    if solution == "opt":
        input_opt = "./data/opt.dat"
        gen_input_opt(input_opt, ni, nj, nt, mat_a, mat_b, mat_c, mat_d, mat_loc, mat_lbd, mat_cap, alpha, beta)
        obj_opt = run_opt(input_opt)
        print "The optimal objective value is: {}".format(obj_opt)

    elif solution == "approx":

        obj_approx = 0
        mat_pre = [[0 for j in range(nj)] for i in range(ni)]

        for t in range(nt):

            print "Starting iteration {}...".format(t + 1)

            input_approx = "./data/approx_{}.dat".format(t + 1)
            gen_input_approx(input_approx, t + 1, ni, nj, nt, mat_a, mat_b, mat_c, mat_d,
                         mat_loc, mat_lbd, mat_cap, mat_pre, alpha, beta, eps1, eps2)
            instance = run_approx(input_approx)

            obj_approx += alpha * sum(sum(mat_a[i][t] * instance.x[i + 1, j + 1].value for j in range(nj)) for i in range(ni))
            obj_approx += alpha * sum(sum(mat_d[i][mat_loc[j][t]] for j in range(nj)) for i in range(ni))

            if t != 0:
                for i in range(ni):
                    load_cur = sum(instance.x[i + 1, j + 1].value for j in range(nj))
                    load_pre = sum(mat_pre[i][j] for j in range(nj))
                    obj_approx += beta * mat_c[i] * (abs(load_cur - load_pre) + load_cur - load_pre) / 2

                obj_approx += beta * sum(sum(
                            mat_b[i] * (abs(instance.x[i + 1, j + 1].value - mat_pre[i][j])
                                        + (instance.x[i + 1, j + 1].value - mat_pre[i][j]))/2
                        for j in range(nj)) for i in range(ni))

            for i in range(ni):
                for j in range(nj):
                    mat_pre[i][j] = instance.x[i + 1, j + 1].value
            print instance.OBJ()
            print "The approximited objective value is: {}".format(obj_approx)


    elif solution == "greedy":

        obj_greedy = 0
        mat_pre = [[0 for j in range(nj)] for i in range(ni)]

        for t in range(nt):

            print "Starting iteration {}...".format(t + 1)

            input_greedy = "./data/greedy_{}.dat".format(t + 1)
            gen_input_greedy(input_greedy, t + 1, ni, nj, nt, mat_a, mat_b, mat_c, mat_d,
                         mat_loc, mat_lbd, mat_cap, mat_pre, alpha, beta)
            instance = run_greedy(input_greedy)
            obj_greedy += instance.OBJ()

            for i in range(ni):
                for j in range(nj):
                    mat_pre[i][j] = instance.x[i + 1, j + 1].value

            print "The greedy objective value is: {}".format(obj_greedy)

    else:
        print "No solution applied."



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="ICDCS-2017-Exp")
    parser.add_argument('-d', "--distance", help='distrance matrix file',
                        default="../station/roma_metro_dist.dat")
    parser.add_argument('-l', "--location", help='location matrix file',
                        default="../trajectory/roma_taxi_2014021115_loc.dat")
    parser.add_argument('-g', "--generate", help='generate new data: 0:no 1:powerlaw 2:normal 3:uniform', default=0)
    parser.add_argument('-s', "--solution", help='choose solution', default="")
    parser.add_argument('-a', "--alpha", type=float, help='alpha', default=1.0)
    parser.add_argument('-b', "--beta", type=float, help='beta', default=1.0)
    parser.add_argument('-e', "--epsilon", type=float, help='epsilon', default=0.1)

    args = parser.parse_args()


    main(args.distance, args.location, args.generate, args.solution,
         args.alpha, args.beta, args.epsilon, args.epsilon)
