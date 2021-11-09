#!/usr/bin/python
# DHT Sensor Data-logging to MQTT Temperature channel

# Requies a Mosquitto Server Install On the destination.

# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
# MQTT Encahncements: David Cole (2016)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import json
import requests
import sys
import time
import datetime
import paho.mqtt.client as mqtt
import Adafruit_DHT


#==================================================================================================================================================
#Usage
#python mqtt.channel.py <temp topic> <humidity topic> <gpio pin> <optional update frequency>
# eg python mqtt.channel.py 'cupboard/temperature1' 'cupboard/humidity1' 4
# will start an instance using 'cupboard/temperature1' as the temperature topic, and using gpio port 4 to talk to a DHT22 sensor
# it will use the default update time of 300 secons.
#==================================================================================================================================================

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.DHT22

# Example of sensor connected to Raspberry Pi pin 23
DHT_PIN  = sys.argv[3]
# Example of sensor connected to Beaglebone Black pin P8_11
#DHT_PIN  = 'P8_11'

if (len(sys.argv) < 2):
   raise  ValueError('Input arguments of mqtt channel temperature humidity not passed')

MOSQUITTO_HOST = 'servername'
MOSQUITTO_PORT = 1883
MOSQUITTO_TEMP_MSG = str(sys.argv[1]) # Old channel name in here
MOSQUITTO_HUMI_MSG = str(sys.argv[2]) # Old channel name now passed by argument
MOSQUITTO_BASE_TOPIC = str(sys.argv[1]).split('/') # Extract the base topic
MOSQUITTO_LWT_TOPIC = MOSQUITTO_BASE_TOPIC[0] + '/LWT' #Create the last-will-and-testament topic
print('Mosquitto Temp MSG {0}'.format(MOSQUITTO_TEMP_MSG))
print('Mosquitto Humidity MSG {0}'.format(MOSQUITTO_HUMI_MSG))
print('Mosquitto LWT MSG {0}'.format(MOSQUITTO_LWT_TOPIC))

# How long to wait (in seconds) between measurements.
print ("Args length: " + str(len(sys.argv)))
FREQUENCY_SECONDS      = 300

if (len(sys.argv) > 4):
	FREQUENCY_SECONDS = float(sys.argv[4])


print('Logging sensor measurements to {0} every {1} seconds.'.format('MQTT', FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')
print('Connecting to MQTT on {0}'.format(MOSQUITTO_HOST))
mqttc = mqtt.Client("python_pub")
mqttc.will_set(MOSQUITTO_LWT_TOPIC, payload='offline', qos=0, retain=True)
mqttc.connect(MOSQUITTO_HOST,MOSQUITTO_PORT, keepalive=FREQUENCY_SECONDS+10)
mqttc.publish(MOSQUITTO_LWT_TOPIC, payload='online', qos=0, retain=True)
try:

    while True:
        # Attempt to get sensor reading.
        humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)

        # Skip to the next reading if a valid measurement couldn't be taken.
        # This might happen if the CPU is under a lot of load and the sensor
        # can't be reliably read (timing is critical to read the sensor).
        if humidity is None or temp is None:
           time.sleep(2)
           continue

        currentdate = time.strftime('%Y-%m-%d %H:%M:%S')
        print('Date Time:   {0}'.format(currentdate))
        print('Temperature: {0:0.2f} C'.format(temp))
        print('Humidity:    {0:0.2f} %'.format(humidity))

        # Publish to the MQTT channel
        try:
            print ('Updating {0}'.format(MOSQUITTO_TEMP_MSG))
            (result1,mid) = mqttc.publish(MOSQUITTO_TEMP_MSG,temp)
            print ('Updating {0}'.format(MOSQUITTO_HUMI_MSG))
	    time.sleep(1)
            (result2,mid) = mqttc.publish(MOSQUITTO_HUMI_MSG,humidity)
            print ('MQTT Updated result {0} and {1}'.format(result1,result2))
            if result1 == 1 or result2 == 1:
                raise ValueError('Result for one message was not 0')

        except Exception,e:
            # Error appending data, most likely because credentials are stale.
            # Null out the worksheet so a login is performed at the top of the loop.
            print('Append error, logging in again: ' + str(e))
            continue

        # Wait 30 seconds before continuing
        print('Wrote a message to MQTT broker')
        time.sleep(FREQUENCY_SECONDS)

except Exception as e:
    print('Error connecting to the MQTT server: {0}'.format(e))

