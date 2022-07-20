"""Types used by the SBS decoder"""

import enum


class Transaction:
    """Collection of multiple I2C events representing a single transaction"""

    class Direction(enum.Enum):
        Read = 1
        Write = 2

    def __init__(self):
        self.start_time = None
        self.end_time = None

        self.direction = None

        self.device_address = None
        self.payload = bytearray()
        self.ack = []
