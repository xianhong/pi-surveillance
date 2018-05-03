# pi-surveillance
Turn Pi3 into a surveillance device and have it controlled via a server running Flask, MQTT broker and Redis

 It’s about having Pi3 capture and “analyze” live video stream about an environment , detect motion in real time and optionally send images with detected motion to cloud storage . MQTT messaging broker service is used to facilitate switching on/off pi3’s video surveillance. A python program deployed onto a virtual server in cloud provides a very basic  web front-end (Flask) for sending controlling signals to Pi3 (MQTT) and checking up-to-date Pi3 running status (MQTT, Redis) . In this case, MQTT broker service ,Redis and Python program (using Flask, MQTT & Redis) all run on the same virtual server in cloud (ex: AWS). 
 * There are a few running states of Python program on Pi: "Program started", "Surveillance started","Surveillance stopped" and "Program stopped". The RGB bulb on Pi will change color when the program running state transits.For example, bulb turns green when surveillance is in action and blue when the program exiting the surveillance mode.
 * When the Python program changes running state, it also notifies the server (in cloud) by publishing a MQTT message. The server will update Pi's running status in Redis upon receiving the MQTT message announcing Pi's state change.
 * User can change Pi's running state by pointing a browser to the server (in cloud) and having it publish MQTT messages to Pi for it to change state. User can check out current Pi's running state through a web page on the server (in cloud).
 
## Credits
* The motion detection python code is based on a tutorial of pyimagesearch.com:  

https://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/

## Hardware involved:
* Raspberry Pi3 , PiCamera ,a RGB bulb and breadboard with jumper wires.
* a virtual server in cloud (ex: AWS EC2 Ubuntu instance)
* Any web browser for remote control of the Pi3 via the server in cloud.

## Platform software
* Raspberry : Raspbian Stretch (OS), OpenCV 3.3 Python binding 
  For installation of OpenCV 3.3 python binding on Raspbian Stretch , please check out the tutorial (https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi/). One caveat,though,is to add an argument(-D WITH_GTK=ON) to 'cmake' command  in Step #5 in order for OpenCV image rendering functions to work out properly.

* virtual server in cloud: Ubuntu 16.04 (OS), Python 2.7,  Paho-Mosquitto, Flask, Redis
* cloud based object storage account : portal.ECStestdrive.com

## How to use:
* Deploy codes in "pi" folder onto Pi; 
   Make necessary changes to file 'conf-template.json' and save it to a file named 'conf.json'in the same directory as the python codes. 
* Deply codes in "flask_mqtt_redis_server" folder onto the virtual server in cloud
   When running the server side Python program--'server.py' ,you need to provide MQTT broker service user id and password as arguments.

