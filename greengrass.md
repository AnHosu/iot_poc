# Using Greengrass to Connect Things
It is time to create an edge, to take advantage of the compute that is available right where the data is gathered. Even if you use the AWS IoT services, there are several ways you could go about doing device management and creating an edge. The AWS offering is Greengrass, a piece of software running on your device and a accompanying cloud service, but you could also develop your own or use third-party software. In this demonstration we introduce key concepts in the context of the edge using Greengrass.<br>
In this demonstration we will
- Install AWS Greengrass on our Raspberry Pi
- Register the Pi as a Device in AWS Greengrass console
- Connect a our sensor as a Thing through Greengrass, sending data to AWS IoT
- Define a calculation in the cloud and deploy it onto the edge
# Motivation
When you walk through the demonstration 
