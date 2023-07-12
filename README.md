# Polygon Economic Model

[![Python package](https://github.com/CADLabs/ethereum-model/actions/workflows/python.yml/badge.svg)](https://github.com/CADLabs/ethereum-model/actions/workflows/python.yml)

A simulation model of Polygon 2.0 to study validator incentives and ecosystem security. It forked from [ethereum-economic-model](https://github.com/CADLabs/ethereum-economic-model) and has been constructed using the open-source Python library [radCAD](https://github.com/CADLabs/radCAD), which is an enhancement of [cadCAD](https://cadcad.org).



## Environment Setup

1. Clone or download the Git repository: `git clone https://github.com/0xPolygon/polygon2.0-economic-model.git` or using GitHub Desktop
2. Set up your development environment using one of the following three options:

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
python3 -m ipykernel install --user --name python-pol-model --display-name "Python (Polygon Economic Model)"
```

You'll then be able to select the kernel with display name `Python (Polygon Economic Model)` to use for your notebook from within Jupyter.

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

The [experiments/notebooks/Polygon_analysis](experiments/notebooks/Polygon_analysis) directory contains the most recent released cryptoeconomics simulation results. Specifically, [Polygon2.0 Economics v0.1](experiments/notebooks/Polygon_analysis/Polygon2.0_economics_v0.1.ipynb)presents a comprehensive analysis of the primary validator economics in the current model iteration. The simulation specs in this notebook is aligned with the POL whitepaper, ensuring that the simulation specifications are consistent with the official documentation.  The notebook shows
* $POL token price trajectory
* Three chains adoption rate scenarios
* Validator yields over time per scenario
* Validator profit break down analysis in both yields and dollars.










