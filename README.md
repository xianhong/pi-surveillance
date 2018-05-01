# pi-surveillance
Turn Pi3 into a surveillance device and have it controlled via a server running Flask, MQTT broker and Redis

 It’s about having Pi3 capture and “analyze” live video stream about an environment , detect motion in real time and optionally send images with detected motion to cloud storage . MQTT messaging broker service is used to facilitate switching on/off pi3’s video surveillance. A python program deployed onto a virtual server in cloud provides a very basic  web front-end (Flask) for sending controlling signals to Pi3 (MQTT) and checking up-to-date Pi3 running status (MQTT, Redis) . In this case, MQTT broker service ,Redis and Python program (using Flask, MQTT & Redis) all run on the same virtual server in cloud (ex: AWS). 
## Credits
* The motion detection python code is based on a tutorial of pyimagesearch.com:  
https://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/

## Hardware involved:
* Raspberry Pi3 (RASPBian)
* a virtual server in cloud (ex: AWS EC2 Ubuntu instance)
* Any web browser for remote control of the Pi3 via the server in cloud.

## Platform software
* Raspberry : Python OpenCV 3.3 binding (Reference :https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi/)
* virtual server in cloud: Ubuntu 16.04 (OS), Python 2.7,  Paho-Mosquitto, Flask, Redis
* cloud based object storage account : portal.ECStestdrive.com

## How to use:
* Deploy codes in "pi" folder onto Pi3
* Deply codes in "flask_mqtt_redis_server" folder onto the virtual server in cloud

