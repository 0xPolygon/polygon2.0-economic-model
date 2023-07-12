import requests
import pandas as pd
import numpy as np


def get_validator_info():
    response = requests.get('https://staking-api.polygon.technology/api/v2/validators?limit=150&offset=0')
    data = response.json()
    data = data['result']
    # Assume the data is a list of dictionaries where each dictionary is a row
    df = pd.DataFrame(data)
    validator_name = df['name'].tolist()
    stake_amount = df['totalStaked'].tolist()
    commission_rate = df['commissionPercent'].tolist()
    checkpoints_signed = df['performanceIndex'].tolist()
    return validator_name, stake_amount, commission_rate, checkpoints_signed


def get_validator_staking_values(default=np.repeat(30_000_000, 100)):
    validator_name, stake_amount, _, _ = get_validator_info()
    if len(stake_amount) > 0:
        return np.array(stake_amount)
    else:
        return default


def get_validator_staking_total_value(default=3_000_000_000):
    total_stake = sum(get_validator_staking_values())/1e18
    return total_stake

def force_staking_ratio(polygn_staked_per_validator, total_supply = 10_000_000_000, staking_ratio = 0.3):
    total_stake = sum(polygn_staked_per_validator)
    polygn_staked_per_validator = polygn_staked_per_validator * staking_ratio / (total_stake/total_supply)
    return polygn_staked_per_validator, staking_ratio*total_supply

