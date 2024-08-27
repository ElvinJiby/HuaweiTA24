
import numpy as np
import pandas as pd
from seeds import known_seeds
from utils import save_solution
from evaluation import get_actual_demand


def get_my_solution(actual_demand, datacenters, servers, selling_prices):
    solution = []

    for time_step in range(len(actual_demand)):
        # Analyze the demand at this time step
        current_demand = actual_demand.iloc[time_step]

        # Example decision: Buy servers if demand exceeds a certain threshold
        if current_demand['some_metric'] > threshold:
            action = {
                'time_step': time_step + 1,
                'action': 'buy',
                'server_generation': 'CPU.S1',
                'datacenter_id': 'DC1',
                'quantity': 10  # Adjust based on your logic
            }
            solution.append(action)

        # Example decision: Sell servers if they are underutilized
        if some_condition_for_selling:
            action = {
                'time_step': time_step + 1,
                'action': 'sell',
                'server_generation': 'CPU.S2',
                'datacenter_id': 'DC1',
                'quantity': 5
            }
            solution.append(action)

    return solution


seeds = known_seeds('training')

demand = pd.read_csv('./data/demand.csv')
for seed in seeds:
    # SET THE RANDOM SEED
    np.random.seed(seed)
    # print(seed)
    # GET THE DEMAND
    actual_demand = get_actual_demand(demand)
    print(len(actual_demand))
    print(actual_demand)
    a = actual_demand.iloc[0]
    # print(a)
    # break

    # CALL YOUR APPROACH HERE
    # solution = get_my_solution(actual_demand)
    # print(solution)
    break
    # SAVE YOUR SOLUTION
    #save_solution(solution, f'./output/{seed}.json')

