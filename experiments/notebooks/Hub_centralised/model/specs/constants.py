"""
Constants used in the model e.g. number of epochs in a year, Gwei in 1 Ether
"""
from ssz_typing import Bytes1, Bytes4
from spec_typing import (Gwei, Epoch, Slot, DomainType)

gwei = 1e9
wei = 1e18
slots_per_epoch = 178
epochs_per_day = 225 # 6.4 min an epoch, 40k blocks a day
epochs_per_month = 6750
epochs_per_year = 82180
pow_blocks_per_epoch = 32.0 * 12 / 13
eth_deposited_per_validator = 32

PoS_checkpoint_gas_cost = 210000

FAR_FUTURE_EPOCH = Epoch(2**64 - 1)
EFFECTIVE_BALANCE_INCREMENT	= Gwei(2**0 * 10**9)
MAX_EFFECTIVE_BALANCE = Gwei(3e9 * 10**9)

EPOCHS_PER_SLASHINGS_VECTOR = 2**13
MAX_BLOCK_PER_CHECKPOINT = 2**14
MAX_DEPOSITS = 1e2

MAX_PRIVATE_CHAINS = 2**15
MAX_PUBLIC_CHAINS = 2**4
MAX_VALIDATOR_COUNT = 1e2
VALIDATOR_REGISTRY_LIMIT = 1e2

CHECKPOINT_CADENCE = [1,1,2,2,2**2,2**4,2**6,2**8]
BLOCKTIME = [20,100,500,1000]
