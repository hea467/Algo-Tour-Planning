import copy
import pickle
import math
from tkinter import *


class Graph:
    def __init__(self, time, reward, destinations):
        self.start = "S44"
        self.end = "X41"
        self.time = time
        self.reward = reward
        with open("parsed_graph.p", "rb") as pickle_file:
            self.parsed_graph = pickle.load(pickle_file)
        with open("node_coor.p", "rb") as pickle_file:
            self.node_coor = pickle.load(pickle_file)

        speed = 100
        # the conversion between time for each task and distance travel time could be used if needed
        # or be set to 1 if not needed
        self.reward_nodes = {}
        for i in range(len(destinations)):
            self.reward_nodes[destinations[i]] = {
                "time": self.time[i] * speed,
                "reward": self.reward[i],
            }

        # Format the graph as a nested dictionary, of the form:
        # self.parsed_graph['start_node']['end_node']['edge_parameter'], where edge parameters are:
        # 'coordinate': coordiante of the end_node
        # 'time': time it takes to transition along the edge
        # 'reward': reward gained for transitioning along the edge
        updated_graph = {}
        for disgusting_key in self.parsed_graph:
            new_dict = {}
            for node_info in self.parsed_graph[disgusting_key]:
                new_dict[node_info[0]] = {
                    "coordinate": node_info[1],
                    "time": node_info[2],
                    "reward": 0,
                }
            updated_graph[disgusting_key[0]] = new_dict
        self.parsed_graph = updated_graph

        # The tour locations are represented as a 'self edge', both starting and ending at the location node.
        # Next, add these reward edges to the graph.
        for reward_node in self.reward_nodes:
            coordinate = self.node_coor[reward_node]  # coordinate of the reward node
            time = self.reward_nodes[reward_node]["time"]  # time taken at the location
            reward = self.reward_nodes[reward_node]["reward"]  # reward gained
            self.parsed_graph[reward_node][reward_node] = {
                "coordinate": coordinate,
                "time": time,
                "reward": reward,
            }

        # Create an 'end' node, connected to the last location of the tour. This gives the agent the ability to pass
        # through the last node without having to end the tour.
        self.parsed_graph[self.end]["end"] = {
            "coordinate": self.node_coor[self.end],
            "time": 0,
            "reward": 0,
        }

    def get_neighboring_nodes(self, node):
        # Returns the keys for the neighboring nodes
        return self.parsed_graph[node].keys()

    def get_reward_time(self, curr_path, next_node):
        """
        Return the reward and time for passing along an edge of the graph
        [input] current path hoping to be modified by or not i guess huh what am i doing
        [input] next_note: edge ending node
        [output] reward, time: reward gained and time cost for traversing the edge
        """
        time = self.parsed_graph[curr_path.current_node][next_node]["time"]
        reward = self.parsed_graph[curr_path.current_node][next_node]["reward"]

        if curr_path.current_node == next_node:
            (curr_path.explored_reward).append(next_node)

        return reward, time


# Path class, used to represent each potential path through the graph.
class Path:
    def __init__(self):
        self.explored_reward = []  #
        start_node = "S44"
        self.path = [start_node]  # list of all visted nodes
        self.explored_nodes = [start_node]  # we don't have to search these nodes
        self.time = 0  # total time of path
        self.reward = 0  # total reward of path
        self.current_node = start_node  # last node of the path

    def step(self, next_node, reward, time):
        self.time += time
        self.reward += reward
        self.path.append(next_node)

        # after receiving a reward, we may want to 'double back' on the path, so
        # clear the explored_nodes list
        if reward > 0:
            self.explored_nodes = []
        self.explored_nodes.append(self.current_node)
        self.current_node = next_node


def generate_graph(time, reward, destinations):
    return Graph(time, reward, destinations)


def run_search(max_time, goal_reward_used, goal_reward, graph):
    end_node = "end"
    paths_to_explore = [Path()]  # intialize the que of paths to explore
    best_path = paths_to_explore[0]  # We'll update this as we find better paths.
    end_coordinate = graph.node_coor["X41"]

    def pythagorean_dist(p1, p2):
        (a, b) = p1
        (c, d) = p2
        return math.sqrt((c - a) ** 2 + (d - b) ** 2)

    i = 0  # counter for total steps
    while paths_to_explore != []:
        if i % 10000 == 0:
            print(i)
        i += 1
        current_path = paths_to_explore.pop()  # path to search along
        # get all neighbor nodes and loop through them. The list command is needed
        # because the dictionary can be altered durring the loop (only after they are visted).
        neighbors = list(graph.get_neighboring_nodes(current_path.current_node))
        for node in neighbors:
            if node in current_path.explored_nodes:
                # skip nodes that are in the explored list
                continue
            if node == current_path.current_node:
                if node in current_path.explored_reward:
                    continue
            # Branch the path, going forward one step.
            new_path = copy.deepcopy(current_path)
            reward, time = graph.get_reward_time(new_path, node)
            new_path.step(node, reward, time)
            if new_path.time > max_time:
                # skip thats that will go over max time
                continue
            if new_path.current_node != "end" and (
                pythagorean_dist(graph.node_coor[new_path.current_node], end_coordinate)
            ) >= (max_time - new_path.time):
                continue
            # Add the new path to the list of paths to explore, unless the path has reached the end node.
            if node != end_node:
                paths_to_explore.append(new_path)

            # if the node has reached the end node, check if the new path is better than the best path. If so, replace best path.
            elif (new_path.reward > best_path.reward) or (
                new_path.reward == best_path.reward and new_path.time < best_path.time
            ):
                best_path = copy.deepcopy(new_path)
            elif goal_reward_used and (new_path.reward > goal_reward):
                best_path = copy.deepcopy(new_path)
                break
    return [
        i,
        best_path.path,
        best_path.reward,
        best_path.time,
        best_path.explored_reward,
    ]


def draw_path(canvas, paths):
    # This draws out the path generated by the algorithm
    with open("destinations.p", "rb") as pickle_file:
        destinations = pickle.load(pickle_file)
    with open("node_coor.p", "rb") as pickle_file:
        look_up = pickle.load(pickle_file)
    path = []
    for p in paths:
        if p != "end":
            path.append(look_up[p])

    for i in range(len(path) - 1):
        (x1, y1) = path[i]
        (x2, y2) = path[i + 1]
        (x1, y1) = (x1 * 0.5, (y1 * 0.5) - 150)
        (x2, y2) = (x2 * 0.5, (y2 * 0.5) - 150)
        canvas.create_line(x1, y1, x2, y2, fill="red")

    for d in destinations:
        (x1, y1) = look_up[d]
        canvas.create_oval(
            x1 * 0.5 - 2, y1 * 0.5 - 153, x1 * 0.5 + 3, 0.5 * y1 - 147, fill="green"
        )


def draw_nodes(canvas):
    # This draws out the nodes in the graph
    with open("parsed_graph.p", "rb") as pickle_file:
        graph = pickle.load(pickle_file)
    for loc in graph.keys():
        for info in graph[loc]:
            (x1, y1) = loc[1]
            (x2, y2) = info[1]
            (x1, y1) = (x1 * 0.5, (y1 * 0.5) - 150)
            (x2, y2) = (x2 * 0.5, (y2 * 0.5) - 150)
            canvas.create_oval(x1 - 1, y1 - 1, x1 + 1, y1 + 1, fill="blue")
            canvas.create_line(x1, y1, x2, y2)


def run_graph(w, h, path):
    # main function to draw the graph
    root = Tk()
    canvas = Canvas(root, width=w, height=h)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    draw_nodes(canvas)
    draw_path(canvas, path)
    root.mainloop()


def run_process(time, reward, destinations, limit, with_reward):
    # This runs the algorithm
    graph = generate_graph(time, reward, destinations)
    x = run_search(limit, with_reward, 42, graph)
    print(x)
    return x


if __name__ == "__main__":
    # Time and reward given in this case.
    time = [5, 6, 1, 3, 7, 2, 3, 6, 10, 11, 4, 3]  # provided info, could be read in
    reward = [9, 7, 8, 4, 6, 5, 2, 1, 3, 8, 1, 2]
    with open("destinations.p", "rb") as pickle_file:
        destinations = pickle.load(pickle_file)
    result = run_process(time, reward, destinations, 7000, False)
    run_graph(1500, 1500, result[1])
