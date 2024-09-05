import pandas as pd

from evaluation import get_known


def buy_initial_demand(time_step, current_demand, solution, fleet, datacenters, servers, server_id_counter, profit):
    """ Function that carries out the BUY action for the FIRST time step"""
    for index, row in current_demand.iterrows():
        server_generation = row['server_generation']
        # print(f"server_generation @ time step {time_step}? {server_generation}.")

        # Get the demand for this server generation and latency sensitivity
        demand_high = row['high']
        demand_low = row['low']
        demand_medium = row['medium']

        # Get the available servers of this generation
        available_servers = servers[(servers['server_generation'] == server_generation) &
                                    (servers['release_time'].apply(lambda x: time_step in eval(x)))]
        # print(f"Available servers at time step {time_step}: {available_servers}")

        for _, server in available_servers.iterrows():
            # Buying strategy: Meet high latency demand first, then medium, then low
            demand_to_meet = [demand_high, demand_medium, demand_low]
            latency_labels = ['high', 'medium', 'low']

            for demand, latency in zip(demand_to_meet, latency_labels): # the zip method puts the demand numbers and latency into pairs
                required_capacity = 0
                if demand > 0:
                    required_capacity = demand

                    # Calculate how many servers are needed
                    num_servers_to_buy = required_capacity // server['capacity'] # // is the floor division operator (i.e. divides then floors result)
                    remaining_slots = datacenters[datacenters['latency_sensitivity'] == latency]['slots_capacity'].iloc[0]

                    # Ensure we don't exceed slot capacity
                    servers_to_buy = min(num_servers_to_buy, remaining_slots // server['slots_size'])

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

                        fleet_df = pd.DataFrame([{**action_df,
                                                'slots_size': server['slots_size'],
                                                'lifespan': 0,
                                                'moved': 0,
                                                'life_expectancy': server['life_expectancy'],
                                                'capacity': server['capacity'],
                                                'latency_sensitivity': latency
                                                  }])
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

    return solution, fleet, server_id_counter, profit

def handle_buy_action(time_step, current_demand, solution, fleet, datacenters, servers, server_id_counter, profit):
    """Function that carries out the BUY action for any time step"""
    for index, row in current_demand.iterrows():
        server_generation = row['server_generation']
        # print(f"server_generation @ time step {time_step}: {server_generation}.")

        # Get the demand for this server generation and latency sensitivity
        demand_high = row['high']
        demand_low = row['low']
        demand_medium = row['medium']

        # Check existing fleet capacity before buying new servers
        existing_capacity = fleet[fleet['server_generation'].astype(str) == server_generation]['capacity'].sum()
        # print(f"Existing capacity at time step {time_step}: {existing_capacity}")

        # Calculate unmet demand after considering existing capacity
        unmet_demand_high = max(demand_high - existing_capacity, 0)
        unmet_demand_medium = max(demand_medium - existing_capacity, 0)
        unmet_demand_low = max(demand_low - existing_capacity, 0)

        # Get the available servers of this generation
        available_servers = servers[(servers['server_generation'] == server_generation) &
                                    (servers['release_time'].apply(lambda x: time_step in eval(x)))]


        # print(f"Available servers at time step {time_step}: {available_servers.empty}")

        for _, server in available_servers.iterrows():
            # Buying strategy: Meet high latency demand first, then medium, then low
            demand_to_meet = [unmet_demand_high, unmet_demand_medium, unmet_demand_low]
            latency_labels = ['high', 'medium', 'low']

            for demand, latency in zip(demand_to_meet, latency_labels):
                required_capacity = 0
                if demand > 0:
                    required_capacity = demand

                    # Calculate how many servers are needed
                    num_servers_to_buy = required_capacity // server['capacity']
                    remaining_slots = datacenters[datacenters['latency_sensitivity'] == latency]['slots_capacity'].iloc[0]

                    # Ensure we don't exceed slot capacity
                    servers_to_buy = min(num_servers_to_buy, remaining_slots // server['slots_size'])

                    for _ in range(servers_to_buy):
                        action = {
                            'time_step': time_step,
                            'datacenter_id':
                                datacenters[datacenters['latency_sensitivity'] == latency]['datacenter_id'].iloc[0],
                            'server_generation': server_generation,
                            'server_id': f"{server_generation}_{server_id_counter}",
                            'action': 'buy'
                        }

                        action_df = pd.DataFrame([action])
                        solution = pd.concat([solution, action_df], ignore_index=True)

                        fleet_df = pd.DataFrame([{**action,
                                                  'slots_size': server['slots_size'],
                                                  'lifespan': 0,
                                                  'moved': 0,
                                                  'life_expectancy': server['life_expectancy'],
                                                  'capacity': server['capacity'],
                                                  'latency_sensitivity': latency
                                                  }])
                        fleet = pd.concat([fleet, fleet_df], ignore_index=True)

                        # Increment the server ID counter
                        server_id_counter += 1

                        # Reduce the unmet demand
                        required_capacity -= server['capacity']
                        if required_capacity <= 0:
                            break  # Move to the next demand category

                # Update the remaining demand for subsequent latency categories
                if latency == 'high':
                    unmet_demand_high = required_capacity
                elif latency == 'medium':
                    unmet_demand_medium = required_capacity
                elif latency == 'low':
                    unmet_demand_low = required_capacity

    return solution, fleet, server_id_counter, profit

def handle_sell_action(time_step, current_demand, solution, fleet, selling_prices, server_id_counter, profit):
    """Function that carries out the SELL action for any time step"""
    for index, row in current_demand.iterrows():
        server_generation = row['server_generation']

        # Get the demand for this server generation and latency sensitivity
        demand_high = row['high']
        demand_low = row['low']
        demand_medium = row['medium']

        # Check existing fleet capacity before deciding to sell servers
        existing_capacity = fleet[fleet['server_generation'].astype(str) == server_generation]['capacity'].sum()

        # Calculate excess capacity after meeting the demand
        excess_capacity_high = max(existing_capacity - demand_high, 0)
        excess_capacity_medium = max(existing_capacity - demand_medium, 0)
        excess_capacity_low = max(existing_capacity - demand_low, 0)

        # Get servers in the fleet that can be sold
        servers_in_fleet = fleet[fleet['server_generation'].astype(str) == server_generation]

        for _, server in servers_in_fleet.iterrows():
            # Selling strategy: Reduce excess capacity starting with high latency demand, then medium, then low
            excess_capacity_to_reduce = [excess_capacity_high, excess_capacity_medium, excess_capacity_low]
            latency_labels = ['high', 'medium', 'low']

            for excess, latency in zip(excess_capacity_to_reduce, latency_labels):
                if excess > 0:
                    capacity_to_remove = server['capacity']
                    num_servers_to_sell = min(excess // capacity_to_remove, len(servers_in_fleet))

                    for i in range(num_servers_to_sell):
                        action = {
                            'time_step': time_step,
                            'datacenter_id': server['datacenter_id'],
                            'server_generation': server_generation,
                            'server_id': f"{server_generation}_TS{time_step}_{server_id_counter}",  # Use existing server ID to remove it
                            'action': 'sell'
                        }

                        action_df = pd.DataFrame([action])
                        solution = pd.concat([solution, action_df], ignore_index=True)

                        # Remove the server from the fleet
                        fleet = fleet[fleet['server_id'].astype(str) != server['server_id']]

                        # Increment server ID counter
                        server_id_counter += 1

                        # Reduce the excess capacity
                        excess -= capacity_to_remove
                        if excess <= 0:
                            break  # Move to the next excess category

                # Update the remaining excess capacity for subsequent latency categories
                if latency == 'high':
                    excess_capacity_high = excess
                elif latency == 'medium':
                    excess_capacity_medium = excess
                elif latency == 'low':
                    excess_capacity_low = excess

    return solution, fleet, server_id_counter, profit


def handle_move_action(time_step, current_demand, solution, fleet, datacenters, servers, server_id_counter, profit):
    """Function that carries out the MOVE action for any time step"""
    for index, row in current_demand.iterrows():
        server_generation = row['server_generation']

        # Get the demand for this server generation and latency sensitivity
        demand_high = row['high']
        demand_low = row['low']
        demand_medium = row['medium']

        # Calculate current fleet capacity per latency sensitivity
        high_capacity = fleet[(fleet['server_generation'].astype(str) == server_generation) & (fleet['latency_sensitivity'] == 'high')]['capacity'].sum()
        medium_capacity = fleet[(fleet['server_generation'].astype(str) == server_generation) & (fleet['latency_sensitivity'] == 'medium')]['capacity'].sum()
        low_capacity = fleet[(fleet['server_generation'].astype(str) == server_generation) & (fleet['latency_sensitivity'] == 'low')]['capacity'].sum()

        # Determine if there's a need to move servers to better match the demand
        unmet_demand_high = max(demand_high - high_capacity, 0)
        unmet_demand_medium = max(demand_medium - medium_capacity, 0)
        unmet_demand_low = max(demand_low - low_capacity, 0)

        # Identify excess capacity in latency categories that could be used elsewhere
        excess_capacity_high = max(high_capacity - demand_high, 0)
        excess_capacity_medium = max(medium_capacity - demand_medium, 0)
        excess_capacity_low = max(low_capacity - demand_low, 0)

        # Move servers based on unmet demand and excess capacity
        for excess, source_latency, target_demand, target_latency in [
            (excess_capacity_high, 'high', unmet_demand_medium, 'medium'),
            (excess_capacity_high, 'high', unmet_demand_low, 'low'),
            (excess_capacity_medium, 'medium', unmet_demand_low, 'low'),

        ]:
            if excess > 0 and target_demand > 0:
                # Identify servers in the fleet that can be moved
                servers_to_move = fleet[(fleet['server_generation'].astype(str) == server_generation) &
                                        (fleet['latency_sensitivity'] == source_latency)]

                for _, server in servers_to_move.iterrows():
                    if target_demand <= 0:
                        break

                    # Move one server at a time
                    action = {
                        'time_step': time_step,
                        'datacenter_id': datacenters[datacenters['latency_sensitivity'] == target_latency]['datacenter_id'].iloc[0],
                        'server_generation': server_generation,
                        'server_id':  f"{server_generation}_TS{time_step}_{server_id_counter}",
                        'action': 'move',
                    }

                    action_df = pd.DataFrame([action])
                    solution = pd.concat([solution, action_df], ignore_index=True)

                    # Update the server's latency sensitivity and datacenter in the fleet
                    fleet.loc[fleet['server_id'] == server['server_id'], 'latency_sensitivity'] = target_latency
                    fleet.loc[fleet['server_id'] == server['server_id'], 'datacenter_id'] = action['datacenter_id']

                    # Increment server ID counter
                    server_id_counter += 1
                    # Adjust the remaining demand and excess capacity
                    target_demand -= server['capacity']
                    excess -= server['capacity']

    return solution, fleet, server_id_counter, profit


def decide_actions_for_time_step(time_step, current_demand, solution, fleet, datacenters, servers, selling_prices, server_id_counter, profit):
    # print(f"Entered decision logic for time step {time_step}")
    # print("Init: Fleet empty?: ", fleet.empty)
    # print("Move: Solution empty?: ", solution.empty)

    # Action: Move
    solution, fleet, server_id_counter, profit = handle_move_action(time_step, current_demand, solution, fleet, datacenters, servers, server_id_counter, profit)
    # print("Move: Fleet empty?: ", fleet.empty)
    # print("Move: Solution empty?: ", solution.empty)

    # Action: Buy
    solution, fleet, server_id_counter, profit = handle_buy_action(time_step, current_demand, solution, fleet, datacenters, servers, server_id_counter, profit)
    # print("Buy: Fleet empty?: ", fleet.empty)
    # print("Buy: Solution empty?: ", solution.empty)

    # Action: Sell
    solution, fleet, server_id_counter, profit = handle_sell_action(time_step, current_demand, solution, fleet, selling_prices, server_id_counter, profit)
    # print("Sell: Fleet empty?: ", fleet.empty)
    # print("Sell: Solution empty?: ", solution.empty)

    return solution, fleet, server_id_counter, profit


def get_my_solution(actual_demand, datacenters, servers, selling_prices):
    # Initialise the solution data frame
    solution_columns = ['time_step', 'datacenter_id', 'server_generation', 'server_id', 'action']
    solution = pd.DataFrame(columns=solution_columns)

    # Initialise the fleet data frame
    fleet_columns = ['time_step', 'datacenter_id', 'server_generation', 'server_id', 'action',
                     'slots_size', 'lifespan', 'moved', 'life_expectancy', 'capacity', 'latency_sensitivity']
    fleet = pd.DataFrame(columns=fleet_columns)

    # Counter to store server ID (for output)
    server_id_counter = 0

    # Variable to store profit
    profit = 0

    # Iterate over each time step
    for time_step in range(1, get_known('time_steps')):
        # Get demand for the current time step
        current_demand = actual_demand[actual_demand['time_step'] == time_step]

        # copy of solution, fleet
        solution_copy, fleet_copy = solution.copy(), fleet.copy()

        print("Time Step: ", time_step)
        if time_step > 1:
            # Decide on actions based on demand and current fleet
            solution, fleet, server_id_counter, profit = decide_actions_for_time_step(time_step, current_demand, solution, fleet, datacenters, servers, selling_prices, server_id_counter, profit)
        else: # First Time Step - i.e. no servers initially
            solution, fleet, server_id_counter, profit = buy_initial_demand(time_step, current_demand, solution, fleet, datacenters, servers, server_id_counter, profit)

        # print(f"Has solution & fleet remained unchanged after Time Step: {time_step}? {solution_copy.equals(solution)} {fleet_copy.equals(fleet)}")

    return solution

