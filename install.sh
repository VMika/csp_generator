#! /bin/bash

# Installing venv
apt-get install -y python3-venv

# Creating venv
python3 -m venv ./venv
source venv/bin/activate

# Installing pip directly from pypi (bypassing TLS restrictions)
python -m pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org --upgrade pip

# Installing certificate handler and upgrading installing tools
pip install certifi
pip install --upgrade incremental
pip install --upgrade setuptools


# Install packages
apt-get install -y python3.5-dev
apt-get install -y libffi-dev
apt-get install -y libxml2-dev libxslt-dev
apt-get install -y python3-lxml


# Install requirements
pip3 install -r requirements.txt -v


# Setup the headless firefox browser and virtual display
apt-get install -y firefox
apt-get install -y xvfb
Xvfb :99 -ac &
export DISPLAY=:99
