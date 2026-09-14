#!/usr/bin/env bash

set -e

# Example: scan Modbus holding registers.
#
# Port 502 is used automatically unless --port is specified.

HOST="127.0.0.1"
DEVICE_ID=1
START=0
COUNT=20
BLOCK_SIZE=10

modscanner scan-registers \
    --host "$HOST" \
    --device-id "$DEVICE_ID" \
    --start "$START" \
    --count "$COUNT" \
    --block-size "$BLOCK_SIZE"


# For a non-default port:

#!/usr/bin/env bash

set -e

HOST="127.0.0.1"
PORT=1502
DEVICE_ID=1

modscanner scan-registers \
    --host "$HOST" \
    --port "$PORT" \
    --device-id "$DEVICE_ID" \
    --start 0 \
    --count 20