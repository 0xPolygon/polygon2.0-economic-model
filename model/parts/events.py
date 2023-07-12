"""
# Events

"""

import typing

import model.constants as constants
import numpy as np
from model.types import Stage
from datetime import datetime
import random

def event_slashing_on_large_service(
    params, substep, state_history, previous_state
) -> typing.Dict[str, any]:
    # Parameters
    dt = params["dt"]
    date_slashing = params["date_slashing"]
    slashing_fraction = params["slashing_fraction"]
    # State Variables
    current_stage = previous_state["stage"]
    timestamp = previous_state["timestamp"]
    staking_metrics = previous_state["staking_metrics"]
    polygn_staked_per_validator = previous_state["polygn_staked_per_validator"]

    # mark the validators who got slashed
    slashed_chain_id = random.choice([0,1,2])
    #slashed_chain_id = 2 # The slashed chain has 70% validators
    validator_group_by_event = np.where(staking_metrics[slashed_chain_id]!=0, 1, 0)
    unassigned_rewards_ratio = 0

    # Stage finite-state machine
    if current_stage == Stage.ALL.value:
        # If Stage ALL selected, transition through all stages
        # at different timestamps
        
        if (
            timestamp > date_slashing
        ):
            current_stage = Stage.SLASHING_on_LARGE_SERVICE
            # On this moment, attack happens and large service (Public Chain 0) slashing initiated
            staking_metrics = staking_metrics.astype(float)
            
            slashing_amount = staking_metrics[slashed_chain_id] * slashing_fraction
            unassigned_rewards_ratio = np.sum(slashing_amount)/np.sum(staking_metrics)     
            staking_metrics[slashed_chain_id] = staking_metrics[slashed_chain_id] - slashing_amount
            # Iterate over each chain (row in original_stakes)
            for i in range(staking_metrics.shape[1]):
                # Iterate over each node (column in original_stakes)
                # Calculate the remaining stake after slashing
                polygn_staked_per_validator[i] = max(polygn_staked_per_validator[i] - slashing_amount[i],0)
                for j in range(staking_metrics.shape[0]):            
                    # If the total stake of a node is smaller than the original stake of the node on a specific chain
                    staking_metrics[j, i] = min(staking_metrics[j, i], polygn_staked_per_validator[i])

              

    return {
        "stage": current_stage,
        "staking_metrics": staking_metrics,
        "polygn_staked_per_validator": polygn_staked_per_validator,
        "polygn_staked": polygn_staked_per_validator.sum(),
        "validator_group_by_event": validator_group_by_event,
        "unassigned_rewards_ratio": unassigned_rewards_ratio,
    }