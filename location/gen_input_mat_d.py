from sys import *
from geopy.distance import vincenty

def read_stations(file_name):

    locations = []
    file_handle = open(file_name, 'r')
    lines = file_handle.readlines()

    for line in lines:
        eles = line.rstrip().split('\t')
        locations.append((eles[1], eles[2]))

    return locations


def calculate_distance(locations, ni):

    mat_dist = [[0 for ia in range(ni)] for ib in range(ni)]
    for ia in range(ni):
        for ib in range(ni):
            mat_dist[ia][ib] = vincenty(locations[ia], locations[ib]).kilometers


    return mat_dist


def write_dist(file_name, mat_dist, ni):
    file_handle = open(file_name, 'w')
    for ia in range(ni):
        for ib in range(ni):
            file_handle.write(str(mat_dist[ia][ib]) + ' ')
        file_handle.write('\n')

    file_handle.close()

def main():

    sta_file = "./roma_metro_sta_sel.dat"
    locations = read_stations(sta_file)
    mat_dist = calculate_distance(locations, 13)
    write_dist("./roma_metro_dist.dat", mat_dist, 13)



if __name__ == "__main__":
    main()