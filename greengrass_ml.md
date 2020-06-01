# Advanced Features of Greengrass
We are about to build something really cool. Machine learning inference managed from the cloud but performed at the edge might sound like a sequence of flimsy business colloquialisms and to some extent they might be. In this demonstration, however, we will dive into the actual technical substance behind these terms.<br>
Specifically, we will apply advanced features of AWS Greengrass, including
- Creating and interacting with a local Shadow
- Shadow synchronisation with the cloud
- Decoupling data generation and application using a Shadow
- Long-running Lambda functions
- Machine learning resources
- Machine learning inference in the Greengrass Group with a Tensorflow2 model

The target of the demonstration is to build a small IoT application that predicts whether it is raining or not, given the current temperature, relative humidity, and pressure. The weather data comes from our BME680 air quality sensor, and our Raspberry Pi 3B+ will play the role of gateway device.<br>
We will be utilising expertise from the previous demonstrations of [publishing](publishing.md), [subscribing](pubsub.md), [Shadows](shadow.md), and [general Greengrass features](greengrass.md).<br>
# Set Up
To build the target demonstration, we will walk through three parts. First we will set up a local Shadow within our Greengrass group and use obtained sensor values to contiuously update the Shadow. Then we will enable synchronisation between the local Shadow and a cloud copy of the Shadow. Last, but not least, we will set up inference with a Tensorflow2 machine learning model.<br>
We will not cover installing and setting up Greengrass Group with a device as this was covered in the [general introduction to Greengrass](greengrass.md#install-and-configure-greengrass). Be sure to refer to previous demonstrations when in doubt.<br>
<div align="center">
	<img width=500 src="images/greengrass_ml_architecture.jpg" alt="Greengrass ML Demo Architechture">
	<br>
    This is the overall architechture of the application we will build in this demonstration.
</div>

Let us get started!
# Publish to Local Shadow 
In this section we will set up a local Shadow and build a Lambda function that takes values published by our sensor and updates the Shadow.<br>
## Prepare the Thing
We already have a [script](greengrass_thing.md) that connects our Thing, the sensor, and publishes readings to our Greengrass Group on a local topic. There is no need to modify it in any way. We will just leave it running, continuously publishing values to a local topic. I went with the topic `bme680/readings` but any topic goes, just remember it, as we need it in a moment.
## The Local Shadow Service
Any Thing we include in our Greengrass Group lives only inside the Group and only connects to the cloud when first discovering the Group. This is great for reducing the number of devices connected to the cloud, but it also means that we cannot directly take advantage of the Shadow that is in the cloud.<br>
Fortunately, Greengrass provides a Local Shadow Service inside Greengrass that we can use instead. The local Shadow service works in a very similar way to the Shadow in the cloud. The Shadow document follows the same schema, it is interacted with using the exact same topics, and it can be get, updated, and deleted. The Shadow lives inside the Greengrass Group and is only accessible to entities connected to the group.<br>
For instance, assume we have a Thing called `my_sensor` and an MQTT client that is connected to our Greengrass Core, we can publish an update to the Shadow of our Thing like this:
```python
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
client = AWSIoTMQTTClient('my_sensor')
# Connect the client to Greengrass Core 
# ... left out for clarity
# Build an update for the Shadow
message = {}
message["state"] = { "reported" : {"temperature" : 12. } } 
# Publish the update to the Shadow
client.publish('$aws/things/my_sensor/shadow/update', json.dumps(message))
```
The message goes to whichever MQTT server the client is connected to. Since we are connected to Greengrass Core and not AWS IoT, the message never reaches the cloud. So even though the topic is exactly the same as if we were updating the cloud based Shadow, the cloud based Shadow is not updated.<br>
As a matter of fact, the message also does not reach the local Shadow. At least not yet. Since we are working with local topics, we need to [set up subscriptions](greengrass.md#configure-subscriptions-in-greengrass) and deploy them to the Group before any messages are relayed.
<div align="center">
	<img width=500 src="images/greengrass_subscription_toshadow.png" alt="Greengrass ML Demo Architechture">
	<br>
    This is the overall architechture of the application we will build in this demonstration.
</div>

This is how it could look, but since there is a much easier way, this is not how we will do it.
## Republish to Shadow
We will build a Lambda function that will reside in the Greengrass Group. Its purpose is twofold: it will do a bit of transformation on the sensor readings and it will republish the readings as an update to the local Shadow.<br>
### Interact with the local Shadow service from a Lambda function
For a Greengrass MQTT client running in Lambda function that is deployed into a Greengrass Group, interacting with the local Shadow service is very straight forward. We connect and then perform the action we desire:
```python
import greengrasssdk
import json
# Hardcoding the thing name is not a good idea. We will look at an alternative
#  in a moment
THING_NAME = 'my_sensor'
# Define and connect the client
client = greengrasssdk.client('iot-data')
# Update the Shadow
update = {"state" : { "reported" : {"value" : 3 }}}
client.update_thing_shadow(thingName=THING_NAME, payload=json.dumps(message))
# Get the Shadow
shadow = client.get_thing_shadow(thingName=THING_NAME)
shadow = json.loads(shadow['payload']) # It takes a bit of unpacking...
# Delete the Shadow
client.delete_thing_shadow(thingName=THING_NAME)
```
There is no need to deal with callback functions - everthing is taken care of behind the scenes. Furthermore, there is no need to explicitly define the subscriptions in the Greengrass Group for these actions. As long as we use the Greengrass MQTT client, the messages find their way to the local Shadow service.<br>
We now know everything we need to have our Lambda function perform the transformations we need and update the Shadow. There is just one small aesthetic detail to attend to before we can start building.
### Setting environment variables for Lambda functions in Greengrass

Leave greengrass thing script as is. Modify lambda to update shadow instead of publishing to AWS IoT. Subscriptions.
# Setup Shadow Synchronisation
<div align="center">
	<img width=500 src="images/aws_shadow_local_sync.png" alt="Local to Cloud Shadow Sync">
	<br>
</div>

# ML at the Edge
## Set Up Device
[Tensorflow wheels](https://github.com/PINTO0309/Tensorflow-bin)
ML Resources
Inference lambda
Subscriptions
# In Production
?