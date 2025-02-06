#!/bin/bash

# Run autoflake to remove unused imports
uv run -m autoflake --in-place --remove-all-unused-imports --ignore-init-module-imports --recursive studio/

# Run ruff to format the code
uv run -m ruff format studio/

# Format React app code
npm run format
npm run lint