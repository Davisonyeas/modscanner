#!/usr/bin/env bash

set -e

# Example: write multiple Modbus coils using FC15.
#
# Values are comma-separated.
#
#   1 = ON
#   0 = OFF

HOST="127.0.0.1"
DEVICE_ID=1
START_ADDRESS=0
VALUES="1,0,1,0"

modscanner write coils \
    --host "$HOST" \
    --device-id "$DEVICE_ID" \
    --address "$ADDRESS" \
    --values "$VALUES"