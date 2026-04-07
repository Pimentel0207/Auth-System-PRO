#!/bin/bash

echo "Setting up Auth System PRO..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -e .
pip install -r requirements-dev.txt

# Create .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created. Please update it with your configuration."
fi

echo "Setup complete! Run 'source venv/bin/activate' to activate the virtual environment."
