# Publishing to AWS
In this tutorial we will obtain a value from a sensor and publish it to a topic on AWS. No added shenanigans; this is as simple as it gets.

## Registering the Sensor in IoT Core

## Setting up the SDK

## Scripting
It is finally time to code. Let us review what we are trying to do.
At the core of it we want to grab a reading from the sensor, wrap it in a message with some useful metadata, and publish that to AWS IoT. We will want to do that continuosly on a loop, meaning that our script should end up being structured as follows.<br>
```
Prepare the sensor
Set up connection to AWS
while true
    get a sensor reading
    pack it up
    publish it
```
I will not elaborate on the sensort setup here, but if you are interested in the BME680 sensor, I will happily do a seperate tutorial. For now, let us focus on the connection and publishing parts.<br>
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
That way you can direct these messages to the store or dashboard for the same line but seperate lambdas, if that is needed for your application.<br>
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
and when unsuccessful
```json
{
    "utc_timestamp": 1581417925,
    "value": null,
    "origin": "BME680 temperature",
    "status": "fail"
}
```
### Quality of Service (QoS)
The messages are published to AWS using the MQTT protocol. This is a protocol commonly used in manufacturing systems, and is documented [online](http://mqtt.org/documentation "MQTT documentation"). You can also read about the [AWS flavour](https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html "AWS MQTT Documentation") of MQTT.<br>
As for Quality of Service (QoS), it is a flag specifying what happens when messages get lost in the network. The AWS flavour of MQTT accepts two 