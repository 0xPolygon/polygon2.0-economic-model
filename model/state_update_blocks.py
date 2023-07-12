"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""

import model.parts.hub_system as hub
import model.parts.pos_incentives as incentives
import model.parts.system_metrics as metrics
import model.parts.validators as validators
import model.parts.treasury as treasury
import model.parts.staking as staking
import model.parts.supernets as supernets
import model.parts.events as events
import model.parts.decentralization as decentralization
from model.system_parameters import parameters
from model.utils import update_from_signal

# Edited
state_update_block_stages = {
    "description": """
        Transition between stages of network upgrade process
    """,
    "policies": {"upgrade_stages": hub.policy_upgrade_stages},
    "variables": {
        "stage": update_from_signal("stage"),
        "timestamp": update_from_signal("timestamp"),
    },
}

# Added
state_update_slashing_event = {
    "description": """
        Update slashing events
    """,
    "policies": {"slashing": events.event_slashing_on_large_service},
    "variables": {
        "stage": update_from_signal("stage"),
        "staking_metrics": update_from_signal("staking_metrics"),
        "polygn_staked_per_validator": update_from_signal("polygn_staked_per_validator"),
        "polygn_staked": update_from_signal("polygn_staked"),
        "validator_group_by_event": update_from_signal("validator_group_by_event"),
        "unassigned_rewards_ratio": update_from_signal("unassigned_rewards_ratio"),
    },
}

# Added
state_supernets = {
        "description": """
            Update Supernets Adoption
        """,
        "policies": {
            "supernets": supernets.policy_new_supernet_staking,
        },
        "variables": {
            "chain_specific_checkpoint_submission_cadence": update_from_signal("chain_specific_checkpoint_submission_cadence"),
            "liveness_metrics": update_from_signal("liveness_metrics"),
            "staking_metrics": update_from_signal("staking_metrics"),
            "PRIVATE_CHAINS_CNT": update_from_signal("PRIVATE_CHAINS_CNT"),
            "PUBLIC_CHAINS_CNT": update_from_signal("PUBLIC_CHAINS_CNT"),
            "share_by_validator_in_SingleStaking": update_from_signal("share_by_validator_in_SingleStaking"),
        },
}

state_multistaking_metrics_update = {
        "description": """
            Update multistaking by Gaussian sampling
        """,
        "policies": {
            "multistaking_metrics_update": staking.policy_staking_multistaking_sampling,
        },
        "variables": {
            "staking_metrics": update_from_signal("staking_metrics"),
        },
}

# Edited
state_update_block_polygon = {
    "description": """
        Environmental Polygon processes:
        * POLYGN price update
        * Staking of POLYGN for new validators
    """,
    "policies": {
        "staking": validators.policy_staking,
    },
    "variables": {
        "polygn_price": hub.update_polygn_price,
        "polygn_staked": update_from_signal("polygn_staked"),
    },
}

# Edited
state_update_block_validators = {
    "description": """
        Environmental validator processes:
        * Validator activation queue
        * Validator rotation
        * Validator uptime
    """,
    "policies": {
        "policy_validators": validators.policy_validators,
    },
    "variables": {
        "number_of_validators_in_activation_queue": update_from_signal(
            "number_of_validators_in_activation_queue"
        ),
        "number_of_active_validators": update_from_signal(
            "number_of_active_validators"
        ),
        "number_of_awake_validators": update_from_signal("number_of_awake_validators"),
        "validator_uptime": update_from_signal("validator_uptime"),
    },
}

# TODO: Add update function to sync with staking hub
# state_eip1559 = {
#         "description": """
#             EIP-1559 transaction pricing for public chain
#         """,
#         "policies": {
#             "eip1559": hub.policy_eip1559_transaction_pricing,
#         },
#         "variables": {
#             "public_base_fee_to_domain_treasury": update_from_signal("public_base_fee_to_domain_treasury"),
#             "private_base_fee_to_domain_treasury": update_from_signal("private_base_fee_to_domain_treasury"),
#             "total_priority_fee_to_validators": update_from_signal(
#                 "total_priority_fee_to_validators"
#             ),
#             "total_priority_fee_to_validators_usd": update_from_signal(
#                 "total_priority_fee_to_validators_usd"
#             ),
#             "private_treasury_balance": update_from_signal("private_treasury_balance"),
#         },
# }

state_txn_pricing = {
        "description": """
            EIP-1559 transaction pricing for public chain
        """,
        "policies": {
            "eip1559": hub.policy_transaction_pricing,
        },
        "variables": {
            "total_txn_fee_to_validators": update_from_signal(
                "total_txn_fee_to_validators"
            ),
            "total_txn_fee_to_validators_usd": update_from_signal(
                "total_txn_fee_to_validators_usd"
            ),
        },
}

# Added
state_treasury = {
        "description": """
            Domian treasury balance
        """,
        "policies": {
            "treasury": treasury.policy_domain_treasury_balance,
        },
        "variables": {
            "domain_treasury_balance_locked": update_from_signal("domain_treasury_balance_locked"),
        },
}

_state_update_blocks = [
    {
        "description": """
            Average effective balance & base reward
        """,
        "policies": {
            "average_effective_balance": validators.policy_average_effective_balance,
        },
        "variables": {
            "average_effective_balance": update_from_signal(
                "average_effective_balance"
            ),
        },
    },
    {
        "description": """
            Inflation amount
        """,
        "policies": {
            "inflation": hub.policy_inflation,
        },
        "variables": {
            "total_inflation_to_validators": update_from_signal(
                "total_inflation_to_validators"
            ),
            "total_inflation_to_validators_usd": update_from_signal(
                "total_inflation_to_validators_usd"
            ),
            "total_inflation_to_validators_normal": update_from_signal(
                "total_inflation_to_validators_normal"
            ),
            "total_inflation_to_validators_normal_usd": update_from_signal(
                "total_inflation_to_validators_normal_usd"
            ),
            "total_inflation_to_validators_deviate": update_from_signal(
                "total_inflation_to_validators_deviate"
            ),
            "total_inflation_to_validators_deviate_usd": update_from_signal(
                "total_inflation_to_validators_deviate_usd"
            ),
        },
    },
    {
        "description": """
            Slashing rewards & penalties
        """,
        "policies": {
            "slashing": incentives.policy_slashing,
        },
        "variables": {
            "amount_slashed": update_from_signal("amount_slashed"),
        },
    },
    {
        "description": """
            Online validator reward aggregation
        """,
        "policies": {
            "livenss": staking.policy_signature_check,
        },
        "variables": {
            "liveness_metrics": update_from_signal(
                "liveness_metrics"
            ),
        },
    },
    {
        "description": """
            Signature Checks
        """,
        "policies": {
            "calculate_total_online_validator_rewards": metrics.policy_total_online_validator_rewards,
        },
        "variables": {
            "total_online_validator_rewards": update_from_signal(
                "total_online_validator_rewards"
            ),
        },
    },
    {
        "description": """
            Accounting of Hub issuance & inflation
        """,
        "policies": {
            "issuance": hub.policy_network_issuance,
        },
        "variables": {
            "polygn_supply": hub.update_polygn_supply,
            "supply_inflation": metrics.update_supply_inflation,
            "network_issuance": update_from_signal("network_issuance"),

        },
    },
    {
        "description": """
            Accounting of validator costs and online validator rewards
        """,
        "post_processing": False,
        "policies": {
            "metric_validator_costs": metrics.policy_validator_costs,
        },
        "variables": {
            "validator_count_distribution": update_from_signal(
                "validator_count_distribution"
            ),
            "validator_hardware_costs": update_from_signal("validator_hardware_costs"),
            # "validator_cloud_costs": update_from_signal("validator_cloud_costs"),
            # "validator_third_party_costs": update_from_signal(
            #     "validator_third_party_costs"
            # ),
            "validator_checkpoint_costs": update_from_signal("validator_checkpoint_costs"),
            "total_network_costs": update_from_signal("total_network_costs"),
        },
    },
    {
        "description": """
            Accounting of validator yield metrics
        """,
        "post_processing": False,
        "policies": {
            "yields": metrics.policy_validator_yields,
        },
        "variables": {
            "validator_polygn_staked": update_from_signal("validator_polygn_staked"),
            "validator_revenue": update_from_signal("validator_revenue"),
            "validator_profit": update_from_signal("validator_profit"),
            "validator_revenue_yields": update_from_signal("validator_revenue_yields"),
            "validator_profit_yields": update_from_signal("validator_profit_yields"),
            "total_revenue": update_from_signal("total_revenue"),
            "total_profit": update_from_signal("total_profit"),
            "total_revenue_yields": update_from_signal("total_revenue_yields"),
            "total_profit_yields": update_from_signal("total_profit_yields"),
            "validator_checkpoint_costs_yields": update_from_signal(
                "validator_checkpoint_costs_yields"
            ),
            "validator_hardware_costs_yields": update_from_signal(
                "validator_hardware_costs_yields"
            ),
            "total_txn_fee_to_validators_yields": update_from_signal(
                "total_txn_fee_to_validators_yields"
            ),
            "total_inflation_to_validators_yields": update_from_signal(
                "total_inflation_to_validators_yields"
            ),
            "total_inflation_to_validators_normal_yields": update_from_signal(
                "total_inflation_to_validators_normal_yields"
            ),
            "total_inflation_to_validators_deviate_yields": update_from_signal(
                "total_inflation_to_validators_deviate_yields"
            ),
                   
        },
    },
    {
        "description": """
            Calculate decentralization/centralization metrics
        """,
        "post_processing": False,
        "policies": {
            "yields": decentralization.policy_staking_centralization_metric,
        },
        "variables": {
            "staking_centralization_metrics_51": update_from_signal("staking_centralization_metrics_51"),
            "staking_centralization_metrics_33": update_from_signal("staking_centralization_metrics_33"),
            "avg_gini": update_from_signal("avg_gini"),
            "avg_hhi": update_from_signal("avg_hhi"),
            "total_top_51_control": update_from_signal("total_top_51_control"),
            "total_top_33_control": update_from_signal("total_top_33_control"),   
            "num_nodes_51": update_from_signal("num_nodes_51"),
            "num_nodes_33": update_from_signal("num_nodes_33"),
            "node_counts_51_array": update_from_signal("node_counts_51_array"),
            "node_counts_33_array": update_from_signal("node_counts_33_array"),               
        },
    },
    {
        "description": """
            Calculate monoply metrics
        """,
        "post_processing": False,
        "policies": {
            "yields": decentralization.policy_monoply,
        },
        "variables": {
            "monoply_51": update_from_signal("monoply_51"),
            "monoply_33": update_from_signal("monoply_33"),            
        },
    },
    {
        "description": """
            Calculate system total slashable amount for large services
        """,
        "post_processing": False,
        "policies": {
            "yields": decentralization.policy_slashable_amount,
        },
        "variables": {
            "slashing_amount_large_service": update_from_signal("slashing_amount_large_service"),         
        },
    },    
]



# Conditionally update the order of the State Update Blocks using a ternary operator
_state_update_blocks = (
    # If driving with environmental ETH staked process, structure as follows:
    [
        state_update_block_stages,
        state_update_block_polygon,
        state_update_slashing_event,
        state_supernets,
        state_txn_pricing, 
        state_update_block_validators,
        state_treasury,
        
    ]
    + _state_update_blocks
    if parameters["polygn_staked_process"][0](0, 0) is not None
    # Otherwise, if driving with validator adoption (implied ETH staked) process, switch Ethereum and validator blocks:
    else [
        state_update_block_stages,
        state_update_block_polygon,
        state_update_slashing_event,
        state_supernets,
        state_txn_pricing,
        state_update_block_validators,
        state_treasury,
    ]
    + _state_update_blocks
)

# Split the state update blocks into those used during the simulation (state_update_blocks)
# and those used in post-processing to calculate the system metrics (post_processing_blocks)
state_update_blocks = [
    block for block in _state_update_blocks if not block.get("post_processing", False)
]
post_processing_blocks = [
    block for block in _state_update_blocks if block.get("post_processing", False)
]
