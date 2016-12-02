import sys
import random
import numpy as np


def gen_mat_a(ni, nt):

    file_handle = open("./data/a.dat", 'w')
    bases = [random.uniform(1, 5) for i in range(ni)]
    mat_a = []
    for i in range(ni):
        mat_a.append([abs(random.gauss(bases[i], 1)) for t in range(nt)])
        for val in mat_a[i]:
            file_handle.write("{} ".format(val))
        if i != ni - 1:
            file_handle.write("\n")
    file_handle.close()
    return mat_a


def gen_mat_b(ni):

    file_handle = open("./data/b.dat", 'w')
    mat_b = [0 for i in range(ni)]
    group = [i for i in range(ni)]
    random.shuffle(group)
    for i in range(ni):
        if i % 3 == 0:
            mat_b[group[i]] = 0.5
        if i % 3 == 1:
            mat_b[group[i]] = 1
        if i % 3 == 2:
            mat_b[group[i]] = 2

    for i in range(ni):
        if i != ni - 1:
            file_handle.write("{}\n".format(mat_b[i]))
        else:
            file_handle.write("{}".format(mat_b[i]))
    file_handle.close()
    return mat_b


def gen_mat_c(ni):

    file_handle = open("./data/c.dat", 'w')
    mat_c = [abs(random.normalvariate(2, 2)) for i in range(ni)]
    for i in range(ni):
        if i != ni - 1:
            file_handle.write("{}\n".format(mat_c[i]))
        else:
            file_handle.write("{}".format(mat_c[i]))
    file_handle.close()
    return mat_c


def gen_mat_lbd(nj, is_gen):

    mat_lbd = []
    if is_gen == 1:
        mat_lbd = np.random.power(1, nj) * 10
    elif is_gen == 2:
        mat_lbd = [abs(random.normalvariate(10, 3)) for j in range(nj)]
    else:
        mat_lbd = [random.uniform(5, 15) for j in range(nj)]

    file_handle = open("./data/lbd.dat", 'w')
    for j in range(nj):
        if j != nj - 1:
            file_handle.write("{}\n".format(mat_lbd[j]))
        else:
            file_handle.write("{}".format(mat_lbd[j]))
    file_handle.close()
    return mat_lbd


def gen_mat_cap(ni, mat_lbd, mat_loc):

    total_cap = sum(mat_lbd) * 1.25

    mat_cap = [0 for i in range(ni)]

    count = [0 for i in range(ni)]
    for list_loc in mat_loc:
        for i in range(ni):
            count[i] += list_loc.count(i)

    for i in range(ni):
        mat_cap[i] = total_cap * count[i] / sum(count)

    file_handle = open("./data/cap.dat", 'w')
    for i in range(ni):
        if i != ni - 1:
            file_handle.write("{}\n".format(mat_cap[i]))
        else:
            file_handle.write("{}".format(mat_cap[i]))
    file_handle.close()

    return mat_cap


def read_mat_a(file_name):

    mat_a = []
    file_handle = open(file_name, 'r')
    lines = file_handle.readlines()

    for line in lines:
        ai = map(float, line.split())
        mat_a.append(ai)

    return mat_a


def read_mat_b(file_name):

    mat_b = []
    file_handle = open(file_name, 'r')
    lines = file_handle.readlines()

    for line in lines:
        mat_b.append(line.rstrip())

    return map(float, mat_b)


def read_mat_c(file_name):

    mat_c = []
    file_handle = open(file_name, 'r')
    lines = file_handle.readlines()

    for line in lines:
        mat_c.append(line.rstrip())

    return map(float, mat_c)


def read_mat_d(file_name):

    mat_d = []
    file_handle = open(file_name, 'r')
    lines = file_handle.readlines()

    for line in lines:
        di = map(float, line.split())
        mat_d.append(di)

    return mat_d


def read_mat_lbd(file_name):

    mat_lbd = []
    file_handle = open(file_name, 'r')
    lines = file_handle.readlines()

    for line in lines:
        mat_lbd.append(line.rstrip())

    return map(float, mat_lbd)


def read_mat_cap(file_name):

    mat_cap = []
    file_handle = open(file_name, 'r')
    lines = file_handle.readlines()

    for line in lines:
        mat_cap.append(line.rstrip())

    return map(float, mat_cap)


def read_mat_loc(file_name):

    mat_loc = []
    file_handle = open(file_name, 'r')
    lines = file_handle.readlines()

    for line in lines:
        loc_user = map(int, line.rstrip().split())
        mat_loc.append(loc_user)

    return mat_loc


def gen_input_opt(file_name, ni, nj, nt, mat_a, mat_b, mat_c, mat_d, mat_loc, mat_lbd, mat_cap, alpha, beta):

    file_handle = open(file_name, 'w')
    file_handle.write("param t := {} ;\n".format(nt))
    file_handle.write("param i := {} ;\n".format(ni))
    file_handle.write("param j := {} ;\n".format(nj))

    file_handle.write("param alpha := {} ;\n".format(alpha))
    file_handle.write("param beta := {} ;\n".format(beta))

    file_handle.write("param a := \n")
    for i in range(ni):
        for t in range(nt):
            file_handle.write("{} {} {}\n".format(i + 1, t + 1, mat_a[i][t]))
    file_handle.write(";\n")

    file_handle.write("param c := \n")
    for i in range(ni):
        file_handle.write("{} {}\n".format(i + 1, mat_c[i]))
    file_handle.write(";\n")

    file_handle.write("param b := \n")
    for i in range(ni):
        file_handle.write("{} {}\n".format(i + 1, mat_b[i]))
    file_handle.write(";\n")

    file_handle.write("param d := \n")
    for j in range(nj):
        for i in range(ni):
            file_handle.write("[{},{},*] ".format(i + 1, j + 1))
            for t in range(nt):
                file_handle.write("{} {} ".format(t + 1, mat_d[mat_loc[j][t]][i]))
            file_handle.write("\n")
    file_handle.write(";\n")

    file_handle.write("param lbd := \n")
    for j in range(nj):
        file_handle.write("{} {}\n".format(j + 1, mat_lbd[j]))
    file_handle.write(";\n")

    file_handle.write("param cap := \n")
    for i in range(ni):
        file_handle.write("{} {}\n".format(i + 1, mat_cap[i]))
    file_handle.write(";\n")

    file_handle.close()


def gen_input_approx(file_name, time, ni, nj, nt, mat_a, mat_b, mat_c, mat_d,
                     mat_loc, mat_lbd, mat_cap, mat_pre, alpha, beta, eps1, eps2):

    file_handle = open(file_name, 'w')
    file_handle.write("param i := {} ;\n".format(ni))
    file_handle.write("param j := {} ;\n".format(nj))

    file_handle.write("param alpha := {} ;\n".format(alpha))
    file_handle.write("param beta := {} ;\n".format(beta))

    file_handle.write("param eps1 := {} ;\n".format(eps1))
    file_handle.write("param eps2 := {} ;\n".format(eps2))

    file_handle.write("param a :=\n")
    for i in range(ni):
        file_handle.write("{} {}\n".format(i + 1, mat_a[i][time - 1]))
    file_handle.write(";\n")

    file_handle.write("param c := \n")
    for i in range(ni):
        if time == 1:
            file_handle.write("{} {}\n".format(i + 1, 0))
        else:
            file_handle.write("{} {}\n".format(i + 1, mat_c[i]))
    file_handle.write(";\n")

    file_handle.write("param b := \n")
    for i in range(ni):
        if time == 1:
            file_handle.write("{} {}\n".format(i + 1, 0))
        else:
            file_handle.write("{} {}\n".format(i + 1, mat_b[i]))
    file_handle.write(";\n")

    file_handle.write("param lbd := \n")
    for j in range(nj):
        file_handle.write("{} {}\n".format(j + 1, mat_lbd[j]))
    file_handle.write(";\n")

    file_handle.write("param cap := \n")
    for i in range(ni):
        file_handle.write("{} {}\n".format(i + 1, mat_cap[i]))
    file_handle.write(";\n")

    file_handle.write("param d := \n")
    for j in range(nj):
        for i in range(ni):
            file_handle.write("{} {} {}\n".format(i + 1, j + 1, mat_d[mat_loc[j][time - 1]][i]))
    file_handle.write(";\n")

    file_handle.write("param pre := \n")
    for i in range(ni):
        for j in range(nj):
            if time == 1:
                file_handle.write("{} {} 0\n".format(i + 1, j + 1))
            else:
                file_handle.write("{} {} {}\n".format(i + 1, j + 1, mat_pre[i][j]))
    file_handle.write(";\n")

    file_handle.close()


def gen_input_greedy(file_name, time, ni, nj, nt, mat_a, mat_b, mat_c, mat_d,
                     mat_loc, mat_lbd, mat_cap, mat_pre, alpha, beta):

    file_handle = open(file_name, 'w')
    file_handle.write("param i := {} ;\n".format(ni))
    file_handle.write("param j := {} ;\n".format(nj))

    file_handle.write("param alpha := {} ;\n".format(alpha))
    file_handle.write("param beta := {} ;\n".format(beta))

    file_handle.write("param a :=\n")
    for i in range(ni):
        file_handle.write("{} {}\n".format(i + 1, mat_a[i][time - 1]))
    file_handle.write(";\n")

    file_handle.write("param c := \n")
    for i in range(ni):
        if time == 1:
            file_handle.write("{} {}\n".format(i + 1, 0))
        else:
            file_handle.write("{} {}\n".format(i + 1, mat_c[i]))
    file_handle.write(";\n")

    file_handle.write("param b := \n")
    for i in range(ni):
        if time == 1:
            file_handle.write("{} {}\n".format(i + 1, 0))
        else:
            file_handle.write("{} {}\n".format(i + 1, mat_b[i]))
    file_handle.write(";\n")

    file_handle.write("param lbd := \n")
    for j in range(nj):
        file_handle.write("{} {}\n".format(j + 1, mat_lbd[j]))
    file_handle.write(";\n")

    file_handle.write("param cap := \n")
    for i in range(ni):
        file_handle.write("{} {}\n".format(i + 1, mat_cap[i]))
    file_handle.write(";\n")

    file_handle.write("param d := \n")
    for j in range(nj):
        for i in range(ni):
            file_handle.write("{} {} {}\n".format(i + 1, j + 1, mat_d[mat_loc[j][time - 1]][i]))
    file_handle.write(";\n")

    file_handle.write("param pre := \n")
    for i in range(ni):
        for j in range(nj):
            if time == 1:
                file_handle.write("{} {} 0\n".format(i + 1, j + 1))
            else:
                file_handle.write("{} {} {}\n".format(i + 1, j + 1, mat_pre[i][j]))
    file_handle.write(";\n")

    file_handle.close()