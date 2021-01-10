DEVS_MAC = {
    'Local name': 'WoHand',
    'Complete 128b Services': 'WoMeter',
}
DEVS = {'16b Service Data': '000d5410e4079345'}


def test_device_mac():
    from switchbotmeter import Device
    mac = '11:22:33:44:55:66'

    class FakeDeviceMac:
        addr = mac

        def getScanData(self):
            for key, value in DEVS_MAC.items():
                yield None, key, value

    assert Device(FakeDeviceMac()).mac == mac
    assert str(Device(FakeDeviceMac())) == 'Unknown device'


def test_device_data_bool():
    from switchbotmeter import Device
    mac = '11:22:33:44:55:66'

    class FakeDeviceMac:
        addr = mac

        def getScanData(self):
            for key, value in {**DEVS_MAC, **DEVS}.items():
                yield None, key, value

    # Test __bool__
    device = Device(FakeDeviceMac())
    assert device


def test_device_data_repr():
    from switchbotmeter import Device
    mac = '11:22:33:44:55:66'

    class FakeDeviceMac:
        addr = mac

        def getScanData(self):
            for key, value in {**DEVS_MAC, **DEVS}.items():
                yield None, key, value

    # Test __bool__
    device = Device(FakeDeviceMac())
    assert str(device) == '<T (10) temp: 19.70 humidity: 69%> (11:22:33:44:55:66)'


def test_device_data_data():
    from switchbotmeter import Device
    mac = '11:22:33:44:55:66'

    class FakeDeviceMac:
        addr = mac

        def getScanData(self):
            for key, value in {**DEVS_MAC, **DEVS}.items():
                yield None, key, value

    device = Device(FakeDeviceMac())

    # Test __repr__
    assert device.model
    assert device.mode
    assert device.date
    assert device.temp
    assert device.humidity
