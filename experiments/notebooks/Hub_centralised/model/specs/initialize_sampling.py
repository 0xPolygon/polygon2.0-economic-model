import secrets
from typing import Set, Optional, Sequence, Tuple
from experiments.notebooks.Hub_centralised.model.specs.szz_typing import (
    Container, boolean, Bytes4, Bytes8, Bytes32, Bytes48, Bytes96, Vector, Bitlist, Bitvector, List, uint64
)
from spec_typing import *
from constants import *

from state_variables import (
    HubState, ChainsState,
)
from specs import (
    Deposit, DepositData, Liveness, Chain,

)
from blockchain import (
    eth_to_gwei,
    process_deposit,
)
from model.system_parameters import parameters


def aggregate_pubkeys(pubkeys) -> BLSPubkey:
    return secrets.token_bytes(48)


# Create an array of `Deposit` objects
def get_initial_deposits(n):
    return [Deposit(
        data=DepositData(
            amount=eth_to_gwei(3e7),
            pubkey=secrets.token_bytes(48))
    ) for i in range(n)]


def initialize_hub_state(deposits: Sequence[Deposit]) -> HubState:
    state = HubState().__dict__

    # Process deposits
    for deposit in deposits:
        process_deposit(state, deposit)
    
    return state


def random_checkpoint_cadence() -> Epoch:
    return secrets.choice(CHECKPOINT_CADENCE)


def random_blocktime() -> Epoch:
    return secrets.choice(BLOCKTIME)


def initial_chain(chain_type: ChainType, chain_index: ChainIndex) -> Chain:
    chain = Chain(
        chain_type=chain_type,
        chain_index=chain_index,
        stake = [],
        pending_blocks = [],
        pending_base_rewards = [],
        pending_priority_rewards = []
    )

    chain.checkpoint_cadence = random_checkpoint_cadence()
    chain.blocktime = random_blocktime()

    return chain


def initialize_chains_state(state: HubState) -> HubState:
    # Initialize chains
    chains = []
    public_chains = state.public_chain_cnt
    private_chains = state.private_chain_cnt
    chain_types = {'public': public_chains, 'private': private_chains}
    for chain_type, chain_indices in chain_types.items():
        for chain_index in range(chain_indices):
            chain = initial_chain(chain_type, chain_index)
            chains.append(chain)

    state.chains = chains

    return state


def update_chain_liveness(state: HubState)->Liveness:
    