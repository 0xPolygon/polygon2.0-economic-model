import itertools
import math
from datetime import datetime
import numpy as np

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ipywidgets import widgets
from plotly.subplots import make_subplots

from experiments.notebooks.visualizations.plotly_theme import (
    cadlabs_colors,
    cadlabs_colorway_sequence,
)
import model.constants as constants


# Set plotly as the default plotting backend for pandas
pd.options.plotting.backend = "plotly"

def plot_yeilds_per_subset(dfs, scenario_names):
    num_of_subsets = len(dfs)
    color_scale = px.colors.sequential.Plasma
    color_generator = (color_scale[i] for i in np.linspace(0, len(color_scale) - 1, num_of_subsets).astype(int))

    fig = go.Figure()

    for subset, df in dfs.items(): # each subset
        color = next(color_generator)
        
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["total_revenue_yields_pct"],
                name=f"{scenario_names[subset]}",
                line=dict(color=color),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["total_profit_yields_pct"],
                name=f"{scenario_names[subset]} Profit Yields",
                line=dict(color=color, dash="dash"),
                visible=False,
            ),
        )

    fig.update_layout(
        title="Revenue and Profit Yields Over Time - At a Glance",
        xaxis_title="Date",
        yaxis_title="Revenue Yields (%/year)",
        legend_title="",
    )

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Revenue",
                        method="update",
                        args=[{"visible": [True, "legendonly"]}, {"showlegend": True}],
                    ),
                    dict(
                        label="Profit",
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

    fig.write_html('/Users/wenxuan/Desktop/polygon/cadCAD/Token-Redesign/experiments/notebooks/visualizations/plots/yields.html')

    return fig

def plot_rewards_by_validator_group_per_subset(dfs, scenario_names):
    num_of_subsets = len(dfs)
    color_scale = px.colors.sequential.Plasma
    color_generator = (color_scale[i] for i in np.linspace(0, len(color_scale) - 1, num_of_subsets).astype(int))

    fig = go.Figure()

    for subset, df in dfs.items(): # each subset
        color = next(color_generator)
        
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["total_inflation_to_validators_normal_usd"],
                name=f"{scenario_names[subset]}-normal",
                line=dict(color=color),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["total_inflation_to_validators_deviate_usd"],
                name=f"{scenario_names[subset]}-deviate",
                line=dict(color=color, dash="dash"),
                #visible=False,
            ),
        )

    fig.update_layout(
        title="Inflation _usd - Normal and Deviate Validator Group",
        xaxis_title="Date",
        yaxis_title="USD",
        legend_title="",
        hovermode="x",
    )
    
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

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Normal",
                        method="update",
                        args=[{"visible": np.tile([True, False], num_of_subsets).tolist()}, {"showlegend": True}],
                    ),
                    dict(
                        label="Deviate",
                        method="update",
                        args=[{"visible": np.tile([False, True], num_of_subsets).tolist()}, {"showlegend": True}],
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

    fig.write_html('/Users/wenxuan/Desktop/polygon/cadCAD/Token-Redesign/experiments/notebooks/visualizations/plots/rewards_usd.html')

    return fig

def plot_multichain_attack_51_per_subset(dfs, scenario_names):
    num_of_subsets = len(dfs)
    color_scale = px.colors.sequential.Plasma
    color_generator = (color_scale[i] for i in np.linspace(0, len(color_scale) - 1, num_of_subsets).astype(int))

    fig = go.Figure()

    for subset, df in dfs.items(): # each subset
        color = next(color_generator)
        
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["num_nodes_51"],
                name=f"{scenario_names[subset]}-51",
                line=dict(color=color),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["num_nodes_33"],
                name=f"{scenario_names[subset]}-33",
                line=dict(color=color),
            ),
        )
    

    fig.update_layout(
        title="Total node number who can initiate 51/33 attack on no less than 2 chains",
        xaxis_title="Date",
        yaxis_title="Total node number",
        legend_title="",
        hovermode="x",
    )
    
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black"),
            name="51",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black", dash="dash"),
            name="33",
        )
    )

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="51",
                        method="update",
                        args=[{"visible": np.tile([True, False], num_of_subsets).tolist()}, {"showlegend": True}],
                    ),
                    dict(
                        label="33",
                        method="update",
                        args=[{"visible": np.tile([False, True], num_of_subsets).tolist()}, {"showlegend": True}],
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
    fig.write_html('/Users/wenxuan/Desktop/polygon/cadCAD/Token-Redesign/experiments/notebooks/visualizations/plots/attack_nodes_number.html')

    return fig


def plot_monopoly_per_subset(dfs, scenario_names):
    num_of_subsets = len(dfs)
    color_scale = px.colors.sequential.Plasma
    color_generator = (color_scale[i] for i in np.linspace(0, len(color_scale) - 1, num_of_subsets).astype(int))

    fig = go.Figure()

    for subset, df in dfs.items(): # each subset
        color = next(color_generator)
        
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["monoply_51"],
                name=f"{scenario_names[subset]}-51",
                line=dict(color=color),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["monoply_33"],
                name=f"{scenario_names[subset]}-33",
                line=dict(color=color),
            ),
        )
    

    fig.update_layout(
        title="Staking share of monopoly group who can initiate 51/33 attack",
        xaxis_title="Date",
        yaxis_title="Staking share",
        legend_title="",
        hovermode="x",
    )
    
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black"),
            name="51",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black", dash="dash"),
            name="33",
        )
    )

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="51",
                        method="update",
                        args=[{"visible": np.tile([True, False], num_of_subsets).tolist()}, {"showlegend": True}],
                    ),
                    dict(
                        label="33",
                        method="update",
                        args=[{"visible": np.tile([False, True], num_of_subsets).tolist()}, {"showlegend": True}],
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
    fig.write_html('/Users/wenxuan/Desktop/polygon/cadCAD/Token-Redesign/experiments/notebooks/visualizations/plots/monopoly_set_staking_share.html')

    return fig

def plot_staking_centralization_per_subset(dfs, scenario_names):
    num_of_subsets = len(dfs)
    color_scale = px.colors.sequential.Plasma
    color_generator = (color_scale[i] for i in np.linspace(0, len(color_scale) - 1, num_of_subsets).astype(int))

    fig = go.Figure()

    for subset, df in dfs.items(): # each subset
        color = next(color_generator)
        
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["avg_gini"],
                name=f"{scenario_names[subset]}-gini",
                line=dict(color=color),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["avg_hhi"],
                name=f"{scenario_names[subset]}-hhi",
                line=dict(color=color),
            ),
        )
    

    fig.update_layout(
        title="Staking centralization after big slashing (Gini/HHI Index)",
        xaxis_title="Date",
        yaxis_title="Ave Gini Index",
        legend_title="",
        hovermode="x",
    )
    
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black"),
            name="gini",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black", dash="dash"),
            name="hhi",
        )
    )

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="gini",
                        method="update",
                        args=[{"visible": np.tile([True, False], num_of_subsets).tolist()}, {"showlegend": True}],
                    ),
                    dict(
                        label="hhi",
                        method="update",
                        args=[{"visible": np.tile([False, True], num_of_subsets).tolist()}, {"showlegend": True}],
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
    fig.write_html('/Users/wenxuan/Desktop/polygon/cadCAD/Token-Redesign/experiments/notebooks/visualizations/plots/staking_centralization.html')

    return fig