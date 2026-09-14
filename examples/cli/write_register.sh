#!/usr/bin/env bash

set -e

# Example: write one Modbus holding register using FC06.

HOST="127.0.0.1"
DEVICE_ID=1
ADDRESS=108
VALUE=100

modscanner write register \
    --host "$HOST" \
    --device-id "$DEVICE_ID" \
    --address "$ADDRESS" \
    --value "$VALUE"