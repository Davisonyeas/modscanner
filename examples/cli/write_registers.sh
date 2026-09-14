#!/usr/bin/env bash

set -e

# Example: write multiple Modbus holding registers using FC16.
#
# Values are supplied as a comma-separated list.

HOST="127.0.0.1"
DEVICE_ID=1
START_ADDRESS=200
VALUES="10,20,30,40"

modscanner write registers \
    --host "$HOST" \
    --device-id "$DEVICE_ID" \
    --address "$ADDRESS" \
    --values "$VALUES"