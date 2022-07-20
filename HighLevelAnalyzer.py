from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting
from saleae.data import GraphTimeDelta

from sbs_decoder import Decoder, Transaction
from smart_battery_system import to_sbs_command, register_device_address, Battery, FuelCell


def to_command(device_address: int, cmd_code: int) -> str:
    try:
        return str(to_sbs_command(device_address, cmd_code))
    except KeyError:
        return f"Unknown command ({cmd_code:02x})"


def format_payload(device_address: int, cmd_code: int, payload: bytearray):
    def is_string(cmd):
        return cmd in (
            Battery.ManufacturerName,
            Battery.DeviceName,
            Battery.DeviceChemistry,
        )

    try:
        cmd = to_sbs_command(device_address, cmd_code)

        if is_string(cmd):
            return payload.decode("ascii")

        tmp = int.from_bytes(payload, byteorder="little")
        return f"0x{tmp:02x}"
    except:
        return payload


def generate_write_cmd_payload_result(transaction):
    cmd = to_command(transaction.device_address, transaction.payload[0])
    payload = format_payload(transaction.device_address, transaction.payload[0], transaction.payload[1:])
    return AnalyzerFrame(
        "write_cmd_payload",
        transaction.start_time,
        transaction.end_time,
        {
            "device_address": f"0x{transaction.device_address:02x}",
            "command": cmd,
            "payload": payload,
        },
    )


def generate_write_cmd_result(transaction):
    cmd = to_command(transaction.device_address, transaction.payload[0])
    return AnalyzerFrame(
        "write_cmd",
        transaction.start_time,
        transaction.end_time,
        {"device_address": f"0x{transaction.device_address:02x}", "command": cmd},
    )


def generate_read_cmd_payload_result(write_cmd, read_cmd):
    cmd = to_command(write_cmd.device_address, write_cmd.payload[0])
    payload = format_payload(write_cmd.device_address, write_cmd.payload[0], read_cmd.payload)
    return AnalyzerFrame(
        "read_cmd_payload",
        write_cmd.start_time,
        read_cmd.end_time,
        {
            "device_address": f"0x{write_cmd.device_address:02x}",
            "command": cmd,
            "payload": payload,
        },
    )


def generate_read_payload_result(transaction):
    return AnalyzerFrame(
        "read_payload",
        transaction.start_time,
        transaction.end_time,
        {
            "device_address": f"0x{transaction.device_address:02x}",
            "payload": transaction.payload,
        },
    )


def generate_nack_result(transaction):
    return AnalyzerFrame(
        "nack",
        transaction.start_time,
        transaction.end_time,
        {"device_address": f"0x{transaction.device_address:02x}"},
    )


class Hla(HighLevelAnalyzer):
    custom_battery = StringSetting(label="Custom battery addresses")

    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        "nack": {"format": "NACK from {{data.device_address}}"},
        "read_cmd_payload": {
            "format": "Read from {{data.device_address}}, command: {{data.command}}, payload: {{data.payload}}"
        },
        "read_payload": {
            "format": "Read from {{data.device_address}}, payload: {{data.payload}}"
        },
        "write_cmd": {
            "format": "Write to {{data.device_address}}, command: {{data.command}}"
        },
        "write_cmd_payload": {
            "format": "Write to {{data.device_address}}, command: {{data.command}}, payload: {{data.payload}}"
        },
    }

    def __init__(self):
        """
        Initialize HLA.

        Settings can be accessed using the same name used above.
        """
        print("Smart Battery System Analyzer")
        print("Custom addresses:", self.custom_battery)

        addresses = self.custom_battery.split(",")
        for address in addresses:
            address = int(address.strip())
            register_device_address(address, [Battery, FuelCell])

        # Low level decoder
        self._decoder = Decoder()
        self._decoder.set_timeout(GraphTimeDelta(second=0, millisecond=35))

        # List of decoded transactions ready to be processed
        self._queue = []

    def __process_frame(self, frame: AnalyzerFrame):
        """Processes an AnalyzerFrame

        Returns
            True when a complete frame is decoded
        """

        result = self._decoder.process(frame)
        if result is None:
            return False

        # print(f"DECODED: {result}")
        self._queue.append(result)
        return True

    def decode(self, frame: AnalyzerFrame):
        """
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.

        The type and data values in `frame` will depend on the input analyzer.
        """

        do_parsing = self.__process_frame(frame)
        if do_parsing:
            index = 0
            # while index < len(self._queue):
            transaction = self._queue[index]

            if not all(transaction.ack):
                # we got an NACK
                result = generate_nack_result(transaction)
                self._queue.remove(transaction)
                return result

            if transaction.direction == Transaction.Direction.Write:
                if len(transaction.payload) > 1:
                    result = generate_write_cmd_payload_result(transaction)
                    self._queue.remove(transaction)
                    return result

                # This is a single write, might be part of a read...
                try:
                    next = self._queue[index + 1]

                    if next.direction == Transaction.Direction.Read:
                        result = generate_read_cmd_payload_result(transaction, next)
                        self._queue.remove(transaction)
                        self._queue.remove(next)
                        return result

                    result = generate_write_cmd_result(transaction)
                    self._queue.remove(transaction)
                    return result
                except IndexError:
                    # no next element yet, cannot decide what to do
                    # break
                    pass
            elif transaction.direction == Transaction.Direction.Read:
                result = generate_read_payload_result(transaction)
                self._queue.remove(transaction)
                return result

            index += 1

        return None
