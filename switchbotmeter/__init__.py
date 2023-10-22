from bluepy.btle import Scanner, DefaultDelegate
import binascii
import datetime

SERVICE_UUID = 'cba20d00-224d-11e6-9fb8-0002a5d5c51b'


class DevScanner(DefaultDelegate):
    """Device Scanner.

    Iterate trough this device

    Arguments:

        device: HCI device to scan on
        wait: On each scan, how much time to wait for devices
        macs: Optional list of MAC addresses
        *args, **kwargs: DefaultDelegate arguments
    """
    def __init__(self, device='hci0', wait=5, macs=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait_time = int(wait)
        self.scanner = Scanner().withDelegate(self)
        self.macs = macs

    def __iter__(self):
        """Use as iterator."""
        return self

    def __next__(self):
        """Each time we call next() over a `DevScanner` object, it will return
           an iterator with the whole currently-available list of devices.
        """
        res = self.scanner.scan(self.wait_time)
        return filter(None, (Device(d, self.macs) for d in res))


class Device:
    """Represents a device.

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
    """
    def __init__(self, device, mac_filter):
        self.device = device
        self.mac = None
        self.data = {}
        actions = {
            '16b Service Data': self.set_service_data,
            'Local name': self.set_mac,
            'Complete 128b Services': self.set_mac
        }
        for (_, key, value) in self.device.getScanData():
            # Load data
            actions.get(key, lambda x: {})(value)
        if mac_filter:
            self.mac = self.device.addr if self.device.addr in mac_filter else None

    def __getattr__(self, attr):
        """Enable direct access to data attributes"""
        if attr in self.data:
            return self.data[attr]

    def __bool__(self):
        """Return false if the device is not a switchbot meter"""
        return bool(self.mac and self.data)

    def __repr__(self):
        """Represent data model, temp, humidity and mac."""
        if self.data:
            return (f'<{self.data["model"]} ({self.data["mode"]}) '
                    f'temp: {self.data["temp"]:.2f} '
                    f'humidity: {self.data["humidity"]}%> ({self.mac})')
        return 'Unknown device'

    def set_mac(self, value):
        """Set device mac."""
        if value in ('WoHand', 'WoMeter', SERVICE_UUID):
            self.mac = self.device.addr

    def set_service_data(self, value):
        """Extract service data"""
        if len(value) != 16:
            return
        hexv = binascii.unhexlify(value)
        self.data = dict(model=hexv[2:3].decode(),
                         mode=hexv[3:4].hex(),
                         date=datetime.datetime.now(),
                         temp=int(hexv[6:7].hex(), 16) - 128 + (hexv[5] / 10),
                         humidity=hexv[7])
        print(self.data)
