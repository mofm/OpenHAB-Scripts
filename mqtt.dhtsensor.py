#!/usr/bin/python
# DHT Sensor Data-logging to MQTT Temperature channel

# Requies a Mosquitto Server Install On the destination.

import sys
import time
import paho.mqtt.client as mqtt
import grovepi


# ======================================================================================================================
# Usage
# python mqtt.channel.py <temp topic> <humidity topic> <grovepi dht pin> <optional update frequency>
# eg python mqtt.channel.py 'cupboard/temperature1' 'cupboard/humidity1' 7
# will start an instance using 'cupboard/temperature1' as the temperature topic, and using grovepi port 7 to talk
# to a DHT11 sensor
# it will use the default update time of 300 secons.
# ======================================================================================================================

# Type of sensor, can be blue or white. blue = 0, white = 1
DHT_TYPE = 0

# Example of sensor connected to GrovePi Digital Pin 7
DHT_PIN = int(sys.argv[3])

if len(sys.argv) < 2:
    raise ValueError('Input arguments of mqtt channel temperature humidity not passed')

MOSQUITTO_HOST = '127.0.0.1'
MOSQUITTO_PORT = 1883
MOSQUITTO_TEMP_MSG = str(sys.argv[1])  # Old channel name in here
MOSQUITTO_HUMI_MSG = str(sys.argv[2])  # Old channel name now passed by argument
MOSQUITTO_BASE_TOPIC = str(sys.argv[1]).split('/')  # Extract the base topic
MOSQUITTO_LWT_TOPIC = MOSQUITTO_BASE_TOPIC[0] + '/LWT'  # Create the last-will-and-testament topic
print('Mosquitto Temp MSG {0}'.format(MOSQUITTO_TEMP_MSG))
print('Mosquitto Humidity MSG {0}'.format(MOSQUITTO_HUMI_MSG))
print('Mosquitto LWT MSG {0}'.format(MOSQUITTO_LWT_TOPIC))

# How long to wait (in seconds) between measurements.
print("Args length: " + str(len(sys.argv)))
FREQUENCY_SECONDS = 30

if len(sys.argv) > 4:
    FREQUENCY_SECONDS = float(sys.argv[4])


print('Logging sensor measurements to {0} every {1} seconds.'.format('MQTT', FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')
print('Connecting to MQTT on {0}'.format(MOSQUITTO_HOST))
mqttc = mqtt.Client("python_pub")
mqttc.will_set(MOSQUITTO_LWT_TOPIC, payload='offline', qos=0, retain=True)
mqttc.connect(MOSQUITTO_HOST, MOSQUITTO_PORT, keepalive=FREQUENCY_SECONDS+10)
mqttc.publish(MOSQUITTO_LWT_TOPIC, payload='online', qos=0, retain=True)
try:

    while True:
        # Attempt to get sensor reading.
        [temp, humidity] = grovepi.dht(DHT_PIN, DHT_TYPE)

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
            print('Updating {0}'.format(MOSQUITTO_TEMP_MSG))
            (result1, mid) = mqttc.publish(MOSQUITTO_TEMP_MSG, temp)
            print('Updating {0}'.format(MOSQUITTO_HUMI_MSG))
            time.sleep(1)
            (result2, mid) = mqttc.publish(MOSQUITTO_HUMI_MSG, humidity)
            print('MQTT Updated result {0} and {1}'.format(result1, result2))
            if result1 == 1 or result2 == 1:
                raise ValueError('Result for one message was not 0')

        except Exception as e:
            # Error appending data, most likely because credentials are stale.
            # Null out the worksheet so a login is performed at the top of the loop.
            print('Append error, logging in again: ' + str(e))
            continue

        # Wait 30 seconds before continuing
        print('Wrote a message to MQTT broker')
        time.sleep(FREQUENCY_SECONDS)

except Exception as e:
    print('Error connecting to the MQTT server: {0}'.format(e))
