# Machine Learning at the Edge with Greengrass
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

Before jumping into the demonstration, 
# Publish to Local
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