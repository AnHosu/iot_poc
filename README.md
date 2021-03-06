# Industrial IoT with AWS and Python
This repo is structured as an introduction to Industrial Internet of Things (iIoT). On one hand, it will be a simple introduction to how we might go about getting our sensor data from sensors to the cloud. On the other hand, we will dive into advanced IoT concepts. So if you are looking for demonstrations of concepts like edge inference, device fleet management, MQTT, and shadow records you have come to the right place.<br>
There are many ways to do IoT and there is an ocean of offerings out there. This introduction focuses on AWS IoT services like IoT Core and Greengrass and uses the AWS IoT SDK for Python. The concepts are transferrable to other services, but we will write code specifically for AWS IoT and we will do so mostly in Python.<br>
AWS offers multiple ways to ingest and store data but, for industrial scale sensor data, it especially makes sense to look at the AWS IoT and streaming offerings. However, even here there are different ways to go about doing the same thing and the nuances can get confusing. This tutorial consists of a general introduction and five seperate demonstrations designed to exemplify increasingly complex IoT functionality. In each demonstration, We will work from scratch to the full setup, making it a full proof of concept for an AWS IoT architecture. I recommend starting at case 1 and working your way through each case before proceeding to the next. A full disclaimer before you get started though; the tutorial does reflect some subjective opinions and I am by no means an expert on the subject, but the tutorial arises from my work with IoT in a manufacturing setting.<br>
## Contents
* [Hardware Setup](README.md#the-hardware-setup)
* [Cases](README.md#case-setups)
    * [Simple Publishing](README.md#1-publish-industrial-data-with-aws-iot)
    * [Publish and Subscribe](README.md#2-publish-and-subscribe)
    * [Utilise Thing Shadows](README.md#3-utilise-thing-shadows)
    * [Build an Edge with Greengrass](README.md#4-build-an-edge-with-greengrass)
    * [Advanced Features and ML in Greengrass](README.md#5-advanced-greengrass-features)
* [Introduction to AWS IoT](README.md#iot-with-aws-iot)
# The Hardware Setup
It would not be IoT without at least one device. The demonstrations focus on the software layer but use actual hardware, not simulations, to prove concepts. I have been using a Raspberry Pi 3 Model B+ along with a Bosch BME680 sensor on a [breakout](https://shop.pimoroni.com/products/bme680-breakout "Pimoroni BME680 breakout"). Any sensor would do, but I like this one and this particular breakout beacause it has a nice [library](https://github.com/pimoroni/bme680-python "Pimoroni BME680 library") which allows us to reduce the amount of code we need to query our sensor to a minimum. Furthermore, this particular sensor has four different components, allowing us to measure temperature, atmospheric pressure, relative humidity, and, with a bit of additional work, air quality. I will not elaborate too much on this particular sensor equipment for this demonstration and I will try to be clear about when you can replace my example code with code querying your particular sensor.<br>
In IoT terms the sensor is the 'Thing' or 'Device', and our Raspberry Pi is the 'Edge' or 'Gateway Device'. Names are not too important and, in real life, you would use different hardware for different situations.
<div align="center">
	<img width=500 src="images/hardware_setup.jpg" alt="iot setup">
	<br>
    Raspberry Pi 3 Model B+ with the BME680 sensor. The sensor is intentionally placed quite close to the CPU, which will interfere with the temperature readings. In demonstration 4, we will deploy calculations from AWS onto the Pi to correct for this, as an example of edge calculations.
    <br>
    <br>
</div>

Hardware-wise everything will be the same throughout each demonstration; BME680 connected to the Pi which is connected to the internet. If you are using the same breakout, take a look at [this tutorial](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-bme680-breakout "BME680 tutorial") to set it up.
# Demonstrations
The five demonstrations are the main attraction of this tutorial, and if you are looking for examples and code snippets, then go ahead and dive right in. If you prefer a bit of theoretical background before you get started, then jump to the next section before starting the cases.
## 1) Publish Industrial Data with AWS IoT
The simplest way to do IoT with AWS. We will register our sensor as a thing in AWS IoT Core and will be using the AWS IoT Python SDK to publish sensor readings to a topic. We go through concepts such as things, topics, MQTT, and more.<br>
In this case, the Raspberry Pi is simply simulating a microcontroller that will query the sensor and publish the result.<br><br>
[Get started here](publishing.md "simple publishing case").
Here is the full [example script](example_scripts/simple_publishing.py "simple publishing example").
<div align="center">
	<img width="500" src="images/publishing_architecture.png" alt="IoT overview">
  <br>
  Schematic of the architecture we are building in the demonstration of publishing.
</div>

## 2) Publish and Subscribe
In this case, we build upon the previous case and will construct a setup where our device will not just send data but also respond to messages sent to it.<br>
The Raspberry Pi is still just simulating a microcontroller, but we start to see how having compute at the edge is useful and can be managed with AWS IoT.<br><br>
[Get started here](pubsub.md "simple pub/sub case"). Here is the full [example script](example_scripts/simple_pubsub.py "simple pubsub example").
<div align="center">
	<img width="500" src="images/pubsub_architecture.png" alt="pubsub overview">
  <br>
  Schematic of the architecture we are building in the demonstration of publishing and subscribing.
</div>

## 3) Utilise Thing Shadows
Using the Thing Shadow feature of AWS IoT, we will create a twin/shadow of our device in the cloud and update it whenever a new reading is available. We could use this cool feature to build a digital twin of our process.<br>
The Raspberry Pi is still simulating a microcontroller that will query the sensor, but instead of just publishing the result, it will update the Shadow document of the thing, our sensor.<br><br>
[Get started here](shadow.md "Shadow case"). Here is the full [example script](example_scripts/shadow.py "shadow example").
<div align="center">
	<img width=500 src="images/shadow_architecture.png" alt="iot setup">
	<br>
  Schematic of the architecture we are building in the demonstration of Shadow functionality.
</div>

## 4) Build an Edge with Greengrass
Now our Pi will act the part of gateway device. The gateway device effectively represents an edge that is manageable from the cloud and where data transformations or calculations can happen. This could be signal processing, edge analytics, or even machine learning models. Greengrass is the AWS software offering for gateway devices. In this demonstration, we will set up Greengrass on the Pi, connect a thing, our sensor, to Greengrass, and deploy a calculation from the cloud to the edge using a Lambda function.<br><br>
[Get started here](greengrass.md "Greengrass case"). Here is the full [example script for a local device](example_scripts/greengrass_thing.py "Example of Thing for Greengrass") and the [Lambda function](example_scripts/greengrass_sys_lambda.py "Lambda example") we will deploy into Greengrass Core.
<div align="center">
	<img width=500 src="images/greengrass_group_architecture.png" alt="iot setup">
    <br>
    This is the architecture we are building in the demonstration of Greengrass functionality.
	<br>
</div>

## 5) Advanced Greengrass Features
In this final demonstration, we will combine everything from the previous demonstrations to deploy a machine learning model from the cloud into Greengrass and do inference at the edge. This requires us to explore additional advanced features and configurations of Greengrass, but shows how, with a few means and a bit of engineering, we can achieve quite complex functionality.<br><br>
[Get started here](greengrass_ml.md "Advanced Greengrass case"). This demonstration uses the same [example script for a local device](example_scripts/greengrass_thing.py "Example of Thing for Greengrass") as the previous but has two new examples of Lambda functions, [including one](example_scripts/ml_inference_lambda.py "ML inference Lambda") doing machine learning inference.
<div align="center">
	<img width=500 src="images/greengrass_ml_architecture.png" alt="Greengrass ML Demo Architechture">
	<br>
    This is the architechture of the application we will build in the demonstration of advanced Greengrass Features.
</div>

# IoT with AWS IoT
This section has a bit of theoretical context for the demonstrations. We will try to understand some core concepts of internet of things in the context of an industrial setting and AWS IoT. 
## Things
Let us start with the Things in an internet of things. In an industrial setting, a thing is often anything that has a measurable state, is being actively measured, and is connected to a network. A simple example might be temperature at the factory floor. This is obviously a critical variable in many manufacturing processes and one can often find old school thermometers installed here and there. These are not things, however, until they are connected to a network either directly or indirectly through a gateway device. Other examples could be the airflow through a specific nozzle or the injection pressure for the plastic in an injection moulding process. The airflow could be measured using a flowmeter and the injection pressure with a pressure sensor. These could then be connected to a small computer that in turn connects to the internet.<br>
Given this vague definition of things, an obvious question arises for those who have been in a manufacturing context for a while. Manufacturing processes are usually associated with process control loops. These include connecting key process parameters to a process logic controller (PLC) that in turn controls actuators to regulate the process. An example would be the flow of water through a pipe, measured by a flow sensor and regulated by the opening or closing of a valve. The question is: are these control loops also IoT? The answer is that they could be. The process parameters and the state of the valve are all potential things that when connected to a network could become things in an internet of things. The key difference between IoT and a control loop would be all the other things and applications that might be on the network. The PLC is there to do process control, not neccessarily to send or store data, and connecting it to new networks could be a major risk for the manufacturing process, but also potentially unlocks the data for new valuable applications. In IoT, we use dedicated devices to buffer and send data to storage in the cloud or somewhere else.<br>
One network that an IoT could take advantage of is a cloud. Cloud service providers like AWS and Azure have IoT-specific offerings that can help build new IoTs. AWS is our cloud of choice for this tutorial. In AWS IoT Core, we can [register](https://docs.aws.amazon.com/iot/latest/developerguide/create-aws-thing.html "how to register a thing in AWS IoT Core") and manage our things. A thing is the highest level of granularity, and it makes sense to register each parameter we measure as a seperate thing. We can then aggregate and manage hierarchies of things using [groups and types](https://docs.aws.amazon.com/iot/latest/developerguide/iot-thing-management.html "about managing hierarchies of things").
<div align="center">
	<img width=500 src="images/iot_overview.png" alt="iot setup">
	<br>
</div>

## The Edge and Gateway Devices
We stumbled up the term gateway devices a few times. A gateway device is basically just a computer. It could be as small as a microcontroller and as large as a distributed compute system. In this tutorial we will use a Raspberry Pi to play the part of gateway device. In an industrial setting the gateway devices are there to do the things that a PLC should not do, like connecting to the internet, doing heavy calculations, and buffering data. It might be obvious at this point, but the gateway device is essentially what is referred to as the 'edge'. Running machine learning at the edge essentially means having a machine learning algorithm do inference using the compute in our gateway device. A gateway device can be used for a bunch of other things though, such as signal processesing, data aggregation, or data transformation. Imagine for instance that our sensor reports the factory floor temperature in degrees Celcius. Maybe we want to convert that into Kelvins before sending and storing it in the cloud. Of course we could store the measurement in Celcius and then do the transformation later or directly in our application, but that would be more expensive (cloud compute is expensive, cloud storage is cheap) and less elegant. We run our computations at the edge whenever it makes sense and save money.<br>
The edge device is where we will run the client that connects to AWS IoT, sends data, and maybe receives instructions. To do so we will use the AWS IoT Python SDK. AWS also provides software for managing and running our applications on gateway devices. These are called Greengrass and SiteWise (which is just additional software on top of Greengrass). Greengrass allows us to do cool things such as running Lambda functions and deploy machine learning models from the cloud to the edge. Greengrass and its functionality is covered in demonstrations 4 and 5.<br> 
## Shadows
We are doing IoT for a reason. Maybe we are building a dashboard for the operators of our manufacturing line, maybe we are developing a predictive maintenance model that uses measured parameters from the line to predict the remaining lifespan of a critical component. Whatever our application, we will need fresh data from our things. Unless we have gone all in on a massive synchronisation effort, our data points will not arrive at exactly matching timestamps, however. Factory floor humidity might be reported every 5 minutes while frequency and amplitude of a vibrating element might be reported every 15 seconds. Maybe the gateway device handling data from our flow sensors has been updating its software such that no values have been reported for the past 12 minutes. What does our application do when the refresh rate might be every 30 seconds? If all values are stored in a database, the application could just grab the latest values, but that might not be possible or introduce unwanted latency. There is another way, however.<br>
A Shadow record is a record of the latest process parameters, such that the currently most reliable view of reality is always available for applications. The notion is similar to a database, the key difference being that this record only ever keeps the latest entry. With such a record we can design our application to do what it needs to do and even dynamically correct for old data without ever worrying about not having available data or waiting for data to appear, thus effectively decoupling the IoT and our application.<br>
Shadow records are a part of the AWS IoT offering. Each thing registered in AWS IoT automatically has a shadow, which is a json document containing the latest record for that thing, assuming we have set up our IoT to update it. In demonstration 3, we will explore how to interact with shadows in the cloud. Using Greengrass, we can also keep a shadow on the edge and even enable shadow synchronisation between the edge and the cloud. In this way our applications running at the edge can access shadow records with low latency, while cloud based applications have a copy available to them as well. We will explore the use of local shadows with Greengrass for a machine learning application in demonstration 5.
<div align="center">
	<img width="500" src="images/shadow_flow.png" alt="iot setup">
	<br>
</div>

## SDK
We will be using the Python SDK to configure the client that communicates with AWS. This means that our gateway device has to be able to run Python. This is no problem on a Raspberry Pi, but would not work for a microcontroller and probably would not be ideal for a web application. AWS IoT offers SDKs for a bunch of [other languages](https://docs.aws.amazon.com/iot/latest/developerguide/iot-sdks.html "AWS IoT SDKs), however.<br>
This tutorial uses the [first version](https://github.com/aws/aws-iot-device-sdk-python "AWS IoT Python SDK V1") of the Python SDK. A [version two](https://github.com/aws/aws-iot-device-sdk-python-v2 "AWS IoT Python SDK V2") that uses a very different syntax was released, but will not be covered here.<br>
## The MQTT Protocol
Communication with AWS is facilitated by the MQTT protocol. This is a protocol commonly used in manufacturing systems, and is documented [online](http://mqtt.org/documentation "MQTT documentation"). The [AWS flavour](https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html "AWS MQTT Documentation") of MQTT is a slightly simpler implementation of the protocol. Communicating using HTTPS is also possible but is not covered in this tutorial.<br>
To get started using the MQTT protocol with AWS IoT, we only need to know a few concepts: message, topic, quality of service (QoS), publishing, and subsribing. These concepts are summarised right here, but we will discuss them in detail when they show up in the demonstrations.
### Messages
At the core of MQTT is the message, The message contains the actual data along with any metadata. It is structured as a json and we can put whatever we want in there, but we will want the reading from our thing, a timestamp for the time of sampling, and maybe an idication whether the reading was succesful or not. 
### Topics
Messages in AWS are distributed and filtered using topics. Topics are a kind of tag that we can use to identify the source of the message and distribute it accordingly. It is just a single string, generally in the format
```
main_tag/secondary_tag/tertiary_tag/etc
```
For instance, if we had several factories each with several manufacturing lines with several stations each eqipped with sensors, we might do something like
```
factoryA/line22/drying/temperature
```
and then have another sensor on the same line publish to
```
factoryA/line22/milling/torque
```
That way we can direct these messages to the store or dashboard for the same line but seperate Lambda functions, if that is needed for our application.<br>
The topic system is quite flexible and we will have to rely on our own rigid naming conventions if we want to effectivly utilise topics in an application with many things. Some specific topics are reserved for specific purposes such as interacting with shadows. We will dive deeper into the use of topics and reserved topics in the demonstrations.
### Publishing and Subscribing
Messages are transmitted using the publish subscribe model. A message always has a single publisher. The publisher client is the origin of the message and will publish that message to a given topic. A topic can have several publishes, meaning that several clients can publish messages to the same topic. Messages reach their destination through subscribers. Subscribers are clients that listen to a topic to get whatever messages are published there. A topic can also have multiple subscribers.
### Server/Broker
The MQTT server is responsible for orchestrating the MQTT communication. It is the server that will authenticate MQTT clients and will route messages from publishers to subscribers using topic filters. AWS IoT Cores is essentially an infinitely scalable MQTT server. Greengrass is also an MQTT server that runs locally on a gateway device.
### Client
The MQTT client is used to create an MQTT publisher or a subscriber. The core functionality of the AWS IoT SDKs is to abstract away the intricacies of setting up and authenticating an MQTT client.
### Quality of Service
Quality of Service, abbreviated QoS, is a flag specifying what happens when messages get lost in the network. The AWS flavour of MQTT accepts two QoS flags. The flag 0 means that the message is delivered to subsrcibers 'at most once'. The flag 1 means that the message is delivered to subsribers 'at least once'. So for QoS=0 the publisher will send the message once and then forget about it. If it does not get delivered, it is lost. For QoS=1, however, the message is sent, and the publisher then waits for a reply from the subscriber before forgetting the message, and resends if neccessary. This ensures that the subscriber gets the message at least once.