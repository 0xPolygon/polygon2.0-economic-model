import itertools
import math
from datetime import datetime
import os 

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from ipywidgets import widgets
from plotly.subplots import make_subplots
from plotly.colors import n_colors

from experiments.notebooks.visualizations.plotly_theme import (
    cadlabs_colors,
    cadlabs_colorway_sequence,
)
from model.system_parameters import parameters, validator_environments
import model.constants as constants
from . import multi_sim

# Create a folder for storing experiment results
output_folder = '../../outputs'
output_images_folder = os.path.join(output_folder, 'jpegs')
output_htmls_folder = os.path.join(output_folder, 'htmls')

os.makedirs(output_images_folder, exist_ok=True)
os.makedirs(output_htmls_folder, exist_ok=True)

# Set plotly as the default plotting backend for pandas
pd.options.plotting.backend = "plotly"

validator_environment_name_mapping = {
    "custom": "Custom",
    "diy_hardware": "DIY Hardware",
    "diy_cloud": "DIY Cloud",
    "pool_staas": "Pool StaaS",
    "pool_hardware": "Pool Hardware",
    "pool_cloud": "Pool Cloud",
    "staas_full": "StaaS Full",
    "staas_self_custodied": "StaaS Self-custodied",
}

legend_state_variable_name_mapping = {
    "timestamp": "Date",
    "eth_price": "ETH Price",
    "eth_staked": "ETH Staked",
    "eth_supply": "ETH Supply",
    "source_reward_eth": "Source Reward",
    "target_reward_eth": "Target Reward",
    "head_reward_eth": "Head Reward",
    "block_proposer_reward_eth": "Block Proposer Reward",
    "sync_reward_eth": "Sync Reward",
    "total_priority_fee_to_validators_eth": "Priority Fees",
    "total_realized_mev_to_validators": "Realized MEV",
    "supply_inflation_pct": "ETH Supply inflation",
    "total_revenue_yields_pct": "Total Revenue Yields",
    "total_profit_yields_pct": "Total Profit Yields",
    "revenue_profit_yield_spread_pct": "Revenue/Profit Yield Spread",
    **dict(
        [
            (
                validator.type + "_profit_yields_pct",
                validator_environment_name_mapping[validator.type],
            )
            for validator in validator_environments
        ]
    ),
}

axis_state_variable_name_mapping = {
    **legend_state_variable_name_mapping,
    "eth_price": "ETH Price (USD/ETH)",
    "eth_staked": "ETH Staked (ETH)",
    "eth_supply": "ETH Supply (ETH)",
}

millnames = ["", " k", " m", " bn", " tn"]


def millify(n):
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    return "{:.0f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])


def update_legend_names(fig, name_mapping=legend_state_variable_name_mapping):
    for i, dat in enumerate(fig.data):
        for elem in dat:
            if elem == "name":
                try:
                    fig.data[i].name = name_mapping[fig.data[i].name]
                except KeyError:
                    continue
    return fig


def update_axis_names(fig, name_mapping=axis_state_variable_name_mapping):
    def update_axis_name(axis):
        title = axis["title"]
        text = title["text"]
        updated_text = name_mapping.get(text, text)
        title.update({"text": updated_text})

    fig.for_each_xaxis(lambda ax: update_axis_name(ax))
    fig.for_each_yaxis(lambda ax: update_axis_name(ax))
    return fig


def apply_plotly_standards(
    fig,
    title=None,
    xaxis_title=None,
    yaxis_title=None,
    legend_title=None,
    axis_state_variable_name_mapping_override={},
    legend_state_variable_name_mapping_override={},
):
    update_axis_names(
        fig,
        {
            **axis_state_variable_name_mapping,
            **axis_state_variable_name_mapping_override,
        },
    )
    update_legend_names(
        fig,
        {
            **legend_state_variable_name_mapping,
            **legend_state_variable_name_mapping_override,
        },
    )

    if title:
        fig.update_layout(title=title)
    if xaxis_title:
        fig.update_layout(xaxis_title=xaxis_title)
    if yaxis_title:
        fig.update_layout(yaxis_title=yaxis_title)
    if legend_title:
        fig.update_layout(legend_title=legend_title)

    return fig


def plot_validating_rewards(df, subplot_titles=[]):
    validating_rewards = [
        "source_reward_eth",
        "target_reward_eth",
        "head_reward_eth",
        "block_proposer_reward_eth",
        "sync_reward_eth",
    ]

    fig = make_subplots(
        rows=1,
        cols=len(df.subset.unique()),
        shared_yaxes=True,
        subplot_titles=subplot_titles,
    )

    for subset in df.subset.unique():
        color_cycle = itertools.cycle(cadlabs_colorway_sequence)
        df_subset = df.query(f"subset == {subset}")
        for reward_index, reward_key in enumerate(validating_rewards):
            color = next(color_cycle)
            fig.add_trace(
                go.Scatter(
                    x=df_subset.timestamp,
                    y=df_subset[reward_key],
                    stackgroup="one",
                    showlegend=(True if subset == 0 else False),
                    line=dict(color=color),
                    name=validating_rewards[reward_index],
                ),
                row=1,
                col=subset + 1,
            )

    update_legend_names(fig)

    fig.update_layout(
        title="Validating Rewards",
        xaxis_title="Date",
        yaxis_title="Reward (ETH)",
        legend_title="",
    )

    return fig


def plot_validator_incentives_pie_chart(df):
    title = "Validator Incentives (Rewards, Priority Fees, & MEV)"
    validator_rewards = df.iloc[-1][
        [
            "total_priority_fee_to_validators_eth",
            "total_realized_mev_to_validators",
            "source_reward_eth",
            "target_reward_eth",
            "head_reward_eth",
            "block_proposer_reward_eth",
            "sync_reward_eth",
        ]
    ].to_dict()
    labels = [
        "Priority Fees",
        "MEV",
        "Source Reward",
        "Target Reward",
        "Head Reward",
        "Block Proposer Reward",
        "Sync Reward",
    ]

    fig = go.Figure(data=[go.Pie(labels=labels, values=list(validator_rewards.values()), pull=[0.2, 0.2, 0, 0, 0, 0, 0])])

    fig.for_each_trace(
        lambda trace: trace.update(
            textinfo="label+percent",
            insidetextorientation="radial",
            marker=dict(line=dict(color="#000000", width=2)),
        ),
    )

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Reward (ETH)",
        height=600,
        showlegend=False,
    )

    return fig


def plot_revenue_profit_yields_over_polygn_staked(df):
    fig = go.Figure()

    df_subset_0 = df.query("subset == 0")
    df_subset_1 = df.query("subset == 1")
    df_subset_2 = df.query("subset == 2")
    df_subset_3 = df.query("subset == 3")

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=df_subset_0.polygn_staked,
            y=df_subset_0.total_revenue_yields_pct,
            name="Revenue Yields",
            line=dict(color=cadlabs_colorway_sequence[3]),
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df_subset_0.polygn_staked,
            y=df_subset_0.total_profit_yields_pct,
            name=f"Profit Yields @ {df_subset_0.polygn_price.iloc[0]:.0f} USD/POLYGN",
            line=dict(color=cadlabs_colorway_sequence[4], dash="dash"),
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df_subset_1.polygn_staked,
            y=df_subset_1.total_profit_yields_pct,
            name=f"Profit Yields @ {df_subset_1.polygn_price.iloc[0]:.0f} USD/POLYGN",
            line=dict(color=cadlabs_colorway_sequence[5], dash="dash"),
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df_subset_2.polygn_staked,
            y=df_subset_2.total_profit_yields_pct,
            name=f"Profit Yields @ {df_subset_2.polygn_price.iloc[0]:.0f} USD/POLYGN",
            line=dict(color=cadlabs_colorway_sequence[6], dash="dash"),
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df_subset_3.polygn_staked,
            y=df_subset_3.total_profit_yields_pct,
            name=f"Profit Yields @ {df_subset_3.polygn_price.iloc[0]:.0f} USD/POLYGN",
            line=dict(color=cadlabs_colorway_sequence[6], dash="dash"),
        ),
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Revenue and Profit Yields Over POLYGN Staked",
        xaxis_title="POLYGN Staked (POLYGN)",
        # yaxis_title="",
        legend_title="",
    )

    # Set secondary y-axes titles
    fig.update_yaxes(title_text="Yields (%/year)")
    fig.update_layout(hovermode="x unified")

    return fig


def plot_revenue_profit_yields_over_polygn_price(df):
    fig = go.Figure()

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=df.polygn_price,
            y=df.total_revenue_yields_pct,
            name=f"Revenue Yields @ ({millify(df.polygn_staked.iloc[0])} POLYGN Staked)",
            line=dict(color=cadlabs_colorway_sequence[3]),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.polygn_price,
            y=df.total_profit_yields_pct,
            name=f"Profit Yields @ ({millify(df.polygn_staked.iloc[0])} POLYGN Staked)",
            line=dict(color=cadlabs_colorway_sequence[4], dash="dash"),
        ),
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Revenue and Profit Yields Over POLYGN Price",
        xaxis_title="POLYGN Price (USD/POLYGN)",
        # yaxis_title="",
        legend_title="",
    )

    # Set secondary y-axes titles
    fig.update_yaxes(title_text="Yields (%/year)")
    fig.update_layout(hovermode="x unified")

    return fig


def plot_validator_environment_yields(df):
    validator_profit_yields_pct = [
        validator.type + "_profit_yields_pct" for validator in validator_environments
    ]

    fig = df.plot(
        x="eth_price",
        y=(validator_profit_yields_pct + ["total_profit_yields_pct"]),
        facet_col="subset",
        facet_col_wrap=2,
        facet_col_spacing=0.05,
    )

    fig.for_each_annotation(
        lambda a: a.update(
            text=f"ETH Staked = {df.query(f'subset == {a.text.split(chr(61))[1]}').eth_staked.iloc[0]:.0f} ETH"
        )
    )

    fig.update_layout(
        title=f"Profit Yields of Validator Environments",
        xaxis_title="ETH Price (USD/ETH)",
        yaxis_title="Profit Yields (%/year)",
        legend_title="",
    )

    fig.for_each_xaxis(lambda x: x["title"].update({"text": "ETH Price (USD/ETH)"}))
    fig.update_yaxes(matches=None)
    fig.update_yaxes(showticklabels=True)

    update_legend_names(fig)

    return fig


def plot_three_region_yield_analysis(fig_df):
    fig = fig_df.plot(
        x="eth_price",
        y=["total_revenue_yields_pct", "total_profit_yields_pct"],
    )

    fig.add_annotation(
        x=fig_df["eth_price"].min() + 100,
        y=fig_df["total_revenue_yields_pct"].max(),
        text="Cliff",
        showarrow=False,
        yshift=10,
    )

    fig.add_annotation(
        x=fig_df["eth_price"].median(),
        y=fig_df["total_revenue_yields_pct"].max(),
        text="Economics of Scale",
        showarrow=False,
        yshift=10,
    )

    fig.add_annotation(
        x=fig_df["eth_price"].max() - 100,
        y=fig_df["total_revenue_yields_pct"].max(),
        text="Stability",
        showarrow=False,
        yshift=10,
    )

    update_legend_names(fig)

    fig.update_layout(
        title=f"Three Region Yield Analysis @ {millify(fig_df.eth_staked.iloc[0])} ETH Staked",
        xaxis_title="ETH Price (USD/ETH)",
        yaxis_title="Revenue Yields (%/year)",
        legend_title="",
    )

    return fig


def plot_revenue_yields_vs_network_inflation(df):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    df_subset_0 = df.query("subset == 0")
    df_subset_1 = df.query("subset == 1")

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=df_subset_0.eth_staked,
            y=df_subset_0.total_revenue_yields_pct,
            name="Revenue Yields",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df_subset_0.eth_staked,
            y=df_subset_0.total_profit_yields_pct,
            name=f"Profit Yields @ {df_subset_0.eth_price.iloc[0]} USD/ETH",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df_subset_1.eth_staked,
            y=df_subset_1.total_profit_yields_pct,
            name=f"Profit Yields @ {df_subset_1.eth_price.iloc[0]} USD/ETH",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df_subset_0.eth_staked,
            y=df_subset_0.supply_inflation_pct,
            name="Network Inflation Rate",
        ),
        secondary_y=True,
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Revenue Yields vs. Network Inflation",
        xaxis_title="ETH Staked (ETH)",
        # yaxis_title="",
        legend_title="",
    )

    # Set secondary y-axes titles
    fig.update_yaxes(title_text="Revenue Yields (%/year)", secondary_y=False)
    fig.update_yaxes(title_text="Network Inflation Rate (%/year)", secondary_y=True)

    return fig


def plot_validator_environment_yield_contour(df):
    grouped = df.groupby(["eth_price", "eth_staked"]).last()["total_profit_yields_pct"]

    x = df.groupby(["run"]).first()["eth_price"].unique()
    y = df.groupby(["run"]).first()["eth_staked"].unique()
    z = []

    for eth_staked in y:
        row = []
        for eth_price in x:
            z_value = grouped[eth_price][eth_staked]
            row.append(z_value)
        z.append(row)

    fig = go.Figure(
        data=[
            go.Contour(
                x=x,
                y=y,
                z=z,
                line_smoothing=0.85,
                colorscale=cadlabs_colors,
                colorbar=dict(
                    title="Profit Yields (%/year)",
                    titleside="right",
                    titlefont=dict(size=14),
                ),
            )
        ]
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Profit Yields Over ETH Price vs. ETH Staked",
        xaxis_title="ETH Price (USD/ETH)",
        yaxis_title="ETH Staked (ETH)",
        width=1000,
        legend_title="",
        autosize=False,
    )

    return fig


def plot_revenue_profit_yield_spread(df):
    grouped = df.groupby(["eth_price", "eth_staked"]).last()[
        "revenue_profit_yield_spread_pct"
    ]

    x = df.groupby(["run"]).first()["eth_price"].unique()
    y = df.groupby(["run"]).first()["eth_staked"].unique()
    z = []

    for eth_staked in y:
        row = []
        for eth_price in x:
            z_value = grouped[eth_price][eth_staked]
            row.append(z_value)
        z.append(row)

    fig = go.Figure(
        data=[
            go.Contour(
                x=x,
                y=y,
                z=z,
                line_smoothing=0.85,
                contours=dict(
                    showlabels=True,  # show labels on contours
                    labelfont=dict(  # label font properties
                        size=12,
                        color="white",
                    ),
                ),
                colorbar=dict(
                    title="Spread (%/year)", titleside="right", titlefont=dict(size=14)
                ),
                colorscale=cadlabs_colors,
            )
        ]
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Revenue/Profit Yield Spread Over ETH Price vs. ETH Staked",
        xaxis_title="ETH Price (USD/ETH)",
        yaxis_title="ETH Staked (ETH)",
        width=1000,
        legend_title="",
        autosize=False,
    )

    return fig


def plot_validator_environment_yield_surface(df):
    grouped = df.groupby(["eth_price", "eth_staked"]).last()["total_profit_yields_pct"]

    x = df.groupby(["run"]).first()["eth_price"].unique()
    y = df.groupby(["run"]).first()["eth_staked"].unique()
    z = []

    for eth_staked in y:
        row = []
        for eth_price in x:
            z_value = grouped[eth_price][eth_staked]
            row.append(z_value)
        z.append(row)

    fig = go.Figure(
        data=[
            go.Surface(
                x=x,
                y=y,
                z=z,
                colorbar=dict(
                    title="Profit Yields (%/year)",
                    titleside="right",
                    titlefont=dict(size=14),
                ),
                colorscale=cadlabs_colors,
            )
        ]
    )

    fig.update_traces(contours_z=dict(show=True, usecolormap=True, project_z=True))

    update_legend_names(fig)

    fig.update_layout(
        title="Profit Yields Over ETH Price vs. ETH Staked",
        autosize=False,
        legend_title="",
        margin=dict(l=65, r=50, b=65, t=90),
        scene={
            "xaxis": {
                "title": {"text": "ETH Price (USD/ETH)"},
                "type": "log",
            },
            "yaxis": {"title": {"text": "ETH Staked (ETH)"}},
            "zaxis": {"title": {"text": "Profit Yields (%/year)"}},
        },
    )

    return fig


def fig_add_stage_vrects(df, fig, parameters=parameters):
    date_start = parameters["date_start"][0]
    date_eip1559 = parameters["date_eip1559"][0]
    date_pos = parameters["date_pos"][0]
    date_end = df.index[-1]

    fig.add_vrect(
        x0=date_eip1559,
        x1=date_pos,
        row="all",
        col=1,
        layer="below",
        fillcolor="gray",
        opacity=0.25,
        line_width=0,
    )

    fig.add_vrect(
        x0=date_pos,
        x1=date_end,
        row="all",
        col=1,
        layer="below",
        fillcolor="gray",
        opacity=0.1,
        line_width=0,
    )
    return fig


def fig_add_stage_markers(df, column, fig, secondary_y=None, parameters=parameters):
    # Frontier 📆 Jul-30-2015 03:26:13 PM +UTC
    # Frontier thawing Sep-07-2015 09:33:09 PM +UTC
    # Homestead Mar-14-2016 06:49:53 PM +UTC
    # DAO fork Jul-20-2016 01:20:40 PM +UTC
    # Tangerine whistle Oct-18-2016 01:19:31 PM +UTC
    # Spurious Dragon Nov-22-2016 04:15:44 PM +UTC
    # Byzantium Oct-16-2017 05:22:11 AM +UTC
    # Constantinople Feb-28-2019 07:52:04 PM +UTC
    # Istanbul Dec-08-2019 12:25:09 AM +UTC
    # Muir Glacier Jan-02-2020 08:30:49 AM +UTC
    # Staking deposit contract deployed Oct-14-2020 09:22:52 AM +UTC
    # Beacon Chain genesis Dec-01-2020 12:00:35 PM +UTC

    historical_dates = [
        ("Frontier", datetime.strptime("Jul-30-2015", "%b-%d-%Y"), (-20, 45)),
        ("Frontier thawing", datetime.strptime("Sep-07-2015", "%b-%d-%Y"), (35, 50)),
        ("Homestead", datetime.strptime("Mar-14-2016", "%b-%d-%Y"), (-30, 0)),
        ("Byzantium", datetime.strptime("Oct-16-2017", "%b-%d-%Y"), (30, 40)),
        ("Constantinople", datetime.strptime("Feb-28-2019", "%b-%d-%Y"), (30, -15)),
        ("Istanbul", datetime.strptime("Dec-08-2019", "%b-%d-%Y"), (30, -10)),
        ("Muir Glacier", datetime.strptime("Jan-02-2020", "%b-%d-%Y"), (-35, 0)),
    ]

    system_dates = [
        ("Beacon Chain", datetime.strptime("Dec-01-2020", "%b-%d-%Y")),
        # ("Today", parameters["date_start"][0]),
        ("EIP1559", parameters["date_eip1559"][0]),
        ("Proof of Stake", parameters["date_pos"][0]),
    ]

    for (name, date, (ay, ax)) in historical_dates:
        nearest_row = df.iloc[
            df.index.get_loc(date.strftime("%Y-%m-%d"), method="nearest")
        ]
        x_datetime = nearest_row["timestamp"][0]
        y_value = nearest_row[column][0]
        fig.add_annotation(
            x=x_datetime,
            y=y_value,
            text=name,
            ay=ay,
            ax=ax,
            showarrow=True,
            arrowhead=2,
            arrowsize=1.25,
        )

    for idx, (name, date) in enumerate(system_dates):
        if date > parameters["date_start"][0]:
            x_datetime = date
            y_value = df.loc[date.strftime("%Y-%m-%d")][column][0]

        else:
            nearest_row = df.iloc[
                df.index.get_loc(date.strftime("%Y-%m-%d"), method="nearest")
            ]
            x_datetime = nearest_row["timestamp"][0]
            y_value = nearest_row[column][0]
                

        fig.add_trace(
            go.Scatter(
                mode="markers+text",
                x=[x_datetime],
                y=[y_value],
                marker_symbol=["diamond"],
                marker_line_width=2,
                marker_size=10,
                hovertemplate=name,
                name=name,
                # textfont_size=11,
                text=name,
                textposition="top center",
                legendgroup="markers",
                showlegend=False,
            ),
            *(secondary_y, secondary_y) if secondary_y else (),
        )

    return fig


def plot_eth_supply_over_all_stages(df):
    df = df.set_index("timestamp", drop=False)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x=df.timestamp, y=df.eth_supply, name="ETH Supply"),
    )

    fig_add_stage_markers(df, "eth_supply", fig)
    fig_add_stage_vrects(df, fig)

    # Add range slider
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    update_legend_names(fig)

    fig.update_layout(
        title="ETH Supply Over Time",
        xaxis_title="Date",
        yaxis_title="ETH Supply (ETH)",
        legend_title="",
    )

    return fig


def plot_eth_supply_and_inflation(df_historical, df_simulated, parameters=parameters):
    df_historical = df_historical.set_index("timestamp", drop=False)
    df_simulated = df_simulated.set_index("timestamp", drop=False)

    df_historical["supply_inflation_pct"] = df_historical[
        "supply_inflation_pct_rolling"
    ]
    df_historical = df_historical.drop(df_historical.tail(1).index)
    df_historical.loc[df_simulated.index[0]] = df_simulated.iloc[0]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df_historical.timestamp,
            y=df_historical.supply_inflation_pct,
            name="Historical Network Inflation Rate",
            line=dict(color="#FC1CBF"),
            legendgroup="historical",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df_historical.timestamp,
            y=df_historical.eth_supply,
            name="Historical ETH Supply",
            line=dict(color="#3283FE"),
            legendgroup="historical",
        ),
        secondary_y=True,
    )

    for subset in df_simulated.subset.unique():
        df_subset = df_simulated.query(f"subset == {subset}")
        fig.add_trace(
            go.Scatter(
                x=df_subset.timestamp,
                y=df_subset.supply_inflation_pct,
                name="Simulated Network Inflation Rate",
                line=dict(color="#FC1CBF", dash="dot"),
                showlegend=(True if subset == 0 else False),
                legendgroup="simulated",
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=df_subset.timestamp,
                y=df_subset.eth_supply,
                name="Simulated ETH Supply",
                line=dict(color="#3283FE", dash="dot"),
                showlegend=(True if subset == 0 else False),
                legendgroup="simulated",
            ),
            secondary_y=True,
        )
        # fill=('tonexty' if subset > 0 else None)

    df = df_historical.append(df_simulated)

    fig_add_stage_markers(
        df, "supply_inflation_pct", fig, secondary_y=False, parameters=parameters
    )
    fig_add_stage_vrects(df, fig, parameters=parameters)

    date_inflation_annotation = datetime.strptime("Dec-01-2024", "%b-%d-%Y")
    fig.add_annotation(
        x=date_inflation_annotation,
        y=-2.75,
        text="Deflationary",
        showarrow=True,
        ay=-35,
        ax=0,
        arrowhead=2,
        arrowsize=1.25,
    )

    fig.add_annotation(
        x=date_inflation_annotation,
        y=2.75,
        text="Inflationary",
        showarrow=True,
        ay=35,
        ax=0,
        arrowhead=2,
        arrowsize=1.25,
    )

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True,
            ),
            rangeslider_thickness=0.15,
            type="date",
        )
    )

    update_legend_names(fig)

    fig.update_layout(
        xaxis_title="Date",
        title="ETH Supply Simulator",
        legend_title="",
        height=550,
        legend=dict(
            title=dict(
                text="",
            ),
            orientation="h",
            yanchor="top",
            y=-0.475,
            xanchor="center",
            x=0.5,
            traceorder="grouped",
            itemclick=False,
        ),
        margin=dict(l=60, r=0, t=30, b=20),
    )

    fig.add_hline(
        y=0,
        line_color="#808080",
        line_width=0.75,
        annotation_text="",
        annotation_position="bottom right",
    )

    # Set secondary y-axes titles
    fig.update_yaxes(title_text="Network Inflation Rate (%/year)", secondary_y=False)
    fig.update_yaxes(title_text="ETH Supply (ETH)", secondary_y=True)

    return fig


def plot_network_inflation_over_all_stages(df):
    df = df.set_index("timestamp", drop=False)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x=df.timestamp, y=df.supply_inflation_pct)  # , fill='tozeroy'
    )

    fig.add_hline(
        y=0, annotation_text="Ultra-sound barrier", annotation_position="bottom right"
    )

    fig_add_stage_markers(df, "supply_inflation_pct", fig)
    fig_add_stage_vrects(df, fig)

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    update_legend_names(fig)

    fig.update_layout(
        title="Network Inflation Over Time",
        xaxis_title="Date",
        yaxis_title="Network Inflation Rate (%/year)",
        legend_title="",
    )

    return fig


def plot_eth_staked_over_all_stages(df):
    df = df.set_index("timestamp", drop=False)

    fig = df.plot(x="timestamp", y="eth_staked")

    fig_add_stage_markers(df, "eth_staked", fig)

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    update_legend_names(fig)

    fig.update_layout(
        title="ETH Staked",
        xaxis_title="Date",
        yaxis_title="ETH Staked (ETH)",
        legend_title="",
    )

    return fig

def plot_number_of_supernets_per_subset(df, scenario_names):
    color_cycle = itertools.cycle(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])
    fig = go.Figure()

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df[df.subset == subset]["timestamp"],
                y=df[df.subset == subset]["PRIVATE_CHAINS_CNT"],
                name=scenario_names[subset],
                line=dict(color=color),
            )
        )

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Supernets",
        legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="bottom",
            y=-0.3,  # Position it a bit below the x-axis
            xanchor="center",
            x=0.5,  # Center it
            font=dict(
                size=18,  # Adjust the size as needed
                color="black",
            ),
        ),
        hovermode="x unified",
        template="plotly_white",
        font=dict(
            family="Arial",
            size=18,
            color="black"),
        plot_bgcolor='rgba(255, 255, 255, 1)', 
        paper_bgcolor='rgba(255, 255, 255, 1)', 
    )

    html_file_path = os.path.join(output_htmls_folder, 'adoption_rate.html')
    fig.write_html(html_file_path)

    fig.update_layout(autosize=False, width=900, height=600)
    jpeg_file_path = os.path.join(output_images_folder, 'adoption_rate.jpeg')
    pio.write_image(fig, jpeg_file_path)

    return fig


# def plot_number_of_public_chains_per_subset(df, scenario_names):
#     fig = go.Figure()

#     for subset in df.subset.unique():
#         fig.add_trace(
#             go.Scatter(
#                 x=df["timestamp"],
#                 y=df[df.subset == subset]["PUBLIC_CHAINS_CNT"],
#                 name=scenario_names[subset],
#             )
#         )

#     fig.update_layout(
#         title="Public Chains Adoption Scenarios",
#         xaxis_title="Date",
#         yaxis_title="Total Public Chains Number",
#         legend_title="",
#         xaxis=dict(rangeslider=dict(visible=True)),
#     )
#     fig.update_layout(hovermode="x unified")
#     fig.write_html('/Users/wenxuan/Desktop/polygon/cadCAD/Token-Redesign/experiments/notebooks/visualizations/plots/adoption_rate_public.html')


#     return fig

def plot_number_of_public_chains_per_subset(df, scenario_names):
    from plotly.colors import n_colors
    color_cycle = itertools.cycle(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])
    fig = go.Figure()

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df[df.subset == subset]["timestamp"],
                y=df[df.subset == subset]["PUBLIC_CHAINS_CNT"],
                name=scenario_names[subset],
                line=dict(color=color),
            )
        )

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Public Chains",
        legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="bottom",
            y=-0.3,  # Position it a bit below the x-axis
            xanchor="center",
            x=0.5,  # Center it
            font=dict(
                size=18,  # Adjust the size as needed
                color="black",
            ),
        ),
        hovermode="x unified",
        template="plotly_white",
        font=dict(
            family="Arial",
            size=18,
            color="black"),
        plot_bgcolor='rgba(255, 255, 255, 1)', 
        paper_bgcolor='rgba(255, 255, 255, 1)', 
    )

    html_file_path = os.path.join(output_htmls_folder, 'adoption_rate_public.html')
    fig.write_html(html_file_path)

    fig.update_layout(autosize=False, width=900, height=600)
    jpeg_file_path = os.path.join(output_images_folder, 'adoption_rate_public.jpeg')
    pio.write_image(fig, jpeg_file_path)
    
    return fig



def plot_number_of_validators_in_activation_queue_over_time(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig_df = df.query("subset == 2")

    fig.add_trace(
        go.Scatter(
            x=fig_df["timestamp"],
            y=fig_df["number_of_validators"],
            name="Number of validators",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=fig_df["timestamp"],
            y=fig_df["number_of_validators_in_activation_queue"],
            name="Activation queue",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="Number of Validators in Activation Queue Over Time",
        xaxis_title="Date",
        
    )

    fig.update_yaxes(title_text="Number of Validators", secondary_y=False)
    fig.update_yaxes(title_text="Activation Queue", secondary_y=True)

    update_legend_names(fig)

    return fig


# def plot_yields_per_subset_subplots(df, subplot_titles=[]):
#     color_cycle = itertools.cycle(cadlabs_colorway_sequence)

#     fig = make_subplots(
#         rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
#     )

#     for subset in df.subset.unique():
#         color = next(color_cycle)
#         # fig.add_trace(
#         #     go.Scatter(
#         #         x=df["timestamp"],
#         #         y=df[df.subset == subset]["total_revenue_yields_pct"],
#         #         name="Revenue Yields",
#         #         line=dict(color=color),
#         #         showlegend=False,
#         #     ),
#         #     row=1,
#         #     col=subset + 1,
#         # )
#         fig.add_trace(
#             go.Scatter(
#                 x=df["timestamp"],
#                 y=df[df.subset == subset]["total_profit_yields_pct"],
#                 name="Validator Yields",
#                 line=dict(color=color, dash="dash"),
#                 showlegend=False,
#             ),
#             row=1,
#             col=subset + 1,
#         )


#     for subset in df.subset.unique():
#         fig.add_shape(
#             go.layout.Shape(
#                 type="line",
#                 x0=df.loc[1,["timestamp"]].values,
#                 y0=0,
#                 x1=df.tail(1)['timestamp'].values,
#                 y1=0,
#                 line=dict(color='red',width=6,dash="dashdot"),
#             ),
#             row=1,
#             col=subset + 1,
#         )


#     # Add uncoloured legend for traces
#     # fig.add_trace(
#     #     go.Scatter(
#     #         x=df["timestamp"],
#     #         y=[None],
#     #         mode="lines",
#     #         line=dict(color="black"),
#     #         name="Revenue Yields",
#     #     )
#     # )
#     fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"],
#             y=[None],
#             mode="lines",
#             line=dict(color="black", dash="dash"),
#             name="Validator Yields",
#         )
#     )

#     fig.update_layout(
#         title="Validator Yields Over Time - At a Glance",
#         xaxis_title="Date",
#         yaxis_title="Yields (%/year)",
#         legend_title="",
#         hovermode="x",
#     )

#     fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

#     # Removes the 'subset=' from the facet_col title
#     fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

#     update_legend_names(fig)
#     fig.update_annotations(font_size=12)
#     fig.write_html('/Users/wenxuan/Desktop/polygon/cadCAD/Token-Redesign/experiments/notebooks/visualizations/plots/validator_yields.html')


#     return fig

def plot_yields_per_subset_subplots(df, scenario_names):
    color_cycle = itertools.cycle(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])
    fig = go.Figure()

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df[df.subset == subset]["timestamp"],
                y=df[df.subset == subset]["total_profit_yields_pct"],
                name=scenario_names[subset],
                line=dict(color=color,dash='dot'),
            )
        )

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Yields (%/year)",
        legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="bottom",
            y=-0.3,  # Position it a bit below the x-axis
            xanchor="center",
            x=0.5,  # Center it
            font=dict(
                size=18,  # Adjust the size as needed
                color="black",
            ),
        ),
        hovermode="x unified",
        template="plotly_white",
        font=dict(
            family="Arial",
            size=18,
            color="black"),
        plot_bgcolor='rgba(255, 255, 255, 1)', 
        paper_bgcolor='rgba(255, 255, 255, 1)',
    )

    update_legend_names(fig)
    html_file_path = os.path.join(output_htmls_folder, 'validator_yields.html')
    fig.write_html(html_file_path)

    fig.update_layout(autosize=False, width=900, height=600)
    jpeg_file_path = os.path.join(output_images_folder, 'validator_yields.jpeg')
    pio.write_image(fig, jpeg_file_path)

    return fig


def plot_yields_per_staking_mode(df, subplot_titles=[]):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = make_subplots(
        rows=1, cols=2, shared_yaxes=True, subplot_titles=subplot_titles
    )

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["total_revenue_yields_pct"],
                name="Revenue Yields",
                line=dict(color=color),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["total_profit_yields_pct"],
                name="Profit Yields",
                line=dict(color=color, dash="dash"),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )
    for subset in df.subset.unique():
        fig.add_shape(
            go.layout.Shape(
                type="line",
                x0=df.loc[1,["timestamp"]].values,
                y0=0,
                x1=df.tail(1)['timestamp'].values,
                y1=0,
                line=dict(color='red',width=6,dash="dashdot"),
            ),
            row=1,
            col=subset + 1,
        )

    # Add uncoloured legend for traces
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black"),
            name="Revenue Yields",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black", dash="dash"),
            name="Profit Yields",
        )
    )

    fig.update_layout(
        title="Revenue and Profit Yields Over Time - At a Glance",
        xaxis_title="Date",
        yaxis_title="Revenue Yields (%/year)",
        legend_title="",
        hovermode="x",
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)

    return fig

def plot_yields_per_subset(df, scenario_names):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = go.Figure()

    for subset in df.subset.unique():
        df_subset = df.query(f"subset == {subset}").copy()

        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["total_revenue_yields_pct"],
                name=f"{scenario_names[subset]} Revenue Yields",
                line=dict(color=color),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["total_profit_yields_pct"],
                name=f"{scenario_names[subset]} Profit Yields",
                line=dict(color=color, dash="dash"),
                visible=False,
            ),
        )

    fig.update_layout(
        title="Revenue or Profit Yields Over Time",
        xaxis_title="Date",
        yaxis_title="Yields (%/year)",
        legend_title="",
    )

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Revenue Yields",
                        method="update",
                        args=[{"visible": [True, "legendonly"]}, {"showlegend": True}],
                    ),
                    dict(
                        label="Profit Yields",
                        method="update",
                        args=[{"visible": ["legendonly", True]}, {"showlegend": True}],
                    ),
                ],
                direction="right",
                showactive=True,
                pad={"t": 10},
                x=0,
                xanchor="left",
                y=1.3,
                yanchor="top",
            )
        ]
    )

    fig.update_layout(hovermode="x unified")

    return fig


def plot_cumulative_yields_per_subset(df, DELTA_TIME, scenario_names):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = go.Figure()

    for subset in df.subset.unique():
        df_subset = df.query(f"subset == {subset}").copy()

        df_subset["daily_revenue_yields_pct"] = (
            df_subset["total_revenue_yields_pct"] / (constants.epochs_per_year / DELTA_TIME)
        )
        df_subset["daily_profit_yields_pct"] = (

            df_subset["total_profit_yields_pct"] / (constants.epochs_per_year / DELTA_TIME)
        )

        df_subset["cumulative_revenue_yields_pct"] = (
            df_subset["daily_revenue_yields_pct"].expanding().sum()
        )
        df_subset["cumulative_profit_yields_pct"] = (
            df_subset["daily_profit_yields_pct"].expanding().sum()
        )

        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["cumulative_revenue_yields_pct"],
                name=f"{scenario_names[subset]} Revenue Yields",
                line=dict(color=color),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["cumulative_profit_yields_pct"],
                name=f"{scenario_names[subset]} Profit Yields",
                line=dict(color=color, dash="dash"),
                visible=False,
            ),
        )

    fig.update_layout(
        title="Cumulative Revenue or Profit Yields Over Time",
        xaxis_title="Date",
        yaxis_title="Cumulative Yields (%)",
        legend_title="",
    )

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Revenue Yields",
                        method="update",
                        args=[{"visible": [True, "legendonly"]}, {"showlegend": True}],
                    ),
                    dict(
                        label="Profit Yields",
                        method="update",
                        args=[{"visible": ["legendonly", True]}, {"showlegend": True}],
                    ),
                ],
                direction="right",
                showactive=True,
                pad={"t": 10},
                x=0,
                xanchor="left",
                y=1.3,
                yanchor="top",
            )
        ]
    )

    fig.update_layout(hovermode="x unified")

    return fig


def plot_cumulative_revenue_yields_per_subset(df, scenario_names):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = go.Figure()

    for subset in df.subset.unique():
        df_subset = df.query(f"subset == {subset}").copy()

        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["cumulative_revenue_yields_pct"],
                name=f"{scenario_names[subset]}",
                line=dict(color=color),
            ),
        )

    fig.update_layout(
        title="Cumulative Revenue Yields Over Time",
        xaxis_title="Date",
        yaxis_title="Cumulative Revenue Yields (%)",
        legend_title="",
    )

    fig.update_layout(hovermode="x unified")

    return fig


def plot_stacked_cumulative_column_per_subset(df, column, scenario_names):
    color_cycle = itertools.cycle([
        "#782AB6",
        "#1C8356",
        "#F6222E",
    ])

    fig = go.Figure()

    for subset in df.subset.unique():
        df_subset = df.query(f"subset == {subset}").copy()

        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset[column],
                name=f"{scenario_names[subset]}",
                line=dict(color=color),
                stackgroup='one',
            ),
        )

    fig.update_layout(
        hovermode="x unified",
        margin=dict(r=30, b=65, l=80),
        xaxis_title="Date",
        xaxis=dict(
            rangeslider=dict(
                visible=True,
            ),
            rangeslider_thickness=0.15,
            type="date",
        )
    )

    return fig


def plot_cumulative_returns_per_subset(df):
    scenario_names = {0: "Normal Adoption", 1: "Low Adoption", 2: "High Adoption"}
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = go.Figure()

    for subset in df.subset.unique():
        df_subset = df.query(f"subset == {subset}").copy()

        df_subset["daily_revenue_yields_pct"] = (
            df_subset["total_revenue_yields_pct"] / 365
        )
        df_subset["daily_profit_yields_pct"] = (
            df_subset["total_profit_yields_pct"] / 365
        )

        df_subset["cumulative_revenue_yields_pct"] = (
            df_subset["daily_revenue_yields_pct"].expanding().sum()
        )
        df_subset["cumulative_profit_yields_pct"] = (
            df_subset["daily_profit_yields_pct"].expanding().sum()
        )

        df_subset["cumulative_revenue"] = (
            1 + df_subset["cumulative_revenue_yields_pct"] / 100
        )
        df_subset["cumulative_profit"] = (
            1 + df_subset["cumulative_revenue_yields_pct"] / 100
        )

        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["cumulative_revenue"],
                name=f"{scenario_names[subset]} Revenue Yields",
                line=dict(color=color),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["cumulative_profit"],
                name=f"{scenario_names[subset]} Profit Yields",
                line=dict(color=color, dash="dash"),
                visible=False,
            ),
        )

    fig.update_layout(
        title="Cumulative Revenue or Profit Returns Over Time",
        xaxis_title="Date",
        yaxis_title="Cumulative Returns (USD)",
        legend_title="",
    )

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Revenue Yields",
                        method="update",
                        args=[{"visible": [True, "legendonly"]}, {"showlegend": True}],
                    ),
                    dict(
                        label="Profit Yields",
                        method="update",
                        args=[{"visible": ["legendonly", True]}, {"showlegend": True}],
                    ),
                ],
                direction="right",
                showactive=True,
                pad={"t": 10},
                x=0,
                xanchor="left",
                y=1.1,
                yanchor="top",
            )
        ]
    )

    fig.update_layout(hovermode="x unified")

    return fig


def plot_figure_widget_revenue_yields_over_time_foreach_subset(df):
    subset = widgets.Dropdown(
        options=list(df["subset"].unique()),
        value=0,
        description="Scenario:",
    )

    fig_df = df.query("subset == 0")

    trace1 = go.Scatter(
        x=fig_df["timestamp"],
        y=fig_df["total_revenue_yields_pct"],
    )

    fig = go.FigureWidget(data=[trace1])

    fig.update_layout(
        title="Revenue Yields Over Time",
        xaxis_title="Date",
        yaxis_title="Revenue Yields (%/year)",
        yaxis=dict(tickmode="linear", dtick=0.5),
    )

    max_y = fig_df["total_revenue_yields_pct"].max()
    min_y = fig_df["total_revenue_yields_pct"].min()
    fig.add_hline(
        y=max_y,
        line_dash="dot",
        annotation_text=f"Default scenario max={max_y:.2f}%/year",
        annotation_position="bottom right",
    )
    fig.add_hline(
        y=min_y,
        line_dash="dot",
        annotation_text=f"Default scenario min={min_y:.2f}%/year",
        annotation_position="bottom right",
    )

    def response(change):
        _subset = subset.value
        fig_df = df.query(f"subset == {_subset}")

        with fig.batch_update():
            fig.data[0].x = fig_df["timestamp"]
            fig.data[0].y = fig_df["total_revenue_yields_pct"]

    subset.observe(response, names="value")

    container = widgets.HBox([subset])

    update_legend_names(fig)

    return widgets.VBox([container, fig])


def plot_revenue_yields_rolling_mean(df):
    
    rolling_window = df.groupby('timestamp')['total_revenue_yields_pct'].mean().rolling(7)
    df_rolling = pd.DataFrame()
    df_rolling['rolling_std'] = rolling_window.std()
    df_rolling['rolling_mean'] = rolling_window.mean()
    df_rolling['max'] = df.groupby('timestamp')['total_revenue_yields_pct'].max()
    df_rolling['min'] = df.groupby('timestamp')['total_revenue_yields_pct'].min()
    df_rolling = df_rolling.fillna(method="ffill")
    df_rolling = df_rolling.reset_index()
    
    fig = go.Figure(
        [
            go.Scatter(
                name="Mean",
                x=df_rolling["timestamp"],
                y=df_rolling["rolling_mean"],
                mode="lines",
            ),
            go.Scatter(
                name="Max",
                x=df_rolling["timestamp"],
                y=df_rolling["max"],
                mode="lines",
                marker=dict(color="#444"),
                line=dict(width=0),
                showlegend=False,
            ),
            go.Scatter(
                name="Min",
                x=df_rolling["timestamp"],
                y=df_rolling["min"],
                marker=dict(color="#444"),
                line=dict(width=0),
                mode="lines",
                fillcolor="rgba(68, 68, 68, 0.3)",
                fill="tonexty",
                showlegend=False,
            ),
        ]
    )
    fig.update_layout(
        yaxis_title="Revenue Yields (%/year)",
        xaxis_title="Date",
        title="Revenue Yields Rolling Mean Over Time",
        hovermode="x",
    )

    update_legend_names(fig)

    return fig


def plot_profit_yields_by_environment_over_time(df):
    validator_profit_yields = [
        validator.type + "_profit_yields_pct" for validator in validator_environments
    ]

    fig = go.Figure()

    for key in validator_profit_yields:
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[key],
                name=legend_state_variable_name_mapping[key],
            )
        )

    fig.update_layout(
        title="Profit Yields by Environment Over Time",
        xaxis_title="Date",
        yaxis_title="Profit Yields (%/year)",
        legend_title="",
        xaxis=dict(rangeslider=dict(visible=True), type="date"),
        hovermode="x unified",
    )

    return fig


def plot_network_issuance_scenarios(df, simulation_names):
    df = df.set_index("timestamp", drop=False)

    fig = go.Figure()

    initial_simulation = 0
    for subset in df.query(f"simulation == {initial_simulation}").subset.unique():
        simulation_key = list(simulation_names.keys())[initial_simulation]
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df.query(
                    f"subset == {subset} and simulation == {initial_simulation}"
                ).eth_supply,
                name=simulation_names[simulation_key][subset],
                visible=True,
            )
        )

    buttons = []

    for simulation_index in df.simulation.unique():
        simulation_key = list(simulation_names.keys())[simulation_index]
        simulation_df = df.query(f"simulation == {simulation_index}")
        subset_len = len(simulation_df.subset.unique())
        visible_traces = [False for i in range(4)]
        visible_traces[:subset_len] = [True for i in range(subset_len)]
        buttons.append(
            dict(
                method="update",
                label=str(simulation_key),
                visible=True,
                args=[
                    {
                        "visible": visible_traces,
                        "y": [
                            simulation_df.query(f"subset == {subset}").eth_supply
                            for subset in simulation_df.subset.unique()
                        ],
                        "x": [df.index],
                        "name": list(
                            [
                                simulation_names[simulation_key][subset]
                                for subset in simulation_df.subset.unique()
                            ]
                        ),
                        "type": "scatter",
                    }
                ],
            )
        )

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=buttons,
                direction="right",
                showactive=True,
                pad={"t": 25},
                x=0,
                xanchor="left",
                y=1.25,
                yanchor="top",
            )
        ]
    )

    fig.update_layout(
        yaxis_title="ETH Supply (ETH)",
        xaxis_title="Date",
        title="Inflation Rate and ETH Supply Analysis Scenarios",
        hovermode="x unified",
    )

    return fig

def plot_treasury_per_subset(df, scenario_names):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = go.Figure()

    for subset in df.subset.unique():
        df_subset = df.query(f"subset == {subset}").copy()

        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["total_domain_treasury_balance"],
                name=f"{scenario_names[subset]} Domain Treasury",
                line=dict(color=color),
            ),
        )
        # fig.add_trace(
        #     go.Scatter(
        #         x=df["timestamp"],
        #         y=df_subset["total_profit_yields_pct"],
        #         name=f"{scenario_names[subset]} Profit Yields",
        #         line=dict(color=color, dash="dash"),
        #         visible=False,
        #     ),
        # )

    fig.update_layout(
        title="Domain Treasury Balance",
        xaxis_title="Date",
        yaxis_title="Balance (POLYGN)",
        legend_title="",
    )

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Domain Treasury",
                        method="update",
                        args=[{"visible": [True, "legendonly"]}, {"showlegend": True}],
                    ),
                    # dict(
                    #     label="Profit Yields",
                    #     method="update",
                    #     args=[{"visible": ["legendonly", True]}, {"showlegend": True}],
                    # ),
                ],
                direction="right",
                showactive=True,
                pad={"t": 10},
                x=0,
                xanchor="left",
                y=1.3,
                yanchor="top",
            )
        ]
    )

    fig.update_layout(hovermode="x unified")

    return fig


# costs
# def plot_validator_yields_breakdown_usd(df, subplot_titles=[]):
#     color_cycle = itertools.cycle(cadlabs_colorway_sequence)

#     fig = make_subplots(
#         rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
#     )

#     for subset in df.subset.unique():
#         color = next(color_cycle)
#         # fig.add_trace(
#         #     go.Scatter(
#         #         x=df["timestamp"],
#         #         y=df[df.subset == subset]["validator_checkpoint_costs"],
#         #         name="Validator Checkpoints Costs (USD)",
#         #         line=dict(color=color),
#         #         showlegend=False,
#         #     ),
#         #     row=1,
#         #     col=subset + 1,
#         # )
#         fig.add_trace(
#             go.Scatter(
#                 x=df["timestamp"],
#                 y=df[df.subset == subset]["total_inflation_to_validators_usd"],
#                 name="Validator issuance revenue (USD)",
#                 line=dict(color='green', dash="dash"),
#                 showlegend=False,
#             ),
#             row=1,
#             col=subset + 1,
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=df["timestamp"],
#                 y=df[df.subset == subset]["total_txn_fee_to_validators_usd"],
#                 name="Validator fees revenue (USD)",
#                 line=dict(color='green', dash="dot"),
#                 showlegend=False,
#             ),
#             row=1,
#             col=subset + 1,
#         )
#         # fig.add_trace(
#         #     go.Scatter(
#         #         x=df["timestamp"],
#         #         y=df[df.subset == subset]["total_revenue"],
#         #         name="Total revenue (USD)",
#         #         line=dict(color='grey', dash="dot"),
#         #         showlegend=False,
#         #     ),
#         #     row=1,
#         #     col=subset + 1,
#         # )
#         fig.add_trace(
#             go.Scatter(
#                 x=df["timestamp"],
#                 y=df[df.subset == subset]["total_profit"],
#                 name="Validator profit (USD)",
#                 line=dict(color='grey', width=4, dash="dot"),
#                 showlegend=False,
#             ),
#             row=1,
#             col=subset + 1,
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=df["timestamp"],
#                 y=df[df.subset == subset]["validator_hardware_costs"],
#                 name="Validator running costs (USD)",
#                 line=dict(color='red', width=4, dash="dot"),
#                 showlegend=False,
#             ),
#             row=1,
#             col=subset + 1,
#         )

#     fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"],
#             y=[None],
#             mode="lines",
#             line=dict(color="green", dash="dash"),
#             name="Validator issuance revenue (USD)",
#         )
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"],
#             y=[None],
#             mode="lines",
#             line=dict(color="green", dash="dot"),
#             name="Validator fees revenue (USD)",
#         )
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"],
#             y=[None],
#             mode="lines",
#             line=dict(color="grey", width=4, dash="dot"),
#             name="Validator profit (USD)",
#         )
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"],
#             y=[None],
#             mode="lines",
#             line=dict(color="red", width=4, dash="dot"),
#             name="Validator running costs (USD)",
#         )
#     )

#     fig.update_layout(
#         title="Validator Profits (USD) - Breakdown",
#         xaxis_title="Date",
#         yaxis_title="USD",
#         legend_title="",
#         hovermode="x",
#     )

#     fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

#     # Removes the 'subset=' from the facet_col title
#     fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

#     update_legend_names(fig)

#     fig.update_annotations(font_size=9)
#     fig.write_html('/Users/wenxuan/Desktop/polygon/cadCAD/Token-Redesign/experiments/notebooks/visualizations/plots/validator_profit_breakdown_in_usd.html')


#     return fig

def plot_validator_yields_breakdown_usd(df, subplot_titles=[]):
    import matplotlib.cm as cm

    color_cycle_traces = itertools.cycle(px.colors.qualitative.D3)
    traces = ["total_inflation_to_validators_usd", "total_txn_fee_to_validators_usd", "total_profit", "validator_hardware_costs"]
    trace_colors = {name: next(color_cycle_traces) for name in traces}
    trace_names = {
        "total_inflation_to_validators_usd": "Validator issuance revenue (USD)",
        "total_txn_fee_to_validators_usd": "Validator fees revenue (USD)",
        "total_profit": "Validator profit (USD)",
        "validator_hardware_costs": "Validator running costs (USD)",
    }
    trace_line_styles = {
        "total_inflation_to_validators_usd": "dash",
        "total_txn_fee_to_validators_usd": "dot",
        "total_profit": "dot",
        "validator_hardware_costs": "dot",
    }



    def rgba_to_rgb_str(rgba):
        return f'rgb({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)})'


    fig = make_subplots(
        rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
    )

    for i, subset in enumerate(df.subset.unique(), start=1):
        for trace in traces:
            fig.add_trace(
                go.Scatter(
                    x=df[df.subset == subset]["timestamp"],
                    y=df[df.subset == subset][trace],
                    name=trace_names[trace],
                    line=dict(color=trace_colors[trace], dash=trace_line_styles[trace]),
                    showlegend=False,  # Do not show legend for each subplot
                ),
                row=1,
                col=i
            )

    # Add a single legend for all subplots
    for trace in traces:
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=[None],
                mode="lines",
                line=dict(color=trace_colors[trace], dash=trace_line_styles[trace]),
                name=trace_names[trace],
            ),
            row=1,
            col=1,
        )


    fig.update_layout(
        title={
            'text': "Validator Profits (USD) - Breakdown",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        #xaxis_title="Date",
        yaxis_title="USD",
        legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="bottom",
            y=-0.5,  # Position it a bit below the x-axis
            xanchor="center",
            x=0.5,  # Center it
            font=dict(
                size=18,  # Adjust the size as needed
                color="black",
            ),
        ),
        hovermode="x",
        template="plotly_white",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"),
        plot_bgcolor='rgba(255, 255, 255, 1)', 
        paper_bgcolor='rgba(255, 255, 255, 1)', 
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    html_file_path = os.path.join(output_htmls_folder, 'validator_profit_breakdown_in_usd.html')
    fig.write_html(html_file_path)

    fig.update_layout(autosize=False, width=900, height=600)
    jpeg_file_path = os.path.join(output_images_folder, 'validator_profit_breakdown_in_usd.jpeg')
    pio.write_image(fig, jpeg_file_path)

    return fig




# def plot_validator_checkpoint_costs_yields(df, subplot_titles=[]):
#     color_cycle = itertools.cycle(cadlabs_colorway_sequence)

#     fig = make_subplots(
#         rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
#     )

#     for subset in df.subset.unique():
#         color = next(color_cycle)
#         # fig.add_trace(
#         #     go.Scatter(
#         #         x=df["timestamp"],
#         #         y=df[df.subset == subset]["validator_checkpoint_costs_yields_pct"],
#         #         name="Validator Checkpoints Costs",
#         #         line=dict(color=color),
#         #         showlegend=False,
#         #     ),
#         #     row=1,
#         #     col=subset + 1,
#         # )
#         fig.add_trace(
#             go.Scatter(
#                 x=df["timestamp"],
#                 y=df[df.subset == subset]["total_inflation_to_validators_yields_pct"],
#                 name="Validator issuance revenue (yield)",
#                 line=dict(color='green', dash="dash"),
#                 showlegend=False,
#             ),
#             row=1,
#             col=subset + 1,
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=df["timestamp"],
#                 y=df[df.subset == subset]["total_txn_fee_to_validators_yields_pct"],
#                 name="Validator fees revenue (yield)",
#                 line=dict(color='green', dash="dot"),
#                 showlegend=False,
#             ),
#             row=1,
#             col=subset + 1,
#         )
#         # fig.add_trace(
#         #     go.Scatter(
#         #         x=df["timestamp"],
#         #         y=df[df.subset == subset]["total_revenue_yields_pct"],
#         #         name="Total revenue",
#         #         line=dict(color='grey', dash="dot"),
#         #         showlegend=False,
#         #     ),
#         #     row=1,
#         #     col=subset + 1,
#         # )
#         fig.add_trace(
#             go.Scatter(
#                 x=df["timestamp"],
#                 y=df[df.subset == subset]["total_profit_yields_pct"],
#                 name="Validator yield",
#                 line=dict(color='grey', width=4, dash="dot"),
#                 showlegend=False,
#             ),
#             row=1,
#             col=subset + 1,
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=df["timestamp"],
#                 y=df[df.subset == subset]["validator_hardware_costs_yields_pct"],
#                 name="Validator running costs (yield)",
#                 line=dict(color='red', width=4, dash="dot"),
#                 showlegend=False,
#             ),
#             row=1,
#             col=subset + 1,
#         )

#     # Add uncoloured legend for traces
#     # fig.add_trace(
#     #     go.Scatter(
#     #         x=df["timestamp"],
#     #         y=[None],
#     #         mode="lines",
#     #         line=dict(color="black"),
#     #         name="Validator Checkpoints Costs",
#     #     )
#     # )
#     fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"],
#             y=[None],
#             mode="lines",
#             line=dict(color="green", dash="dash"),
#             name="Validator issuance revenue (yield)",
#         )
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"],
#             y=[None],
#             mode="lines",
#             line=dict(color="green", dash="dot"),
#             name="Validator fees revenue (yield)",
#         )
#     )
#     # fig.add_trace(
#     #     go.Scatter(
#     #         x=df["timestamp"],
#     #         y=[None],
#     #         mode="lines",
#     #         line=dict(color="grey", dash="dot"),
#     #         name="Total revenue",
#     #     )
#     # )
#     fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"],
#             y=[None],
#             mode="lines",
#             line=dict(color="grey", width=4, dash="dot"),
#             name="Validator yield",
#         )
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"],
#             y=[None],
#             mode="lines",
#             line=dict(color="red", width=4, dash="dot"),
#             name="Validator running costs (yield)",
#         )
#     )

#     fig.update_layout(
#         title="Validator Yields - Breakdown",
#         xaxis_title="Date",
#         yaxis_title="Yields (%/year)",
#         legend_title="",
#         hovermode="x",
#     )

#     fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

#     # Removes the 'subset=' from the facet_col title
#     fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

#     update_legend_names(fig)

#     fig.update_annotations(font_size=9)
#     fig.write_html('/Users/wenxuan/Desktop/polygon/cadCAD/Token-Redesign/experiments/notebooks/visualizations/plots/validator_profit_breakdown_in_yield.html')


#     return fig


def plot_validator_yields_breakdown_yields(df, subplot_titles=[]):
    import matplotlib.cm as cm

    color_cycle_traces = itertools.cycle(px.colors.qualitative.D3)
    traces = ["total_inflation_to_validators_yields_pct", "total_txn_fee_to_validators_yields_pct", "total_profit_yields_pct", "validator_hardware_costs_yields_pct"]
    trace_colors = {name: next(color_cycle_traces) for name in traces}
    trace_names = {
        "total_inflation_to_validators_yields_pct": "Validator issuance revenue (USD)",
        "total_txn_fee_to_validators_yields_pct": "Validator fees revenue (USD)",
        "total_profit_yields_pct": "Validator profit (USD)",
        "validator_hardware_costs_yields_pct": "Validator running costs (USD)",
    }
    trace_line_styles = {
        "total_inflation_to_validators_yields_pct": "dash",
        "total_txn_fee_to_validators_yields_pct": "dot",
        "total_profit_yields_pct": "dot",
        "validator_hardware_costs_yields_pct": "dot",
    }



    def rgba_to_rgb_str(rgba):
        return f'rgb({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)})'


    fig = make_subplots(
        rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
    )

    for i, subset in enumerate(df.subset.unique(), start=1):
        for trace in traces:
            fig.add_trace(
                go.Scatter(
                    x=df[df.subset == subset]["timestamp"],
                    y=df[df.subset == subset][trace],
                    name=trace_names[trace],
                    line=dict(color=trace_colors[trace], dash=trace_line_styles[trace]),
                    showlegend=False,  # Do not show legend for each subplot
                ),
                row=1,
                col=i
            )

    # Add a single legend for all subplots
    for trace in traces:
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=[None],
                mode="lines",
                line=dict(color=trace_colors[trace], dash=trace_line_styles[trace]),
                name=trace_names[trace],
            ),
            row=1,
            col=1,
        )


    fig.update_layout(
        title={
            'text': "Validator Yields - Breakdown",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        #xaxis_title="Date",
        yaxis_title="USD",
        legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="bottom",
            y=-0.5,  # Position it a bit below the x-axis
            xanchor="center",
            x=0.5,  # Center it
            font=dict(
                size=18,  # Adjust the size as needed
                color="black",
            ),
        ),
        hovermode="x",
        template="plotly_white",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"),
        plot_bgcolor='rgba(255, 255, 255, 1)', 
        paper_bgcolor='rgba(255, 255, 255, 1)', 
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    html_file_path = os.path.join(output_htmls_folder, 'validator_profit_breakdown_in_yield.html')
    fig.write_html(html_file_path)

    return fig

# Token Price
def plot_token_price_per_subset(df, subplot_titles=[]):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = make_subplots(
        rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
    )

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["polygn_price"],
                name="polygn_price",
                line=dict(color=color),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )
        

    # Add uncoloured legend for traces
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black"),
            name="Token Price",
        )
    )
    

    fig.update_layout(
        title="Validator Costs and Rewards",
        xaxis_title="Date",
        yaxis_title="USD",
        legend_title="",
        hovermode="x",
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)

    return fig

def plot_token_price(df):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)
    fig = go.Figure()

    color = next(color_cycle)
    fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == 0]["polygn_price"],
                name="polygn_price",
                line=dict(color=color),
                showlegend=False,
                hoverinfo='x+y',
            ),
        )
        
    # Add uncoloured legend for traces
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black"),
            name="Token Price",
            hoverinfo='x',
        )
    )
    
    fig.update_layout(
        title={
            'text': "POLYGN Token Price",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis_title="Date",
        yaxis_title="USD",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1),
        hovermode="x",
        template="plotly_white",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"),
        plot_bgcolor='rgba(255, 255, 255, 1)', 
        paper_bgcolor='rgba(255, 255, 255, 1)', 
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    html_file_path = os.path.join(output_htmls_folder, 'token_price.html')
    fig.write_html(html_file_path)

    return fig



def plot_revenue_profit_yields_over_issuance_curves(df):
    fig = go.Figure()

    df_subset_0 = df.query("subset == 0")
    df_subset_1 = df.query("subset == 1")


    # Add traces
    fig.add_trace(
        go.Scatter(
            x=df_subset_0.polygn_staked,
            y=df_subset_0.total_profit_yields_pct,
            name=f"Profit Yields @ 3.3B staked with 3% yield",
            line=dict(color=cadlabs_colorway_sequence[4]),
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=df_subset_0.polygn_staked,
            y=df_subset_0.total_inflation_to_validators_yields_pct,
            name=f"Inflation Yields @ 3.3B staked with 3% yield",
            line=dict(color=cadlabs_colorway_sequence[4], dash="dash"),
        ),
    )


    fig.add_trace(
        go.Scatter(
            x=df_subset_1.polygn_staked,
            y=df_subset_1.total_profit_yields_pct,
            name=f"Profit Yields @ constant 1% yield",
            line=dict(color="black"),
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=df_subset_1.polygn_staked,
            y=df_subset_1.total_inflation_to_validators_yields_pct,
            name=f"Inflation Yields @ constant 1% yield",
            line=dict(color="black", dash="dash"),
        ),
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Revenue and Profit Yields Over Issuance Curves",
        xaxis_title="POLYGN Staked (POLYGN)",
        # yaxis_title="",
        legend_title="",
    )

    # Set secondary y-axes titles
    fig.update_yaxes(title_text="Yields (%/year)")
    fig.update_layout(hovermode="x unified")

    return fig

## staking centralization
def plot_total_top_51_control_per_subset_subplots(df, subplot_titles=[]):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = make_subplots(
        rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
    )

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["total_top_51_control"],
                name="Total node number of top 51 control",
                line=dict(color=color),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )

    fig.update_layout(
        title="Staking centralization after big slashing",
        xaxis_title="Date",
        yaxis_title="Total node number of top 51 control",
        legend_title="",
        hovermode="x",
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    fig.update_annotations(font_size=12)

    return fig

def plot_total_top_33_control_per_subset_subplots(df, subplot_titles=[]):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = make_subplots(
        rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
    )

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["total_top_33_control"],
                name="Total node number of top 1/3 control",
                line=dict(color=color),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )

    fig.update_layout(
        title="Staking centralization after big slashing",
        xaxis_title="Date",
        yaxis_title="Total node number of top 1/3 control",
        legend_title="",
        hovermode="x",
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    fig.update_annotations(font_size=12)

    return fig

def plot_gini_per_subset_subplots(df, subplot_titles=[]):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = make_subplots(
        rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
    )

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["avg_gini"],
                name="Average Gini index",
                line=dict(color=color),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )

    fig.update_layout(
        title="Staking centralization after big slashing (Gini Index)",
        xaxis_title="Date",
        yaxis_title="Ave Gini Index",
        legend_title="",
        hovermode="x",
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    fig.update_annotations(font_size=12)

    return fig

def plot_hhi_per_subset_subplots(df, subplot_titles=[]):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = make_subplots(
        rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
    )

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["avg_hhi"],
                name="Average HHI index",
                line=dict(color=color),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )

    fig.update_layout(
        title="Staking centralization after big slashing (HHI Index)",
        xaxis_title="Date",
        yaxis_title="Ave HHI Index",
        legend_title="",
        hovermode="x",
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    fig.update_annotations(font_size=12)

    return fig

def plot_multichain_attack_51_per_subset_subplots(df, subplot_titles=[]):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = make_subplots(
        rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
    )

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["num_nodes_51"],
                name="Total node number who can initiate 51 attack on no less than 2 chains",
                line=dict(color=color),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )

    fig.update_layout(
        title="Total node number who can initiate 51 attack on no less than 2 chains",
        xaxis_title="Date",
        yaxis_title="Total node number",
        legend_title="",
        hovermode="x",
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    fig.update_annotations(font_size=12)

    return fig

def plot_multichain_attack_33_per_subset_subplots(df, subplot_titles=[]):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = make_subplots(
        rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
    )

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["num_nodes_33"],
                name="Total node number who can initiate 1/3 attack on no less than 2 chains",
                line=dict(color=color),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )

    fig.update_layout(
        title="Total node number who can initiate 1/3 attack on no less than 2 chains",
        xaxis_title="Date",
        yaxis_title="Total node number",
        legend_title="",
        hovermode="x",
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    fig.update_annotations(font_size=12)

    return fig

def plot_monoply_51_per_subset_subplots(df, subplot_titles=[]):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = make_subplots(
        rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
    )

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["monoply_51"],
                name="Staking share of monoply group who can initiate 51 attack",
                line=dict(color=color),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )

    fig.update_layout(
        title="Staking share of monoply group who can initiate 51 attack",
        xaxis_title="Date",
        yaxis_title="Staking share",
        legend_title="",
        hovermode="x",
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    fig.update_annotations(font_size=12)

    return fig

def plot_monoply_33_per_subset_subplots(df, subplot_titles=[]):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = make_subplots(
        rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
    )

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["monoply_33"],
                name="Staking share of monoply group who can initiate 1/3 attack",
                line=dict(color=color),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )

    fig.update_layout(
        title="Staking share of monoply group who can initiate 1/3 attack",
        xaxis_title="Date",
        yaxis_title="Staking share",
        legend_title="",
        hovermode="x",
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    fig.update_annotations(font_size=12)

    return fig


def plot_slashing_amount_per_subset(df, scenario_names):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = go.Figure()

    for subset in df.subset.unique():
        df_subset = df.query(f"subset == {subset}").copy()

        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["slashing_amount_large_service"],
                name=f"{scenario_names[subset]}",
                line=dict(color=color),
            ),
        )
        # fig.add_trace(
        #     go.Scatter(
        #         x=df["timestamp"],
        #         y=df_subset["total_profit_yields_pct"],
        #         name=f"{scenario_names[subset]} Profit Yields",
        #         line=dict(color=color, dash="dash"),
        #         visible=False,
        #     ),
        # )

    fig.update_layout(
        title="Total Slashing amount from large services in Restaking Mode",
        xaxis_title="Date",
        yaxis_title="Balance (POLYGN)",
        legend_title="",
    )

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Slashable amount",
                        method="update",
                        args=[{"visible": [True, "legendonly"]}, {"showlegend": True}],
                    ),
                    # dict(
                    #     label="Profit Yields",
                    #     method="update",
                    #     args=[{"visible": ["legendonly", True]}, {"showlegend": True}],
                    # ),
                ],
                direction="right",
                showactive=True,
                pad={"t": 10},
                x=0,
                xanchor="left",
                y=1.3,
                yanchor="top",
            )
        ]
    )

    fig.update_layout(hovermode="x unified")

    html_file_path = os.path.join(output_htmls_folder, 'slashable_amount.html')
    fig.write_html(html_file_path)

    return fig

def plot_rewards_by_validator_group_per_subset_subplots(df, subplot_titles=[]):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = make_subplots(
        rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
    )

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["total_inflation_to_validators_normal_yields"],
                name="normal",
                line=dict(color=color),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["total_inflation_to_validators_deviate_yields"],
                name="deviate",
                line=dict(color=color, dash="dash"),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["total_inflation_to_validators_yields"],
                name="aggregate",
                line=dict(color=color, dash="dot"),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )


    for subset in df.subset.unique():
        fig.add_shape(
            go.layout.Shape(
                type="line",
                x0=df.loc[1,["timestamp"]].values,
                y0=0,
                x1=df.tail(1)['timestamp'].values,
                y1=0,
                line=dict(color='red',width=6,dash="dashdot"),
            ),
            row=1,
            col=subset + 1,
        )


    # Add uncoloured legend for traces
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black"),
            name="Normal",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black", dash="dash"),
            name="Deviate",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black", dash="dot"),
            name="aggregate",
        )
    )

    fig.update_layout(
        title="Inflation Yield - Normal and Deviate Validator Group",
        xaxis_title="Date",
        yaxis_title="Yields",
        legend_title="",
        hovermode="x",
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    fig.update_annotations(font_size=12)

    return fig


def plot_rewards_usd_by_validator_group_per_subset_subplots(df, subplot_titles=[]):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = make_subplots(
        rows=1, cols=len(subplot_titles), shared_yaxes=True, subplot_titles=subplot_titles
    )

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["total_inflation_to_validators_normal_usd"],
                name="normal",
                line=dict(color=color),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["total_inflation_to_validators_deviate_usd"],
                name="deviate",
                line=dict(color=color, dash="dash"),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )


    for subset in df.subset.unique():
        fig.add_shape(
            go.layout.Shape(
                type="line",
                x0=df.loc[1,["timestamp"]].values,
                y0=0,
                x1=df.tail(1)['timestamp'].values,
                y1=0,
                line=dict(color='red',width=6,dash="dashdot"),
            ),
            row=1,
            col=subset + 1,
        )


    # Add uncoloured legend for traces
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black"),
            name="Normal",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black", dash="dash"),
            name="Deviate",
        )
    )

    fig.update_layout(
        title="Inflation USD per step - Normal and Deviate Validator Group",
        xaxis_title="Date",
        yaxis_title="USD (per step)",
        legend_title="",
        hovermode="x",
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    fig.update_annotations(font_size=12)

    return fig


def plot_treasury_balance(df):
    color_cycle = itertools.cycle(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])
    fig = go.Figure()

    color = next(color_cycle)
    fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                #y=df[df.subset == 0]["cumulative_treasury_balance_usd"],
                y=df[df.subset == 0]["annual_treasury_inflow"],
                #y=df[df.subset == 0]["total_inflation_to_validators_usd"],
                name="Treasury balance",
                line=dict(color=color),
                showlegend=False,
                hoverinfo='x+y',
            ),
        )
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Annual Treasury Inflow",
        hovermode="x",
        template="plotly_white",
        font=dict(
            family="Arial",
            size=18,
            color="black"),
        plot_bgcolor='rgba(255, 255, 255, 1)', 
        paper_bgcolor='rgba(255, 255, 255, 1)', 
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    html_file_path = os.path.join(output_htmls_folder, 'treasury_inflow.html')
    fig.write_html(html_file_path)

    fig.update_layout(autosize=False, width=900, height=600)
    jpeg_file_path = os.path.join(output_images_folder, 'treasury_inflow.jpeg')
    pio.write_image(fig, jpeg_file_path)

    return fig


def plot_treasury_balance_barplot(df):
    color_cycle = itertools.cycle(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])
    fig = go.Figure()
    annual_treasury_inflow =  df[df.subset == 0].groupby(['year'])['total_inflation_to_validators_usd'].sum().reset_index()
    fig = px.bar(annual_treasury_inflow, x='year', y='total_inflation_to_validators_usd', barmode='group',color_discrete_sequence=['#1f77b4'])
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Annual Treasury Inflow",
        hovermode="x",
        template="plotly_white",
        font=dict(
            family="Arial",
            size=18,
            color="black"),
        plot_bgcolor='rgba(255, 255, 255, 1)', 
        paper_bgcolor='rgba(255, 255, 255, 1)', 
    )


    update_legend_names(fig)
    fig.write_html('../../outputs/htmls/treasury_inflow_barplot.html')

    fig.update_layout(autosize=False, width=900, height=600)
    pio.write_image(fig, '../../outputs/jpegs/treasury_inflow_barplot.jpeg')

    return fig


## Emission Model
def create_emission_df():
    # Define the duration
    start_date = datetime.today()
    end_date = start_date.replace(year=start_date.year + 15)
    dates = pd.date_range(start=start_date, end=end_date, freq='M')

    # Initialize the DataFrame
    df = pd.DataFrame(index=dates)
    df.index.name = 'timestamp'

    # Define the inflation rates for the first 10 years
    first_10_years = (df.index.year - start_date.year < 10)

    df['option_1'] = 0.01  # Option 1: The inflation rate remains at 1% for the entire duration
    df.loc[first_10_years, 'option_2'] = 0.01  # Option 2: The inflation rate is 1% for the first 10 years
    df.loc[first_10_years, 'option_3'] = 0.01  # Option 3: The inflation rate is 1% for the first 10 years
    df.loc[first_10_years,'curve_group'] = 0

    # Define the inflation rates for the last 5 years
    last_5_years = ~first_10_years

    # Convert date index to series
    date_series = pd.Series(df.index)

    # Calculate the years into last 5 years
    years_into_last_5 = (df.index[last_5_years].year - df.index[last_5_years].year.min()) + \
                        (df.index[last_5_years].month - df.index[last_5_years].month.min()) / 12

    # Option 2: The inflation rate decreases quadratically
    df.loc[last_5_years, 'option_2'] = np.maximum(0.01 * (1 - (years_into_last_5 / 7) ** 2),0)

    # Option 3: The inflation rate decreases exponentially
    df.loc[last_5_years, 'option_3'] = np.maximum(0.01 * (1 - (years_into_last_5 / 3) ** 2),0)

    # mark the last 5 years as curve group 1
    df.loc[last_5_years,'curve_group'] = 1

    df.reset_index(level=0, inplace=True)

    return df


def plot_validator_emission_model(df):
    fig = go.Figure()

    for i in range(3):
        # Split the data into two parts
        df_first_10_years = df[df['timestamp'].dt.year - df['timestamp'].dt.year.min() < 10]
        df_last_5_years = df[df['timestamp'].dt.year - df['timestamp'].dt.year.min() >= 10]

        # Add the trace for the first 10 years with a solid line
        fig.add_trace(
                go.Scatter(
                    x=df_first_10_years["timestamp"],
                    y=df_first_10_years[f'option_{i+1}'],
                    name="Inflation Model " + str(i+1),
                    line=dict(color='red'),
                    showlegend=False,
                ),
            )
        
        # Add the trace for the last 5 years with a dotted line
        fig.add_trace(
                go.Scatter(
                    x=df_last_5_years["timestamp"],
                    y=df_last_5_years[f'option_{i+1}'],
                    name="Inflation Model " + str(i+1),
                    line=dict(color='red',dash='dot'),
                    showlegend=False,
                ),
            )
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Validator Emission",
        yaxis=dict(
            tickmode='array',
            tickvals=[0.005, 0.01, 0.015],
            ticktext=['0.5%', '1.0%', '1.5%'],
            range=[0, 0.016]
        ),
        hovermode="x",
        template="plotly_white",
        font=dict(
            family="Arial",
            size=18,
            color="black"),
        plot_bgcolor='rgba(255, 255, 255, 1)', 
        paper_bgcolor='rgba(255, 255, 255, 1)', 
    )

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    html_file_path = os.path.join(output_htmls_folder, 'Validator_emission_model.html')
    fig.write_html(html_file_path)

    fig.update_layout(autosize=False, width=900, height=600)
    jpeg_file_path = os.path.join(output_images_folder, 'Validator_emission_model.jpeg')
    pio.write_image(fig, jpeg_file_path)

    return fig


def plot_treasury_emission_model(df):
    fig = go.Figure()

    for i in range(3):
        # Split the data into two parts
        df_first_10_years = df[df['timestamp'].dt.year - df['timestamp'].dt.year.min() < 10]
        df_last_5_years = df[df['timestamp'].dt.year - df['timestamp'].dt.year.min() >= 10]

        # Add the trace for the first 10 years with a solid line
        fig.add_trace(
                go.Scatter(
                    x=df_first_10_years["timestamp"],
                    y=df_first_10_years[f'option_{i+1}'],
                    name="Inflation Model " + str(i+1),
                    line=dict(color='#1f77b4'),
                    showlegend=False,
                ),
            )
        
        # Add the trace for the last 5 years with a dotted line
        fig.add_trace(
                go.Scatter(
                    x=df_last_5_years["timestamp"],
                    y=df_last_5_years[f'option_{i+1}'],
                    name="Inflation Model " + str(i+1),
                    line=dict(color='#1f77b4',dash='dot'),
                    showlegend=False,
                ),
            )
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Treasury Emission",
        yaxis=dict(
            tickmode='array',
            tickvals=[0.005, 0.01, 0.015],
            ticktext=['0.5%', '1.0%', '1.5%'],
            range=[0, 0.016]
        ),
        hovermode="x",
        template="plotly_white",
        font=dict(
            family="Arial",
            size=18,
            color="black"),
        plot_bgcolor='rgba(255, 255, 255, 1)', 
        paper_bgcolor='rgba(255, 255, 255, 1)', 
    )

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)
    html_file_path = os.path.join(output_htmls_folder, 'Treasury_emission_model.html')
    fig.write_html(html_file_path)

    fig.update_layout(autosize=False, width=900, height=600)
    jpeg_file_path = os.path.join(output_images_folder, 'Treasury_emission_model.jpeg')
    pio.write_image(fig, jpeg_file_path)
    
    return fig