"""
Definition of State Variables, their types, and default values.

By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""


import numpy as np
from dataclasses import dataclass
from datetime import datetime

import model.constants as constants
import data.api.etherscan as etherscan
import data.api.validator_staking_selenium as validator_staking_selenium
import model.system_parameters as system_parameters
from model.system_parameters import validator_environments
from model.types import (
    Gwei,
    Gwei_per_Gas,
    ETH,
    POLYGN,
    USD,
    USD_per_POLYGN,
    Percentage,
    Stage,
    List,
)
from data.historical_values import eth_price_mean, eth_price_min, eth_price_max

from spec_typing import *
from constants import *
from experiments.notebooks.Hub_centralised.model.specs.szz_typing import (
    Container, 
    boolean, 
    Bytes4, Bytes8, Bytes32, Bytes48, Bytes96, 
    Vector, Bitlist, Bitvector, List, 
    uint64,
    )
import secrets
from specs import (
    Validator, SystemMetrics, Chain
)





@dataclass
class HubState(Container):
    """State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value
    """

    # Network state variables
    public_chain_cnt: int = 5
    private_chain_cnt: int = 10
    # Time state variables
    stage: Stage = None
    timestamp: datetime = None # `datetime` object, starting from `date_start` Parameter.
    # POLYGN state variables
    polygn_price: USD_per_POLYGN = 1.0
    eth_price: USD_per_POLYGN = 1500.0
    polygn_supply: POLYGN = 10e9
    # Inflation
    supply_inflation: Percentage = 0
    network_issuance: POLYGN = 0


    # Slashings
    slashings: Vector[Gwei, EPOCHS_PER_SLASHINGS_VECTOR]  # Per-epoch sums of slashed effective balances

    # EIP-1559 state variables
    base_fee_per_gas_supernet: Gwei_per_Gas = 5

    # Registry
    validators: List[Validator, VALIDATOR_REGISTRY_LIMIT]
    balances: List[Gwei, VALIDATOR_REGISTRY_LIMIT]

    # System metric state variables
    system_metrics: SystemMetrics

    # Asynchronous model
    liveness_metrics: np.ndarray = np.reshape(
        np.random.binomial(
            100, 
            0.95, 
            number_of_active_validators * (PUBLIC_CHAINS_CNT + PRIVATE_CHAINS_CNT))
            /100,
        ((PUBLIC_CHAINS_CNT + PRIVATE_CHAINS_CNT), number_of_active_validators)
        )
    """
    Numeric matrix of liveness in [Chains, Validators]
    Default set by every validators are alive
    """

    # Chains
    chains: List[Chain, MAX_PRIVATE_CHAINS]  


