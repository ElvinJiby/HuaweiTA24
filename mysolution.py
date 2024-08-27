
import numpy as np
import pandas as pd

from evaluation_example import datacenters
from seeds import known_seeds
from utils import save_solution
from evaluation import get_actual_demand


def get_my_solution(actual_demand):
    solution = []
    threshold = {
        "CPU.S1": [0, 0, 0],
        "CPU.S2": [0, 0, 0],
        "CPU.S3": [0, 0, 0],
        "GPU.S1": [0, 0, 0],
        "GPU.S2": [0, 0, 0],
        "GPU.S3": [0, 0, 0],
    }
    datacenters_info = {
        "DC1" : {
            "CPU.S1": [0, 0, 0],
            "CPU.S2": [0, 0, 0],
            "CPU.S3": [0, 0, 0],
            "GPU.S1": [0, 0, 0],
            "GPU.S2": [0, 0, 0],
            "GPU.S3": [0, 0, 0]
        },
        "DC2": {
            "CPU.S1": [0, 0, 0],
            "CPU.S2": [0, 0, 0],
            "CPU.S3": [0, 0, 0],
            "GPU.S1": [0, 0, 0],
            "GPU.S2": [0, 0, 0],
            "GPU.S3": [0, 0, 0]
        },
        "DC3": {
            "CPU.S1": [0, 0, 0],
            "CPU.S2": [0, 0, 0],
            "CPU.S3": [0, 0, 0],
            "GPU.S1": [0, 0, 0],
            "GPU.S2": [0, 0, 0],
            "GPU.S3": [0, 0, 0]
        },
        "DC4": {
            "CPU.S1": [0, 0, 0],
            "CPU.S2": [0, 0, 0],
            "CPU.S3": [0, 0, 0],
            "GPU.S1": [0, 0, 0],
            "GPU.S2": [0, 0, 0],
            "GPU.S3": [0, 0, 0]
        }
    }
    datacenters_info.get("DC1").get("CPU.S1")[0] = 1000
    print(datacenters_info.get("DC1").get("CPU.S1"))

    # hml=["high","low","medium"]
    # for time_step in range(len(actual_demand)):
    #     # Analyze the demand at this time step
    #     current_demand = actual_demand.iloc[time_step]
    #     print(current_demand['server_generation'])
    #
    #     # Example decision: Buy servers if demand exceeds a certain threshold
    #     for a in range(3):
    #         if current_demand[hml[a]] > threshold.get(current_demand['server_generation'])[a]:
    #
    #             # calculate and save O value for each data center
    #             # determine which datacenter to allocate servers to
    #
    #             action = {
    #                 'time_step': time_step + 1,
    #                 'action': 'buy',
    #                 'server_generation': current_demand['server_generation'],
    #                 'datacenter_id': 'DC1',
    #                 'quantity': current_demand[hml[a]]-threshold.get(current_demand['server_generation'])[a] # Adjust based on your logic
    #             }
    #
    #             solution.append(action)
    #             threshold.get(current_demand['server_generation'])[a] = current_demand[hml[a]]
    #
    #     # Example decision: Sell servers if they are underutilized
    #     # if some_condition_for_selling:
    #     #     action = {
    #     #         'time_step': time_step + 1,
    #     #         'action': 'sell',
    #     #         'server_generation': 'CPU.S2',
    #     #         'datacenter_id': 'DC1',
    #     #         'quantity': 5
    #     #     }
    #     #     solution.append(action)
    #     break

    return solution


seeds = known_seeds('training')

demand = pd.read_csv('./data/demand.csv')
for seed in seeds:
    # SET THE RANDOM SEED
    np.random.seed(seed)
    # print(seed)
    # GET THE DEMAND
    actual_demand = get_actual_demand(demand)
    # print(len(actual_demand))
    # print(actual_demand)
    # a = actual_demand.iloc[0]
    # print(a)
    # break

    # CALL YOUR APPROACH HERE
    solution = get_my_solution(actual_demand)
    # print(solution)
    break
    # SAVE YOUR SOLUTION
    #save_solution(solution, f'./output/{seed}.json')


