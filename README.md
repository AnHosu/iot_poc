# iot_poc

# Introduction
This repo is an introduction to how you might go about getting your sensor data all the way from your sensor to AWS.<br>
AWS offers multiple ways to ingest and store data, but for sensor data it especially makes sense to look at the AWS IoT and streaming offerings. However, even here there are a lot of ways to go about doing the same thing and the nuances can get confusing. I did not find a great tutorial comparing different paths side by side, so I supposed that I would have to make it.<br>
## The Hardware Setup
It would not be IoT without at least one IoT device. For this demonstration I have been using a Raspberry Pi 3 Model B+ along with a Bosch BME680 sensor on a [breakout](https://shop.pimoroni.com/products/bme680-breakout "Pimoroni BME680 breakout"). Any sensor would do, but I like this one and this particular breakout beacause it has a nice [library](https://github.com/pimoroni/bme680-python "Pimoroni BME680 library") which allows us to reduce the amount of code we need to query our sensor to a minimum. Furthermore, this particular sensor has four different components, allowing us to measure temperature, pressure, humidity, and, with a bit of additional work, air quality. I will not elaborate too much on this particular sensor equipment for this demonstration and I will try to be clear about when you can replace my code with that querying your particular sensor.<br><br>
We are going to do four different pipelines in total. Hardware-wise everything will be the same throughout the cases: BME680 connected to the Pi which in turn is connected to the internet via wifi. If you are using the same breakout, take a look at ["this tutorial"](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-bme680-breakout "BME680 tutorial") to set it up.

## Case Setups
### 1) Connecting a Thing to AWS IoT
The simplest way to do IoT with AWS. We will register our sensor as a thing in AWS IoT Core and will be using the AWS IoT Python SDK to publish sensor readings to a topic.<br>
In this case the Raspberry is simply simulating a microcontroller that will query the sensor and publish the result.
### 2) Using Thing Shadows
Using the Thing Shadow feature of AWS IoT to store a twin/shadow of the device in the cloud and update it whenever a new reading is available.
### 3) Connecting Things through AWS Greengrass
Now our Pi will act the part of gateway device. The gateway device is where edge calculations will happen. This could be signal processing, edge analytics, or even machine learning models. Greengrass is the AWS offering for gateway devices.
### 4) Shadows, Greengrass, and ML Models
We will combine everything and finally deploy a machine learning model to our "edge".