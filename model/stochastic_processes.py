"""
Helper functions to generate stochastic environmental processes
"""

import numpy as np
from stochastic import processes
import math

import model.constants as constants

import experiments.simulation_configuration as simulation
from experiments.utils import rng_generator


def create_convex_polygn_price_process(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    rng=np.random.default_rng(10),
    minimum_polygn_price=1,
):
    maximum_polygn_price = 10
    #linear
    samples = [minimum_polygn_price + (10-minimum_polygn_price)*i/(timesteps * dt + 2) for i in range((timesteps * dt + 2))]
    # qudratic convex
    t = timesteps*dt
    para = (maximum_polygn_price-minimum_polygn_price)/((t+1)**2)
    samples = [para * (i**2)+minimum_polygn_price for i in range(t+2)]
    # Ensure that the average token price is set at $5
    curr_average = sum(samples)/len(samples)-minimum_polygn_price
    target_avg = 5
    samples = [(sample-minimum_polygn_price) / curr_average * (target_avg -minimum_polygn_price)+ minimum_polygn_price for sample in samples] 
    return samples

def create_stochastic_polygn_price_process(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    rng=np.random.default_rng(1),
    minimum_polygn_price=1,
):
    """Configure environmental POLYGN price process

    > A Brownian excursion is a Brownian bridge from (0, 0) to (t, 0) which is conditioned to be non-negative on the interval [0, t].

    See https://stochastic.readthedocs.io/en/latest/continuous.html
    """
    maximum_polygn_price = 10
    # Brownian Motion
    process = processes.continuous.BrownianExcursion(t=(timesteps * dt), rng=rng)
    #process = processes.continuous.BrownianMotion(t=(timesteps * dt), rng=rng)
    samples = process.sample(timesteps * dt + 1)
    maximum_polygn_price_in_samples = max(samples)
    samples = [
        polygn_price_sample / maximum_polygn_price_in_samples * maximum_polygn_price
        for polygn_price_sample in samples
    ]
    # convex curve
    t = timesteps*dt
    para = (maximum_polygn_price-minimum_polygn_price)/((t+1)**2)
    samples_convex = [para * (i**2)+minimum_polygn_price for i in range(t+2)]
    # two samples addition
    samples = [i+j for i,j in zip(samples_convex, samples)]
    # Ensure that the average token price is set at $5
    curr_average = sum(samples)/len(samples)-minimum_polygn_price
    target_avg = 5
    samples = [(sample-minimum_polygn_price) / curr_average * (target_avg -minimum_polygn_price)+ minimum_polygn_price for sample in samples]
    return samples


def create_exp_adoption_rate(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    rng=np.random.default_rng(1),
    final_chains_num=1000,
):
    t = timesteps*dt
    para = (final_chains_num-2)/(t**2)
    rates = [int(para * (dt*i)**2) for i in range(timesteps+1)]
    rates = [j-i for i, j in zip(rates[:-1], rates[1:])]
    rates = [rate for rate in rates for _ in range(dt)]
    return rates


def create_moore_s_law_hardware_cost(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    rng=np.random.default_rng(1),
    init_hardware_cost=500,
):
    ## Moore's Law
    # transit dt to real year
    t = timesteps*dt
    final_year = t/constants.epochs_per_year
    # Moore's Law
    moore_low_year_half_period = 3
    hardware_cost = [init_hardware_cost/(2**(i/t*final_year/moore_low_year_half_period)) for i in range(t)]
    return hardware_cost


def create_validator_process(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    rng=np.random.default_rng(1),
    validator_adoption_rate=4,
):
    """Configure environmental validator staking process

    > A Poisson process with rate lambda is a count of occurrences of i.i.d. exponential random variables with mean 1/lambda. This class generates samples of times for which cumulative exponential random variables occur.

    See https://stochastic.readthedocs.io/en/latest/continuous.html
    """
    process = processes.continuous.PoissonProcess(
        rate=1 / validator_adoption_rate, rng=rng
    )
    samples = process.sample(timesteps * dt + 1)
    samples = np.diff(samples)
    samples = [int(sample) for sample in samples]
    return samples


def create_stochastic_process_realizations(
    process,
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    runs=5,
    final_chains_num=1000,
    init_hardware_cost = 500,
):
    """Create stochastic process realizations

    Using the stochastic processes defined in `processes` module, create random number generator (RNG) seeds,
    and use RNG to pre-generate samples for number of simulation timesteps.
    """

    switcher = {
        "convex_polygn_price_samples": [
            create_convex_polygn_price_process(timesteps=timesteps, dt=dt, rng=rng_generator())
            for _ in range(runs)
        ],
        "stochastic_polygn_price_samples": [
            create_stochastic_polygn_price_process(timesteps=timesteps, dt=dt, rng=rng_generator())
            for _ in range(runs)
        ],
        "adoption_rates": [
            create_exp_adoption_rate(timesteps=timesteps, dt=dt, rng=rng_generator(), final_chains_num=final_chains_num)
            for _ in range(runs)
        ],
        "validator_samples": [
            create_validator_process(timesteps=timesteps, dt=dt, rng=rng_generator())
            for _ in range(runs)
        ],
        "validator_uptime_samples": [
            rng_generator().uniform(0.96, 0.99, timesteps * dt + 1) for _ in range(runs)
        ],
        "hardware_costs": [
            create_moore_s_law_hardware_cost(timesteps=timesteps, dt=dt, rng=rng_generator(), init_hardware_cost=init_hardware_cost)
            for _ in range(runs)
        ],
    }

    return switcher.get(process, "Invalid Process")




def create_intial_state_risk_service_validator(public_chain_cnt,private_chain_cnt, validator_cnt):
    chain_cnt = public_chain_cnt + private_chain_cnt
    p = simulation.p_service(chain_cnt)
    for i in range(public_chain_cnt):
        p[i]=1 # 100% of validators would stake on public chains
    for i in range(private_chain_cnt):
        p[public_chain_cnt+i]=0.15 # 15% of validators would stake on public chains

    ## Randomize staking metrics for restaking (MultiStaking) mode
    # Initialize an empty matrix
    matrix_restaking = np.zeros((chain_cnt, validator_cnt))
    
    # Fill the matrix with Bernoulli trials
    for i in range(chain_cnt):
        n = simulation.n_user(validator_cnt)
        for j in range(validator_cnt):
            matrix_restaking[i][j] = np.random.binomial(1, p[i]) * n[j]    
    # Ensure at least 10% of entries in each row are non-zero
    for i in range(chain_cnt):
        non_zero_cnt = 6  # each service should have at least 6 validators
        zero_indices = np.where(matrix_restaking[i] != 0)[0]  # indices where the row is zero
        if len(zero_indices) < non_zero_cnt:
            #non_zero_cnt = len(zero_indices)  # adjust if there are fewer than 10% zeros
            matrix_restaking[i] = 0
            non_zero_indices = np.random.choice(list(range(len(matrix_restaking[i]))), non_zero_cnt, replace=False)  # random select zero indices
            n = simulation.n_user(non_zero_cnt)
            matrix_restaking[i][non_zero_indices] = n  # replace selected zeros with non-zero values
    ## Randomize staking metrics for liquidity fragmentation (SingleStaking) mode
    # Initialize an empty matrix
    sum_per_node = matrix_restaking.sum(axis=0)
    # print(matrix_restaking)
    # print(matrix_restaking)
    # print(sum_per_node)
    # print(np.any(sum_per_node == 0))  # Check for zeros
    # print(np.any(np.isnan(sum_per_node)))  # Check for NaNs
    matrix_liquidity_fragmentation = matrix_restaking / sum_per_node[np.newaxis, :]
    return p, matrix_restaking/100, matrix_liquidity_fragmentation

