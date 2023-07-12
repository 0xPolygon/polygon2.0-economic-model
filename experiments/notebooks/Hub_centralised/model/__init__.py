"""
CADLabs Ethereum Economic Model
"""
__version__ = "1.1.7"

from radcad import Model

from model.system_parameters import parameters
from model.state_update_blocks import state_update_blocks
from model.specs.initialize_sampling import (
    initialize_hub_state, get_initial_deposits,
)


# initialise state variables
genesis_hub_state = initialize_hub_state(get_initial_deposits(100))


initial_conditions = {
    'hub_state': genesis_hub_state,
}


# Instantiate a new Model
model = Model(
    params=parameters,
    initial_state=initial_conditions,
    state_update_blocks=state_update_blocks,
)
