"""
# Cumulative Yield Analysis
"""

import copy

import model.constants as constants
from model.stochastic_processes import create_stochastic_process_realizations
from model.types import Stage
from experiments.default_experiment import experiment


# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

DELTA_TIME = constants.epochs_per_week  # epochs per timestep
SIMULATION_TIME_DAYS = 10*365  # number of months
TIMESTEPS = constants.epochs_per_day * SIMULATION_TIME_DAYS // DELTA_TIME

# DELTA_TIME = 3
# TIMESTEPS = 10

# Generate stochastic process realizations
## Linear
polygn_price_samples = create_stochastic_process_realizations("convex_polygn_price_samples", timesteps=TIMESTEPS, dt=DELTA_TIME)
#polygn_price_samples = create_stochastic_process_realizations("stochastic_polygn_price_samples", timesteps=TIMESTEPS, dt=DELTA_TIME)

adoption_rates_slow = create_stochastic_process_realizations("adoption_rates", timesteps=TIMESTEPS, dt=DELTA_TIME, final_chains_num=500)
adoption_rates_med = create_stochastic_process_realizations("adoption_rates", timesteps=TIMESTEPS, dt=DELTA_TIME, final_chains_num=2000)
adoption_rates_fast = create_stochastic_process_realizations("adoption_rates", timesteps=TIMESTEPS, dt=DELTA_TIME, final_chains_num=3500)


adoption_rates_public_slow = create_stochastic_process_realizations("adoption_rates", timesteps=TIMESTEPS, dt=DELTA_TIME, final_chains_num=5)
adoption_rates_public_med = create_stochastic_process_realizations("adoption_rates", timesteps=TIMESTEPS, dt=DELTA_TIME, final_chains_num=15)
adoption_rates_public_fast = create_stochastic_process_realizations("adoption_rates", timesteps=TIMESTEPS, dt=DELTA_TIME, final_chains_num=25)

hardware_cost_moores_law = create_stochastic_process_realizations("hardware_costs", timesteps=TIMESTEPS, dt=DELTA_TIME, init_hardware_cost=500)


parameter_overrides = {
    "polygn_price_process": [
        lambda run, timestep: polygn_price_samples[run - 1][timestep],
        #lambda run, timestep: 1,
        ],
    'Adoption_speed_process': [
        lambda run, timestep: adoption_rates_slow[run - 1][timestep],
        lambda run, timestep: adoption_rates_med[run - 1][timestep],
        lambda run, timestep: adoption_rates_fast[run - 1][timestep],
        ],
    "Adoption_speed_public_process": [
        lambda run, timestep: adoption_rates_public_slow[run - 1][timestep],
        lambda run, timestep: adoption_rates_public_med[run - 1][timestep],
        lambda run, timestep: adoption_rates_public_fast[run - 1][timestep],
        ],
    "validator_hardware_costs_per_month_process": [
        lambda run, timestep: hardware_cost_moores_law[run - 1][timestep],
        ],
}

# Override default experiment Simulation and System Parameters related to timing
experiment.simulations[0].timesteps = TIMESTEPS
experiment.simulations[0].model.params.update({"dt": [DELTA_TIME]})

# Override default experiment System Parameters
experiment.simulations[0].model.params.update(parameter_overrides)
