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
This repo is an introduction to how you might go about getting your sensor data all the way from your sensor to AWS.<br>
AWS offers multiple ways to ingest and store data, but for sensor data it especially makes sense to look at the AWS IoT and streaming offerings. However, even here there are a lot of ways to go about doing the same thing and the nuances can get confusing. I did not find a great tutorial comparing different paths side by side, so I supposed that I would have to make it. Each path is presented as a case, where we will work from scratch to the full setup, not skipping any details. In this way, each case will be a full proof of concept for an AWS IoT setup. Each case is then followed by a discussion of its applications in real life settings and its limitations.<br>
**What if I just want the code to publish sensor data to IoT?** Well, then you should head straight for case 1: simple publishing.
# AWS IoT
* Things
* Shadows
* SDK
# The Hardware Setup
It would not be IoT without at least one IoT device. For this demonstration I have been using a Raspberry Pi 3 Model B+ along with a Bosch BME680 sensor on a [breakout](https://shop.pimoroni.com/products/bme680-breakout "Pimoroni BME680 breakout"). Any sensor would do, but I like this one and this particular breakout beacause it has a nice [library](https://github.com/pimoroni/bme680-python "Pimoroni BME680 library") which allows us to reduce the amount of code we need to query our sensor to a minimum. Furthermore, this particular sensor has four different components, allowing us to measure temperature, pressure, humidity, and, with a bit of additional work, air quality. I will not elaborate too much on this particular sensor equipment for this demonstration and I will try to be clear about when you can replace my code with that querying your particular sensor.<br><br>
We are going to do four different pipelines in total. Hardware-wise everything will be the same throughout the cases: BME680 connected to the Pi which in turn is connected to the internet via wifi. If you are using the same breakout, take a look at [this tutorial](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-bme680-breakout "BME680 tutorial") to set it up.
# Cases
## 1) Connecting a Thing to AWS IoT
The simplest way to do IoT with AWS. We will register our sensor as a thing in AWS IoT Core and will be using the AWS IoT Python SDK to publish sensor readings to a topic.<br>
In this case the Raspberry is simply simulating a microcontroller that will query the sensor and publish the result.
## 2) Using Thing Shadows
Using the Thing Shadow feature of AWS IoT to store a twin/shadow of the device in the cloud and update it whenever a new reading is available.
## 3) Publish and Subscribe
We are building a setup where our device will not just send data but also respond to messages sent to it.
## 4) Connecting Things through AWS Greengrass
Now our Pi will act the part of gateway device. The gateway device is where edge calculations will happen. This could be signal processing, edge analytics, or even machine learning models. Greengrass is the AWS offering for gateway devices.
## 5) Shadows, Greengrass, and ML Models
We will combine everything and finally deploy a machine learning model to our "edge".