"""
Created on Wed Nov 12 07:30:05 2020
@author: AnHosu

This simple example of publishing to AWS IoT with is to be used 
 along with the tutorial at:
 https://github.com/AnHosu/iot_poc/blob/master/simple_publishing.py
"""

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import argparse
import json
from datetime import datetime
import time

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

# Gets the CPU temperature in degrees C
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

factor = 1.0  # Smaller numbers adjust temp down, vice versa
smooth_size = 10  # Dampens jitter due to rapid CPU temp changes
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

# Publish to the same topic in a loop forever
cpu_temps = []
loopCount = 0
while True:
    if sensor.get_sensor_data():
        # This is all about getting the temperature from my sensor
        #  compensating for the fact that I put it next to the CPU
        cpu_temp = get_cpu_temperature()
        cpu_temps.append(cpu_temp)

        if len(cpu_temps) > smooth_size:
            cpu_temps = cpu_temps[1:]

        smoothed_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
        raw_temp = sensor.data.temperature
        comp_temp = raw_temp - ((smoothed_cpu_temp - raw_temp) / factor)

        print("Compensated temperature: {:05.2f} *C".format(comp_temp))

        message = {}
        message['value'] = comp_temp
        message['sequence'] = loopCount
        message['timestamp_utc'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        message['status'] = "success"
        messageJson = json.dumps(message)
         # This is the actual publishing to AWS
        myAWSIoTMQTTClient.publish(topic, messageJson, 1)
        print('Published topic %s: %s\n' % (topic, messageJson))
        loopCount += 1
    else:
        message = {}
        message['value'] = None
        message['sequence'] = loopCount
        message['timestamp_utc'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        message['status'] = "fail"
        messageJson = json.dumps(message)
         # This is the actual publishing to AWS
        myAWSIoTMQTTClient.publish(topic, messageJson, 1)
        print('Published topic %s: %s\n' % (topic, messageJson))

    time.sleep(1)