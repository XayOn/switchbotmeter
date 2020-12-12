.. image:: ./docs/switchbot.png

**Python Swithbot Meter API**

Comprehensible `SwitchBot Meter <https://www.switch-bot.com/products/switchbot-meter) API>`_.
Read your SwitchBot Meter status in real time via BLE. 

|pypi| |release| |downloads| |python_versions| |pypi_versions| |coverage| |actions|

.. |pypi| image:: https://img.shields.io/pypi/l/switchbotmeter
.. |release| image:: https://img.shields.io/librariesio/release/pypi/switchbotmeter
.. |downloads| image:: https://img.shields.io/pypi/dm/switchbotmeter
.. |python_versions| image:: https://img.shields.io/pypi/pyversions/switchbotmeter
.. |pypi_versions| image:: https://img.shields.io/pypi/v/switchbotmeter
.. |coverage| image:: https://codecov.io/gh/XayOn/switchbotmeter/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/XayOn/switchbotmeter
.. |actions| image:: https://github.com/XayOn/switchbotmeter/workflows/CI%20commit/badge.svg
    :target: https://github.com/XayOn/switchbotmeter/actions

Installation
------------

This library is available on `Pypi <https://pypi.org/project/switchbotmeter/>`_, you can install it directly with pip::

        pip install switchbotmeter

This library acts as a BLE client, so you need a
BLE-capable device (a bluetooth dongle or integrated)

Usage
-----

This library exports a DeviceScanner object that will
dected any SwitchBot Meter devices nearby. 
Note that you need to have permissions to access your
bluetooth device, the scope of wich will not be covered by
this readme :

.. code:: python

    from switchbotmeter import DevScanner

    for current_devices in DevScanner(): 
        for device in current_devices:
            print(device)
            print(f'{device.mac} -> {device.temp}')


.. code:: bash

    <T temp: 19.8 humidity: 73> (c6:97:89:d6:c8:09)
    c6:97:89:d6:c8:09 -> 19.8
    ...
    <T temp: 20.4 humidity: 71> (c6:97:89:d6:c8:09)
    c6:97:89:d6:c8:09 -> 20.4
