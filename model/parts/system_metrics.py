"""
# System Metrics

Calculation of metrics such as validator operational costs and yields.
"""

import typing
import numpy as np

import model.constants as constants
from model.types import Percentage, Gwei



# Edited
def policy_validator_costs(
    params, substep, state_history, previous_state
) -> typing.Dict[str, any]:
    """
    ## Validator Costs Policy Function
    Calculate the aggregate validator costs.
    """
    # Parameters
    dt = params["dt"]
    validator_percentage_distribution = params["validator_percentage_distribution"]
    validator_hardware_costs_per_month_process = params["validator_hardware_costs_per_month_process"]
    validator_cloud_costs_per_epoch = params["validator_cloud_costs_per_epoch"]
    validator_third_party_costs_per_epoch = params[
        "validator_third_party_costs_per_epoch"
    ]
    basic_epochs_once_a_checkpoint_submission = params[
        "basic_epochs_once_a_checkpoint_submission"
    ]
    checkpoint_gas_cost = params[
        "checkpoint_gas_cost"
    ]
    checkpoint_fee_process = params[
        "checkpoint_fee_process"
    ]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    polygn_price = previous_state["polygn_price"]
    eth_price = previous_state["eth_price"]
    number_of_validators = previous_state["number_of_active_validators"]
    total_online_validator_rewards = previous_state["total_online_validator_rewards"]
    chain_specific_checkpoint_submission_cadence = previous_state["chain_specific_checkpoint_submission_cadence"]
    PUBLIC_CHAINS_CNT = previous_state["PUBLIC_CHAINS_CNT"]
    PRIVATE_CHAINS_CNT = previous_state["PRIVATE_CHAINS_CNT"]
    staking_metrics = previous_state["staking_metrics"]

    # Calculate hardware, cloud, and third-party costs per validator type
    validator_count_distribution = (
        np.count_nonzero(staking_metrics)
        * validator_percentage_distribution
    )

    ## TODO: not rigourous right now
    validator_count_distribution = (
        (100*PUBLIC_CHAINS_CNT + 15*PRIVATE_CHAINS_CNT)
        * validator_percentage_distribution
    )

    validator_hardware_costs_per_month = validator_hardware_costs_per_month_process(run, (timestep-1) * dt)
    validator_hardware_costs = (
        validator_count_distribution * (validator_hardware_costs_per_month / constants.epochs_per_month) * dt
    )
    validator_hardware_costs = validator_hardware_costs.sum(axis=0)


    # validator_cloud_costs = (
    #     validator_count_distribution * validator_cloud_costs_per_epoch * dt
    # )

    # validator_third_party_costs = (
    #     validator_percentage_distribution
    #     * validator_third_party_costs_per_epoch  # % of total
    #     * total_online_validator_rewards
    # )

    checkpoint_fee_per_gas = checkpoint_fee_process(run, timestep * dt)
    total_network_checkpoint_submission_cnt = sum(
        dt/chain_specific_checkpoint_submission_cadence/basic_epochs_once_a_checkpoint_submission
    )
    validator_checkpoint_costs = (
        total_network_checkpoint_submission_cnt
        * checkpoint_gas_cost
        * checkpoint_fee_per_gas
    )

    # validator_third_party_costs /= constants.gwei  # Convert from Gwei to POLYGN
    # validator_third_party_costs *= polygn_price  # Convert from POLYGN to Dollars

    validator_checkpoint_costs /= constants.gwei  # Convert from Gwei to POLYGN
    #validator_checkpoint_costs *= polygn_price  # Convert from POLYGN to Dollars if gas paied by POLYGN
    validator_checkpoint_costs *= eth_price  # Convert from POLYGN to Dollars if gas paied by ETH

    # Calculate total validator costs per validator type and total network costs
    #total_network_costs = validator_hardware_costs+validator_checkpoint_costs
    total_network_costs = validator_hardware_costs

    return {
        "validator_count_distribution": validator_count_distribution,
        "validator_hardware_costs": validator_hardware_costs,
        # "validator_cloud_costs": validator_cloud_costs,
        # "validator_third_party_costs": validator_third_party_costs,
        "validator_checkpoint_costs": validator_checkpoint_costs,
        "total_network_costs": total_network_costs,
    }

# Edited
def policy_validator_yields(
    params, substep, state_history, previous_state
) -> typing.Dict[str, any]:
    """
    ## Validator Yields Policy Function
    Calculate the aggregate validator revenue and profit yields.
    """
    # Parameters
    dt = params["dt"]
    validator_percentage_distribution = params["validator_percentage_distribution"]

    # State Variables
    polygn_price = previous_state["polygn_price"]
    polygn_staked = previous_state["polygn_staked"]
    total_network_costs = previous_state["total_network_costs"]
    total_online_validator_rewards = previous_state["total_online_validator_rewards"]
    validator_count_distribution = previous_state["validator_count_distribution"]
    average_effective_balance = previous_state["average_effective_balance"]
    validator_checkpoint_costs = previous_state["validator_checkpoint_costs"]
    validator_hardware_costs = previous_state["validator_hardware_costs"]
    total_txn_fee_to_validators_usd = previous_state["total_txn_fee_to_validators_usd"]
    total_inflation_to_validators_usd = previous_state["total_inflation_to_validators_usd"]
    total_inflation_to_validators_normal_usd = previous_state["total_inflation_to_validators_normal_usd"]
    total_inflation_to_validators_deviate_usd = previous_state["total_inflation_to_validators_deviate_usd"]
    validator_group_by_event = previous_state["validator_group_by_event"]
    polygn_staked_per_validator = previous_state["polygn_staked_per_validator"]

    # Calculate ETH staked per validator type
    validator_polygn_staked = validator_count_distribution * average_effective_balance
    validator_polygn_staked /= constants.gwei  # Convert from Gwei to ETH

    # Calculate the revenue per validator type
    validator_revenue = (
        validator_percentage_distribution * total_online_validator_rewards
    )
    validator_revenue /= constants.gwei  # Convert from Gwei to POLYGN
    validator_revenue *= polygn_price  # Convert from ETH to Dollars
    # validator_revenue *= 1  # Convert from POLYGN to Dollars

    # Calculate the profit per validator type
    validator_profit = validator_revenue - total_network_costs

    # Calculate the revenue yields per validator type
    validator_revenue_yields = validator_revenue / (validator_polygn_staked * polygn_price)
    validator_revenue_yields *= constants.epochs_per_year / dt  # Annualize value

    # Calculate the profit yields per validator type
    validator_profit_yields = validator_profit / (validator_polygn_staked * polygn_price)
    validator_profit_yields *= constants.epochs_per_year / dt  # Annualize value

    # Calculate the total network revenue
    total_revenue = validator_revenue.sum(axis=0)

    # Calculate the total network profit
    total_profit = total_revenue - total_network_costs

    # Calculate the total network revenue yields
    total_revenue_yields = total_revenue / (polygn_staked * polygn_price)
    total_revenue_yields *= constants.epochs_per_year / dt  # Annualize value

    # Calculate the total network profit yields
    total_profit_yields = total_profit / (polygn_staked * polygn_price)
    total_profit_yields *= constants.epochs_per_year / dt  # Annualize value

    # calculate remaining broken up yields, annualized
    validator_checkpoint_costs_yields = validator_checkpoint_costs / (polygn_staked * polygn_price) * constants.epochs_per_year / dt
    validator_hardware_costs_yields = validator_hardware_costs / (polygn_staked * polygn_price)* constants.epochs_per_year / dt
    total_txn_fee_to_validators_yields = total_txn_fee_to_validators_usd / (polygn_staked * polygn_price)* constants.epochs_per_year / dt
    total_inflation_to_validators_yields = total_inflation_to_validators_usd / (polygn_staked * polygn_price)* constants.epochs_per_year / dt
    polygn_staked_deviate = (validator_group_by_event * polygn_staked_per_validator).sum()
    polygn_staked_normal = polygn_staked - polygn_staked_deviate
    total_inflation_to_validators_normal_yields = total_inflation_to_validators_normal_usd / (polygn_staked_normal * polygn_price)* constants.epochs_per_year / dt
    total_inflation_to_validators_deviate_yields = total_inflation_to_validators_deviate_usd / (polygn_staked_deviate * polygn_price)* constants.epochs_per_year / dt
    


    return {
        # Per validator type
        "validator_polygn_staked": validator_polygn_staked,
        "validator_revenue": validator_revenue,
        "validator_profit": validator_profit,
        "validator_revenue_yields": validator_revenue_yields,
        "validator_profit_yields": validator_profit_yields,
        # Aggregate
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_revenue_yields": total_revenue_yields,
        "total_profit_yields": total_profit_yields,
        "validator_checkpoint_costs_yields": validator_checkpoint_costs_yields,
        "validator_hardware_costs_yields": validator_hardware_costs_yields,
        "total_txn_fee_to_validators_yields": total_txn_fee_to_validators_yields,
        "total_inflation_to_validators_yields": total_inflation_to_validators_yields,
        "total_inflation_to_validators_normal_yields": total_inflation_to_validators_normal_yields,
        "total_inflation_to_validators_deviate_yields": total_inflation_to_validators_deviate_yields,
    }


# Edited
def policy_total_online_validator_rewards(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    ## Total Online Validator Rewards Policy Function
    Calculate the aggregate total online validator rewards.
    """
    # Parameters
    dt = params["dt"]

    # State Variables
    inflation_rewards = previous_state["total_inflation_to_validators"]
    total_txn_fee_to_validators = previous_state[
        "total_txn_fee_to_validators"
    ]
    liveness_metrics = previous_state["liveness_metrics"]

    # Calculate total rewards for online validators
    total_online_validator_rewards = (
        inflation_rewards
        + total_txn_fee_to_validators
    )


    return {
        "total_online_validator_rewards": total_online_validator_rewards,
    }
 

# Reviewed
def update_supply_inflation(
    params, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, Percentage]:
    """
    ## Supply Inflation State Update Function
    Update the annualized POLYGN supply inflation.
    """
    # Policy Inputs
    network_issuance = policy_input["network_issuance"]

    # Parameters
    dt = params["dt"]

    # State Variables
    polygn_supply = previous_state["polygn_supply"]

    # Calculate the ETH supply inflation
    supply_inflation = network_issuance / polygn_supply
    supply_inflation *= constants.epochs_per_year / dt  # Annualize value

    return "supply_inflation", supply_inflation
