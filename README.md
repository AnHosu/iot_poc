# Contents
* [Introduction](https://github.com/AnHosu/iot_poc#introduction)
* [Introduction to AWS IoT](https://github.com/AnHosu/iot_poc#aws-iot)
* [Hardware Setup](https://github.com/AnHosu/iot_poc#the-hardware-setup)
* [Cases](https://github.com/AnHosu/iot_poc#case-setups)
    * [Simple publishing](https://github.com/AnHosu/iot_poc#1-connecting-a-thing-to-aws-iot)
    * [Using thing shadows](https://github.com/AnHosu/iot_poc#2-using-thing-shadows)
    * [Publish and subscribe](https://github.com/AnHosu/iot_poc#3-publish-and-subscribe)
    * [Using Greengrass](https://github.com/AnHosu/iot_poc#4-connecting-things-through-aws-greengrass)
    * [Shadows, Greengrass, and ML models](https://github.com/AnHosu/iot_poc#5-connecting-things-through-aws-greengrass)

# Introduction
This repo is structured as an introduction to Industrial Internet of Things. On one hand it will be a simple introduction to how you might go about getting your sensor data from your sensor to the cloud. On the other hand, we will dive into advanced IoT concepts, so if you are looking for explanations to concepts like edge inference, fleet management, MQTT, and digital twins you have come to the right place.<br>
There are many ways to do IoT and there is an ocean of offerings out there. This introduction focuses on AWS IoT and uses the AWS IoT SDK for Python. The concepts are transferrable to other services, but we will write code specifically for AWS IoT and we will do so mostly in Python.<br>
AWS actually offers multiple ways to ingest and store data, but for industrial scale sensor data it especially makes sense to look at the AWS IoT and streaming offerings. However, even here there are different ways to go about doing the same thing and the nuances can get confusing. I did not find a great tutorial comparing different paths side by side, so I supposed that I would have to make it. Each path is presented as a case, where we will work from scratch to the full setup, not skipping any details. In this way, each case will be a full proof of concept for an AWS IoT setup. Each case is then followed by a discussion of its applications in real life settings and its limitations.<br>
**What if I just want the code to publish sensor data to IoT?** Well, then you should head straight for case 1: simple publishing.
# IoT with AWS IoT
I am going to do my best to explain core concepts of IoT. 
* Things
* Shadows
* Edge
* SDK
* MQTT
# The Hardware Setup
It would not be IoT without at least one IoT device. For this demonstration I have been using a Raspberry Pi 3 Model B+ along with a Bosch BME680 sensor on a [breakout](https://shop.pimoroni.com/products/bme680-breakout "Pimoroni BME680 breakout"). Any sensor would do, but I like this one and this particular breakout beacause it has a nice [library](https://github.com/pimoroni/bme680-python "Pimoroni BME680 library") which allows us to reduce the amount of code we need to query our sensor to a minimum. Furthermore, this particular sensor has four different components, allowing us to measure temperature, pressure, humidity, and, with a bit of additional work, air quality. I will not elaborate too much on this particular sensor equipment for this demonstration and I will try to be clear about when you can replace my code with that querying your particular sensor.<br>
In IoT terms the sensor is the 'thing' or 'device', and our Rasoberry Pi is the 'edge' or 'gateway device'. Names are not too important and, in real life, you would use different hardware for different situations.<br><br>
We are going to do four different cases in total. Hardware-wise everything will be the same throughout; BME680 connected to the Pi which in turn is connected to the internet. If you are using the same breakout, take a look at [this tutorial](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-bme680-breakout "BME680 tutorial") to set it up.
# Cases
## 1) Connecting a Thing to AWS IoT
The simplest way to do IoT with AWS. We will register our sensor as a thing in AWS IoT Core and will be using the AWS IoT Python SDK to publish sensor readings to a topic.<br>
In this case the Raspberry is simply simulating a microcontroller that will query the sensor and publish the result.<br><br>
[Get started here](https://github.com/AnHosu/iot_poc/blob/master/publishing.md "simple publishing case").
Here is the full [example script](https://github.com/AnHosu/iot_poc/blob/master/simple_publishing.py "simple publishing example").
## 2) Publish and Subscribe
In this case, we build upon the previous case and are constructing a setup where our device will not just send data but also respond to messages sent to it.<br>
The Raspberry Pi is still just simulating a microcontroller, but we start to see how compute at the edge is usefull and can be managed with AWS IoT.<br><br>
[Get started here](https://github.com/AnHosu/iot_poc/blob/master/pubsub.md "simple publishing case"). Here is the full [example script](https://github.com/AnHosu/iot_poc/blob/master/simple_pubsub.py "simple pubsub example").
## 3) Using Thing Shadows
Using the Thing Shadow feature of AWS IoT to store a twin/shadow of the device in the cloud and update it whenever a new reading is available.<br>
In this case the Raspberry is simply simulating a microcontroller that will query the sensor and publish the result.<br><br>
This case is still under construction.
## 4) Connecting Things through AWS Greengrass
Now our Pi will act the part of gateway device. The gateway device is where edge calculations will happen. This could be signal processing, edge analytics, or even machine learning models. Greengrass is the AWS offering for gateway devices.<br><br>
This case is still under construction, but here is the [example script](https://github.com/AnHosu/iot_poc/blob/master/greengrass_thing.py "simple greengrass example") so far.
## 5) Shadows, Greengrass, and ML Models
We will combine everything and finally deploy a machine learning model to our "edge".<br><br>
This case is still under construction.