## Firmware
- Changes from generic ESP32 firmware
    - Disabled Bluetooth: needed to free up memory for urequests
    - Enabled Split heap: make more memory available when needed

- Modules frozen in firmware:
    - [Microdot](https://github.com/miguelgrinberg/microdot)
    - [bme680](https://github.com/adafruit/Adafruit_CircuitPython_BME680)
    - [bme680AQ](https://github.com/thstielow/raspi-bme680-iaq)
    - [pms5003](https://github.com/kevinkk525/pms5003_micropython)
    - [ulogger](https://github.com/whales-chen/micropython-ulogger) (some changes were made)
    - ntptime (already in generic ESP32 firmware)
    - aqUtils (custom functions)
