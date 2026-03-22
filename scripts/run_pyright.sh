#!/bin/bash

node "$(dirname "$0")/../pyright/packages/pyright/dist/pyright.js" \
    --typeshedpath "$(dirname "$0")/../typeshed" \
    "$@"
