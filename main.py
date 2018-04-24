import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle


plt.ion()


NUM_WORLDS = 200
KEEP_PROP = 0.6
NUM_PLAYERS = 7
NUM_PERIODS = 12
GENERATIONS = 200

a = pd.read_excel("Demand_Data.xls")
b = pd.read_excel("Company_Data.xls", range(NUM_PLAYERS))
types = ["Bay View", "Big Coal", "Fossil Light", "Beachfront", "Old Timers", "Big Gas", "East Bay"]
demands = a.demand
colors = ['dimgray','c','g','y','r','b','m']


class GeneticPlayer:
    def __init__(self, capacity, var_cost, OM, num_periods=12, name="", names=[], r=0.25, s=0.5):
        self.name = name
        self.names = names
        self.num_periods = num_periods
        self.N = len(capacity)
        self.capacity = capacity
        self.MC = np.array(var_cost)
        self.OM = OM
        self.bids = (1+r*np.random.random((self.N, num_periods))) * (self.MC[:, np.newaxis]) \
                                  + np.random.normal(0, s, (self.N, self.num_periods))**2

    def get_bids(self, period):
        assert period < self.num_periods
        return self.bids[:, period]

def play_game(players):
    assert len(players) == NUM_PLAYERS
    total_profit = np.zeros(NUM_PLAYERS)
    for period in range(NUM_PERIODS):
        bids_quantities_MC_play_numbers = []
        for i, player in enumerate(players):
            for j, bid in enumerate(player.get_bids(period)):
                quantity = player.capacity[j]
                MC = player.MC[j]
                bids_quantities_MC_play_numbers.append((bid, quantity, MC, i))
        bids_quantities_MC_play_numbers.sort()
        total_quantity = 0
        i = 0
        demand_this_period = demands[period]
        while total_quantity < demand_this_period:
            total_quantity += bids_quantities_MC_play_numbers[i][1]
            i += 1
        price = bids_quantities_MC_play_numbers[i-1][0]
        total_demand_remaining = demand_this_period
        for j in range(i):
            bid, quantity, MC, player_number = bids_quantities_MC_play_numbers[j]
            assert total_demand_remaining >= 0
            assert bid <= price
            assert MC <= bid
            total_profit[player_number] += (price-MC) * min(total_demand_remaining, quantity)
            total_demand_remaining -= quantity

        if period % 4 == 0:
            for i, player in enumerate(players):
                total_profit[i] -= player.OM

    return total_profit


def mix_players(player_1, player_2):
    new_player = GeneticPlayer(player_1.capacity, player_1.MC, player_1.OM,
                               player_1.num_periods, player_1.name, player_1.names)
    for i in range(len(new_player.bids)):
        for j in range(len(new_player.bids[0])):
            new_player.bids[i, j] = np.random.choice((player_1, player_2)).bids[i, j]
            if np.random.random() < 0.05:
                new_player.bids[i, j] = player_1.MC[i]*(1+np.random.normal(0, 0.5)**2)
    return new_player


def get_pop_types():
    data = []
    for i in range(7):
        name = types[i]
        OM = sum(b[i].OM)
        capacity = tuple(b[i].Capacity)
        var_cost = tuple(b[i].Total_Var_Cost)
        names = tuple(b[i].Parts)
        data.append({"name": name, "OM": OM, "capacity": capacity, "var_cost": var_cost, "names": names})
    return data


pop_types = get_pop_types()


def make_world():
    players = []
    for pop_type in pop_types:
        players.append(GeneticPlayer(**pop_type))
    return players


def make_worlds(num_worlds):
    worlds = []
    for i in range(num_worlds):
        worlds.append(make_world())
    return worlds


def evaluate_worlds(worlds):
    scores = np.zeros((len(worlds), NUM_PLAYERS))
    for i, world in enumerate(worlds):
        scores[i, :] = play_game(world)
    return scores


def kill_weak(worlds, scores, keep_num=4):
    order = np.argsort(-1*scores/np.sum(scores, axis=1)[:, np.newaxis], axis=0) #np.argsort(-1*scores/np.sum(scores, axis=1)[:,np.newaxis], axis=0)
    new_worlds = np.empty((keep_num, NUM_PLAYERS), dtype=worlds.dtype)
    for i in range(keep_num):
        for j in range(NUM_PLAYERS):
            new_worlds[i, j] = worlds[order[i, j], j]
    # for world in new_worlds:
    #     for player in world:
    #         print player.name, "|",
    #     print
    # print new_worlds
    return new_worlds


def populate(worlds, N):
    new_worlds = list(worlds)
    while len(new_worlds) < N:
        if np.random.random() < 0.025:
            new_worlds.append(make_world())
        else:
            world = []
            for i in range(NUM_PLAYERS):
                player_1 = worlds[np.random.choice(range(len(worlds)))][i]
                player_2 = worlds[np.random.choice(range(len(worlds)))][i]
                world.append(mix_players(player_1, player_2))
            new_worlds.append(world)
    return new_worlds


def make_simple_world():
    players = []
    for pop_type in pop_types:
        players.append(GeneticPlayer(r=0, s=0, **pop_type))
    return players


simple_world = make_simple_world()
base_score = list(play_game(simple_world))
print base_score


def simulate():
    worlds = np.array(make_worlds(NUM_WORLDS))
    scores_graph = []
    for _ in range(GENERATIONS):
        worlds = np.array(populate(worlds, NUM_WORLDS))
        np.random.shuffle(worlds)
        scores = evaluate_worlds(worlds)
        scores_graph.append(np.mean(scores, axis=0))
        worlds = kill_weak(worlds, scores, int(KEEP_PROP*len(worlds)))
        plt.clf()
        for p in range(NUM_PLAYERS):
            plt.plot(np.array(scores_graph)[:, p], c=colors[p], linestyle='-')
            plt.hlines(base_score[p], 0, len(scores_graph)-1, color=colors[p], linestyle='--')
            plt.plot([], c=colors[p], label=types[p])
        plt.plot([], c='k', linestyle='-', label="Genetic")
        plt.plot([], c='k', linestyle='--', label="bid = MC")
        plt.title("Average Total Profit at Each Generation")
        plt.xlabel("Generation")
        plt.ylabel("Average Total Profit")
        plt.legend()
        plt.pause(0.001)
    print np.mean(scores, axis=0)
    plt.show()
    scores = evaluate_worlds(worlds)
    worlds = kill_weak(worlds, scores,1)
    return worlds[0]

def flatten_world(world, period=0):
    data = []
    for porfolio in world:
        name = porfolio.name
        for j, part in enumerate(porfolio.names):
            bid = porfolio.bids[j, period]
            capacity = porfolio.capacity[j]
            data.append((bid, capacity, part, types.index(name)))
    return data

def get_flat_worlds():
    world = simulate()
    data = []
    for period in range(NUM_PERIODS):
        data.append(flatten_world(world, period=period))
    return data

if __name__ == "__main__":
    world = simulate()
    flat_world = flatten_world(world)
    pickle.dump(flat_world, open("world.p", 'w'))

