import math, random, copy
import pickle, itertools
from tkinter import *

# Get the graph, coordinates and edges dictionaries as setup
with open("parsed_graph.p", "rb") as pf:
    graph = pickle.load(pf)
with open("node_coor.p", "rb") as pf2:
    look_up = pickle.load(pf2)
with open("locations.p", "rb") as pf3:
    locations = pickle.load(pf3)

# Generate possible destination list
possible_dest = [
    locations[i] for i in [random.randint(0, len(locations) - 1) for j in range(15)]
]
# Generate priority for each destination
weights = [random.randint(0, 10) for i in range(15)]
# Set a limit for the time
limit_time = 5000


def BFS_search(graph, start, end):
    # BFS algorithm that finds a path between the start and end
    # returns the resuling path and the distance of the path
    explored = set()
    to_explore = [(start, [start[0]], 0)]
    while to_explore != []:
        (new_node, prev, dist) = to_explore.pop(0)
        if new_node[0] == end[0]:
            return (prev, dist)
        explored.add(new_node[0])
        for node in graph[new_node]:
            if node[0] not in explored:
                to_explore.append(
                    ((node[0], node[1]), prev + [(node[0])], dist + node[2])
                )
    return None


def run_algo(possible_dest, graph, weights, pool, time_limit):
    def get_path(binary_list):
        # convert a list of 0s 1s to a path with name
        r = []
        reward = 0
        for l in range(len(binary_list)):
            if binary_list[l] == 1:
                reward += weights[l]
                r.append(possible_dest[l])
        return (["X41"] + r + ["S44"], reward)

    def get_BFS_result(location_list, reward):
        # BFS function that returns the distance of a path and the reward it collected
        total_dist = 0
        for i in range(len(location_list) - 1):
            (path, dist) = BFS_search(
                graph,
                (location_list[i], look_up[location_list[i]]),
                (location_list[i + 1], look_up[location_list[i + 1]]),
            )
            total_dist += dist
        return (total_dist, reward)

    def select(pool):
        # Select a random bit-vector from the pool
        x = -1
        x = random.randint(0, len(pool) - 1)
        return pool[x]

    def calculate_value(list1_stat):
        # Calculates the value of path
        (list1, rew1) = list1_stat
        (dist1, reward1) = get_BFS_result(list1, rew1)
        if dist1 > time_limit:
            return -1
        if dist1 == 0:
            return -1
        # The value function used is reward/(distance * 0.01)
        # Could replace with other functions
        return reward1 / (dist1 / 100)

    def crossover(l1, l2):
        # Takes in two bit vectors and selects a random pivot
        # slices each bit vector at the pivot
        # merge two seperate halves
        common_len = min(len(l1), len(l2))
        split_indx = random.randint(0, common_len - 1)
        first_half = l1[:split_indx]
        second_half = l2[split_indx:]
        final = first_half + second_half
        while random.random() < 0.4:
            i = random.randint(0, common_len - 1)
            final[i] = 0 if final[i] == 1 else 1
        return final

    def round(pool):
        # Sort the pool by it's calcualted value
        new_pool = []
        for i in range(len(pool)):
            new_pool.append((pool[i], calculate_value(get_path(pool[i]))))
        new_pool = sorted(new_pool, key=lambda x: x[1])
        # Get rid of the lower half
        new_pool = new_pool[0 : (int(len(pool) / 2))]
        updated_pool = [r for (r, k) in new_pool]
        # For the bit vectors that have value in the top 50%, randomly cross over
        while len(updated_pool) < 100:
            l1 = select(updated_pool)
            l2 = select(updated_pool)
            updated_pool.append(crossover(l1, l2))
        # Pool has size back at 100, returns this new pool
        return updated_pool
        # This is one round of the algorithm

    def run(pool):
        # Set a number of rounds this algorithm should run
        rounds = 20
        new_pool = pool
        # Run the algorithm for that many rounds
        while rounds > 0:
            new_pool = round(new_pool)
            rounds -= 1
        # Calculate the value for each bit vector in the final pool
        for i in range(len(new_pool)):
            new_pool[i] = (new_pool[i], calculate_value(get_path(new_pool[i])))
        result = sorted(new_pool, key=lambda x: x[1])
        # Get bit vector with highest value
        (final_list, value) = result[len(new_pool) - 1]
        # Get the path from the bit vector
        return (get_path(final_list), value)

    return run(pool)


def get_result(graph, possible_dest, weights, limit_time):
    # Generate the initial pool of 100 bit vectors randomly
    def generate_pool(possible_dest):
        result_pool = []
        for i in range(100):
            child = []
            for j in range(len(possible_dest)):
                coin = random.random()
                if coin < 0.5:
                    child.append(0)
                else:
                    child.append(1)
            result_pool.append(child)
        return result_pool

    pool = generate_pool(possible_dest)

    ((result, reward), value) = run_algo(
        possible_dest, graph, weights, pool, limit_time
    )

    def full_path(graph, l):
        # After getting the result, construct the full path using BFS
        path = []
        for i in range(len(l) - 1):
            segment = BFS_search(
                graph, (l[i], look_up[l[i]]), (l[i + 1], look_up[l[i + 1]])
            )
            path += segment[0]
        return path

    result_path = full_path(graph, result)
    distance = (1 / (value / reward)) * 100

    # Return the result as 5 seperate metrics.
    return (len(result_path), reward, distance, len(result))


get_result(graph, possible_dest, weights, limit_time)
