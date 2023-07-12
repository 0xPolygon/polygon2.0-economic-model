"""
# ETH Price Sweep Analysis

Creates a parameter sweep of the ETH price process,
with a static value for ETH staked set to the current ETH staked value from Beaconcha.in.
"""

import numpy as np
import copy

from model.state_variables import polygn_staked
from model.types import Stage
from experiments.default_experiment import experiment, TIMESTEPS, DELTA_TIME
import model.constants as constants


DELTA_TIME = 7*constants.epochs_per_day  # epochs per timestep
SIMULATION_TIME_MONTHS = 12 * 10  # number of months
TIMESTEPS = constants.epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME

# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

# ETH price range from 100 USD/ETH to the maximum over the last 12 months
polygn_price_samples = np.linspace(start=0.5, stop=10, num=50)

PoS_checkpoint_gas_cost = constants.PoS_checkpoint_gas_cost
parameter_overrides = {
    "polygn_price_process": [
        lambda run, _timestep: polygn_price_samples[run - 1]
    ],
    "polygn_staked_process": [
        lambda _run, _timestep: polygn_staked,
    ],
    "Adoption_speed": [0],
    "checkpoint_gas_cost": [0.1 * PoS_checkpoint_gas_cost]
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Set runs to number of combinations in sweep
experiment.simulations[0].runs = len(polygn_price_samples)
# Run single timestep, set unit of time to multiple epochs
experiment.simulations[0].timesteps = 1
experiment.simulations[0].model.params.update({"dt": [ TIMESTEPS * DELTA_TIME]})
