from specs import (
    Deposit, Validator,
)
from state_variables import (
    HubState,
)
from spec_typing import ValidatorIndex
from constants import *

def eth_to_gwei(eth):
    return eth * (10 ** 9)

def increase_balance(state: HubState, index: ValidatorIndex, delta: Gwei) -> None:
    """
    Increase the validator balance at index ``index`` by ``delta``.
    """
    state.balances[index] += delta

def process_deposit(state: HubState, deposit: Deposit) -> None:
    pubkey = deposit.data.pubkey
    amount = deposit.data.amount
    validator_pubkeys = [v.pubkey for v in state.validators]
    if pubkey not in validator_pubkeys:
        # Add validator and balance entries
        state.validators.append(Validator(
            pubkey=pubkey,
            withdrawal_credentials=deposit.data.withdrawal_credentials,
            effective_balance=min(amount - amount % EFFECTIVE_BALANCE_INCREMENT, MAX_EFFECTIVE_BALANCE),
            activation_eligibility_epoch=FAR_FUTURE_EPOCH,
            activation_epoch=FAR_FUTURE_EPOCH,
            exit_epoch=FAR_FUTURE_EPOCH, 
        ))
        state.balances.append(amount)
    else:
        # Increase balance by deposit amount
        index = ValidatorIndex(validator_pubkeys.index(pubkey))
        increase_balance(state, index, amount)

