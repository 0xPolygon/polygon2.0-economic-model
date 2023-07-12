"""
Simulation configuration such as the number of timesteps and Monte Carlo runs
"""

from model.constants import epochs_per_month, epochs_per_day
import numpy as np


DELTA_TIME = epochs_per_day  # epochs per timestep
SIMULATION_TIME_MONTHS = 12  # number of months
TIMESTEPS = (
    epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME
)  # number of simulation timesteps
MONTE_CARLO_RUNS = 1  # number of runs


# event-based randomization seeds
def p_service(chain_cnt):
    return np.random.uniform(0, 1, size=chain_cnt)


def n_user(validator_cnt):
    return np.clip(np.random.normal(90,30, size = validator_cnt), 30, 100)

