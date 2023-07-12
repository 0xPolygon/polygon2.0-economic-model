"""
# Evaludation on staking centralization

"""
import numpy as np
import typing

# Added
def policy_staking_centralization_metric(
    params, substep, state_history, previous_state
) -> typing.Dict[str, any]:
    # Parameters
    dt = params["dt"]

    # state variables
    staking_metrics = previous_state["staking_metrics"]
    number_of_active_validators = previous_state["number_of_active_validators"]


    def calculate_metrics(staking_metrics):
        node_counts_51 = {}
        node_counts_33 = {}
        staking_centralization_metrics_51 = np.array([])
        staking_centralization_metrics_33 = np.array([])
        multi_chains_num = 2

        # For each chain
        for i, chain in enumerate(staking_metrics, multi_chains_num):
            # Sort the nodes in descending order of staking amount
            sorted_indices = np.argsort(chain)[::-1]
            total_stake = np.sum(chain)
            attack_stake = 0
            attack_nodes_51 = 0
            attack_nodes_33 = 0

            # Add nodes to the attack until their combined stake is more than 51%
            for index in sorted_indices:
                attack_stake += chain[index]
                attack_nodes_51 += 1
                if attack_stake <= total_stake * 0.33:
                    attack_nodes_33 += 1
                    if index in node_counts_33:
                        node_counts_33[index] += 1
                    else:
                        node_counts_33[index] = 1
                if attack_stake <= total_stake * 0.51:
                    if index in node_counts_51:
                        node_counts_51[index] += 1
                    else:
                        node_counts_51[index] = 1
                else:
                    break

            staking_centralization_metrics_51 = np.append(staking_centralization_metrics_51, attack_nodes_51)
            staking_centralization_metrics_33 = np.append(staking_centralization_metrics_33, attack_nodes_33)

        # Convert the dictionaries to numpy arrays
        node_counts_51_array = np.zeros(number_of_active_validators)
        node_counts_33_array = np.zeros(number_of_active_validators)
        for index, count in node_counts_51.items():
            node_counts_51_array[index] = count
        for index, count in node_counts_33.items():
            node_counts_33_array[index] = count

        node_counts_51_array = np.where(node_counts_51_array > multi_chains_num)
        num_nodes_51 = len(np.where(node_counts_51_array)[0])
        node_counts_33_array = np.where(node_counts_33_array > multi_chains_num)
        num_nodes_33 = len(np.where(node_counts_33_array)[0])

        return staking_centralization_metrics_51, staking_centralization_metrics_33, node_counts_51_array, node_counts_33_array, num_nodes_51, num_nodes_33

    staking_centralization_metrics_51, staking_centralization_metrics_33,node_counts_51_array, node_counts_33_array, num_nodes_51, num_nodes_33 = calculate_metrics(staking_metrics)
    

    # Calculate staking centralization metric
    for i, chain in enumerate(staking_metrics):
        # Sort the nodes in descending order of staking amount
        sorted_chain = np.sort(chain)[::-1]
        total_stake = np.sum(sorted_chain)
        attack_stake = 0
        attack_nodes_51 = 0
        attack_nodes_33 = 0

        # Add nodes to the attack until their combined stake is more than 51%
        for stake in sorted_chain:
            attack_stake += stake
            attack_nodes_51 += 1
            if attack_stake <= total_stake * 0.33:
                attack_nodes_33 +=1
            if attack_stake > total_stake * 0.51:
                break
        staking_centralization_metrics_51 = np.append(staking_centralization_metrics_51,attack_nodes_51)
        staking_centralization_metrics_33 = np.append(staking_centralization_metrics_33,attack_nodes_33)

    def gini_coefficient(x):
        # Based on bottom eq: http://www.statsdirect.com/help/content/image/stat0206_wmf.gif
        # from: http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
        n = len(x)
        s = x.sum()
        r = np.argsort(np.argsort(-x))  # calculates zero-based ranks
        return 1 - (2 * (r * x).sum() + s) / (n * s)

    def hhi(x):
        # Calculate the squares of the market shares
        squares = np.square(x / np.sum(x))
        # Sum up the squares and multiply by 10,000 to get the HHI
        return np.sum(squares) * 10000

    def average_gini_and_hhi(chains):
        gini_coeffs = []
        hhis = []
        for chain in chains:
            gini_coeffs.append(gini_coefficient(np.array(chain)))
            hhis.append(hhi(np.array(chain)))
        avg_gini = np.mean(gini_coeffs)
        avg_hhi = np.mean(hhis)
        return avg_gini, avg_hhi
    

    avg_gini, avg_hhi = average_gini_and_hhi(staking_metrics)

    return {
        "staking_centralization_metrics_51": staking_centralization_metrics_51,
        "staking_centralization_metrics_33": staking_centralization_metrics_33,
        "avg_gini": avg_gini,
        "avg_hhi": avg_hhi,
        "total_top_51_control": staking_centralization_metrics_51.sum(),
        "total_top_33_control": staking_centralization_metrics_33.sum(),
        "num_nodes_51": num_nodes_51,
        "num_nodes_33": num_nodes_33,
        "node_counts_51_array": node_counts_51_array, 
        "node_counts_33_array": node_counts_33_array,
    } 


def policy_slashable_amount(
    params, substep, state_history, previous_state
) -> typing.Dict[str, any]:
    """
    This policy is measure the system slashable amount from large services,
    especially for the comparison between restaking (MultiStaking) and liquidity fragmentation (SingleStaking)
    """
    # Parameters
    staking_mode = params["staking_mode"]
    slashing_fraction = params["slashing_fraction"]

    # state variables
    staking_metrics = previous_state["staking_metrics"]
    staking_metrics_if_fragmentation = previous_state["staking_metrics_if_fragmentation"]
    service_trust_size = previous_state["service_trust_size"]
    polygn_staked_per_validator = previous_state["polygn_staked_per_validator"]


    # Set the slashing rates by service trust size
    large_service_indices = np.where(service_trust_size > 0.7)
    
    # Calculate the estimated system slashable amount
    if staking_mode == "MultiStaking":
        staking_metrics_large_service = staking_metrics[large_service_indices]
        slashing_per_validator = staking_metrics_large_service.sum(axis=0) * slashing_fraction
        slashing_per_validator = np.array([min(polygn_staked_per_validator[i], slashing_per_validator[i]) for i in range(len(polygn_staked_per_validator))])
        slashing_amount = np.sum( slashing_per_validator)
    else:
        slashing_fraction = 1
        staking_metrics_if_fragmentation_large_service = staking_metrics_if_fragmentation[large_service_indices]
        slashing_per_validator = staking_metrics_if_fragmentation_large_service.sum(axis=0) * slashing_fraction
        slashing_amount = np.sum(slashing_per_validator)
        

    return {
        "slashing_amount_large_service": slashing_amount,
    }





def policy_monoply(
    params, substep, state_history, previous_state
) -> typing.Dict[str, any]:
    """
    This policy is measure the system monoply,
    especially for the comparison between restaking (MultiStaking) and liquidity fragmentation (SingleStaking)
    """
    # state variables
    staking_metrics = previous_state["staking_metrics"]
    node_counts_51_array = previous_state["node_counts_51_array"]
    node_counts_33_array = previous_state["node_counts_33_array"]

    # Calculate the total staking fraction of nodes who can initiate attack on multiple chains
    # The fraction is the sum of the stake on each chains over the total stakes over all nodes
    total_stake_per_node = staking_metrics.sum(axis=0)
    system_total_stake = staking_metrics.sum()
    monoply_51 = total_stake_per_node[node_counts_51_array].sum() / system_total_stake
    monoply_33 = total_stake_per_node[node_counts_33_array].sum() / system_total_stake

    return {
        "monoply_51": monoply_51,
        "monoply_33": monoply_33,
    }

