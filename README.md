# Polygon Economic Model

[![Python package](https://github.com/CADLabs/ethereum-model/actions/workflows/python.yml/badge.svg)](https://github.com/CADLabs/ethereum-model/actions/workflows/python.yml)

A modular dynamical-systems model of Ethereum's validator economics, based on the open-source Python library [radCAD](https://github.com/CADLabs/radCAD), an extension to [cadCAD](https://cadcad.org).

## Table of Contents

* [Introduction](#Introduction)
  * [Model Features](#Model-Features)
  * [Directory Structure](#Directory-Structure)
  * [Model Architecture](#Model-Architecture)
  * [Model Assumptions](#Model-Assumptions)
  * [Mathematical Model Specification](#Mathematical-Model-Specification)
  * [Differential Model Specification](#Differential-Model-Specification)
* [Environment Setup](#Environment-Setup)
* [Simulation Experiments](#Simulation-Experiments)
* [Model Extension Roadmap](#Model-Extension-Roadmap)
* [Tests](#Tests)
* [Change Log](#Change-Log)
* [Acknowledgements](#Acknowledgements)
* [Contributors](#Contributors-)
* [License](#License)

---

## Introduction

This open-source model was developed in collaboration with the Ethereum Robust Incentives Group and funded by an Ethereum ESP (Ecosystem Support Program) grant. While originally scoped with purely modelling-educational intent as part of the cadCAD Edu online course "[cadCAD Masterclass: Ethereum Validator Economics](https://www.cadcad.education/course/masterclass-ethereum)", it has evolved to become a highly versatile, customizable and extensible research model that includes a list of [model extension ideas](#Model-Extension-Roadmap). The model is focused on epoch- and population-level Ethereum validator economics across different deployment types and – at least in its initial setup – abstracts from slot- and agent-level dynamics. Please see [Model Assumptions](ASSUMPTIONS.md) for further context.


### Directory Structure

* [data/](data/): Datasets and API data sources (such as Etherscan.io and Beaconcha.in) used in the model
* [docs/](docs/): Misc. documentation such as auto-generated docs from Python docstrings and Markdown docs
* [experiments/](experiments/): Analysis notebooks and experiment workflow (such as configuration and execution)
* [logs/](logs/): Experiment runtime log files
* [model/](model/): Model software architecture (structural and configuration modules)
* [tests/](tests/): Unit and integration tests for model and notebooks

### Model Architecture

The [model/](model/) directory contains the model's software architecture in the form of two categories of modules: structural modules and configuration modules.

#### Structural Modules

The model is composed of several structural modules in the [model/parts/](model/parts/) directory:

| Module | Description |
| --- | --- |
| [ethereum_system.py](model/parts/ethereum_system.py) | General Ethereum mechanisms, such as managing the system upgrade process, the EIP-1559 transaction pricing mechanism, and updating the ETH price and ETH supply |
| [pos_incentives.py](model/parts/pos_incentives.py) | Calculation of PoS incentives such as attestation and block proposal rewards and penalties |
| [system_metrics.py](model/parts/system_metrics.py) | Calculation of metrics such as validator operational costs and yields |
| [validators.py](model/parts/validators.py) | Validator processes such as validator activation, staking, and uptime |
| [utils/ethereum_spec.py](model/parts/utils/ethereum_spec.py) | Relevant extracts from the official Eth2 spec |

#### Configuration Modules

The model is configured using several configuration modules in the [model/](model/) directory:

| Module | Description |
| --- | --- |
| [constants.py](model/constants.py) | Constants used in the model, e.g. number of epochs in a year, Gwei in 1 Ether |
| [state_update_blocks.py](model/state_update_blocks.py) | cadCAD model State Update Block structure, composed of Policy and State Update Functions |
| [state_variables.py](model/state_variables.py) | Model State Variable definition, configuration, and defaults |
| [stochastic_processes.py](model/stochastic_processes.py) | Helper functions to generate stochastic environmental processes |
| [system_parameters.py](model/system_parameters.py) | Model System Parameter definition, configuration, and defaults |
| [types.py](model/types.py) | Various Python types used in the model, such as the `Stage` Enum and calculation units |
| [utils.py](model/utils.py) | Misc. utility and helper functions |

### Model Assumptions

The model implements the official Ethereum Specification wherever possible, but rests on a few default network-level and validator-level assumptions detailed in the [ASSUMPTIONS.md](ASSUMPTIONS.md) document.

### Mathematical Model Specification

The [Mathematical Model Specification](https://hackmd.io/@CADLabs/ryLrPm2T_) articulates the relevant system dynamics as a state-space representation, the mathematical modelling paradigm underlying the cadCAD simulation library. It can be understood as a minimum viable formalism necessary to enable solid cadCAD modelling.

### Differential Model Specification

The [Differential Model Specification](https://hackmd.io/@CADLabs/HyENPQ36u) depicts the model's overall structure across System States, System Inputs, System Parameters, State Update Logic and System Metrics.

## Environment Setup

1. Clone or download the Git repository: `git clone https://github.com/CADLabs/ethereum-model` or using GitHub Desktop
2. If completing the cadCAD Edu Masterclass MOOC, find and check out the latest ["Masterclass 🎓" release version](https://github.com/CADLabs/ethereum-economic-model/releases): e.g. `git checkout v.1.1.7`
3. Set up your development environment using one of the following three options:

### Option 1: Anaconda Development Environment

This option guides you through setting up a cross-platform, beginner-friendly (yet more than capable enough for the advanced user) development environment using Anaconda to install Python 3 and Jupyter. There is also a video that accompanies this option and walks through all the steps: [Model Quick-Start Guide](https://www.cadcad.education/course/masterclass-ethereum)

1. Download [Anaconda](https://www.anaconda.com/products/individual)
2. Use Anaconda to install Python 3
3. Set up a virtual environment from within Anaconda
4. Install Jupyter Notebook within the virtual environment
5. Launch Jupyter Notebook and open the [environment_setup.ipynb](environment_setup.ipynb) notebook in the root of the project repo
6. Follow and execute all notebook cells to install and check your Python dependencies

### Option 2: Custom Development Environment

This option guides you through how to set up a custom development environment using Python 3 and Jupyter.

Please note the following prerequisites before getting started:
* Python: tested with versions 3.7, 3.8, 3.9
* NodeJS might be needed if using Plotly with Jupyter Lab (Plotly works out the box when using the Anaconda/Conda package manager with Jupyter Lab or Jupyter Notebook)

First, set up a Python 3 [virtualenv](https://docs.python.org/3/library/venv.html) development environment (or use the equivalent Anaconda step):
```bash
# Create a virtual environment using Python 3 venv module
python3 -m venv venv
# Activate virtual environment
source venv/bin/activate
```

Make sure to activate the virtual environment before each of the following steps.

Secondly, install the Python 3 dependencies using [Pip](https://packaging.python.org/tutorials/installing-packages/), from the [requirements.txt](requirements.txt) file within your new virtual environment:
```bash
# Install Python 3 dependencies inside virtual environment
pip install -r requirements.txt
```

To create a new Jupyter Kernel specifically for this environment, execute the following command:
```bash
python3 -m ipykernel install --user --name python-cadlabs-eth-model --display-name "Python (CADLabs Ethereum Economic Model)"
```

You'll then be able to select the kernel with display name `Python (CADLabs Ethereum Economic Model)` to use for your notebook from within Jupyter.

To start Jupyter Notebook or Lab (see notes about issues with [using Plotly with Jupyter Lab](#Known-Issues)):
```bash
jupyter notebook
# Or:
jupyter lab
```

For more advanced Unix/macOS users, a [Makefile](Makefile) is also included for convenience that simply executes all the setup steps. For example, to setup your environment and start Jupyter Lab:
```bash
# Setup environment
make setup
# Start Jupyter Lab
make start-lab
```

### Option 3: Docker Development Environment

Alternatively, you can set up your development environment using the pre-built Docker image with all the dependencies you need: [CADLabs Jupyter Lab Environment](https://github.com/CADLabs/jupyter-lab-environment)

### Known Issues

#### Plotly doesn't display in Jupyter Lab

To install and use Plotly with Jupyter Lab, you might need NodeJS installed to build Node dependencies, unless you're using the Anaconda/Conda package manager to manage your environment. Alternatively, use Jupyter Notebook which works out the box with Plotly.

See https://plotly.com/python/getting-started/

You might need to install the following "lab extension": 
```bash
jupyter labextension install jupyterlab-plotly@4.14.3
```

#### Windows Issues

If you receive the following error and you use Anaconda, try: `conda install -c anaconda pywin32`
> DLL load failed while importing win32api: The specified procedure could not be found.

## Simulation Experiments

The [experiments/](experiments/) directory contains modules for configuring and executing simulation experiments, as well as performing post-processing of the results.

The [experiments/notebooks/](experiments/notebooks/) directory contains initial validator-level and network-level experiment notebooks and analyses. These notebooks and analyses do not aim to comprehensively illuminate the Ethereum protocol, but rather to suggest insights into a few salient questions the Ethereum community has been discussing, and to serve as inspiration for researchers building out their own, customized analyses and structural model extensions.

The [Experiment README notebook](experiments/notebooks/0_README.ipynb) contains an overview of how to execute existing experiment notebooks, and how to configure and execute new ones.

#### Notebook 1. Model Validation

The purpose of this notebook is to recreate selected simulations from the widely acknowledged Hoban/Borgers Ethereum 2.0 Economic Model using the CADLabs model, and to compare the results. We suggest that the CADLabs model has a high degree of validity.

#### Notebook 2. Validator Revenue and Profit Yields (Validator-level Analysis)

The purpose of this notebook is to explore the returns validators can expect from staking in the Ethereum protocol across different time horizons, adoption scenarios, ETH price scenarios and validator environments.

* Analysis 1: Revenue and Profit Yields Over Time
* Analysis 2: Revenue and Profit Yields Over ETH Staked
* Analysis 3: Revenue and Profit Yields Over ETH Price
* Analysis 4: Profit Yields Over ETH Staked vs. ETH Price (Yield Surface)
* Analysis 5: Profit Yields By Validator Environment Over Time

#### Notebook 3. Network Issuance and Inflation Rate (Network-level Analysis)

The purpose of this notebook is to explore ETH issuance and the resulting annualized inflation rate across different time horizons and scenarios.

* Analysis: Inflation Rate and ETH Supply Over Time

## Model Extension Roadmap

The modular nature of the model makes structural and experiment-level extensions straightforward. The [Model Extension Roadmap](ROADMAP.md) provides some inspiration.

## Tests

We use Pytest to test the `model` module code, as well as the notebooks.

To execute the Pytest tests:
```bash
source venv/bin/activate
python3 -m pytest tests
```

To run the full GitHub Actions CI Workflow (see [.github/workflows](.github/workflows)):
```bash
source venv/bin/activate
make test
```


