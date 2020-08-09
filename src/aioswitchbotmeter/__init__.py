from bluepy.btle import Scanner, DefaultDelegate
import asyncio
import binascii
import datetime

SERVICE_UUID = 'cba20d00-224d-11e6-9fb8-0002a5d5c51b'
MANUFACTURER_ID = '5900f46d2c8a5f31'


class DevScanner(DefaultDelegate):
    def __init__(self, device='hci0', wait=5, loop=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop
        self.queue = asyncio.Queue()
        self.wait_time = int(wait)
        self.device_name = device
        self.scan_fut = None

    async def scan(self):
        self.scan_fut = self.loop.run_in_executor(None, self.scan_loop)
        while True:
            yield await self.queue.get()

    def scan_loop(self):
        scanner = Scanner().withDelegate(self)
        while True:
            devs = (Device(d) for d in scanner.scan(self.wait_time))
            result = {a.mac: a.data for a in devs if a.mac}
            self.loop.call_soon_threadsafe(self.queue.put_nowait, result)


class Device:
    def __init__(self, device):
        self.device = device
        self.mac = None
        self.data = {}
        self.actions = {
            '16b Service Data': self.set_service_data,
            'Local name': self.set_mac,
            'Complete 128b Services': self.set_mac
        }
        for (_, key, value) in self.device.getScanData():
            # Load data
            self.actions.get(key, lambda x: {})(value)

    def set_mac(self, value):
        if value in ('WoHand', 'WoMeter', SERVICE_UUID):
            self.mac = self.device.addr

    def set_service_data(self, value):
        """Extract service data"""
        model = binascii.a2b_hex(value[4:6])
        mode = binascii.a2b_hex(value[6:8])

        if len(value) == 16:
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
                             date=str(datetime.datetime.now()),
                             temp=temp_int + temp_fra,
                             humidity=humidity)
