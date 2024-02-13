import math, random
import pickle

# This file gets the layout of the floor from a txt file,
# in this case, nodes_map.txt, and converts it to a dictionary

with open("nodes_map.txt", "r") as f:
    # In this function we find all the locations along with their coordinates.
    locations = []
    coordinates = []
    look_up = {}
    for line in f:
        s = line
        name_indx = []
        location_indx = []
        for i in range(len(line)):
            tmp_name = []
            if line[i] == '"':
                name_indx.append(i)
            if line[i] == ",":
                location_indx.append(i)
            if line[i] == ")":
                location_indx.append(i)
            if line[i] == ";":
                break
        a = (name_indx[0] + 1, name_indx[1] - 1)
        b = (location_indx[0] + 1, location_indx[1] - 1)
        c = (location_indx[1] + 1, location_indx[2] - 1)
        loc = line[a[0] : (a[1] + 1)]
        locations.append(loc)
        coordinate = (int(line[b[0] : b[1] + 1]), int(line[c[0] : c[1] + 1]))
        coordinates.append(coordinate)
        look_up[coordinate] = loc


def pythagorean_dist(p1: tuple, p2: tuple):
    # This function calculates the pythagorean distance
    (a, b) = p1
    (c, d) = p2
    return math.sqrt(((c - a) ** 2) + ((d - b) ** 2))


graph = {}
look = {}
locations = []
# base cases
with open("edges.txt", "r") as f2:
    # This function gets the edges of the graph, and constructs the graph in the form of an adjancency list.
    for line2 in f2:
        coordinate_indx = []
        for c in range(len(line2)):
            if line2[c] == "(":
                coordinate_indx.append(c)
            if line2[c] == ",":
                coordinate_indx.append(c)
            if line2[c] == ")":
                coordinate_indx.append(c)
        a = (coordinate_indx[0] + 1, coordinate_indx[1] - 1)
        b = (coordinate_indx[1] + 1, coordinate_indx[2] - 1)
        c = (coordinate_indx[2] + 1, coordinate_indx[3] - 1)
        d = (coordinate_indx[3] + 1, coordinate_indx[4] - 1)
        coor1 = (int(line2[a[0] : a[1] - 1]), int(line2[b[0] : b[1] - 1]))
        coor2 = (int(line2[c[0] : c[1] - 1]), int(line2[d[0] : d[1] - 1]))
        if (coor1 not in look_up) or (coor2 not in look_up):
            print(f"Problem with edge between {coor1} and {coor2}")
        else:
            node1 = look_up[coor1]
            node2 = look_up[coor2]
            locations.append(node1)
            locations.append(node2)
            dist = round(pythagorean_dist(coor1, coor2), 3)
            look[node1] = coor1
            look[node2] = coor2
            if (node1, coor1) in graph:
                graph[(node1, coor1)].append((node2, coor2, dist))
            else:
                graph[(node1, coor1)] = [(node2, coor2, dist)]
            if (node2, coor2) in graph:
                graph[(node2, coor2)].append((node1, coor1, dist))
            else:
                graph[(node2, coor2)] = [(node1, coor1, dist)]

pickle.dump(graph, open("parsed_graph.p", "wb"))
pickle.dump(look, open("node_coor.p", "wb"))

# look is a lookup table containing the name of the location with its coordinate
# graph is a dictionary representing the graph, with info stored as (name, coor, distance (to parents))
l = len(locations)
destination = [locations[j] for j in [random.randint(0, l - 1) for i in range(12)]]
print(destination)
pickle.dump(destination, open("destinations.p", "wb"))
pickle.dump(locations, open("locations.p", "wb"))
