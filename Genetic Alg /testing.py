import implement2
import pickle, random

with open("locations.p", "rb") as pickle_file:
    locations = pickle.load(pickle_file)
with open("parsed_graph.p", "rb") as pf:
    graph = pickle.load(pf)


def Test_locations(trial_num):
    # This function isn't really used in the final generation of the graph, but
    # is still useful
    def generate_locations():
        # This function generates randomly from the graph, a set of potential locations
        generated_destinations = {}
        l = len(locations)
        for k in [3, 5, 7, 10, 12, 14]:
            # different lengths of lists are genrated
            if k not in generated_destinations:
                generated_destinations[k] = []
            for repeats in range(trial_num):
                # for each length, we generate several lists for different trials
                destination = [
                    locations[j] for j in [random.randint(0, l - 1) for i in range(k)]
                ]
                generated_destinations[k].append(destination)
        assert len(generated_destinations[5]) == trial_num
        # returns a dictionary of length_of_list: generated list of potential locations
        return generated_destinations

    def test():
        overall_result = {}
        generated_destinations = generate_locations()
        for location_number in generated_destinations.keys():
            # for each number of potential destinations, retrieve the generated lists to test on
            des_to_test = generated_destinations[location_number]
            # also randomly generate the priority
            priority = [random.randint(1, 10) for j in range(location_number)]
            total_pathlen = 0
            total_reward = 0
            total_best_time = 0
            total_num_reward = 0
            print(des_to_test)
            # For each trial, we tests 5 metrics of the generated path as listed above
            for destinations in des_to_test:
                result = implement2.get_result(graph, destinations, priority, 5000)
                [path, reward, besttime, visited] = result
                total_pathlen += path
                total_reward += reward
                total_best_time += besttime
                total_num_reward += visited
                # in each trial, accumulate each metric we are measuring
                # In the end we are taking an average
            result = [
                t / trial_num
                for t in [
                    total_pathlen,
                    total_reward,
                    total_best_time,
                    total_num_reward,
                ]
            ]
            overall_result[location_number] = result
            # Take the avaerage and store the result to the dictionary.
        return overall_result

    return test()


def Test_timeLim(trial_num, num_location):
    def generate_locations2():
        # given a trial number, and the number of destinations, generate trial number of destination lists
        output = []
        l = len(locations)
        for i in range(trial_num):
            output.append(
                [
                    locations[j]
                    for j in [random.randint(0, l - 1) for i in range(num_location)]
                ]
            )
        return output

    def test2():
        overall_result = {}
        des_to_test = generate_locations2()
        # for each of the time limit above, generate randomly
        # the lists of time and priority for each destination
        priority = [random.randint(1, 10) for j in range(num_location)]
        for time_limit in [3800, 4000, 4500, 5000, 5500, 6000, 6500]:
            # For each trial, we tests 5 metrics of the generated path as listed above
            total_pathlen = 0
            total_reward = 0
            total_best_time = 0
            total_num_reward = 0
            print(des_to_test)
            for destinations in des_to_test:
                result = implement2.get_result(
                    graph, destinations, priority, time_limit
                )
                [path, reward, besttime, visited] = result
                total_pathlen += path
                total_reward += reward
                total_best_time += besttime
                total_num_reward += visited
            # in each trial, accumulate each metric we are measuring
            # In the end we are taking an average
            result = [
                t / trial_num
                for t in [
                    total_pathlen,
                    total_reward,
                    total_best_time,
                    total_num_reward,
                ]
            ]
            overall_result[time_limit] = result
            # Take the avaerage and store the result to the dictionary.
        return overall_result  # return the distionary

    return test2()


def Time_Location(trial_num):
    """testing the performance of algorithm wth respect to time, while
    changing the number of potential locations to be visited in the algorithm"""
    result = {}  # nested dictionary
    for i in [3, 5, 7, 10, 12, 14]:
        # for each length of destination list
        # obtain the result dictionary of averaged result
        print(f"location {i}")
        x = Test_timeLim(trial_num, i)
        # store the result to the result dictionary
        result[i] = x
    # result is a nested dictionary of detsination length: result for the length containing 5 metrics
    return result


test1 = Time_Location(5)
# This line of the code generates a file containing the result
# We call on this file later to create graphs
pickle.dump(test1, open("time_vs_loc.p", "wb"))
