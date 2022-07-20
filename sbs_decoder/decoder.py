"""High-level decoder

The I2C decoder generates events on every start, stop and byte. The decoder
collects each events and combines these into transactions (or functions).

Each transaction can then be translated into a function being called on a SBS
device and represented as such in the Logic Analyzer.
"""

import enum

from .types import Transaction


class State(enum.Enum):
    Idle = 1
    Address = 2
    Data = 3


class Decoder:
    """Decoder to combine I2C frames into transactions."""

    def __init__(self):
        self._state = State.Idle
        self._transaction = Transaction()
        # self._count = 0
        self._timeout = None

    def set_timeout(self, timeout):
        """Set a timeout to take into account.

        Providing a datetime object will enable timeout checks when processing
        I2C events. Settings timeout to None (default) disables these checks.

        Args:
            timeout: either a datetime type or None
        """
        self._timeout = timeout

    def _timeout_check(self, frame):
        """Checks if a timeout occoured and resets the decoder."""
        if self._timeout is None:
            return

        if self._transaction.start_time is None:
            return

        diff = frame.start_time - self._transaction.start_time
        if diff >= self._timeout:
            self._state = State.Idle

    def process(self, frame):
        """Process a I2C event.

        Handles:
        - plain transaction (start - address - data - stop)
        - restarts (identified by start, within timeout period)

        Returns
            A Transaction when completely decoded.

        Todo:
            Handle ACK/NACK
        """

        # if self._count < 30:
        #     self._count += 1
        #     print(vars(frame))
        # else:
        #     return None

        self._timeout_check(frame)

        if self._state == State.Idle:
            if frame.type == "start":
                self._state = State.Address

                self._transaction = Transaction()
                self._transaction.start_time = frame.start_time
            else:
                self._state = State.Idle
        elif self._state == State.Address:
            if frame.type == "address":
                self._state = State.Data

                self._transaction.device_address = int.from_bytes(
                    frame.data["address"], byteorder="little"
                )
                self._transaction.direction = (
                    Transaction.Direction.Read
                    if frame.data["read"]
                    else Transaction.Direction.Write
                )
                self._transaction.ack.append(frame.data["ack"])

                if not frame.data["ack"]:
                    self._state = State.Idle

                    self._transaction.end_time = frame.end_time
                    return self._transaction
            else:
                self._state = State.Idle
        elif self._state == State.Data:
            if frame.type == "data":
                self._transaction.payload += bytearray(frame.data["data"])
                self._transaction.ack.append(frame.data["ack"])
            elif frame.type == "stop":
                self._state = State.Idle

                self._transaction.end_time = frame.end_time
                return self._transaction
            elif frame.type == "start":
                # This is a restart condition (I2C decoder does not identify it as such)
                self._state = State.Data
            else:
                self._state = State.Idle

        return None
