"""
# Cumulative Yield Analysis
"""

import copy

import model.constants as constants
from model.stochastic_processes import create_stochastic_process_realizations
from model.types import Stage, Run_num
from experiments.default_experiment import experiment, simulation


# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)
simulation_replicate = Run_num.LARGE.value

DELTA_TIME = constants.epochs_per_day  # epochs per timestep
SIMULATION_TIME_MONTHS = 4  # number of months
TIMESTEPS = constants.epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME

# Generate stochastic process realizations
polygn_price_samples = create_stochastic_process_realizations("polygn_price_samples", timesteps=TIMESTEPS, dt=DELTA_TIME)

PoS_checkpoint_gas_cost = constants.PoS_checkpoint_gas_cost
parameter_overrides = {
    # "polygn_price_process": [lambda run, timestep: polygn_price_samples[run - 1][timestep]],
    "Adoption_speed": [5],
    "checkpoint_gas_cost": [PoS_checkpoint_gas_cost]
}

# Override default experiment Simulation and System Parameters related to timing
for i in range(simulation_replicate):
    experiment.add_simulations(simulation)
    experiment.simulations[i].timesteps = TIMESTEPS
    experiment.simulations[i].model.params.update({"dt": [DELTA_TIME]})
    experiment.simulations[i].model.params.update({"run_idx": [i+1]})

    # Override default experiment System Parameters
    experiment.simulations[i].model.params.update(parameter_overrides)
