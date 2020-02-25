# Publishing to AWS
In this tutorial we will obtain a value from a sensor and publish it to a topic on AWS. No added shenanigans; this is as simple as it gets.<br>
At the core of it, we want to grab a reading from the sensor, wrap it in a message with some useful metadata, and publish that to AWS IoT. We will want to do that continuosly on a loop, meaning that our script should end up being structured as follows.<br>
```
Prepare the sensor
Set up connection to AWS
while true
    get a sensor reading
    pack it up
    publish it
```
I will not elaborate too much on the sensor setup here, but we will be using the Bosch BME680 air quality sensor. The BME680 does four different measurements, but for this case we will only be measuring and publishing the temperature.
# Registering the Sensor in IoT Core
Before we can start connecting a sensor to AWS, we need to register the sensor or system as a so-called Thing in AWS IoT Core. The docs have a [getting started guide](https://docs.aws.amazon.com/iot/latest/developerguide/register-device.html "AWS IoT docs") which is pretty good. Follow the guide, but at the end of it, make sure you have the following:
* A device certificate file
* A private key file
* The root certificate file
* In the policy you attached to the certificate, you have allowed publishing from an ID and to a topic that you can remember

The three files should be installed on the controller device. In this case, that just means the files should be in accessible place on the Raspberry Pi. The ID will be used as clientID for the client that we will use to connect to AWS IoT in a little later, and the topic is a flag that helps you direct data along the right path. Both are explained in detail below.<br>
The policy used for examples in this case, follows this pattern:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Publish",
        "iot:Receive"
      ],
      "Resource": [
        "arn:aws:iot:your-region:your-aws-account:topic/bme680/temperature"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect"
      ],
      "Resource": [
        "arn:aws:iot:your-region:your-aws-account:client/simple-publishing"
      ]
    }
  ]
}
```
# Setting up the SDK
We will do scripting for this case using Python. AWS IoT currently has two SDKs for Python. For this case we will use version 1, which is easily installed using pip:
```bash
pip install AWSIoTPythonSDK
```
The AWS IoT code below should work for any version of Python, but the interaction with the BME680 sensor is written with Python 3.7.
# Publishing to AWS IoT
Now we are ready to get started on developing with the SDK.<br>
Publishing a message to AWS using the Python SDK will look something like this
```python
AWSIoTMQTTClient.publish(topic, messageJSON, 1)
```
The AWSIoTMQTTClient is the object that we will use to configure and establish the connection to AWS IoT Core. The [.publish()](https://s3.amazonaws.com/aws-iot-device-sdk-python-docs/sphinx/html/index.html#AWSIoTPythonSDK.MQTTLib.AWSIoTMQTTClient.publish "AWS docs") method publishes the message and takes three arguments: the topic to publish to, the message to be sent, and a Quality of Service (QoS) flag. Lets look at each of these in turn.
### Topics
Messages in AWS are distributed and filtered using topics. Topics are a kind of tag that you can use to identify the source of the message and distribute it accordingly. It is just a single string, generally in the format
```
main_tag/secondary_tag/tertiary_tag/etc
```
For instance, if you had several factories each with several manufacturing lines with several stations each eqipped with sensors, you might do something like
```
factoryA/line22/drying/temperature
```
and then have another sensor on the same line publish to
```
factoryA/line22/milling/torque
```
That way you can direct these messages to the store or dashboard for the same line but seperate lambda functions, if that is needed for your application.<br>
An IoT thing needs permission to publish to a specific topic. This is done by adding a certificate with a permissive policy to the thing. By using the topic naming convention above and wildcards in the policy, you can create hierarchies and differentiated permissions for things in different parts of your application or factory setup.<br>
Now, for this demonstration example, we only have four sensors, and really we will only use one of them, so we will go with a simple topic. Like, say,
```
bme680/temperature
```
We will dive deeper into topics in the next tutorials, but for now we will leave it at this simple one.
### Message
The message is where you have the actual data point along with any metadata. It is structured as a [JSON](https://www.youtube.com/watch?v=wI1CWzNtE-M "JSON tutorial") and you can put whatever you want in there, but you will want the data point, a timestamp for the time of sampling, and maybe an idication whether the reading was succesful or not. In our script, we will structure the message to look something like this, when the sensor reading is successful
```json
{
    "utc_timestamp": 1581417910,
    "value": 23.6,
    "origin": "BME680 temperature",
    "status": "success"
}
```
### Quality of Service (QoS)
The messages are published to AWS using the MQTT protocol. This is a protocol commonly used in manufacturing systems, and is documented [online](http://mqtt.org/documentation "MQTT documentation"). You can also read about the [AWS flavour](https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html "AWS MQTT Documentation") of MQTT.<br>
As for Quality of Service (QoS), it is a flag specifying what happens when messages get lost in the network. The AWS flavour of MQTT accepts two QoS flags, 0 means that the message is delivered 'at most once'. 1 means that the message is delivered 'at least once'. So for QoS 0 the publisher will send the message once and then forget about it. If it does not get delivered, it is lost. For QoS, however, the message is sent, and the publisher then waits for a reply from the receiver before forgetting the message, and resends if neccessary. This ensures that the receiver gets the message at least once.<br>
Now, there are cases where QoS=0 is sufficient, but for this case we will use QoS=1.
# Connecting to AWS IoT
Before we can publish a message, we need to set up and configure the connection to AWS IoT. For this, we are going to need many small bits of information. Let us start by setting up the client.
```python
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
```
First of all, we are giving our client a client ID. This ID is used by the message broker to recognise the specific client or application that it is communicating with. This is especially importtant when we start subscribing to topics as well. For now, just provide an ID allowed by the policy made earlier.<br>
Next up we will setup the networking specifics.
```python
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
```
We are specifying where the MQTT messages are going and how they are authenticated. The host is your AWS IoT custom endpoint which you can find in the AWS Console under IoT Core > Settings. As for the port we will use the default 8883 for MQTT with the X.509 client certificate. Bringing us to the next order of business; certificates. The certificates are the ones you downloaded to your device earlier. You simply provide strings with the paths to each of these certificates; the root certificate file, the private key file, and finally the device certificate file.<br>
Next, we configure what happens when connection between the client and the broker on AWS IoT is lost.
```python
# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
```
With `.configureAutoReconnectBackoffTime(1, 32, 20)` we are telling the client to try to reconnect every 1 seconds after losing connection. If connection keeps being lost, for instance under poor networking conditions, this is exponentially increased to a maximum of every 32 seconds. This is to prevent having too many connection requests which would make the network conditions even works. If connection is maintained for more than 20 seconds, the reconnect interval is reset to 1.<br>
Next we are telling the client to keep all untransmitted messages while connection is lost by setting `.configureOfflinePublishQueueing(-1)`. If any other number is passed, this is the number of messages kept.<br>
When connection is reestablished, we will want to send off any kept messages, but not all at once. With `.configureDrainingFrequency(2)` we are telling the client to send one queued message every 2 seconds.<br>
In a moment, we will connect the client, by sending a connect request to the broker on AWS IoT. The client will then expect an acknowledgement of the request, but we do not want to wait forever. `.configureConnectDisconnectTimeout(10)` tells the client to wait a maximum of 10 seconds before timing out.<br>
Earlier we decided to use QoS=1. This will only work if the server acknowledges any message sent. If that does not happen we will also want a timeout `.configureMQTTOperationTimeout(5)` means that we will wait 5 seconds for that acknowledgement.<br>
Now, all that remains is to attempt the connection.
```python
# Connect to AWS IoT
myAWSIoTMQTTClient.connect()
```
# Bringing it all together
Here is our bare-bones script for connecting and publishing to AWS IoT. 
```python
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time

# Pass in values for clientID, host, port, and paths to certificates
port = 8883 # default

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
    message = {}
    message['sequence'] = loopCount
    message['timestamp_utc'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    # Value and any other data needed here
    messageJson = json.dumps(message)
    # This is the actual publishing to AWS
    myAWSIoTMQTTClient.publish(topic, messageJson, 1)
    loopCount += 1
    time.sleep(1)
```
The script [simple_publishing.py](https://github.com/AnHosu/iot_poc/blob/master/simple_publishing.py) is a full working example using the BME680 sensor. I can be called as follows
```bash
python simple_publishing.py -e <your aws iot endpoint> -r <file containing root certificate> -c <file containing device certificate> -k <file containing private key> -id <a client ID> -t <the topic to publish to>
```
# Running the Case
Running this script on a Pi with the BME680 sensor, when it is working, it should look like this
```
Compensated temperature: 21.58 *C
Published topic bme680/temperature: {"status": "success", "timestamp_utc": "2020-02-15T16:43:16.226983Z", "value": 21.57999999999999, "sequence": 25}

Compensated temperature: 21.58 *C
Published topic bme680/temperature: {"status": "success", "timestamp_utc": "2020-02-15T16:43:17.348050Z", "value": 21.57999999999999, "sequence": 26}

Compensated temperature: 21.58 *C
Published topic bme680/temperature: {"status": "success", "timestamp_utc": "2020-02-15T16:43:18.519356Z", "value": 21.57999999999999, "sequence": 27}
```
But the most interesting part, of course, is whether the data gets to AWS. Let us say that we published to the topic `BME680/temperature`. We can open the AWS Console, go to IoT Core, and find the Test tab. Here we can subscribe to a topic. When I type in the topic `BME680/temperature`, 
![test client](https://github.com/AnHosu/iot_poc/blob/master/images/aws_iot_test_simple_publish.PNG)
I get the messages sent from the Pi.
![test client](https://github.com/AnHosu/iot_poc/blob/master/images/aws_iot_message_simple_publish.PNG)
Congratulations, you are now publishing to AWS IoT! From here the messages can be redirected to whereever you want using AWS SNS, for instance to AWS Kinesis.<br>
# Application
In real life would you fire up a Raspberry PI running Python just to extract and publish data from a single sensor? No, probably not. In a real life setting, if you just wanted to publish data from a single sensor, you might use a microcontroller instead.<br>
On the other hand, if you have hundreds of sensors that you want to query and publish, a Raspberry Pi will not be enough. Instead you might want to use a proper gateway device, like CloudRail along with ethernet modules like IO-Link.