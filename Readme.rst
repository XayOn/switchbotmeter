Asyncio-enabled SwitchBot Meter simple API
------------------------------------------

This exposes a simple library (loosely based on
https://github.com/OpenWonderLabs/python-host/ because of the names, uuids and
temp logic) that will scan for all of your switchbot and allow you to iterate
trought them.

Usage is pretty straightforward::

        async for device in DevScanner().scan():
                print(device.mac)
                print(device.data['humidity'])
                print(device.data['temperature']


This library is a WIP and it's completely not production ready.
I will update it soon, the current TODO list is:

- Add tests
- Improve the ReadMe
- Add inline documentation and sphinx
