"""
# Staking and Messaing

"""

import typing

import model.constants as constants
import numpy as np

def policy_signature_check(
    params, substep, state_history, previous_state
) -> typing.Dict[str, any]:
    """
    ## Check liveness and send liveness metrics from chains to Hub
    """
    # Parameters
    dt = params["dt"]
    staking_mode = params["staking_mode"]

    # State Variables
    # run = previous_state["run"]
    # timestep = previous_state["timestep"]
    number_of_validators = previous_state["number_of_active_validators"]
    liveness_metrics = previous_state["liveness_metrics"]
    PRIVATE_CHAINS_CNT = previous_state["PRIVATE_CHAINS_CNT"]
    PUBLIC_CHAINS_CNT = previous_state["PUBLIC_CHAINS_CNT"]

    CHAINS_CNT = PRIVATE_CHAINS_CNT + PUBLIC_CHAINS_CNT
    # random generate liveness
    liveness_metrics = np.reshape(liveness_metrics, (-1,number_of_validators * CHAINS_CNT))
    # liveness_metrics = (liveness_metrics + np.random.binomial(dt, 0.95, number_of_validators * CHAINS_CNT)/dt)/2
    liveness_metrics = np.random.binomial(dt, 0.95, number_of_validators * CHAINS_CNT)/dt
    liveness_metrics = np.reshape(liveness_metrics, (CHAINS_CNT, number_of_validators))

    return {
        "liveness_metrics": liveness_metrics,
    }

def policy_staking_multistaking_sampling(
    params, substep, state_history, previous_state
) -> typing.Dict[str, any]:
    # Parameters
    dt = params["dt"]
    staking_mode = params["staking_mode"]
    polygn_staked_process = params["polygn_staked_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    polygn_staked_per_validator = previous_state["polygn_staked_per_validator"]
    staking_metrics = previous_state["staking_metrics"]
    number_of_active_validators = previous_state["number_of_active_validators"]

    if polygn_staked_process(0, 0) is not None:
        polygn_staked = polygn_staked_process(run, timestep * dt)
        polygn_staked_per_validator *= polygn_staked

    
    if staking_mode == "MultiStaking":
        staking_metrics = [[ np.random.normal(i,scale=1_000_000) for i in chain]  for chain in staking_metrics]
        cutoff = lambda s,m: min(max(0,s),m)
        staking_metrics = np.array([
            [
                cutoff(chain[i], polygn_staked_per_validator[i])
                for i in range(number_of_active_validators)
            ] for chain in staking_metrics      
        ])
    
    staking_metrics = np.where(staking_metrics<180000,0,staking_metrics)

    return {
        "staking_metrics": staking_metrics,
    }