"""
Definition of State Variables, their types, and default values.

By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""


import numpy as np
from dataclasses import dataclass
from datetime import datetime

import model.constants as constants
import data.api.etherscan as etherscan
import data.api.validator_staking as validator_staking
import model.system_parameters as system_parameters
from model.system_parameters import validator_environments
from model.types import (
    Gwei,
    Gwei_per_Gas,
    ETH,
    POLYGN,
    USD,
    USD_per_POLYGN,
    Percentage,
    Stage,
    List,
)
from data.historical_values import eth_price_mean, eth_price_min, eth_price_max
from model.stochastic_processes import create_intial_state_risk_service_validator

# Get number of validator environments for initializing Numpy array size
number_of_validator_environments = len(validator_environments)

# Initial state from external live data source, setting a default in case API call fails
polygn_staked_per_validator: np.ndarray = (
    validator_staking.get_validator_staking_values()
)
polygn_staked: POLYGN = (
    sum(polygn_staked_per_validator)
)
number_of_active_validators: int = 100
polygn_supply: POLYGN = (
    etherscan.get_polygn_supply(default=10_000_000_000e18) / constants.wei
)
sampling_polygn_staked_per_validator: np.ndarray = (
    np.random.poisson(5, number_of_active_validators)
)
polygn_staked_per_validator, polygn_staked = validator_staking.force_staking_ratio(
    polygn_staked_per_validator, polygn_supply,staking_ratio = 0.3
)

# Network state variables
PUBLIC_CHAINS_CNT: int = system_parameters.parameters["PUBLIC_CHAINS_CNT"][0]
PRIVATE_CHAINS_CNT: int = system_parameters.parameters["PRIVATE_CHAINS_CNT"][0]
# Create the risk metric per node and service
service_trust_size, stake_risk_matrix_restaking, stake_risk_matrix_fragmentation = create_intial_state_risk_service_validator(
        PUBLIC_CHAINS_CNT,
        PRIVATE_CHAINS_CNT,
        number_of_active_validators,
    )


@dataclass
class HubState:
    """State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value
    """




    # Time state variables
    stage: Stage = None
    timestamp: datetime = None

    # Validator state variables
    number_of_validators_in_activation_queue: int = 0
    ## TODO: need to fix the max cap of average effective balance. 
    average_effective_balance: Gwei = 30_000_000 * constants.gwei
    number_of_active_validators: int = number_of_active_validators
    number_of_awake_validators: int = min(
        system_parameters.parameters["MAX_VALIDATOR_COUNT"][0] or float("inf"),
        number_of_active_validators,
    )
    validator_uptime: Percentage = 1

    # Network state variables
    PUBLIC_CHAINS_CNT: int = PUBLIC_CHAINS_CNT
    PRIVATE_CHAINS_CNT: int = PRIVATE_CHAINS_CNT

    # POLYGN state variables
    polygn_price: USD_per_POLYGN = 1.0
    polygn_supply: POLYGN = polygn_supply
    polygn_staked: POLYGN = polygn_staked

    # Stake state variables
    stake_data_onchain: bool = False
    if stake_data_onchain:
        polygn_staked_per_validator: np.ndarray = polygn_staked_per_validator
        """The POLYGN staked per validator as part of the Proof of Stake system"""    
    else:
        polygn_staked_per_validator: np.ndarray = (
            sampling_polygn_staked_per_validator / sampling_polygn_staked_per_validator.sum() * polygn_staked
        )

    # Inflation
    supply_inflation: Percentage = 0 
    """The annualized POLYGN supply inflation rate"""
    network_issuance: POLYGN = 0
    """The total network issuance in POLYGN"""
    eth_price: USD_per_POLYGN = 1500.0
    """The POLYGNspot price"""

    

    # Reward and penalty state variables
    base_reward: Gwei = 0
    total_inflation_to_validators: Gwei = 0
    total_inflation_to_validators_usd: USD = 0
    total_inflation_to_validators_normal: Gwei = 0
    total_inflation_to_validators_normal_usd: USD = 0
    total_inflation_to_validators_deviate: Gwei = 0
    total_inflation_to_validators_deviate_usd: USD = 0
    total_inflation_to_validators_yields: Percentage = 0
    total_inflation_to_validators_normal_yields: Percentage = 0
    total_inflation_to_validators_deviate_yields: Percentage = 0

    # Slashing state variables
    amount_slashed: np.ndarray = np.zeros(
        5000, # TODO: need to fix the max number of chains. 
        dtype=int,
    )

    # EIP-1559 state variables
    base_fee_per_gas: Gwei_per_Gas = 1
    """The base fee burned, in Gwei per gas, dynamically updated for each block"""
    # total_priority_fee_to_validators: Gwei = 0 # when w/ EIP-1559
    # total_priority_fee_to_validators_usd: USD = 0 # when w/ EIP-1559
    # total_priority_fee_to_validators_yields: Percentage = 0 # when w/ EIP-1559
    total_txn_fee_to_validators: Gwei = 0
    total_txn_fee_to_validators_usd: USD = 0
    total_txn_fee_to_validators_yields: Percentage = 0

    # Treasury state variables
    private_base_fee_to_domain_treasury: Gwei = 0
    public_base_fee_to_domain_treasury: Gwei = 0

    # System metric state variables
    validator_polygn_staked: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    validator_revenue: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    validator_profit: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    """The total profit (income received - costs) per validator environment"""
    validator_revenue_yields: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    """The total annualized revenue (income received) yields (percentage of investment amount)
    per validator environment"""
    validator_profit_yields: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    validator_count_distribution: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    validator_hardware_costs: USD = 0
    """The total validator hardware operation costs per validator environment"""
    validator_hardware_costs_yields: Percentage = 0
    """The total validator hardware operation costs per validator environment"""
    validator_cloud_costs: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=USD
    )
    """The total validator cloud operation costs per validator environment"""
    validator_third_party_costs: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=USD
    )
    """The total validator third-party fee costs validator environment"""
    validator_checkpoint_costs: USD = 0
    """The total network checkpoint cost each timestep"""
    validator_checkpoint_costs_yields: Percentage = 0
    """The total network checkpoint cost each timestep"""

    total_online_validator_rewards: Gwei = 0
    """The total rewards received by online validators"""
    total_network_costs: USD = 0
    """The total validator operational costs for securing the network"""
    total_revenue: USD = 0
    """The total validator revenue (income received)"""
    total_profit: USD = 0
    """The total validator profit (income received - costs)"""
    total_revenue_yields: Percentage = 0
    """Annualized revenue (income received) for all validators"""
    total_profit_yields: Percentage = 0
    """Annualized profit (income received - costs) for all validators"""

    domain_treasury_balance_unlocked: Gwei = 0
    """The total unlocked treasury balance"""
    domain_treasury_balance_locked: Gwei = 2_000_000_000 * constants.gwei
    """
    The total locked treasury balance. Initial fund is 2B POLYGN.
    """
    private_treasury_balance: Gwei = 0
    """The total private chain treasury balance"""

    # Asynchronous model
    liveness_metrics: np.ndarray = np.reshape(
        np.random.binomial(
            100, 
            0.95, 
            number_of_active_validators * (PUBLIC_CHAINS_CNT + PRIVATE_CHAINS_CNT))
            /100,
        ((PUBLIC_CHAINS_CNT + PRIVATE_CHAINS_CNT), number_of_active_validators)
        )
    """
    Numeric matrix of liveness in [Chains, Validators]
    Default set by every validators are alive
    """
    staking_metrics: np.ndarray = (
                np.repeat([list(polygn_staked_per_validator)], (PUBLIC_CHAINS_CNT + PRIVATE_CHAINS_CNT), axis=0)
                * stake_risk_matrix_restaking
            )
    # print(stake_risk_matrix_restaking[0])
    # print(staking_metrics[0])
    staking_metrics_if_fragmentation: np.ndarray = (
                np.repeat([list(polygn_staked_per_validator)], (PUBLIC_CHAINS_CNT + PRIVATE_CHAINS_CNT), axis=0)
                * stake_risk_matrix_fragmentation
            )
    """
    Numeric matrix of Staking Assignment in [Chains, Validators]
    """
    chain_specific_checkpoint_submission_cadence: np.ndarray = np.random.binomial(1,0.5,(PUBLIC_CHAINS_CNT + PRIVATE_CHAINS_CNT))+1
    """
    How many epochs does the chain submit checkpoints to the hub, in epochs.
    Each chain has their own cadence to submit to the hub.
    """
    share_by_validator_in_SingleStaking: np.ndarray = np.reshape(
        np.random.poisson(5, (PUBLIC_CHAINS_CNT + PRIVATE_CHAINS_CNT)*number_of_active_validators),
        ((PUBLIC_CHAINS_CNT + PRIVATE_CHAINS_CNT), number_of_active_validators)
    )

    # staking centralization metrics
    validator_group_by_event: np.ndarray = np.zeros(number_of_active_validators, dtype=int)
    unassigned_rewards_ratio: float = 0.0
    service_trust_size: np.ndarray = service_trust_size
    staking_centralization_metrics_51: np.ndarray = np.ones(
        PUBLIC_CHAINS_CNT + PRIVATE_CHAINS_CNT,
        dtype=int
    )
    staking_centralization_metrics_33: np.ndarray = np.ones(
        PUBLIC_CHAINS_CNT + PRIVATE_CHAINS_CNT,
        dtype=int
    )
    avg_gini: float = 0.0
    avg_hhi: float = 0.0
    total_top_51_control: int = 0
    total_top_33_control: int = 0
    num_nodes_51: int = 0
    num_nodes_33: int = 0
    node_counts_51_array: np.ndarray = np.array({})
    node_counts_33_array: np.ndarray = np.array({})
    monoply_51: float = 0.0
    monoply_33: float = 0.0
    slashing_amount_large_service: POLYGN = 0.0



# Initialize State Variables instance with default values
initial_state = HubState().__dict__
