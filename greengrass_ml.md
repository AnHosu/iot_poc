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
	<img width=500 src="images/greengrass_ml_architecture.png" alt="Greengrass ML Demo Architechture">
	<br>
    This is the overall architechture of the application we will build in this demonstration.
</div>

Let us get started!
# Publish to Local Shadow 
In this section, we will set up a local Shadow and build a Lambda function that takes values published by our sensor and updates the Shadow.<br>
<div align="center">
	<img width=500 src="images/greengrass_ml_architecture_repub.png" alt="Greengrass ML Demo Architechture">
	<br>
    This is the part of the architecture we will build in this section.
</div>

## Prepare the Thing
We [register and add](greengrass.md#associate-a-thing-with-a-greengrass-group) our Thing, the sensor, to our Greengrass group.<br>
We already have a [script](greengrass_thing.md) that connects our Thing and publishes readings to our Greengrass Group on a local topic. There is no need to modify it in any way. We will just leave it running, continuously publishing values to a local topic. I went with the topic `bme680/readings` but any topic goes.
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
	<img width=500 src="images/greengrass_subscription_toshadow.png" alt="Subscription with local Shadow">
	<br>
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
There is no need to deal with callback functions - everthing is taken care of behind the scenes. Furthermore, there is no need to explicitly define the subscriptions in the Greengrass Group for these actions. As long as we use the Greengrass MQTT client, the messages find their way to the local Shadow service, which is just a set of hidden Lambda functions.<br>
We now know everything we need to have our Lambda function perform the transformations we need and update the Shadow. There is just one small aesthetic detail to attend to before we can start building.
### Setting environment variables for Lambda functions in Greengrass
In the snippet above, we hard coded the device ID, the Thing name. This will work just fine, but it does make the Lambda function difficult to reuse. We do, however, have a better option. We can provide Lambda functions running in a Greengrass Group with environment variables. Environment values are key-value pairs that are specified outside the running script but can be accessed at runtime. If you are already familiar with environment variables for Lambdas running in the cloud, they work in a very similar fashion, but are specified in a different place when used with Greengrass. Let us take it step by step.<br>
First we will need to decide on a key-value structure. We will go with the key being `THING_NAME` and the value being the ID of our device.<br>
Then we need to write our Lambda function to take advantage of the environment variable. This is fairly straight forward, in Python:
```python
import os
THING_NAME = os.environ('THING_NAME')
```
The last step we need is to actually provide the environment variable to the instance of our Lambda function in the Greengrass Group. We do this by locating our Greengrass Group in the console and configure the lambda in question

<div align="center">
	<img width=500 src="images/greengrass_lambda_configure.png" alt="Configure Greengrass Lambda">
	<br>
	Note that the name of your Greengrass Group and Lambdas may be different
</div>

At the bottom of the configuration options, we find a set of fields where we can provide key value pairs, and we just go ahead and provide ours:
<div align="center">
	<img width=500 src="images/greengrass_lambda_environment_variable.png" alt="Environment variable">
	<br>
</div>

Now, when we deploy the Lambda function, the environment variable will be available for use. This means that if we have multiple sensors we we can use the same Lambda Alias to create multiple Lambda functions deployed to the Greengrass Group serving their exact device. Less code and less work for us.
### Build the republishing Lambda function
To summarise, these are the steps we take to build the Lambda function that recieves readings from our Thing, treats them, and publishes an update to the local Shadow.<br>
- We create a Lambda function with, using the full [example](greengrass_repub_lambda.py)
- We create a Lambda alias
- In the Greengrass Group, we create a Lambda function refferring to the alias
- We configure the Lambda function
  - The timeout should be at least 10 seconds
  - Access to `/sys` should be enabled
  - We should provide the environment variable `THING_NAME`
## Subscriptions
We only need one subsription, one going from our device to the Lambda we just created
<div align="center">
	<img width=500 src="images/greengrass_subscription_repub_shadow.png" alt="Repub to Shadow subscription">
	<br>
</div>

That is it for the first part. Once we deploy, We have a Thing publishing sensor readings, they are treated and used to update the local Shadow. Right now there is not much to see though, as we have done nothing to make use of or even visualise the local Shadow. We will get there soon though.
# Setup Shadow Synchronisation
In this section, we will set up Shadow synchronisation between the local Shadow and the Shadow of our device in the cloud.
<div align="center">
	<img width=500 src="images/greengrass_ml_architecture_sync.png" alt="Greengrass ML Demo Architechture">
	<br>
    This is the part of the architecture we will build in this section.
</div>

Synchronising the Shadow just means that the local Shadow service will send regular updates to the cloud based Shadow such that the status quo is reflected there as well. We would usually do this to support an application running in the cloud, but in this case we are doing it mostly for show.<br>
It is important to note that the synchronisation works both ways. Updates that are done to the local Shadow will eventually be reflected in the cloud based Shadow and vice versa. We will not have anything directly updating the cloud Shadow in this case, however.<br>
Setting up synchronisation is actually fairly straight forward. We navigate to our Greengrass group and find the Device page. Next to the Device we added earlier it should be saing 'Local Shadow Only'. All we have to do is to expand the options for that Device by clicking the three dots and selecting Enable Shadow Synchronisation:
<div align="center">
	<img width=500 src="images/aws_shadow_local_sync.png" alt="Local to Cloud Shadow Sync">
	<br>
</div>

Now we deploy the change.<br>
We can test whether it works by navigating to the page of the particular Device and going to its Shadow tab. If everything we did in the previous section works and the Shadow synchronisation works, we should see that the Shadow gets updated.
<div align="center">
	<img width=500 src="images/.png" alt="Shadow sync working">
	<br>
</div>

# ML at the Edge
In this section, we will deploy a machine learning model into the Greengrass group and have it do inference based on the data coming from our Device.
<div align="center">
	<img width=500 src="images/greengrass_ml_architecture_inference.png" alt="Greengrass ML Demo Architechture">
	<br>
    This is the part of the architecture we will build in this section.
</div>

Specifically, we are going to create a Lambda function that loads a machine learning pipeline consisting of a model that transforms the data into features that are then evaluted in a neural network based model. The data we will get from the local Shadow such that the inference does not rely on live data

## Why is this a difficult thing?

## Set Up Gateway Device
### Installing Tensorflow
[Tensorflow wheels](https://github.com/PINTO0309/Tensorflow-bin)

## Manage Machine Learning Resources
### SavedModel
### S3 Bucket
### Machine Learning Resource in Greengrass
## Inference Lambda
### Long-running Lambdas
### Load Model

# In Production
?