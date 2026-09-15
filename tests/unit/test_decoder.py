import pytest

from modscanner.decoder import decode_registers, registers_per_value
from modscanner.models import DataType, WordOrder

def test_uint16() -> None:
    assert decode_registers(
        (1234,),
        DataType.UINT16,
    ) == 1234

def test_int16() -> None:
    assert decode_registers(
        (0xFFFF,),
        DataType.INT16,
    ) == -1

def test_uint32_big_word_order() -> None:
    assert decode_registers(
        (0x0001, 0x0002),
        DataType.UINT32,
    ) == 0x00010002

def test_uint32_little_word_order() -> None:
    assert decode_registers(
        (0x0001, 0x0002),
        DataType.UINT32,
        WordOrder.LITTLE,
    ) == 0x00020001

def test_float32() -> None:
    assert decode_registers(
        (0x43F1, 0x8000),
        DataType.FLOAT32,
    ) == pytest.approx(483.0)

def test_float32_little_word_order() -> None:
    assert decode_registers(
        (0x8000, 0x43F1),
        DataType.FLOAT32,
        WordOrder.LITTLE,
    ) == pytest.approx(483.0)

def test_wrong_register_count() -> None:
    with pytest.raises(ValueError):
        decode_registers(
            (0x43F1,),
            DataType.FLOAT32,
        )

def test_registers_per_float32() -> None:
    assert registers_per_value(DataType.FLOAT32) == 2