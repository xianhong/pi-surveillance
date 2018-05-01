# pi-surveillance
Turn Pi3 into a surveillance device and have it controlled via a server running Flask, MQTT broker and Redis
## Hardware involved:
* Raspberry Pi3 (RASPBian)
* a virtual server in cloud (ex: AWS EC2 Ubuntu instance)
* Any web browser for remote control of the Pi3 via the server in cloud.

## Platform software
* Raspberry : Python OpenCV 3.3 binding
* virtual server in cloud: Ubuntu 16.04 (OS), Python 2.7,  Paho-Mosquitto, Flask, Redis
* cloud based object storage account : portal.ECStestdrive.com

## How to use:
* Deploy codes in "pi" folder onto Pi3
* Deply codes in "flask_mqtt_redis_server" folder onto the virtual server in cloud

