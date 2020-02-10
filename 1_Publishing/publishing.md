# Publishing to AWS
In this tutorial we will obtain a value from a sensor and publish it to a topic on AWS. No added shenanigans; this is as simple as it gets.

## Registering the Sensor in IoT Core

## Setting up the SDK

## Scripting
It is finally time to code. Let us review what we are trying to do.
At the core of it we want to grab a reading from the sensor, wrap it in a message with some useful metadata, and publish that to AWS IoT. We will want to do that continuosly on a loop, meaning that our script should end up being structured as follows.<br>
```
Prepare the sensor
Set up connection to AWS
while true
    get a sensor reading
    pack it up
    publish it
```
I will not elaborate on the sensort setup here, but if you are interested in the BME680 sensor, I will happily do a seperate tutorial. For now, let us focus on the connection and publishing parts.<br>
