"""
# Cumulative Yield Analysis
"""

import numpy as np
import copy

import model.constants as constants
from model.state_variables import polygn_staked, polygn_supply, eth_price_max
from experiments.default_experiment import experiment
from model.stochastic_processes import create_stochastic_process_realizations


DELTA_TIME = 7*constants.epochs_per_day  # epochs per timestep
SIMULATION_TIME_MONTHS = 12 * 10  # number of months
TIMESTEPS = constants.epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME
# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

polygn_staked_samples = np.linspace(
    polygn_supply * 0.1,
    #polygn_staked,
    polygn_supply * 0.5,  # 50% of current total POLYGN supply
    50
)
PoS_checkpoint_gas_cost = constants.PoS_checkpoint_gas_cost
parameter_overrides = {
    "polygn_staked_process": [
        lambda run, _timestep: polygn_staked_samples[run - 1],
    ],
    "inflation_sqrt_numerator": [
        # A sweep of two fixed POLYGN price points and one stochastic POLYGN price
        0.03 * (3.3e9**0.5) / 3.3,
        0,
    ],
    "Adoption_speed": [0],
    "checkpoint_gas_cost": [0.1 * PoS_checkpoint_gas_cost]
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Set runs to number of items in eth_staked_samples
experiment.simulations[0].runs = len(polygn_staked_samples)
# Run single timestep, set unit of time to multiple epochs
experiment.simulations[0].timesteps = 1
experiment.simulations[0].model.params.update({"dt": [ TIMESTEPS* DELTA_TIME ]})
