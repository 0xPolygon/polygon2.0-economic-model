"""
Constants used in the model e.g. number of epochs in a year, Gwei in 1 Ether
"""

gwei = 1e9
wei = 1e18
slots_per_epoch = 178
epochs_per_day = 225 # 6.4 min an epoch, 40k blocks a day
epochs_per_week = 1575
epochs_per_month = 6750
epochs_per_year = 82180
pow_blocks_per_epoch = 32.0 * 12 / 13
eth_deposited_per_validator = 32

PoS_checkpoint_gas_cost = 210000

txn_per_sec_public = 38
txn_per_sec_private = 19
txn_fee_public = 0.01
txn_fee_private = 0.0005