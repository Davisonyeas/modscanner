#!/usr/bin/env bash

set -e

HOST="127.0.0.1"
DEVICE_ID=1
START=0
COUNT=10

modscanner scan holding \
    --host "$HOST" \
    --device-id "$DEVICE_ID" \
    --start "$START" \
    --count "$COUNT"