"""
Created on Wed Mar 04 15:01:15 2020

@author: AnHosu

This simple example of subscribing to topics from AWS IoT with is to be used 
 along with the tutorial at:
 https://github.com/AnHosu/iot_poc/blob/master/shadow.md
"""
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import argparse
import json
from datetime import datetime

### Setup for my sensor
import bme680

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)

### Sensor stuff done

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub", help="Targeted client id")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
clientId = args.clientId
port = 8883

if not args.certificatePath or not args.privateKeyPath:
    parser.error("Missing credentials for authentication.")
    exit(2)

# Define topic for updates
topic_update = "$aws/things/" + clientId + "/shadow/update"

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
time.sleep(2)

# Specify what to do, when we receive an update
def callback_update_accepted(client, userdata, message):
    print("Got an update, on the topic:")
    print(str(message.topic))
    print("The message is this")
    print(str(message.payload))

# Specify what to do, when the update is rejected
def callback_update_rejected(client, userdata, message):
    print("The update was rejected. Received the following message:")
    print(str(message.payload))

# Subscribe
myAWSIoTMQTTClient.subscribe(topic_update + "/accepted", 1, callback_update_accepted)
time.sleep(2)
myAWSIoTMQTTClient.subscribe(topic_update + "/rejected", 1, callback_update_rejected)
time.sleep(2)
# Publish to the same topic in a loop forever
while True:    
    message = {}
    if sensor.get_sensor_data():
        temperature = sensor.data.temperature
    else:
        temperature = None
    message["state"] = { "reported" : {"temperature" : temperature } }
    messageJson = json.dumps(message)
    # Update the shadow
    myAWSIoTMQTTClient.publish(topic_update, messageJson, 1)
    time.sleep(15)
