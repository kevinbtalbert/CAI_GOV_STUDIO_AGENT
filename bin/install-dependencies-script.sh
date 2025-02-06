#!/bin/bash

# Install python dependencies in uv created environment
# This uses pyproject.toml & uv.lock file to install dependencies
# this should create a subdirectory called .venv (if it doesn't exist)
uv sync

# Get node
touch .bashrc
export NVM_DIR="$(pwd)/.nvm"
mkdir -p $NVM_DIR
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
nvm install 20
nvm use 20
echo $(which node)
echo $(which npm)

# Install frontend dependencies and run build
rm -rf node_modules/
npm install 
npm run build