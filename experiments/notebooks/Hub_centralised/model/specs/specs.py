from spec_typing import *
from constants import *
from experiments.notebooks.Hub_centralised.model.specs.szz_typing import (
    Container, 
    boolean, 
    Bytes4, Bytes8, Bytes32, Bytes48, Bytes96, 
    Vector, Bitlist, Bitvector, List, 
    uint64,
    )


class DepositData(Container):
    pubkey: BLSPubkey
    withdrawal_credentials: Bytes32
    amount: Gwei
    signature: BLSSignature  # signing over DepositMessage


class Deposit(Container):
    data: DepositData

class Checkpoint(Container):
    root_epoch: Epoch

class ChainStake(Container):
    chain_type: ChainType
    chain_index: ChainIndex
    stake_amount: DepositData
    # stake_epoch: Epoch # When validator starts validate on Hub
    # withdraw_epoch: Epoch # When validator exit the chain om Hub
    # withdrawable_epoch: Epoch  # When validator can withdraw funds
    # slashed: boolean

class Attestation(Container):
    # Vote
    yes: List[ValidatorIndex, MAX_VALIDATOR_COUNT]
    no: List[ValidatorIndex, MAX_VALIDATOR_COUNT]


class Liveness(Container):
    inactive_index: List[ValidatorIndex, MAX_VALIDATOR_COUNT]

class Proposer(Container):
    proposer_index: ValidatorIndex

class ChainBlockBody(Container):
    # Stake
    stake: List[ChainStake, MAX_VALIDATOR_COUNT]
    block: Block # block number within a checkpoint
    # Operations
    attestations: List[Attestation, MAX_BLOCK_PER_CHECKPOINT]
    liveness: List[Liveness, MAX_BLOCK_PER_CHECKPOINT]
    proposer: List[Proposer, MAX_BLOCK_PER_CHECKPOINT]
    deposits: List[Deposit, MAX_DEPOSITS]
    # TODO: Add more operations
    # voluntary_exits: List[SignedVoluntaryExit, MAX_VOLUNTARY_EXITS]

class Chain(Container):
    chain_type: ChainType
    chain_index: ChainIndex
    previous_checkpoint: Checkpoint
    checkpoint_cadence: Epoch # Epochs between checkpoints
    blocktime: Block # slot number per checkpoint
    stake: List[ChainStake, MAX_VALIDATOR_COUNT]
    # EIP-1559
    base_fee_per_gas: Gwei
    priority_fee_per_gas: Gwei
    # Pending Blocks
    pending_blocks: List[ChainBlockBody, MAX_BLOCK_PER_CHECKPOINT]
    # Pending Rewards
    pending_base_rewards: List[Gwei, MAX_BLOCK_PER_CHECKPOINT]
    pending_priority_rewards: List[Gwei, MAX_BLOCK_PER_CHECKPOINT]


class Validator(Container):
    pubkey: BLSPubkey
    withdrawal_credentials: Bytes32  # Commitment to pubkey for withdrawals
    effective_balance: Gwei  # Balance at stake
    # Status epochs
    activation_eligibility_epoch: Epoch  # When criteria for activation were met
    activation_epoch: Epoch
    exit_epoch: Epoch
    # Hub Staked
    total_staked: Deposit
    # Chain Staked
    private_chains: List[ChainStake, MAX_PRIVATE_CHAINS]
    public_chains: List[ChainStake, MAX_PUBLIC_CHAINS]
    # Revenue and Cost
    revenue: Gwei
    hardware_cost: USD

class SystemMetrics(Container):
    # System Metrics in USD/Gwei
    total_inflation_rewards: Gwei = 0
    total_txn_rewards: Gwei = 0
    total_revenue: USD = 0
    total_hardware_cost: USD = 0
    total_checkpoint_cost: USD = 0
    total_staked: Gwei = 0
    total_profit: USD = 0
    # System Metrics in Percentage
    total_profit_yield_annual: Percentage = 0.0
    total_revenue_yield_annual: Percentage = 0.0
    total_checkpoint_cost_yield_annual: Percentage = 0.0
    total_inflation_yield_annual: Percentage = 0.0
    total_txn_yield_annual: Percentage = 0.0
    # Treasury
    domain_treasury_balance: Gwei = 0 * gwei



