"""
# Ethereum System

General Ethereum mechanisms, such as managing the system upgrade process,
the EIP-1559 transaction pricing mechanism, and updating the ETH price and ETH supply.
"""

import typing
import datetime
import numpy as np

from model import constants as constants
from model.types import ETH, USD_per_POLYGN, Gwei, Stage




def policy_upgrade_stages(params, substep, state_history, previous_state):
    """
    ## Upgrade Stages Policy

    Transitions the model from one stage in the Ethereum network
    upgrade process to the next at different milestones.

    This is essentially a finite-state machine: https://en.wikipedia.org/wiki/Finite-state_machine
    """

    # Parameters
    dt = params["dt"]
    stage: Stage = params["stage"]
    date_start = params["date_start"]

    # State Variables
    current_stage = previous_state["stage"]
    timestep = previous_state["timestep"]

    # Calculate current timestamp from timestep
    timestamp = date_start + datetime.timedelta(
        days=(timestep * dt / constants.epochs_per_day)
    )

    # Initialize stage State Variable at start of simulation
    if current_stage is None:
        current_stage = stage
    else:
        # Convert Stage enum value (int) to Stage enum
        current_stage = Stage(current_stage)

    return {
        "stage": current_stage.value,
        "timestamp": timestamp,
    }


# Edited
def policy_network_issuance(
    params, substep, state_history, previous_state
) -> typing.Dict[str, ETH]:
    """
    ## Network Issuance Policy Function

    Calculate the total network issuance and issuance from Proof of Work block rewards.
    """


    # State Variables
    amount_slashed = previous_state["amount_slashed"]
    inflation_rewards = previous_state["total_inflation_to_validators"]

    # Calculate network issuance in ETH
    network_issuance = (
        inflation_rewards
        - amount_slashed
    ) / constants.gwei


    return {
        "network_issuance": network_issuance,
    }


def policy_mev(params, substep, state_history, previous_state) -> typing.Dict[str, ETH]:
    """
    ## Maximum Extractable Value (MEV) Policy

    MEV is allocated to miners pre Proof-of-Stake and validators post Proof-of-Stake,
    using the `mev_per_block` System Parameter.

    By default `mev_per_block` is set zero, to only consider the
    influence of Proof-of-Stake (PoS) incentives on validator yields.

    See [ASSUMPTIONS.md](ASSUMPTIONS.md) document for further details.
    """
    # Parameters
    dt = params["dt"]
    mev_per_block = params["mev_per_block"]

    # State Variables
    stage = Stage(previous_state["stage"])

    if stage in [Stage.PROOF_OF_STAKE]:
        total_realized_mev_to_miners = 0
        # Allocate realized MEV to validators post Proof-of-Stake
        total_realized_mev_to_validators = (
            mev_per_block * constants.slots_per_epoch * dt
        )
    else:  # Stage is pre Proof-of-Stake
        # Allocate realized MEV to miners pre Proof-of-Stake
        total_realized_mev_to_miners = (
            mev_per_block * constants.pow_blocks_per_epoch * dt
        )
        total_realized_mev_to_validators = 0

    return {
        "total_realized_mev_to_miners": total_realized_mev_to_miners,
        "total_realized_mev_to_validators": total_realized_mev_to_validators,
    }

def policy_transaction_pricing(
        params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    # Parameters
    dt = params["dt"]
    public_chain_txn_num_process = params["public_chain_txn_num_process"]
    private_chain_txn_num_process = params["private_chain_txn_num_process"]
    public_txn_fee_process = params["public_txn_fee_process"]
    private_txn_fee_process = params["private_txn_fee_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    public_chain_number = previous_state["PUBLIC_CHAINS_CNT"]
    private_chain_number = previous_state["PRIVATE_CHAINS_CNT"]
    polygn_price = previous_state["polygn_price"]

    public_chain_txn_num = public_chain_txn_num_process(run, timestep * dt)
    private_chain_txn_num = private_chain_txn_num_process(run, timestep * dt)
    public_txn_fee = public_txn_fee_process(run, timestep * dt)
    private_txn_fee = private_txn_fee_process(run, timestep * dt)

    public_txn_cnt = dt * 24*60*60/constants.epochs_per_day * public_chain_txn_num
    private_txn_cnt = dt * 24*60*60/constants.epochs_per_day * private_chain_txn_num


    total_txn_fee_to_validators_usd = (
        public_txn_cnt * public_txn_fee * public_chain_number
        + private_txn_fee * private_txn_cnt * private_chain_number
    )

    return {
        "total_txn_fee_to_validators": total_txn_fee_to_validators_usd / polygn_price * constants.gwei,
        "total_txn_fee_to_validators_usd": total_txn_fee_to_validators_usd,
    }


    

# Edited
def policy_eip1559_transaction_pricing(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    ## EIP-1559 Transaction Pricing Policy

    A transaction pricing mechanism that includes fixed-per-block network fee
    that is burned and dynamically expands/contracts block sizes to deal with transient congestion.

    See:
    * https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1559.md
    * https://eips.ethereum.org/EIPS/eip-1559
    """

    # Parameters
    dt = params["dt"]
    gas_target_public_chain_process = params["gas_target_public_chain_process"]  # Gas
    gas_target_private_chain_process = params["gas_target_private_chain_process"]  # Gas
    ELASTICITY_MULTIPLIER = params["ELASTICITY_MULTIPLIER"]
    base_fee_public_chain_process = params["base_fee_public_chain_process"]
    priority_fee_public_chain_process = params["priority_fee_public_chain_process"]
    base_fee_private_chain_process = params["base_fee_private_chain_process"]
    priority_fee_private_chain_process = params["priority_fee_private_chain_process"]
    public_chain_treasury_extraction_rate = params["BASE_FEE_PUBLIC_QUOTIENT"]
    private_chain_treasury_extraction_rate = params["BASE_FEE_PRIVATE_QUOTIENTT"]
 


    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    private_treasury_balance = previous_state["private_treasury_balance"]
    public_chain_number = previous_state["PUBLIC_CHAINS_CNT"]
    private_chain_number = previous_state["PRIVATE_CHAINS_CNT"]
    liveness_metrics = previous_state["liveness_metrics"]
    staking_metrics = previous_state["staking_metrics"]
    polygn_price = previous_state["polygn_price"]

    total_chain_number = public_chain_number + private_chain_number

    # Get samples for current run and timestep from base fee, priority fee, and transaction processes
    base_fee_public_per_gas = base_fee_public_chain_process(run, timestep * dt)  # Gwei per Gas
    base_fee_private_per_gas = base_fee_private_chain_process(run, timestep * dt)  # Gwei per Gas

    gas_target_public_chain = gas_target_public_chain_process(run, timestep * dt)  # Gas
    gas_target_private_chain = gas_target_private_chain_process(run, timestep * dt)  # Gas

    avg_priority_fee_public_chain_per_gas = priority_fee_public_chain_process(run, timestep * dt)  # Gwei per Gas
    avg_priority_fee_private_chain_per_gas = priority_fee_private_chain_process(run, timestep * dt)  # Gwei per Gas


    gas_used_public_chain = constants.slots_per_epoch * gas_target_public_chain  # Gas
    gas_used_private_chain = constants.slots_per_epoch * gas_target_private_chain  # Gas


    # # Get gas used per transaction
    # gas_used_per_txn = gas_used_per_txn_process(run, timestep * dt)
    # txn_number_per_block = txn_number_per_block_process(run, timestep * dt)
    # gas_price_per_txn = gas_price_per_txn_process(run, timestep * dt)

    # # Calculate total txn fees per epoch
    # total_txn_fees =( 
    #     gas_used_per_txn 
    #     * txn_number_per_block 
    #     * gas_price_per_txn
    #     * constants.slots_per_epoch
    # )

    # Calculate the total base fee and priority fee for a single chain
    total_base_fee_public_chain = gas_used_public_chain * base_fee_public_per_gas  # Gwei
    total_base_fee_private_chain = gas_used_private_chain * base_fee_private_per_gas  # Gwei
    total_priority_fee_public_chain = gas_used_public_chain * avg_priority_fee_public_chain_per_gas  # Gwei
    total_priority_fee_private_chain = gas_used_public_chain * avg_priority_fee_private_chain_per_gas  # Gwei


    # Calculate the fee sent to treasuries
    public_base_fee_to_domain_treasury = (
        total_base_fee_public_chain
        * public_chain_treasury_extraction_rate
        * public_chain_number
    ) # Gwei
    private_base_fee_to_domain_treasury = (
        total_base_fee_private_chain
        * private_chain_treasury_extraction_rate
        * private_chain_number
    ) # Gwei

    # Calculate the total priority fee to validators from all public and private chains
    #staking_share_metrics = staking_metrics / staking_metrics.sum(axis=1)[:,np.newaxis] # share of chains by validator
    total_priority_fee_to_validators = (
        public_chain_number * total_priority_fee_public_chain 
        + private_chain_number * total_priority_fee_private_chain
    ) # Gwei

    # Calculate the remain base fee to private chain owned treasury
    private_base_fee_to_private_treasury = (
        total_base_fee_private_chain * (1 - private_chain_treasury_extraction_rate) * private_chain_number
    )


    # # Check if the block used too much gas
    # assert (
    #     gas_used <= gas_target * ELASTICITY_MULTIPLIER * constants.slots_per_epoch
    # ), "invalid block: too much gas used"

    return {
        "public_base_fee_to_domain_treasury": public_base_fee_to_domain_treasury * dt,
        "private_base_fee_to_domain_treasury": private_base_fee_to_domain_treasury * dt,
        "total_priority_fee_to_validators": total_priority_fee_to_validators * dt,
        "total_priority_fee_to_validators_usd": total_priority_fee_to_validators * dt * polygn_price / constants.gwei,
        "private_treasury_balance": private_treasury_balance + private_base_fee_to_private_treasury * dt,
    }

# Added
def policy_inflation(params, substep, state_history, previous_state) -> typing.Dict[str, ETH]:
    """
    ## Inflation Policy

    Inflation is allocated to validators post Proof-of-Stake,
    using the `inflationary_rate_per_year` System Parameter.
    """
    
    # Parameters
    dt = params["dt"]
    inflationary_rate_per_year = params["inflationary_rate_per_year"]
    inflation_sqrt_numerator = params["inflation_sqrt_numerator"]
    polygn_staked_process = params["polygn_staked_process"]
    
    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    polygn_supply = previous_state["polygn_supply"]
    liveness_metrics = previous_state["liveness_metrics"]
    staking_metrics = previous_state["staking_metrics"]
    number_of_active_validators = previous_state["number_of_active_validators"]
    polygn_price = previous_state["polygn_price"]
    validator_group_by_event = previous_state["validator_group_by_event"]
    unassigned_rewards_ratio = previous_state["unassigned_rewards_ratio"]
    

    if inflation_sqrt_numerator != 0 and polygn_staked_process(0, 0) is not None:
        polygn_staked = polygn_staked_process(run, timestep * dt)
        inflationary_rate_per_year = (
            inflation_sqrt_numerator
            / (polygn_staked**0.5)
            * constants.gwei
        )
    
    
    total_inflation_to_validators = (
                    polygn_supply * inflationary_rate_per_year / constants.epochs_per_year * dt
        )
    # need to subtrat the part that supposed go the validators who are slashed from a large service
    # but be burned due to slashing
    total_inflation_to_validators = (
        total_inflation_to_validators 
        - polygn_supply * inflationary_rate_per_year / constants.epochs_per_year * unassigned_rewards_ratio
    )
    



    # Only active and unslashed validators can claim
    total_staking = staking_metrics.sum()
    total_staking_normal = (
        np.multiply(staking_metrics, 1-validator_group_by_event)
    )
    total_staking_deviate = (
        np.multiply(staking_metrics,  validator_group_by_event)
    )
    total_inflation_to_validators = (
        total_inflation_to_validators
        * ((liveness_metrics*staking_metrics).sum()/ total_staking)
    )
    total_inflation_to_validators_normal = (
        total_inflation_to_validators
        * ((liveness_metrics*total_staking_normal).sum()/ total_staking)
    )
    total_inflation_to_validators_deviate = (
        total_inflation_to_validators
        * ((liveness_metrics*total_staking_deviate).sum()/ total_staking)
    )

    
    
    return {
        "total_inflation_to_validators": total_inflation_to_validators,
        "total_inflation_to_validators_usd": total_inflation_to_validators * polygn_price /constants.gwei,
        "total_inflation_to_validators_normal": total_inflation_to_validators_normal,
        "total_inflation_to_validators_normal_usd": total_inflation_to_validators_normal * polygn_price /constants.gwei,
        "total_inflation_to_validators_deviate": total_inflation_to_validators_deviate,
        "total_inflation_to_validators_deviate_usd": total_inflation_to_validators_deviate * polygn_price /constants.gwei,
    }

# Edited
def update_polygn_price(
    params, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, USD_per_POLYGN]:
    """
    ## ETH Price State Update Function

    Update the ETH price from the `eth_price_process`.
    """

    # Parameters
    dt = params["dt"]
    polygn_price_process = params["polygn_price_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]

    # Get the Polygn price sample for the current run and timestep
    polygn_price_sample = polygn_price_process(run, timestep * dt)

    return "polygn_price", polygn_price_sample


# Edited
def update_polygn_supply(
    params, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, ETH]:
    """
    ## ETH Supply State Update Function

    Update the ETH supply from the Network Issuance Policy Function.
    """

    # Policy Inputs
    network_issuance = policy_input["network_issuance"]

    # State variables
    polygn_supply = previous_state["polygn_supply"]

    return "polygn_supply", polygn_supply + network_issuance
