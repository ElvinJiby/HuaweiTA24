import pandas as pd

from evaluation import calc_o_value, is_datacenter_full

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


def buy_initial_demand(time_step, current_demand, solution, fleet, datacenters, servers, selling_prices, server_id_counter):
    for index, row in current_demand.iterrows():
        server_generation = row['server_generation']
        print("Server Gens: ",server_generation)

        # Get the demand for this server generation and latency sensitivity
        demand_high = row['high']
        demand_low = row['low']
        demand_medium = row['medium']

        print("Demand (High):",demand_high, "Demand (Low):", demand_low, "Demand (Medium):", demand_medium)

        # Get the available servers of this generation
        available_servers = servers[(servers['server_generation'] == server_generation) &
                                    (servers['release_time'].apply(lambda x: time_step in eval(x)))]
        print("Available Servers: \n",available_servers)

        for _, server in available_servers.iterrows():
            # Buying strategy: Meet high latency demand first, then medium, then low
            demand_to_meet = [demand_high, demand_medium, demand_low]
            latency_labels = ['high', 'medium', 'low']

            for demand, latency in zip(demand_to_meet, latency_labels): # the zip method puts the demand numbers and latency into pairs
                print("Demand: ", demand, "Latency: ", latency)
                required_capacity = 0
                if demand > 0:
                    required_capacity = demand

                    # Calculate how many servers are needed
                    num_servers_to_buy = required_capacity // server['capacity'] # // is the floor division operator (i.e. divides then floors result)
                    print("Server Capacity: ", server['capacity'])
                    print("Num Servers to Buy: ",num_servers_to_buy)
                    remaining_slots = datacenters[datacenters['latency_sensitivity'] == latency]['slots_capacity'].iloc[0]
                    print("Remaining Slots: ",remaining_slots)

                    # Ensure we don't exceed slot capacity
                    servers_to_buy = min(num_servers_to_buy, remaining_slots // server['slots_size'])
                    print("Server Slot Size: ", server['slots_size'])
                    print("Servers to Buy: ",servers_to_buy, "\n")

                    for _ in range(servers_to_buy):
                        action = {
                            'time_step': time_step,
                            'datacenter_id':
                                datacenters[datacenters['latency_sensitivity'] == latency]['datacenter_id'].iloc[0],
                            'server_generation': server_generation,
                            'server_id': f"{server_generation}_TS{time_step}_{server_id_counter}",
                            'action': 'buy'
                        }

                        action_df = pd.DataFrame([action])
                        solution = pd.concat([solution, action_df], ignore_index=True)

                        fleet_df = pd.DataFrame([{**action_df, 'slots_size': server['slots_size'], 'lifespan': 0,
                                              'moved': 0, 'life_expectancy': server['life_expectancy'],
                                              'capacity': server['capacity']}])
                        fleet = pd.concat([fleet, fleet_df], ignore_index=True)

                        server_id_counter += 1 # increment counter

                        # Reduce the unmet demand
                        required_capacity -= server['capacity']
                        if required_capacity <= 0:
                            break  # Move to the next demand category

                # Update the remaining demand for subsequent latency categories
                if latency == 'high':
                    demand_high = required_capacity
                elif latency == 'medium':
                    demand_medium = required_capacity
                elif latency == 'low':
                    demand_low = required_capacity

    return solution, fleet, server_id_counter


def get_my_solution(actual_demand, datacenters, servers, selling_prices):
    # Initialise the solution data frame
    solution_columns = ['time_step', 'datacenter_id', 'server_generation', 'server_id', 'action']
    solution = pd.DataFrame(columns=solution_columns)

    # Initialise the fleet data frame
    fleet_columns = ['time_step', 'datacenter_id', 'server_generation', 'server_id', 'action',
                     'slots_size', 'lifespan', 'moved', 'life_expectancy', 'capacity']
    fleet = pd.DataFrame(columns=fleet_columns)

    # Counter to store server ID (for output)
    server_id_counter = 0

    # Iterate over each time step
    for time_step in range(1, len(actual_demand) + 1):
        # Get demand for the current time step
        current_demand = actual_demand[actual_demand['time_step'] == time_step]

        if time_step != 1:
            # Decide on actions based on demand and current fleet
            solution, fleet = decide_actions_for_time_step(time_step, current_demand, solution, fleet, datacenters, servers, selling_prices)
        else: # First Time Step - i.e. no servers initially
            solution, fleet, server_id_counter = buy_initial_demand(time_step, current_demand, solution, fleet, datacenters, servers, selling_prices, server_id_counter)
            break

    return solution

