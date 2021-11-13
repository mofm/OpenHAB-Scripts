This repository is my Collection of scripts used for OpenHAB (or any other purpose).  
They will most likely use MQTT as a transport, and therefore will be quite generic.  

They are intended for use on remote devices (raspberry PI for example) for sending sensor information  or responding to command.

### NOTES:

* Converted old mqtt.dhtsensor.py (Python 2) to Python 3 and changed for GroovePI  DHT11 Sensor. 
* Added Systemd service file for OpenHab. (dht11.service)
    - Copy dht11.service file to /etc/systemd/system
    - $ systemctl enable dht11.service
    - $ systemctl start dht11.service
