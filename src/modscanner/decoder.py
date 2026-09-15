"""Decode raw Modbus registers into typed values."""

from __future__ import annotations

import struct
from collections.abc import Sequence
from modscanner.models import DataType, WordOrder

def registers_per_value(data_type: DataType) -> int:
    """return the number of 16-bit registers required for one value."""

    if data_type in {DataType.UINT16, DataType.INT16}:
        return 1

    if data_type in {
        DataType.UINT32,
        DataType.INT32,
        DataType.FLOAT32,
    }:
        return 2

    raise ValueError(f"unsupported data type: {data_type}")

def decode_registers(
    registers: Sequence[int],
    data_type: DataType,
    word_order: WordOrder = WordOrder.BIG,
) -> int | float:
    """decode one typed value from raw 16-bit Modbus registers."""

    required = registers_per_value(data_type)

    if len(registers) != required:
        raise ValueError(
            f"{data_type.value} requires {required} register(s), "
            f"got {len(registers)}"
        )

    for register in registers:
        if isinstance(register, bool) or not 0 <= register <= 0xFFFF:
            raise ValueError(
                f"invalid 16-bit register value: {register!r}"
            )

    words = list(registers)

    if required > 1 and word_order is WordOrder.LITTLE:
        words.reverse()

    payload = b"".join(
        word.to_bytes(2, byteorder="big", signed=False)
        for word in words
    )

    if data_type is DataType.UINT16:
        return struct.unpack(">H", payload)[0]

    if data_type is DataType.INT16:
        return struct.unpack(">h", payload)[0]

    if data_type is DataType.UINT32:
        return struct.unpack(">I", payload)[0]

    if data_type is DataType.INT32:
        return struct.unpack(">i", payload)[0]

    if data_type is DataType.FLOAT32:
        return struct.unpack(">f", payload)[0]

    raise ValueError(f"unsupported data type: {data_type}")