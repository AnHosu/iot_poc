# Publishing and Subscribing with AWS IoT
In this tutorial, we will add upon the [previous](https://github.com/AnHosu/iot_poc/blob/master/publishing.md "simple publishing") tutorial by having our gateway device, the Raspberry Pi, subscribe to messages on a topic. With publishing, the information flow is from the device to AWS IoT, but with subscribing, the flow is reversed to be from AWS IoT to the client we configure. As we will see, the ability to subscribe as well as publish, is extremely useful for structuring and managing devices remotely.<br>
We only need a few simple additions to our existing publish setup to make publishing work. The general structure of what we will do is:
```
prepare the sensor
configure connection to AWS
*define what happens with subscriptions
*start subscribing
while true
    get a sensor reading
    pack it up
    publish it
```
The lines marked with an asterisk*, are new additions and are covered in this tutorial. The rest are covered in the [previous](https://github.com/AnHosu/iot_poc/blob/master/publishing.md "simple publishing") tutorial.
# Registering the Sensor in IoT Core
Just as it is the case with publishing, we need to register the device that will subscribe to messages. We can use the same Thing and certificate as before, but we need to change the policy to allow subscription through using that certificate. This is accomplished by adding an additional statement to the policy allowing the action iot:Subscribe and providing the topic(s) to subscribe from. Here is an example of such a policy document.
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
        "arn:aws:iot:your-region:your-aws-account:topic/bme680/temperature",
        "arn:aws:iot:your-region:your-aws-account:topic/bme680/pressure",
        "arn:aws:iot:your-region:your-aws-account:topic/bme680/humidity",
        "arn:aws:iot:your-region:your-aws-account:topicfilter/bme680/actions"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Subscribe"
      ],
      "Resource": [
        "arn:aws:iot:your-region:your-aws-account:topicfilter/bme680/actions"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect"
      ],
      "Resource": [
        "arn:aws:iot:your-region:your-aws-account:client/simple-subscribing"
      ]
    }
  ]
}
```
This is the policy document we will use for the following example. One thing to note is that the topic we are allowing subscription, `bme680/action`, we are also allowing publishing to. This allows us to test the subscription using the AWS IoT Console without introducing additional devices and certificates.
# Subscribing to Topics
Like publishing, subscribing can be done with just one line of code. We just need to call the [.subscribe()](https://s3.amazonaws.com/aws-iot-device-sdk-python-docs/sphinx/html/index.html#AWSIoTPythonSDK.MQTTLib.AWSIoTMQTTClient.subscribe "subscribe docs") function of the IoT client.
```python
AWSIoTMQTTClient.subscribe(topic, 1, callback)
```
The first argument is the topic to listen to. Note that the certificate provided to the client must have a policy that allows subscription to that specific topic.<br>
The second argument is the Quality of Service, [just as for publishing](https://github.com/AnHosu/iot_poc/blob/master/publishing.md#quality-of-service-qos), 0 means at most once and 1 means at least once. Remember that now the roles are reversed, and the client we are configuring is the one that will have to send a confirmation of a message received. Fortunately that is all taken care of behind the scenes.<br>
The third argument is a custom function that is called whenever a message is received on the topic. This function should follow the pattern `callback_function(client, userdata, message)`. `message` will then be an object containing the topic, `message.topic`, and the body, `message.payload`, of the message. The two variables `client` and `userdata` are there for compatibility of the callback stack. They are flagged for deprecation, and it is not recommended to rely on them. The simplest thing to do when receiving a message, save for doing nothing at all, would be to print the message. Such a function might look like this
```python
def callback_function(client, userdata, message):
    print("Received a new message:\n{0}".format(message.payload))
    print("from topic:\n{0}".format(message.topic))
```
In the next section, we will use this function to do cool things.<br>
The subscription can be set up as soon as connection between the client and AWS IoT is established. The client will then listen for any published messages for as long as it lives or until the subscription is terminated. This also means that we do not have to listen in an infinite loop like we were publishing in an infinite loop earlier.<br>
With this, we have everything needed to set up a subscription:
```python
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

# Define what happens when messages are received
def callback_function(client, userdata, message):
    print("Received a new message:\n{0}".format(message.payload))
    print("from topic:\n{0}".format(message.topic))

# Subscribe
AWSIoTMQTTClient.subscribe(topic, 1, callback)

# Wait for messages to arrive
while True:
    time.sleep(5)
```
A full working example can be found [here](https://github.com/AnHosu/iot_poc/blob/master/simple_subscribing.py "simple subscribing example"). We run the script from a terminal on the Pi:
```bash
python simple_subscribing.py -e <your aws iot endpoint> -r <file containing root certificate> -c <file containing device certificate> -k <file containing private key> -id <a client ID> -t <the topic to subscribe to>
```
Nothing happens before we start publishing messages to our topic of choice. I ran the example on my Pi, using the topic `/bme680/actions`. I then moved to the test suite at AWS IoT Core > Test, and published a message to that topic.<br>
![test client](https://github.com/AnHosu/iot_poc/blob/master/images/aws_iot_test_simple_subscribe.PNG)<br>
The console output on the Pi then looks like this:
```
Received a new message:
{
    "message": "Hello from AWS IoT Console"
}
from topic:
bme680/action
```
Congratulations! You now know how to subscribe to a topic using the AWS IoT Python SDK. The real power of subscription, however, lies in combining it with publishing. In the next section, we will build a small example of how to use subscription with publishing to great effect.
# A Subscription Example
In the case of simple publishing we were getting temperature readings from the BME680 sensor and published them to AWS IoT on an infinite loop. However, the BME680 sensor is also able to measure relative humidity and air pressure. In real life you would want to use this expensive sensor to measure all three at once, but for this case we are going to build a way for us to remotely toggle between measuring these three variables. We will set up a subsription that listens to commands published on a specific topic. We will then use the content of that message to change which variable is measured and published by the device and sensor.<br>
First we will choose our topics. We will publish on three different topics depending on the variable that we are measuring.
```
bme680/temperature
bme680/pressure
bme680/humidity
```
In addition to this, we will reserve a topic for publishing actions to our device.
```
bme680/action
```
Imagine now that we will publish messages on this topic telling the device what to do. For instance, we might send the message
```json
{
    "action":"pressure"
}
```
telling the device to switch to measuring pressure and publish on the appropriate topic. Publishing this message will be simple enough using the AWS IoT test suite, but we need to code up the response behaviour first. To this end, we will use the callback function
```python
topic = None
variable = None
def callback_function(client, userdata, message):
    payload = json.loads(message.payload)
    global pubtopic
    global variable
    if "action" not in payload:
        topic = None
        variable = None
    else:
        if payload["action"] == "temperature":
            topic = "bme680/temperature"
            variable = "temperature"
        elif payload["action"] == "pressure":
            topic = "bme680/pressure"
            variable = "pressure"
        elif payload["action"] == "humidity":
            topic = "bme680/humidity"
            variable = "humidity"
        else:
            topic = None
            variable = None
```
We will then use these global variables to adjust what variable we get from the sensor before publishing on the infinite loop.
```python
while True:
    if sensor.get_sensor_data():
        # Get the value currently toggled
        value = None
        if variable = "temperature":
            value = sensor.data.temperature
        elif variable = "pressure":
            value = sensor.data.pressure
        elif variable = "humidity":
            value = sensor.data.humidity
        elif:
            value = None
        message = {}
        message['value'] = value
        message['variable'] = variable
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
```
The whole script is [here](https://github.com/AnHosu/iot_poc/blob/master/simple_pubsub.py "simple pubsub example"). When run, it will start to listen to the topic subscibed to. Once it receives a message with instructions it will start querying the sensor as instructed and publish. This way we can toggle between different sensors and even shut off messages when we do not need them and save some money.