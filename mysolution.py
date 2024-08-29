
import numpy as np
import pandas as pd

from evaluation import get_actual_demand, calc_o_value, is_datacenter_full, update_fleet, get_time_step_demand

def get_my_solution(actual_demand, datacenters, servers, selling_prices):
    solution_columns = ['time_step', 'datacenter_id', 'server_generation', 'server_id', 'action']
    solution = pd.DataFrame(columns=solution_columns)  # Initialize solution as an empty DataFrame
    # TODO: Running Main.py results in some sort of error in regards to check_release_time.. I have no clue
    #  why it does this but either way there's a little bit of progress in regards to the solution format.
    #  If any of yous figure it out, feel free to fix it or let me (Elvin lol) know

    # Define the initial structure of the fleet DataFrame
    fleet_columns = ['time_step', 'datacenter_id', 'server_generation', 'server_id', 'action',
                     'slots_size', 'lifespan', 'moved', 'life_expectancy']

    fleet = pd.DataFrame(columns=fleet_columns)  # Initialize fleet with the correct columns

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

    sensitivity_list = ["high", "low", "medium"]  # List to store latency sensitivities

    for time_step in range(len(actual_demand)):  # For each time step
        current_demand = actual_demand.iloc[time_step]  # Get the demand for the current time_step

        best_datacenter = None  # Used to determine which datacenter is most suitable to be given servers
        best_o_value = -float('inf')  # Start with a very low value for comparison

        # Iterate through datacenters to find the best one to allocate servers to
        for datacenter_id in datacenters['datacenter_id'].unique():  # For every datacenter
            if not is_datacenter_full(datacenter_id, fleet, datacenters):  # If there is space in the datacenter
                # Calculate the O_value for the current time-step & datacenter
                o_value, fleet = calc_o_value(solution, current_demand, datacenters, servers, selling_prices, time_step, fleet)

                # Store O_value for the datacenter
                datacenters_info[datacenter_id]['O_Value'] = o_value

                # Check if this O_value is the best one so far
                if o_value > best_o_value:
                    best_o_value = o_value  # Replace with the new max
                    best_datacenter = datacenter_id  # Indicate which datacenter has this new max

        # Check threshold before allocating a server to the best datacenter
        if best_datacenter:
            for curr_sensitivity in range(3):
                if current_demand[sensitivity_list[curr_sensitivity]] > threshold[current_demand['server_generation']][
                    curr_sensitivity]:
                    action = {
                        'time_step': time_step + 1,
                        'datacenter_id': best_datacenter,
                        'server_generation': current_demand['server_generation'],
                        'server_id': f"{best_datacenter}_{time_step+1}",
                        'action': 'buy',
                    }

                    fleet_action = {
                        'time_step': time_step + 1,
                        'datacenter_id': best_datacenter,
                        'server_generation': current_demand['server_generation'],
                        'server_id': f"{best_datacenter}_{time_step + 1}",
                        'action': 'buy',
                        'slots_size': servers.loc[
                            servers['server_generation'] == current_demand['server_generation'], 'slots_size'].values[0],
                        'lifespan': 0,  # Initially, lifespan is 0 when the server is bought
                        'moved': 0,  # Initially, moved is 0 when the server is bought
                        'life_expectancy': servers.loc[servers['server_generation'] == current_demand[
                            'server_generation'], 'life_expectancy'].values[0]
                    }

                    # Append the action to the solution
                    solution.append(action)

                    # Update the fleet and threshold
                    fleet = update_fleet(time_step, fleet, pd.DataFrame([action]))
                    threshold[current_demand['server_generation']][curr_sensitivity] = \
                        current_demand[sensitivity_list[curr_sensitivity]]

                    # Update datacenter info
                    datacenters_info[best_datacenter]["capacity_used"] += fleet_action['slots_size']

        # TODO: Implement 'Buy','Dismiss' & 'Move' actions

    print(solution)
    return solution


