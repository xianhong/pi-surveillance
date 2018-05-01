import os
from flask import Flask, render_template, redirect, request, url_for, make_response
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import redis
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-u", "--user", required=True,
	help="mqtt user id")
ap.add_argument("-P", "--password", required=True,
	help="mqtt user password")
	
args = vars(ap.parse_args())
mqtt_user=args['user']
mqtt_password=args['password']
app = Flask(__name__)

@app.route('/')
def mainpage():
	resp = make_response(render_template('template.html'))
	return resp

@app.route('/status')
def status():
	
	last_update_time= r.hget('Pi_Status','time')
	latest_status = r.hget('Pi_Status','status')
	
	resp = "  <h3> - Pi Status Check- </h3> Update time: <b>"+last_update_time
	resp += "</b><br>Pi Status: <b>"
	resp += latest_status
	resp += '</b><br><a href="/"><h3>Back to main menu</h3></a>'
	return resp

@app.route('/suthankyou.html', methods=['POST'])
def suthankyou():
	global broker_address
	## This is how you grab the contents from the form
	username = request.form['username']
	password = request.form['password']
	message = request.form['message']
	
	print username,password,message
	ret=publish.single('pi_surveillance/control',payload=message,hostname=broker_address,auth={'username':username,'password':password})
	
	
	if (ret== None):
		resp= "Publish OK"
	else:
		resp = "Publish error"
	resp += '<br><a href="/status"><h3>Go to check Pi status</h3></a>'
	return resp
	
def on_message(client, userdata, message):
	global r
	m = message.payload.decode("utf-8")
	dic = eval(m) 
	if type(dic)==dict:
		print dic
		r.hmset('Pi_Status', dic)
		print r.hget('Pi_Status','status'),r.hget('Pi_Status','time')


if __name__ == "__main__":
	r = redis.Redis(host='127.0.0.1', port='6379')
	broker_address="127.0.0.1"
	client = mqtt.Client("client1") #create new instance
	client.on_message=on_message #attach function to callback
	print("Connecting to broker ...")
	client.username_pw_set(mqtt_user, password=mqtt_password)
	client.connect(broker_address) #connect to broker
	client.loop_start() #start the loop
	client.subscribe("pi_surveillance/status") ### subscribe to the message to listen to any status update
	app.run(debug=False, host='0.0.0.0',port=int(os.getenv('PORT', '5000')), threaded=True)
	print "Ending main thread"
	client.disconnect() #disconnect
	client.loop_stop() #stop the loop
