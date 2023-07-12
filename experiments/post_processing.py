import pandas as pd
from radcad.core import generate_parameter_sweep

import model.constants as constants
from model.system_parameters import parameters, Parameters, validator_environments
from model.types import List


def assign_parameters(df: pd.DataFrame, parameters: Parameters, set_params=[]):
    if set_params:
        parameter_sweep = generate_parameter_sweep(parameters)
        parameter_sweep = [{param: subset[param] for param in set_params} for subset in parameter_sweep]

        for subset_index in df['subset'].unique():
            for (key, value) in parameter_sweep[subset_index].items():
                df.loc[df.eval(f'subset == {subset_index}'), key] = value

    return df


def post_process(df: pd.DataFrame, drop_timestep_zero=True, parameters=parameters):
    # Assign parameters to DataFrame
    assign_parameters(df, parameters, [
        # Parameters to assign to DataFrame
        'dt'
    ])

    # Dissagregate validator count
    df[[validator.type + '_validator_count' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_count_distribution), axis=1, result_type='expand').astype('float32')

    # Dissagregate validator costs
    # df[[validator.type + '_cloud_costs' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_cloud_costs), axis=1, result_type='expand').astype('float32')
    # df[[validator.type + '_third_party_costs' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_third_party_costs), axis=1, result_type='expand').astype('float32')

    # # Dissagregate individual validator costs
    # _mapping = dict(zip(
    #     [validator.type + '_validator_count' for validator in validator_environments]
    # ))

    # df[['individual_validator_' + validator.type + '_costs' for validator in validator_environments]] = \
    #     df[[validator.type + '_costs' for validator in validator_environments]].rename(columns=_mapping) / \
    #     df[[validator.type + '_validator_count' for validator in validator_environments]]

    # Dissagregate revenue and profit
    df[[validator.type + '_revenue' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_revenue), axis=1, result_type='expand').astype('float32')
    df[[validator.type + '_profit' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_profit), axis=1, result_type='expand').astype('float32')

    # Dissagregate yields
    df[[validator.type + '_revenue_yields' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_revenue_yields), axis=1, result_type='expand').astype('float32')
    df[[validator.type + '_profit_yields' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_profit_yields), axis=1, result_type='expand').astype('float32')

    # Convert decimals to percentages
    df[[validator.type + '_revenue_yields_pct' for validator in validator_environments]] = df[[validator.type + '_revenue_yields' for validator in validator_environments]] * 100
    df[[validator.type + '_profit_yields_pct' for validator in validator_environments]] = df[[validator.type + '_profit_yields' for validator in validator_environments]] * 100
    df['supply_inflation_pct'] = df['supply_inflation'] * 100
    df['total_revenue_yields_pct'] = df['total_revenue_yields'] * 100
    df['total_profit_yields_pct'] = df['total_profit_yields'] * 100
    df['validator_checkpoint_costs_yields_pct'] = df['validator_checkpoint_costs_yields'] * 100
    df['validator_hardware_costs_yields_pct'] = df['validator_hardware_costs_yields'] * 100
    df['total_txn_fee_to_validators_yields_pct'] = df['total_txn_fee_to_validators_yields'] * 100
    df['total_inflation_to_validators_yields_pct'] = df['total_inflation_to_validators_yields'] * 100


    # Calculate revenue-profit yield spread
    df['revenue_profit_yield_spread_pct'] = df['total_revenue_yields_pct'] - df['total_profit_yields_pct']

    # Convert validator rewards from Gwei to ETH
    validator_rewards = [
        # 'validating_rewards',
        # 'validating_penalties',
        'total_online_validator_rewards',
        'total_txn_fee_to_validators',
        'total_inflation_to_validators',
        # 'source_reward',
        # 'target_reward',
        # 'head_reward',
        # 'block_proposer_reward',
        # 'sync_reward',
        # 'whistleblower_rewards'
    ]
    df[[reward + '_polygn' for reward in validator_rewards]] = df[validator_rewards] / constants.gwei

    # Convert validator penalties from Gwei to POLYGN
    validator_penalties = ['amount_slashed']
    df[[penalty + '_polygn' for penalty in validator_penalties]] = df[validator_penalties] / constants.gwei

    # Calculate cumulative revenue and profit yields
    df["daily_revenue_yields_pct"] = df["total_revenue_yields_pct"] / (constants.epochs_per_year / df['dt'])
    df["cumulative_revenue_yields_pct"] = df.groupby('subset')["daily_revenue_yields_pct"].transform('cumsum')
    df["daily_profit_yields_pct"] = df["total_profit_yields_pct"] / (constants.epochs_per_year / df['dt'])
    df["cumulative_profit_yields_pct"] = df.groupby('subset')["daily_profit_yields_pct"].transform('cumsum')

    # Calculate cumulative treasury balance
    df["cumulative_treasury_balance_usd"] = df.groupby('subset')["total_inflation_to_validators_usd"].transform('cumsum')
    # Calculate the total annaul treasury inflow by years
    earliest_date = df['timestamp'].min()
    df['year'] = (df['timestamp'] - earliest_date).dt.days // 365
    df['annual_treasury_inflow'] = df.groupby(['subset', 'year'])['total_inflation_to_validators_usd'].transform('sum')


    # Convert treasury balance from Gwei to POLYGN
    df[['total_domain_treasury_balance']] = df[['domain_treasury_balance_locked']] / constants.gwei

    # Drop the initial state for plotting
    if drop_timestep_zero:
        df = df.drop(df.query('timestep == 0').index)

    return df


def aggregate_df_in_multi_sims(dfs: List[pd.DataFrame]):
    # get the average number for each subset across all df
    agg_dfs = {}
    for subset in dfs[0].subset.unique():
        agg_df_list = []
        for df in dfs:
            df_subset = df.query(f"subset == {subset}").copy()
            #df_subset['data'] = pd.to_numeric(df_subset['data']) # Convert 'data' column to numeric
            agg_df_list.append(df_subset)
        agg_df = pd.concat(agg_df_list) # Using pd.concat instead of df.append
        agg_df = agg_df.groupby('timestamp').mean(numeric_only=True).reset_index() # Specify numeric_only=False
        agg_dfs[subset] = agg_df
    return agg_dfs
