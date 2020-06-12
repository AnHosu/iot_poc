"""
Created on Sat Apr 11 07:30:05 2020
@author: AnHosu
"""

# /*
# * Based on
# * https://github.com/aws/aws-iot-device-sdk-python/blob/master/samples/greengrass/basicDiscovery.py
# * and
# * https://github.com/pimoroni/bme680-python/blob/master/examples/temperature-pressure-humidity.py
# */

import os
import sys
import time
import uuid
import json
import argparse
from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider
from AWSIoTPythonSDK.core.protocol.connection.cores import ProgressiveBackOffCore
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.exception.AWSIoTExceptions import DiscoveryInvalidRequestException

### Setup for my particular sensor
import bme680
import smbus2

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY,smbus2.SMBus(1))
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY,smbus2.SMBus(1))

sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
### Sensor stuff done	
	
# Parameters
GROUP_CA_PATH = "./groupCA/" # Folder for saving gg group CA cert

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
thingName = args.clientId
topic = args.topic

# Configure client for gg core discovery
discoveryInfoProvider = DiscoveryInfoProvider()
discoveryInfoProvider.configureEndpoint(host)
discoveryInfoProvider.configureCredentials(rootCAPath, certificatePath, privateKeyPath)
discoveryInfoProvider.configureTimeout(10)
# Discover gg cores for the thing
discoveryInfo = discoveryInfoProvider.discover(thingName)
# Get connection info
caList = discoveryInfo.getAllCas()
coreList = discoveryInfo.getAllCores()
# Get info for the first core
groupId, ca = caList[0]
coreInfo = coreList[0]
coreConnectivityInfoList = coreInfo.connectivityInfoList

# Since the MQTT client expects a certificate file we have to
#  put the group certificate authority into a file and save
#  the path
groupCA = GROUP_CA_PATH + groupId + "_CA_" + str(uuid.uuid4()) + ".crt"
if not os.path.exists(GROUP_CA_PATH):
    os.makedirs(GROUP_CA_PATH)
groupCAFile = open(groupCA, "w")
groupCAFile.write(ca)
groupCAFile.close()
    
# Initialise the MQTT client
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureCredentials(groupCA, privateKeyPath, certificatePath)

# Loop over and try connection with each set of host name and port
connected = False
for connectionInfo in coreConnectivityInfoList:
    coreHost = connectionInfo.host
    corePort = connectionInfo.port
    myAWSIoTMQTTClient.configureEndpoint(coreHost, corePort)
    try:
        myAWSIoTMQTTClient.connect()
        connected = True
        break
    except BaseException as e:
        pass

if not connected:
    print("Cannot connect to core %s. Exiting..." % coreInfo.coreThingArn)
    sys.exit(-2)


loopCount = 0
while True:
    message = {}
    message['sequence'] = loopCount
    if sensor.get_sensor_data():
        message['temperature'] = sensor.data.temperature
        message['pressure'] = sensor.data.pressure
        message['humidity'] = sensor.data.humidity
        message['message'] = "Succes"
    else:
        message['temperature'] = None
        message['pressure'] = None
        message['humidity'] = None
        message['message'] = "Fail"
    messageJson = json.dumps(message)
    myAWSIoTMQTTClient.publish(topic, messageJson, 0)
    print('Published topic %s: %s\n' % (topic, messageJson))
    loopCount += 1
    time.sleep(10)
