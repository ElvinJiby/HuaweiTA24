import pandas as pd
import numpy as np
import scipy as sp

from evaluation import get_actual_demand
from mysolution import get_my_solution
from seeds import known_seeds
from utils import load_problem_data, save_solution

seeds = known_seeds('training')
demand = pd.read_csv('./data/demand.csv')

for seed in seeds:
    # SET THE RANDOM SEED
    np.random.seed(seed)

    # LOAD DATA
    demand, datacenters, servers, selling_prices = load_problem_data()

    # GET THE DEMAND
    actual_demand = get_actual_demand(demand)
    # print(actual_demand.iloc[:2])

    # CALL YOUR APPROACH HERE
    solution = get_my_solution(actual_demand, datacenters, servers, selling_prices)
    print("Done")

    # break
    # SAVE YOUR SOLUTION
    save_solution(solution, f'./output/{seed}.json')
    break