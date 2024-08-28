
import numpy as np
import pandas as pd

from evaluation_example import datacenters, servers, selling_prices
from seeds import known_seeds
from utils import save_solution
from evaluation import get_actual_demand, calc_o_value, is_datacenter_full, update_fleet


def get_my_solution(actual_demand, datacenters, servers, selling_prices):
    solution = []
    fleet = pd.DataFrame()

    # Dictionary to store threshold values for demand
    threshold = {
        "CPU.S1": [0, 0, 0],
        "CPU.S2": [0, 0, 0],
        "CPU.S3": [0, 0, 0],
        "CPU.S4": [0, 0, 0],
        "GPU.S1": [0, 0, 0],
        "GPU.S2": [0, 0, 0],
        "GPU.S3": [0, 0, 0],
    }

    # Dictionary to store O_value and capacity information for each datacenter
    datacenters_info = {
        "DC1": {"O_Value": 0, "capacity_used": 0},
        "DC2": {"O_Value": 0, "capacity_used": 0},
        "DC3": {"O_Value": 0, "capacity_used": 0},
        "DC4": {"O_Value": 0, "capacity_used": 0}
    }

    sensitivity_list = ["high", "low", "medium"] # List to store latency sensitivites

    for time_step in range(len(actual_demand)): # For each time step
        current_demand = actual_demand.iloc[time_step] # get the demand for current time_step
        best_datacenter = None # Used to determine which datacenter is most suitable to be given servers
        best_o_value = -float('inf')

        # Iterate through datacenters to find best one to allocate servers to
        for datacenter_id in datacenters['datacenter_id'].unique(): # for every datacenter
            if not is_datacenter_full(datacenter_id, fleet, datacenters): # if there is space in the datacenter
                o_value = calc_o_value(datacenter_id, fleet, selling_prices, actual_demand, time_step) # calculate the O_value

                # store o value
                datacenters_info[datacenter_id]['O_Value'] = o_value

                # check if o_value is the best so far
                if o_value > best_o_value:
                    best_o_value = o_value # replace with the new max
                    best_datacenter = datacenter_id # indicate which server contains this new max

        # Check threshold before allocating a server
        if best_datacenter:
            for curr_sensitivity in range(3):
                if (current_demand[sensitivity_list[curr_sensitivity]] >
                        threshold.get(current_demand['server_generation'])[curr_sensitivity]):

                    action = {
                        'time_step': time_step + 1,
                        'action': 'buy',
                        'server_generation': current_demand['server_generation'],
                        'datacenter_id': best_datacenter,
                        'server_id': f"{best_datacenter}_{time_step}"
                    }

                    solution.append(action)

                    # update fleet & threshold
                    fleet = update_fleet(time_step, fleet, pd.DataFrame([action]))
                    threshold[current_demand['server_generation']][curr_sensitivity] = \
                        current_demand[sensitivity_list[curr_sensitivity]]

                    # update datacenter info
                    datacenters_info[best_datacenter]["capacity_used"] += (
                        servers.loc[servers['server_generation'] == current_demand['server_generation'], 'slots_size'].values)[0]

    return solution


seeds = known_seeds('training')

demand = pd.read_csv('./data/demand.csv')
for seed in seeds:
    # SET THE RANDOM SEED
    np.random.seed(seed)

    # GET THE DEMAND
    actual_demand = get_actual_demand(demand)

    # CALL YOUR APPROACH HERE
    solution = get_my_solution(actual_demand.iloc[0], datacenters, servers, selling_prices)
    print(solution)

    break
    # SAVE YOUR SOLUTION
    #save_solution(solution, f'./output/{seed}.json')


