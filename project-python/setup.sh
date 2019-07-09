#!/usr/bin/env bash



if [[ -d env ]]; then
    echo "Already found env dir"
    exit 0
else
    virtualenv --always-copy --verbose -p python3 env && env/bin/pip install --no-cache-dir -r requirements.txt
fi

