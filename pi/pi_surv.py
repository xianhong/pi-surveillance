
from tempimage import TempImage
import paho.mqtt.client as mqtt
import warnings
import datetime
import imutils
import json
import time
import cv2
import boto
import RPi.GPIO as GPIO
import subprocess


def map(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(col):   # For example : col = 0x112233
        R_val = (col & 0x110000) >> 16
        G_val = (col & 0x001100) >> 8
        B_val = (col & 0x000011) >> 0

        R_val = map(R_val, 0, 255, 0, 100)
        G_val = map(G_val, 0, 255, 0, 100)
        B_val = map(B_val, 0, 255, 0, 100)

        p_R.ChangeDutyCycle(100-R_val)     # Change duty cycle
        p_G.ChangeDutyCycle(100-G_val)
        p_B.ChangeDutyCycle(100-B_val)


def on_message(client, userdata, message):
	global terminate
	global start
	m = str(message.payload.decode("utf-8"))
	if m=="START":
		print "Starting video surveillance"
		start = True
	elif m=="STOP":
		print "terminating"
		terminate= True
	
	
def surveillance_loop(conf):
	global terminate
	global cloud_storage_bucket
	# check to see if cloud upload should be used

	# initialize the camera and grab a reference to the raw camera capture
	camera = cv2.VideoCapture(0)	
	camera.set(3,conf["resolution"][0])
	camera.set(4,conf["resolution"][1])
	camera.set(5,conf["fps"])
	time.sleep(0.25)

	# allow the camera to warmup, then initialize the average frame, last
	# uploaded timestamp, and frame motion counter
	print("[INFO] warming up...")
	time.sleep(conf["camera_warmup_time"])
	avg = None
	lastUploaded = datetime.datetime.now()
	motionCounter = 0
	# capture frames from the camera
	while (terminate == False):
		# grab the raw NumPy array representing the image and initialize
		# the timestamp and occupied/unoccupied text
		(grabbed, frame) = camera.read()
		if not grabbed:
			break

		timestamp = datetime.datetime.now()
		text = "Unoccupied"

		# resize the frame, convert it to grayscale, and blur it
		frame = imutils.resize(frame, width=500)
		frame = cv2.flip(frame,-1)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (21, 21), 0)

		# if the average frame is None, initialize it
		if avg is None:
			print("[INFO] starting background model...")
			avg = gray.copy().astype("float")
			#rawCapture.truncate(0)
			continue

		# accumulate the weighted average between the current frame and
		# previous frames, then compute the difference between the current
		# frame and running average
		cv2.accumulateWeighted(gray, avg, 0.5)
		frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

		# threshold the delta image, dilate the thresholded image to fill
		# in holes, then find contours on thresholded image
		thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
			cv2.THRESH_BINARY)[1]
		thresh = cv2.dilate(thresh, None, iterations=2)
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]

		# loop over the contours
		for c in cnts:
			# if the contour is too small, ignore it
			if cv2.contourArea(c) < conf["min_area"]:
				continue

			# compute the bounding box for the contour, draw it on the frame,
			# and update the text
			(x, y, w, h) = cv2.boundingRect(c)
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
			text = "Occupied"

		# draw the text and timestamp on the frame
		ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
		cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
		cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
			0.35, (0, 0, 255), 1)

		# check to see if the room is occupied
		if text == "Occupied":
			setColor(colors['red'])   # Set light to "RED" to indicate that motion detected
			# check to see if enough time has passed between uploads
			if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
				# increment the motion counter
				motionCounter += 1

				# check to see if the number of frames with consistent motion is
				# high enough
				if motionCounter >= conf["min_motion_frames"]:
					# check to see if cloud upload sohuld be used
					if conf["use_cloud"]:
						# write the image to temporary file
						t = TempImage()
						cv2.imwrite(t.path, frame)

						# upload the image to cloud storage and cleanup the tempory image
						print("[UPLOAD] {}".format(ts))
						
						k = cloud_storage_bucket.new_key(ts)
						k.set_contents_from_filename(t.path)
						
						t.cleanup()

					# update the last uploaded timestamp and reset the motion
					# counter
					lastUploaded = timestamp
					motionCounter = 0

		# otherwise, the room is not occupied
		else:
			motionCounter = 0
			setColor(colors['green'])  # set light to "GREEN" to indicate no motion being detected.

		# check to see if the frames should be displayed to screen
		if conf["show_video"]:
			# display the security feed
			cv2.imshow("Security Feed", frame)
			key = cv2.waitKey(1) & 0xFF

			# if the `q` key is pressed, break from the lop
			if key == ord("q"):
				terminate = True

	if conf["show_video"]:cv2.destroyAllWindows()
	camera.release()
try:
	subprocess.call(["sudo modprobe bcm2835-v4l2"],shell=True)  # load the v4l2 driver before using OpenCV's video capturing
	colors = {'red':0xFF0000, 'green':0x00FF00, 'blue':0x0000FF}
	pins = {'pin_R':11, 'pin_G':12, 'pin_B':13}  # pins is a dict			
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	for i in pins:
        	GPIO.setup(pins[i], GPIO.OUT)   # Set pins' mode is output
        	GPIO.output(pins[i], GPIO.HIGH) # Set pins to high(+3.3V) to off led
	p_R = GPIO.PWM(pins['pin_R'], 2000)  # set Frequece to 2KHz
	p_G = GPIO.PWM(pins['pin_G'], 2000)
	p_B = GPIO.PWM(pins['pin_B'], 2000)

	p_R.start(0)      # Initial duty Cycle = 0(leds off)
	p_G.start(0)
	p_B.start(0)
	terminate = False
	start = False
	# filter warnings, load the configuration and initialize the cloud storage access credentials
	warnings.filterwarnings("ignore")
	conf = json.load(open("conf.json"))
	if conf["use_cloud"]:
		session = boto.connect_s3(conf["cloud"]["access_key"], conf["cloud"]["secret_key"], host=conf["cloud"]["endpoint"])
		cloud_storage_bucket = session.get_bucket(conf["cloud"]["bucket"])
		print("[SUCCESS] cloud account linked")


	broker_address=conf['mqtt']['broker']
	client = mqtt.Client(protocol=mqtt.MQTTv31) #create new instance
	client.on_message=on_message #attach function to callback
	print("Connecting to broker ...")
	client.username_pw_set(conf['mqtt']['username'], password=conf['mqtt']['password'])
	client.connect(broker_address) #connect to broker
	client.loop_start() #start the loop
	client.subscribe("pi_surveillance/control") ### USE YOUR OWN TOPIC NAME
	# Set light to "BLUE" to indicate that the surveillance is disabled.
	setColor(colors['blue'])
	
	client.publish('pi_surveillance/status',str({'time':datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),'status':'Program Started'}))
	
	while True:
		if start:
			terminate = False
			client.publish('pi_surveillance/status',str({'time':datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),'status':'Surveillance Started'}))
			surveillance_loop(conf)
			# Set light to "BLUE" to indicate that the surveillance is disabled
			setColor(colors['blue'])
			terminate = False
			start = False
			client.publish('pi_surveillance/status',str({'time':datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),'status':'Surveillance Stopped'}))
		time.sleep(1)
except KeyboardInterrupt:
	# clean up GPIOs
	p_R.stop()
	p_G.stop()
	p_B.stop()
	for i in pins:
		GPIO.output(pins[i], GPIO.HIGH)    # Turn off all leds
	GPIO.cleanup()
	client.publish('pi_surveillance/status',str({'time':datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),'status':'Program stopped'}))
	time.sleep(4)
	client.disconnect() #disconnect
	client.loop_stop() #stop the loop

	
