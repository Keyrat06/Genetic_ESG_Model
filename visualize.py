import matplotlib.pyplot as plt
import pandas as pd
import sys
import numpy as np
import pickle
import main

NUM_PLAYERS = 7

a = pd.read_excel("Demand_Data.xls")
b = pd.read_excel("Company_Data.xls", range(NUM_PLAYERS))
types = ["Bay View", "Big Coal", "Fossil Light", "Beachfront", "Old Timers", "Big Gas", "East Bay"]
demands = a.demand
colors = ['dimgray', 'c', 'g', 'y', 'r', 'b', 'm']


def get_all_data():
    data = [] ## [(var_cost, capacity, plant_name, portfolioname), (var_cost, capacity, plant_name, portfolioname), ...]
    for i in range(NUM_PLAYERS):
        name = str(types[i])
        for j, part in enumerate(b[i].Parts):
            capacity = float(b[i].Capacity[j])
            var_cost = float(b[i].Total_Var_Cost[j])
            data.append((var_cost, capacity, str(part), types.index(name)))
    return sorted(data)

world = get_all_data()

def visualize(data, show=True, period=0):
    cumulative = 0
    data = sorted(data)
    for datapoint in data:
        plt.plot((cumulative, cumulative+datapoint[1]), (datapoint[0], datapoint[0]), color=colors[datapoint[3]])
        plt.text(cumulative, datapoint[0] + 1, datapoint[2], fontsize=5)
        cumulative += datapoint[1]
    for i, type in enumerate(types):
        plt.plot([], label=type, color=colors[i])


    plt.vlines(demands[period], 0, 100)
    plt.text(demands[period]-5, 5, "week {} hour {}".format(int(period)//4 + 1, period%4 + 1), fontsize=5)
    plt.legend()

    if show:
        plt.show()


if __name__ == "__main__":
    data = main.get_flat_worlds()
    for i, world in enumerate(data):
        visualize(world, True, i)
        print i
        for bid in world:
            if bid[-1] == 6:
                print bid

    # if len(sys.argv) == 1:
    #     visualize(world, True, 0)
    # elif len(sys.argv) == 2:
    #     period = int(sys.argv[1])
    #     visualize(world, True, period)
    # else:
    #     world = pickle.load(open(sys.argv[1]))
    #     period = int(sys.argv[2])
    #     visualize(world, True, period)
    #
    # for bid in world:
    #     if bid[-1] == 6:
    #         print bid



