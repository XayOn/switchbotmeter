"""Switchbot Meter."""
from __future__ import annotations

import binascii
import datetime
from typing import Generator

from bluepy.btle import DefaultDelegate, ScanEntry, Scanner

SERVICE_UUID = "cba20d00-224d-11e6-9fb8-0002a5d5c51b"
SERVICE_DATA_LEN: int = 16


class DevScanner(DefaultDelegate):
    """
    Device Scanner.

    Iterate trough this device

    Args.
    -----

        device: HCI device to scan on
        wait: On each scan, how much time to wait for devices
        macs: Optional list of MAC addresses
        *args, **kwargs: DefaultDelegate arguments

    """

    def __init__(
        self: "DevScanner",
        iface: int = 0,
        wait: int = 5,
        macs: list | None = None,
        *args: tuple,
        **kwargs: dict,
    ) -> None:
        """Set up devscanner."""
        super().__init__(*args, **kwargs)
        self.wait_time = int(wait)
        self.scanner = Scanner(iface).withDelegate(self)
        self.macs: list = macs or []

    def __iter__(self: "DevScanner") -> "DevScanner":
        """Use as iterator."""
        return self

    def __next__(self: "DevScanner") -> Generator[Device, None, None]:
        """
        Make devscanner an iterator.

        Each time we call next() over a `DevScanner` object, it will return
        an iterator with the whole currently-available list of devices.
        """
        res = self.scanner.scan(self.wait_time)
        yield from (Device(d, self.macs) for d in res if res)


class Device:
    """
    Represents a device.

    Given a bluepy device object, it gets the scan data and looks for switchbot
    meter information. If found, parses it and populates itself.

    A device will test falsy if it's not a switchbot meter device, wich is used
    with a filter(None, devices) to filter out non-switchbot devices from scan
    data.


    You can access the following data properties after initialization:

        - mac: Device mac
        - model: Device model
        - mode: Device mode
        - date: Date of the current scan
        - temp: Temperature as reported by the meter
        - humidity: Humidity, percentage.
        - data: Complete dict with all the data minus the mac.

    Arguments:
    ---------
        device: Device
        force_devices: Force this devices to be selected regardless of their
                       identification (list of MAC addresses)
    """

    def __init__(
        self: "Device",
        device: ScanEntry,
        forced_devices: list[str] | None = None,
    ) -> None:
        """Set up device."""
        self.device = device
        self.forced_devices = forced_devices or []
        self._mac = ""
        self.data = {}

        actions = {
            "16b Service Data": self.set_service_data,
            "Local name": self.set_mac,
            "Complete 128b Services": self.set_mac,
        }

        for _, key, value in self.device.getScanData():
            actions.get(key, lambda _: {})(value)  # Load data

    @property
    def mac(self: "Device") -> str:
        """
        Return current device mac.

        Can have been set via metadata action or forced.
        """
        if self.device.addr in self.forced_devices:
            return self.device.addr
        return self._mac

    def __getattr__(self: "Device", attr: str) -> str | None:
        """Enable direct access to data attributes."""
        if attr in self.data:
            return self.data[attr]
        return None

    def __bool__(self: "Device") -> bool:
        """Return false if the device is not a switchbot meter."""
        return bool(self.mac and self.data)

    def __repr__(self: "Device") -> str:
        """Represent data model, temp, humidity and mac."""
        if self.data:
            return (
                f'<{self.data["model"]} ({self.data["mode"]}) '
                f'temp: {self.data["temp"]:.2f} '
                f'humidity: {self.data["humidity"]}%> ({self.mac})'
            )
        return "Unknown device"

    def set_mac(self: "Device", value: str) -> None:
        """Set device mac."""
        if value in ("WoHand", "WoMeter", SERVICE_UUID):
            self._mac = self.device.addr

    def set_service_data(self: Device, value: bytes) -> None:
        """Extract service data."""
        if len(value) != SERVICE_DATA_LEN:
            return
        hexv = binascii.unhexlify(value)
        self.data = {
            "model": hexv[2:3].decode(),
            "mode": hexv[3:4].hex(),
            "date": datetime.datetime.now(tz=datetime.timezone.utc),
            "temp": int(hexv[6:7].hex(), 16) - 128 + (hexv[5] / 10),
            "humidity": hexv[7],
        }
