# Advanced Features of Greengrass
We are about to build something really cool. Machine learning inference managed from the cloud but performed at the edge might sound like a sequence of flimsy business colloquialisms and to some extent they might be. In this demonstration, however, we will dive into the actual technical substance behind these terms.<br>
Specifically, we will apply advanced features of AWS Greengrass, including
- Creating and interaction with local shadow
- Shadow synchronisation with the cloud
- Decoupling data generation and application with a Shadow
- Long-running Lambda functions
- Machine learning resources
- Machine learning inference with a Tensorflow2 model

The target of the demonstration is to build a small IoT application that predicts whether it is raining or not, given the current temperature, relative humidity, and pressure. The weather data comes from our BME680 air quality sensor, and our Raspberry Pi 3B+ will play the role of gateway device.<br>
We will be utilising expertise from the previous demonstrations of [publishing](publishing.md), [subscribing](pubsub.md), [Shadows](shadow.md), and [general Greengrass features](greengrass.md).<br>
# Set Up
To build the target demonstration, we will walk through three parts. First we will set up a local Shadow within our Greengrass group and use obtained sensor values to contiuously update the Shadow. Then we will enable synchronisation between the local Shadow and a cloud copy of the Shadow. Last, but not least, we will set up inference with a Tensorflow2 machine learning model.<br>
<div align="center">
	<img width=500 src="images/greengrass_ml_architecture.jpg" alt="Greengrass ML Demo Architechture">
	<br>
</div>

Installing and setting up Greengrass Group with a device was covered in the [general introduction to Greengrass](greengrass.md#install-and-configure-greengrass), and we will work from this starting point but without any subscriptions or lambdas set up.
# Publish to Local Shadow 
In this section we will set up a local Shadow and build a Lambda function that takes values published by our sensor and updates the Shadow.<br>
## Prepare the Thing
We already have a [script](greengrass_thing.md) that connects or Thing, the sensor, and publishes readings to our Greengrass Group on a local topic. There is no need to modify it in any way, we will just leave it running, continuously publishing values to a local topic. I want with the topic `bme680/readings` but anything goes.<br>
## The Local Shadow Service
Any Thing we include in our Greengrass Group lives only inside the Group and only connects to the cloud when first discovering the Group. This is great for reducing the number of devices connected to the cloud, but it also means that we cannot directly take advantage of the Shadow that is in the cloud.<br>
Fortunately, Greengrass provides a Local Shadow Service inside Greengrass that we can use instead. The local Shadow service works in a very similar way to the Shadow in the cloud. The Shadow document follows the same schema, it is interacted with using the exact same topics, and it can be get, updated, and deleted. The Shadow lives inside the Greengrass Group and is only accessible to entities connected to the group.<br>
For instance, assume we have a Thing called `myDevice` and an MQTT client that is connected to our Greengrass Core

```python
message = {}
message["state"] = { "reported" : {"temperature" : 12. } } 
# Client is connected to Greengrass Core
AWSIoTMQTTClient.publish('$aws/things/myDevice/shadow/update/accepted', json.dumps(message))
```
The message goes to whichever MQTT server the client is 
## Republish to Shadow
Environment variables

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