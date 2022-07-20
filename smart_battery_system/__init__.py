"""Helpers to generate command enums based on device and register addresses."""

from .commands import Battery, FuelCell, SystemManager, SbsCommand

_DEVICE_MAP = {}


def register_device_address(device_address: int, sbs_component: SbsCommand) -> None:
    """Associate a custom bus address with a (number of) SBS roles.

    Use this to associate roles to a device, for example: a Smart Battery on 0x0B
    supports the roles Battery and FuelCell.

    Args:
        device_address: device address as used on the bus
        sbs_component: list of roles the device supports
    """
    global _DEVICE_MAP

    if device_address not in _DEVICE_MAP:
        _DEVICE_MAP[device_address] = []

    _DEVICE_MAP[device_address] += sbs_component


register_device_address(0x08, [Battery, FuelCell])  # Host
# register_device_address(0x09, ) # Charger
register_device_address(0x0A, [SystemManager])  # Selector, System manager
register_device_address(0x0B, [Battery, FuelCell])  # Battery


def to_sbs_command(device_address: int, cmd_code: int) -> SbsCommand:
    """Retrieve a SBS command.

    Args:
        device_address: device address as used on the bus
        cmd_code: command code (or function code)

    Returns:
        A SbsCommand

    Raises:
        KeyError: either when the device_address is not registered (use register_device_address)
            or when the given cmd_code is not a valid code.
    """
    roles = _DEVICE_MAP[device_address]
    for cmd in roles:
        try:
            return cmd.from_int(cmd_code)
        except ValueError:
            continue

    raise KeyError
