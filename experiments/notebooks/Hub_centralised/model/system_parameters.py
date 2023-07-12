"""
Definition of System Parameters, their types, and default values.

By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""


import logging
import numpy as np
from dataclasses import dataclass
from datetime import datetime

import model.constants as constants
import experiments.simulation_configuration as simulation
from model.types import (
    Run,
    Timestep,
    Percentage,
    Gwei,
    Gas,
    Gwei_per_Gas,
    ETH,
    POLYGN,
    USD_per_epoch,
    Percentage_per_epoch,
    ValidatorEnvironment,
    List,
    Callable,
    Epoch,
    Stage,
    ValidatorSetSize,
)
from model.utils import default
from data.historical_values import (
    eth_price_mean,
    eth_block_rewards_mean,
)
from data.api import subgraph



mean_validator_deposits_per_epoch = (
    ## TODO: Need to change another subgraph api
    #subgraph.get_6_month_mean_validator_deposits_per_epoch(default=3) 
    0
)

# Configure validator environment distribution
validator_environments = [
    # Configure a custom validator environment using the following as a template:
    ValidatorEnvironment(
        type="custom",
        percentage_distribution=1,  # 100%
        hardware_costs_per_month=100,
    ),
    # ValidatorEnvironment(
    #     type="diy_hardware",
    #     percentage_distribution=0.37,
    #     hardware_costs_per_epoch=0.0014,
    # ),
    # ValidatorEnvironment(
    #     type="diy_cloud",
    #     percentage_distribution=0.13,
    #     cloud_costs_per_epoch=0.00027,
    # ),
    # ValidatorEnvironment(
    #     type="pool_staas",
    #     percentage_distribution=0.27,
    #     third_party_costs_per_epoch=0.12,
    # ),
    # ValidatorEnvironment(
    #     type="pool_hardware",
    #     percentage_distribution=0.05,
    #     hardware_costs_per_epoch=0.0007,
    # ),
    # ValidatorEnvironment(
    #     type="pool_cloud",
    #     percentage_distribution=0.02,
    #     cloud_costs_per_epoch=0.00136,
    # ),
    # ValidatorEnvironment(
    #     type="staas_full",
    #     percentage_distribution=0.08,
    #     third_party_costs_per_epoch=0.15,
    # ),
    # ValidatorEnvironment(
    #     type="staas_self_custodied",
    #     percentage_distribution=0.08,
    #     third_party_costs_per_epoch=0.12,
    # ),
]
"""Validator environment configuration

See ASSUMPTIONS.md document for details of validator environment configuration and assumptions.
"""

# Normalise percentage distribution to a total of 100%
total_percentage_distribution = sum(
    [validator.percentage_distribution for validator in validator_environments]
)

if total_percentage_distribution < 1:
    logging.warning(
        """
        Parameter validator.percentage_distribution normalized due to sum not being equal to 100%
        """
    )
    for validator in validator_environments:
        validator.percentage_distribution /= total_percentage_distribution

# Using list comprehension, map the validator types to each parameter
validator_percentage_distribution = [
    np.array(
        [validator.percentage_distribution for validator in validator_environments],
        dtype=Percentage,
    )
]
validator_hardware_costs_per_month = [
    np.array(
        [validator.hardware_costs_per_month for validator in validator_environments],
        dtype=USD_per_epoch,
    )
]
validator_cloud_costs_per_epoch = [
    np.array(
        [validator.cloud_costs_per_epoch for validator in validator_environments],
        dtype=USD_per_epoch,
    )
]
validator_third_party_costs_per_epoch = [
    np.array(
        [validator.third_party_costs_per_epoch for validator in validator_environments],
        dtype=Percentage_per_epoch,
    )
]


@dataclass
class Parameters:
    # Time parameters
    dt: List[Epoch] = default([simulation.DELTA_TIME]) # Simulation timescale / timestep unit of time, in epoch.
    date_start: List[datetime] = default([datetime.now()]) # datetime


    # Environmental processes
    polygn_price_process: List[Callable[[Run, Timestep], POLYGN]] = default(
        [lambda _run, _timestep: 1.0]
    )
    polygn_staked_process: List[Callable[[Run, Timestep], POLYGN]] = default(
        [lambda _run, _timestep: None]
    )
    validator_process: List[Callable[[Run, Timestep], int]] = default(
        [
            lambda _run, _timestep: mean_validator_deposits_per_epoch,
        ]
    )

    # Chains number
    PUBLIC_CHAINS_CNT: List[int] = default([5])
    PRIVATE_CHAINS_CNT: List[int] = default([10])

    # Ethereum system parameters
    daily_pow_issuance: List[ETH] = default([eth_block_rewards_mean])
    """
    The average daily Proof-of-Work issuance in ETH.

    See https://etherscan.io/chart/blockreward
    """

    MIN_PER_EPOCH_CHURN_LIMIT: List[int] = default([4])
    """
    Used to calculate the churn limit for validator entry and exit. The maximum number of validators that can
    enter or exit the system per epoch.
    In this system it is used for the validator activation queue process.
    """
    ## TODO: the number is arbitrary, need to find a source for this
    MIN_SLASHING_PENALTY_QUOTIENT: List[int] = default([1e7])
    """
    Used to calculate the penalty applied for a slashable offence.
    """
    MAX_VALIDATOR_COUNT: List[int] = default([100])
    """
    A proposal to set the maximum validators (2**19 == 524,288 validators)
    that are validating ("awake") at any given time. This proposal does not stop validators from 
    depositing and becoming active validators, but rather introduces a rotating validator set.
    "Awake" validators are a subset of "active" validators.

    To disable the maximum validator cap, MAX_VALIDATOR_COUNT is set to None.

    The economic impact of this is as follows:
    
    > Once the active validator set size exceeds MAX_VALIDATOR_COUNT,
    > validator returns should start decreasing proportionately to 1/total_deposits
    > and not 1/sqrt(total_deposits).
    
    See https://ethresear.ch/t/simplified-active-validator-cap-and-rotation-proposal
    
    > The goal of this proposal is to cap the active validator set to some fixed value...
    """
    # PoS Inflation Parameters:
    inflationary_rate_per_year: List[Percentage] = default([0.01 * constants.gwei])
    inflation_sqrt_numerator: List[float] = default([0])
    """
    The param of the annual issuance sqrt distribution k, when issuance rate is sqrt of total staked,
    New inflationary_rate_per_year = k/sqrt(polygn_staked) in float
    """


    # Treasury parameters
    BASE_FEE_PUBLIC_QUOTIENT: List[float] = default([1])
    """
    The parameter of quotient of transaction fees from public chains committed to Polygon Treasury
    """
    BASE_FEE_PRIVATE_QUOTIENTT: List[float] = default([0.1])
    """
    The parameter of quotient of transaction fees from public chains committed to Polygon Treasury
    """
    domain_treasury_monthly_unlock_process: List[Callable[[Run, Timestep], float]] = default(
        [lambda _run, _timestep: 0.01]  # Gwei per gas
    )
    """
    A process that returns the monthly unlock percentage of the total treasury balance.
    """

    # Validator parameters
    validator_uptime_process: List[Percentage] = default(
        [lambda _run, _timestep: max(0.98, 2 / 3)]
    )
    """
    The combination of validator internet, power, and technical uptime, as a percentage.

    Minimum uptime is inactivity leak threshold = 2/3, as this model doesn't model the inactivity leak process.
    """
    validator_percentage_distribution: List[np.ndarray] = default(
        validator_percentage_distribution
    )
    """
    The percentage of validators in each environment, normalized to a total of 100%.

    A vector with a value for each validator environment.
    """
    validator_hardware_costs_per_month: List[np.ndarray] = default(
        validator_hardware_costs_per_month
    )
    """
    The validator hardware costs per epoch in dollars.

    A vector with a value for each validator environment.
    """

    # Rewards, penalties, and slashing
    slashing_events_per_1000_epochs: List[int] = default([1])  # 1 / 1000 epochs
    """
    The number of slashing events per 1000 epochs.
    """
    slashing_ratio_for_large_service: List[float] = default([0.1])
    """
    The slashing ratio for large services.
    For example, when the large services with 70% of validators staked cannot have
    a high percentage of penalty. otherwise, the small services will encounter a high risk due
    to rapid shrinked security pool.
    """

    # EIP-1559 transaction pricing parameters
    base_fee_public_chain_process: List[Callable[[Run, Timestep], Gwei_per_Gas]] = default(
        [lambda _run, _timestep: 16]  # Gwei per gas
    )
    priority_fee_public_chain_process: List[Callable[[Run, Timestep], Gwei_per_Gas]] = default(
        [lambda _run, _timestep: 2]  # Gwei per gas
    )
    base_fee_private_chain_process: List[Callable[[Run, Timestep], Gwei_per_Gas]] = default(
        [lambda _run, _timestep: 5]  # Gwei per gas
    )
    priority_fee_private_chain_process: List[Callable[[Run, Timestep], Gwei_per_Gas]] = default(
        [lambda _run, _timestep: 0.4]  # Gwei per gas
    )
    """
    EIP-1559 transaction pricing base fee burned in public chain, in Gwei per gas, for each transaction.
    See https://eips.ethereum.org/EIPS/eip-1559 for EIP-1559 proposal.

    See ASSUMPTIONS.md doc for further details about default value assumption.

    An extract from https://notes.ethereum.org/@vbuterin/eip-1559-faq:
    
    > Each “full block” (ie. a block whose gas is 2x the TARGET) increases the BASEFEE by 1.125x,
    > so a series of constant full blocks will increase the gas price by a factor of 10 every
    > ~20 blocks (~4.3 min on average).
    > Hence, periods of heavy on-chain load will not realistically last longer than ~5 minutes.
    """
    gas_target_public_chain_process: List[Callable[[Run, Timestep], Gas]] = default(
        [lambda _run, _timestep: 15e6]  # Gas per block
    )
    gas_target_private_chain_process: List[Callable[[Run, Timestep], Gas]] = default(
        [lambda _run, _timestep: 5e6]  # Gas per block
    )
    """
    The long-term average gas target per block in private chain.

    The current gas limit is replaced by two values:
    * a “long-term average target” (equal to the current gas limit) == gas target
    * a “hard per-block cap” (twice the current gas limit) == gas limit

    EIP-1559 gas limit = gas_target * ELASTICITY_MULTIPLIER
    
    See ASSUMPTIONS.md doc for further details about default value assumption.
    """
    ELASTICITY_MULTIPLIER: List[int] = default([2])
    """
    Used to calculate gas limit from EIP-1559 gas target
    """

    # Checkpoint Gas Cost
    # checkpoint_gas_cost: List[Callable[[Run, Timestep], Gas]] = default(
    #     [lambda _run, _timestep: constants.PoS_checkpoint_gas_cost]  # gas cost for each chain-to-Hub checkpoint submission  
    # )
    checkpoint_gas_cost: List[Gas] = default([constants.PoS_checkpoint_gas_cost])
    """
    Gas cost for each chain-to-Hub checkpoint submission
    By default, the gas cost is the Polygon PoS checkpoint gas cost to Eth
    It can be customized by adding a percentage multiplier or being a function of chain-specific validator set size, i.e. O(n),O(n^2) or O(log n).
    """
    basic_epochs_once_a_checkpoint_submission: List[float] = default([1])
    """
    How many epochs has passed when there's one checkpoint submitted
    """
    checkpoint_fee_process: List[Callable[[Run, Timestep], Gwei_per_Gas]] = default(
        [lambda _run, _timestep: 12]  # Gwei per gas
    )
    """
    Checkpoint submission price, in Gwei per gas, for each transaction.
    """

    # Staking Design
    staking_mode: List[str] = default(["MultiStaking"]) # "MultiStaking" or "SingleStaking"

    # Chains Adoption
    Adoption_speed: List[int] = default([1])
    """
    Private chain adoption speed per month. Default set as 1.
    TODO: should be transfer to a process when the adoption rate is relative to the timestamp.
    """



# Initialize Parameters instance with default values
parameters = Parameters().__dict__
