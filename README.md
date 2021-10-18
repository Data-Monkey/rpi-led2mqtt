# rpi-led2mqtt
Control ws281x LED strips attached to the RaspberryPi via MQTT

### Why
I wanted to directly attach a WS2812b led strip to my RaspberryPi that I already used to runy Zigbee2MQTT.
The easiest way to control a led strip like this is probably WLED but I had some issues with too many WiFi signals next to each other and interfering. 


### Thanks
So here we are, using the Python version [rpi-ws281x-python](https://github.com/rpi-ws281x/rpi-ws281x-python) wrapping the original library [rpi_ws211x](https://github.com/jgarff/rpi_ws281x) by [Jeremy Graff](https://github.com/jgarff)

The code simple code is very much inspired by [Thomas Hudson](https://gist.github.com/ghomasHudson)'s [OpenRGB to MQTT light](https://gist.github.com/ghomasHudson/7cc24aa187e8141003073e36e068a5a2) code.

And the MQTT structure used by zigbee2mqtt 

