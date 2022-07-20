"""Types to represent Smart Battery System functions."""

import enum
import typing


T = typing.TypeVar("T", bound="SbsCommand")


class SbsCommand:
    """Generic interface for SBS commands."""

    @classmethod
    def from_int(cls: T, cmd_code: int) -> T:
        """Create a Battery enum from a command code."""
        return cls(cmd_code)

    def __str__(self: T) -> str:
        """Generate a string for a given Battery enum."""
        return self.name


class Battery(SbsCommand, enum.Enum):
    """Functions for: Smart Battery Data Specification (rev 1.1)."""

    ManufacturerAccess = 0x00
    RemainingCapacityAlarm = 0x01
    RemainingTimeAlarm = 0x02
    BatteryMode = 0x03
    AtRate = 0x04
    AtRateTimeToFull = 0x05
    AtRateTimeToEmpty = 0x06
    AtRateOK = 0x07
    Temperature = 0x08
    Voltage = 0x09
    Current = 0x0A
    AverageCurrent = 0x0B
    MaxError = 0x0C
    RelativeStateOfCharge = 0x0D
    AbsoluteStateOfCharge = 0x0E
    RemainingCapacity = 0x0F
    FullChargeCapacity = 0x10
    RunTimeToEmpty = 0x11
    AverageTimeToEmpty = 0x12
    AverageTimeToFull = 0x13
    ChargingCurrent = 0x14
    ChargingVoltage = 0x15
    BatteryStatus = 0x16
    CycleCount = 0x17
    DesignCapacity = 0x18
    DesignVoltage = 0x19
    SpecificationInfo = 0x1A
    ManufactureDate = 0x1B
    SerialNumber = 0x1C
    ManufacturerName = 0x20
    DeviceName = 0x21
    DeviceChemistry = 0x22
    ManufacturerData = 0x23


class FuelCell(SbsCommand, enum.Enum):
    """Functions for: SBDS – Addendum For Fuel Cell Systems (rel 1.02)."""

    DesignMaxPower = 0x24
    StartTime = 0x25
    TotalRunTime = 0x26
    FCTemp = 0x27
    FCStatus = 0x28
    FCMode = 0x29
    AutSoftOFF = 0x2A


class SystemManager(SbsCommand, enum.Enum):
    """Functions for: Smart Battery System Manager Specification (rev 1.1)."""

    BatterySystemState = 0x01
    BatterySystemStateCont = 0x02
    BatterySystemInfo = 0x04
