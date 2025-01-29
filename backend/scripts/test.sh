#!/usr/bin/env bash

set -e
set -x

# Enable asyncio debug mode
# Ref: https://github.com/Kludex/fastapi-tips?tab=readme-ov-file#7-enable-asyncio-debug-mode
export PYTHONASYNCIODEBUG=1

coverage run --source=app -m pytest
coverage report --show-missing
coverage html --title "${@-coverage}"
