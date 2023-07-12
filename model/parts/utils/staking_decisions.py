import numpy as np

from model.types import (
    ValidatorEnvironment,
)

validator_env = ValidatorEnvironment()
hardware_costs_per_month = validator_env.hardware_costs_per_month

def policy_decide_min_stake(
    polygn_staked, 
):
    