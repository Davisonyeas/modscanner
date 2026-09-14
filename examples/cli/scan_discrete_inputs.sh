#!/usr/bin/env bash

set -e

HOST="127.0.0.1"
DEVICE_ID=1
START=0
COUNT=8

modscanner scan discrete-inputs \
    --host "$HOST" \
    --device-id "$DEVICE_ID" \
    --start "$START" \
    --count "$COUNT"