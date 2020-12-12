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
        *args, **kwargs: DefaultDelegate arguments
    """
    def __init__(self, device='hci0', wait=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait_time = int(wait)
        self.scanner = Scanner().withDelegate(self)

    def __iter__(self):
        """Use as iterator."""
        return self

    def __next__(self):
        """Each time we call next() over a `DevScanner` object, it will return
           an iterator with the whole currently-available list of devices.
        """
        res = self.scanner.scan(self.wait_time)
        return filter(None, (Device(d) for d in res))


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
    def __init__(self, device):
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
            return (f'<{self.data["model"]} temp: {self.data["temp"]} '
                    f'humidity: {self.data["humidity"]}> ({self.mac})')
        return 'Unknown device'

    def set_mac(self, value):
        """Set device mac."""
        if value in ('WoHand', 'WoMeter', SERVICE_UUID):
            self.mac = self.device.addr

    def set_service_data(self, value):
        """Extract service data"""
        model = binascii.a2b_hex(value[4:6])
        mode = binascii.a2b_hex(value[6:8])

        if len(value) != 16:
            return

        temp_fra = int(value[11:12].encode('utf-8'), 16) / 10.0
        temp_int = int(value[12:14].encode('utf-8'), 16)

        if temp_int < 128:
            temp_int *= -1
            temp_fra *= -1
        else:
            temp_int -= 128

        humidity = int(value[14:16].encode('utf-8'), 16) % 128
        self.data = dict(model=model.decode(),
                         mode=binascii.hexlify(mode).decode(),
                         date=datetime.datetime.now(),
                         temp=temp_int + temp_fra,
                         humidity=humidity)
