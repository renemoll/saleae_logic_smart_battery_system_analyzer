"""Types used by the SBS decoder."""

import enum
import typing


T = typing.TypeVar("T", bound="Transaction")


class Transaction:
    """Collection of multiple I2C events representing a single transaction."""

    class Direction(enum.Enum):
        Read = 1
        Write = 2

    def __init__(self: T) -> None:
        self.start_time = None
        self.end_time = None

        self.direction = None

        self.device_address = None
        self.payload = bytearray()
        self.ack = []
