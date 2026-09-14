#!/usr/bin/env bash

set -e

# Example: write one Modbus coil using FC05.
#
# Coil values:
#   1 = ON
#   0 = OFF

HOST="127.0.0.1"
DEVICE_ID=1
ADDRESS=0
VALUE=1

modscanner write coil \
    --host "$HOST" \
    --device-id "$DEVICE_ID" \
    --address "$ADDRESS" \
    --value "$VALUE"