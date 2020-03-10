# AWS Shadow Service Demonstration
The AWS IoT thing shadow service offers a lot of functionality and the possible applications are numerous and diverse. You can read all about the functions and possible applications in the [documentation](https://docs.aws.amazon.com/iot/latest/developerguide/iot-device-shadows.html "AWS thing shadow docs"). In this case we will not exemplify all of the functionality, rather we will get started using shadows with an example that is as simple in functionality as possible. Once we are done with this case we will not have built all that is possible with shadows but we will have come far enough to start understanding advanced functions and applications work.<br>
We will try to do something like this
```
Prepare the sensor
Set up connection to AWS
while true
    get a sensor reading
    update the shadow
    confirm that the shadow was updated
```
We will then look at the shadow document using the AWS IoT test functionality.
# The Shadow Document
The shadow of a thing is a JSON document containing predetermined fields. An example of a shadow document could be
```json
{
    "state":{
      "reported":{
        "value": 27.87
      }
    },
    "metadata":{
      "reported":{
        "value":{
          "timestamp":1583755496
        }
      }
    },
    "version":4,
    "timestamp":1583755643
}
```
Let us walk through each of the fields one at a time.<br>
`state` holds the current values of the thing. The `reported` field should hold the current values as reported by the device itself. It can hold any number of reporting fields and a field can be an array.<br>
Besides `reported` the `state` field can also hold a `desired` field which can hold desired values as requested by an application or another device. This could be useful if you are doing a case with automation or maybe a home IoT project.<br>
This could be the state of a thing consisting of a valve and a flow meter where an application or maybe a user has just requested a new state:
```json
{
    "state":{
      "reported":{
        "flow": 15.04,
        "valve_state": "open"
      },
      "desired":{
          "flow": 0,
          "valve_state": "closed"
      }
    }
}
```
We will not use the desired field for this demonstration. We will just report the latest temperature
```json
{
    "state":{
      "reported": { "temperature" : 21.6 }
    }
}
```
The `metadata`field holds information on when each of the values in the `state` field were updated. The field follows the sam schema as `state` and the information is given as a UTC timestamp, representing when the value was last updated.<br>
The `version` field is a super useful feature. It is an integer that increases every time an update is made to the document, allowing applications and device to know whether their local copy is the latest.<br>
The `timestamp` field indicates the UTC timestamp of when the update was transmitted from AWS IoT.<br>
Fields that are set to Null are deleted from the shadow document rather than reporting the Null.
You can read more about the shadow document in the [developer guide](https://docs.aws.amazon.com/iot/latest/developerguide/device-shadow-document.html "Shadow document developer guide")
# Updating a Device Shadow
Updating the shadow of a device is done by sending a message to a specific topic. The topic is in the format `$aws/things/yourDevice/shadow/update` and depends on the name of the device registered in AWS IoT. If your device was called 'factory3Airflow' then the topic would be `$aws/things/factory3Airflow/shadow/update`.<br>
The update message might look something like this
```json
{
    "state": {
        "reported": {
            "flow": 2.6
        }
    }
} 
```
Coding such a flow is quite similar to what we did for [publishing](https://github.com/AnHosu/iot_poc/blob/master/publishing.md "publishing case"), except the topic is a bit more elaborate. Assuming that the client ID is the same as the device name, we can configure a connection and start updating the shadow like this:
```python
# Define neccessary topics
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

# Keep updating the shadow on an infinite loop
while True:
    message = {}
    temperature = get_sensor_reading()
    message["state"] = { "reported" : {"temperature" : temperature } }
    messageJson = json.dumps(message)
    # Update the shadow
    myAWSIoTMQTTClient.publish(topic_update, messageJson, 1)
    time.sleep(30)
```
This is fine and all but how do we know that it works?
# Subscribing to Shadow Updates
Whenever a shadow is successfully updated, it generates and publishes a message to the topic `$aws/things/yourDevice/shadow/update/accepted`. Once again, the exact name changes based on your device name. By subscribing to this specific topic with QoS = 1, your device or application can recieve updates whenever there are changes to the shadow.
```python
# Define neccessary topics
topic_update = "$aws/things/" + clientId + "/shadow/update/accepted"

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

# Callback function and subscribing
```
# Topics and Policies for Shadows