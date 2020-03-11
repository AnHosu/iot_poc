# AWS Shadow Service Demonstration
The AWS IoT thing shadow service offers a lot of functionality and the possible applications are numerous and diverse. You can read all about the functions and possible applications in the [documentation](https://docs.aws.amazon.com/iot/latest/developerguide/iot-device-shadows.html "AWS thing shadow docs"). In this case we will not exemplify all of the functionality, rather we will get started using shadows with an example that is as simple in functionality as possible. Once we are done with this case we will not have built all that is possible with shadows but we will have come far enough to start understanding advanced functions and applications work.<br>
We will try to do something like this
```
Prepare the sensor
Set up connection to AWS
while true
    get a sensor reading
    update the shadow
    publish the reading
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

# Configure connection to AWS IoT

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
Whenever a shadow is successfully updated, it generates and publishes a message to the topic `$aws/things/yourDevice/shadow/update/accepted`. Once again, the exact name changes based on your device name. By subscribing to this specific topic with QoS = 1, your device or application can recieve updates whenever there are changes to the shadow.<br>
Another useful topic to subscribe to is `$aws/things/yourDevice/shadow/update/rejected`. A message is published to this topic whenever an update fails and can thus provide excellent feedback for an application or for debugging.<br>
You can subscribe to these topics just like you would any other topics. Again assuming that the client ID is identical to the device name, it might look something like this:
```python
# Define neccessary topics
topic_update = "$aws/things/" + clientId + "/shadow/update"

# Configure connection to AWS IoT

# Specify what to do, when we receive an update
def callback_update_accecpted(client, userdata, message):
    print("Got an update, on the topic:")
    print(message.topic)
    print("The message is this")
    print(message.payload)

# Specify what to do, when the update is rejected
def callback_update_rejected(client, userdata, message):
    print("The update was rejected. Received the following message:")
    print(message.payload)

# Subscribe
myAWSIoTMQTTClient.subscribe(topic_update + "/accepted", 1, callback_update_accepted)
myAWSIoTMQTTClient.subscribe(topic_update + "/rejected", 1, callback_update_rejected)
```
# Policies for Shadows
Before we move on to more shadow related topics, we should take a look at the policies needed to allow devices and applications to utilise these topics. The documentation is quite substantial and even provides [specific examples](https://docs.aws.amazon.com/iot/latest/developerguide/device-shadow-mqtt.html "shadow policy examples") for policies related to shadow interaction. Hence, I will refrain from repeating the documentation here, and we will instead construct an example.<br>
Imagine we have a device registered with the name my_sensor in AWS IoT. We would like to give the device access to establish a connection with AWS IoT, publish readings to the topic my_sensor/reading, update its shadow, and subscribe to the accepted and rejected responses generated on shadow update.<br>
We already know how to construct statements to allow connection and publishing.
```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [ "iot:Publish" ],
      "Resource": [
        "arn:aws:iot:your-region:your-aws-account:topic/my_sensor/reading"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [ "iot:Connect" ],
      "Resource": [ 
        "arn:aws:iot:your-region:your-aws-account:client/my_sensor" 
      ]
    }
  ]
}
```
To allow the desired shadow interactions, we will add another resource to the publish action, mentioning the topic `$aws/things/my_sensor/shadow/update`:<br>
```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [ "iot:Publish" ],
      "Resource": [
        "arn:aws:iot:your-region:your-aws-account:topic/my_sensor/reading",
        "arn:aws:iot:your-region:your-aws-account:topic/$aws/things/my_sensor/shadow/update"
      ]
    }
  ]
}
```
To allow subscription we will add a subscription action and two resources - one for each topic.
```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [ "iot:Subscribe" ],
      "Resource": [
        "$aws/things/my_sensor/shadow/update/accepted",
        "$aws/things/my_sensor/shadow/update/rejected"
      ]
    }
  ]
}
```
Given that the two subscription topics have the same root and that there are more update/ topics to subsrcibe to, it is tempting to add something along the lines of `$aws/things/my_sensor/shadow/update/*`, giving a wildcard for anything below the update root. While this would indeed work as intended now, AWS reserves the right to add additional reserved topics to the existing structure. If we were to use a policy with this type of wildcard, we thus risk allowing access to future topics causing unintended behaviour or information breaches. Therefore AWS discourages the use of wildcards in this way.<br>
Our final policy looks like this:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [ "iot:Publish" ],
      "Resource": [
        "arn:aws:iot:your-region:your-aws-account:topic/my_sensor/reading",
        "arn:aws:iot:your-region:your-aws-account:topic/$aws/things/my_sensor/shadow/update"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [ "iot:Connect" ],
      "Resource": [ 
        "arn:aws:iot:your-region:your-aws-account:client/my_sensor" 
      ]
    },
    {
      "Effect": "Allow",
      "Action": [ "iot:Subscribe", "iot:Receive" ],
      "Resource": [
        "arn:aws:iot:your-region:your-aws-account:topicfilter/$aws/things/my_sensor/shadow/update/accepted",
        "arn:aws:iot:your-region:your-aws-account:topicfilter/$aws/things/my_sensor/shadow/update/rejected"
      ]
    }
  ]
}
```
You might notice that we added an `iot:Receive` action to the subscription topics. This is not strictly needed, but offers us a little extra flexibility. The subscription action is only checked whenever a client connects to AWS, whereas the receive policy is checked each time a message is sent. This means that we have the option to disallow messages from a specific topic to devices using this certificate, even if they are already subscribing to the topic. Maybe useful in your case, maybe not, but now you know it exists.
# Building the Demonstration
