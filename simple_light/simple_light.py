import paho.mqtt.client as mqtt
import json 
from rpi_ws281x import PixelStrip, Color
import _rpi_ws281x as ws
import time

# ======== START USER INPUT ==========

LED_NAME = "rpi_led_strip"

MQTT_HOST = "your host"     # host of your MQTT Broker
MQTT_PORT = 1883            # port of your MQTT Broker
MQTT_USER = "user"          # MQTT username
MQTT_PWD  = "password"      # MQTT password





# LED strip configuration:
LED_COUNT = 37        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP = ws.WS2812_STRIP

HA_DISCOVERY_PREFIX = 'homeassistant'

# ======== END USER INPUT ==========

HA_DISCOVERY_TOPIC = HA_DISCOVERY_PREFIX +'/light/'+LED_NAME+'/config'

# losely following the zigbee2mqtt mqtt topic structure/format
LED2MQTT_TOPIC = 'led2mqtt'

LED_ROOT_TOPIC = LED2MQTT_TOPIC+"/light/"+LED_NAME
LED_MQTT_CONFIG = {  
    "name":           LED_NAME,
    "command_topic":  LED_ROOT_TOPIC+"/cmd",
    "state_topic":    LED_ROOT_TOPIC+"/state",
    "schema":         "json",
    "brightness":     True,
    "rgb":     True
}





# =============================

lightStatus = {
    "state" : "OFF",
    "color" : {"r": 200, "g": 100, "b":100},
    "brightness": 128
}

def publishLightStatus(mqttc):
    mqttc.publish(LED_MQTT_CONFIG["state_topic"], 
                  payload=json.dumps(lightStatus),  
                  qos=0, retain=False)

def on_connect(mqttc, userdata, flags, rc):
    print ("Connected with rc: " + str(rc))
    
    # announce Light to HA Discovery
    mqttc.publish(HA_DISCOVERY_TOPIC, 
                  payload=json.dumps(LED_MQTT_CONFIG), 
                  qos=0, retain=False)
    
    # publish the status
    publishLightStatus(mqttc)

    #subscribe to messages
    mqttc.subscribe(LED_ROOT_TOPIC+'/cmd/#')

def on_message(mqttc, userdata, msg):
    message_topic = msg.topic
    message = json.loads(msg.payload)
    print ("Topic: "+ message_topic+"\nMessage: "+json.dumps(message))
    

    if message["state"] == "OFF":
        colorSolid(strip, Color(0, 0, 0))
        lightStatus["state"]="OFF"


    elif message["state"] == "ON":
        lightStatus["state"]="ON"

        if "color" in message:
            lightStatus["color"] = message["color"]

        elif "brightness" in message:
            lightStatus["brightness"] = message["brightness"]


        newColor = adjustColor(lightStatus["color"], lightStatus["brightness"])
        print (newColor)
        colorSolid(strip, Color(newColor["r"], 
                                newColor["g"], 
                                newColor["b"]))
                            

    publishLightStatus(mqttc)



# =============== LIGHT =========
def adjustColor(color, brightness):
    """adjust the color values by the brightness factor"""
    return {"r": int(color["r"]*brightness/255),
            "g": int(color["g"]*brightness/255),
            "b": int(color["b"]*brightness/255)}


def colorSolid(strip, color, wait_ms=50):
    """set color across display all at the same time."""
    #print("colorSolid:"+ str(color))
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()



# =============== MAIN ============


# Create NeoPixel object with appropriate configuration.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

mqttc = mqtt.Client("LED2MQTT-"+LED_NAME )
mqttc.username_pw_set(MQTT_USER,password=MQTT_PWD)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(MQTT_HOST, MQTT_PORT, 60)


try:
    mqttc.loop_forever()
    
except KeyboardInterrupt:
    '''switch off the strip'''
    colorSolid(strip, Color(0, 0, 0))
    lightStatus["state"]="OFF"
    publishLightStatus(mqttc)
    time.sleep(1)
    mqttc.disconnect()
