
import numpy as np
import pandas as pd

from evaluation import get_actual_demand, calc_o_value, is_datacenter_full, update_fleet, get_time_step_demand

def handle_buy_action(time_step, current_demand, solution, fleet, datacenters, servers, selling_prices):
    best_o_value = -float('inf')
    best_action = None
    best_fleet = fleet.copy()

    # Iterate over latency sensitivities
    for latency in ["high", "low", "medium"]:
        # Filter demand for this latency sensitivity
        latency_demand = current_demand[latency]

        # Find the servers available to meet this demand
        available_servers = servers[(servers['release_time'].apply(lambda x: time_step in eval(x)))
                                    & (servers['capacity'] > 0)]

        for server in available_servers['server_generation'].unique():
            # calculate the unmet demand for this server generation
            unmet_demand = latency_demand - fleet[fleet['server_generation'] == server]['capacity'].sum()

            if unmet_demand > 0:
                # find potential datacenters to allocate servers to
                for datacenter_id in datacenters['datacenter_id'].unique():
                    if not is_datacenter_full(datacenter_id, fleet, datacenters):
                        # temporarily add the server to the fleet and calculate O value
                        temp_fleet = fleet.copy()
                        server_info = servers[servers['server_generation'] == server].iloc[0]
                        temp_fleet = temp_fleet.append({
                            'time_step': time_step,
                            'datacenter_id': datacenter_id,
                            'server_generation': server,
                            'server_id': f"{server}_{time_step}",
                            'action': 'buy',
                            'slots_size': server_info['slots_size'],
                            'lifespan': 0,
                            'moved': 0,
                            'life_expectancy': server_info['life_expectancy'],
                            'capacity': server_info['capacity'],
                        }, ignore_index=True)

                        # Calculate the O value with this temporary fleet
                        o_value, _ = calc_o_value(solution, current_demand, datacenters, servers, selling_prices,
                                                  time_step, temp_fleet)

                        # Compare and select the best action
                        if o_value > best_o_value:
                            best_o_value = o_value
                            best_action = {
                                'time_step': time_step,
                                'datacenter_id': datacenter_id,
                                'server_generation': server,
                                'server_id': f"{server}_{time_step}",
                                'action': 'buy'
                            }
                            best_fleet = temp_fleet.copy()

    # Apply the best action
    if best_action: # whatever this means lol
        solution = solution.append(best_action, ignore_index=True)
        fleet = best_fleet

    return solution, fleet


def handle_dismiss_action(time_step, solution, fleet, datacenters):
    return solution, fleet


def handle_move_action(time_step, solution, fleet, datacenters):
    return solution, fleet


def decide_actions_for_time_step(time_step, current_demand, solution, fleet, datacenters, servers, selling_prices):
    # Action: Buy
    solution, fleet = handle_buy_action(time_step, current_demand, solution, fleet, datacenters, servers, selling_prices)

    # TODO: Action: Sell
    # solution, fleet = handle_dismiss_action(time_step, solution, fleet, datacenters)

    # TODO: Action: Move
    # solution, fleet = handle_move_action(time_step, solution, fleet, datacenters)

    return solution, fleet


def get_my_solution(actual_demand, datacenters, servers, selling_prices):
    # Initialise the solution data frame
    solution_columns = ['time_step', 'datacenter_id', 'server_generation', 'server_id', 'action']
    solution = pd.DataFrame(columns=solution_columns)

    # Initialise the fleet data frame
    fleet_columns = ['time_step', 'datacenter_id', 'server_generation', 'server_id', 'action',
                     'slots_size', 'lifespan', 'moved', 'life_expectancy', 'capacity']
    fleet = pd.DataFrame(columns=fleet_columns)

    # Iterate over each time step
    for time_step in range(1, len(actual_demand) + 1):
        # Get demand for the current time step
        current_demand = actual_demand.iloc[time_step - 1]

        # Decide on actions based on demand and current fleet
        solution, fleet = decide_actions_for_time_step(time_step, current_demand, solution, fleet, datacenters, servers, selling_prices)

    return solution

