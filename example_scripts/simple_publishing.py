"""
Created on Wed Feb 12 07:30:05 2020
@author: AnHosu

This simple example of publishing to AWS IoT with is to be used 
 along with the tutorial at:
 https://github.com/AnHosu/iot_poc/blob/master/publishing.md
"""

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import argparse
import json
from datetime import datetime
import time

### Setup for my sensor
import bme680
import smbus2

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY,smbus2.SMBus(1))
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY,smbus2.SMBus(1))

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
parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
clientId = args.clientId
topic = args.topic
port = 8883

if not args.certificatePath or not args.privateKeyPath:
    parser.error("Missing credentials for authentication.")
    exit(2)

# Initialise the AWS IoT MQTT Client
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# Configuration of the client
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connectto AWS IoT
myAWSIoTMQTTClient.connect()
time.sleep(2)

# Publish to the same topic in a loop forever
loopCount = 0
while True:
    message = {}
    message['sequence'] = loopCount
    if sensor.get_sensor_data():
        message['value'] = sensor.data.temperature
        message['status'] = "success"
    else:
        message['value'] = None
        message['status'] = "fail"
    message['timestamp_utc'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    messageJson = json.dumps(message)
    # This is the actual publishing to AWS
    myAWSIoTMQTTClient.publish(topic, messageJson, 1)
    print('Published topic %s: %s\n' % (topic, messageJson))
    loopCount += 1
    time.sleep(3)
