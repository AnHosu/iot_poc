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
from subprocess import PIPE, Popen

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
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
parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Topic for publishing")
parser.add_argument("-s", "--subtopic", action="store", dest="subtopic", default="sdk/test/Python", help="Topic for subscribing")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
clientId = args.clientId
root_pubtopic = args.topic
subtopic = args.subtopic
port = 8883

if not args.certificatePath or not args.privateKeyPath:
    parser.error("Missing credentials for authentication.")
    exit(2)
    
# Callback function for when we receive a message
def callback_function(client, userdata, message):
    print("Received a new message:\n{0}".format(message.payload))
    print("from topic:\n{0}".format(message.topic))
    payload = json.loads(message.payload)
    global pubtopic
    global variable
    if "action" not in payload:
        pubtopic = None
        variable = None
    else:
        if payload["action"] == "temperature":
            pubtopic = root_pubtopic + "temperature"
            variable = root_pubtopic + "temperature"
        elif payload["action"] == "pressure":
            pubtopic = root_pubtopic + "pressure"
            variable = "pressure"
        elif payload["action"] == "humidity":
            pubtopic = root_pubtopic + "humidity"
            variable = "humidity"
        else:
            pubtopic = None
            variable = None

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
myAWSIoTMQTTClient.subscribe(subtopic, 1, callback_function)
time.sleep(2)

# Publish to the same topic in a loop forever
pubtopic = None
variable = None
loopCount = 0
while True:
    if variable is not None:
        message = {}
        message['sequence'] = loopCount
        if sensor.get_sensor_data():
            # Get the value currently toggled
            value = None
            if variable == "temperature":
                value = sensor.data.temperature
            elif variable == "pressure":
                value = sensor.data.pressure
            elif variable == "humidity":
                value = sensor.data.humidity
            else:
                value = None
            message['value'] = value
            message['status'] = "success"
        else:
            message['value'] = None
            message['status'] = "fail"
        message['timestamp_utc'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        messageJson = json.dumps(message)
        # This is the actual publishing to AWS
        myAWSIoTMQTTClient.publish(pubtopic, messageJson, 1)
        print('Published topic %s: %s\n' % (pubtopic, messageJson))
    loopCount += 1
    time.sleep(5)