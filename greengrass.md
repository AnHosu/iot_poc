# Using Greengrass to Connect Things
It is time to create an edge, to take advantage of the compute that is available right where the data is gathered. Even if you use the AWS IoT services, there are several ways you could go about doing device management and creating an edge. The AWS offering is Greengrass, a piece of software running on your device and a accompanying cloud service, but you could also develop your own or use third-party software. In this demonstration we introduce key concepts in the context of the edge using Greengrass.<br>
In this demonstration we will
- Install AWS Greengrass Core on our Raspberry Pi
- Register the Pi as a Device in AWS Greengrass console
- Connect a our sensor as a Thing through Greengrass, sending data to AWS IoT
- Define a calculation in the cloud and deploy it onto the edge
# Motivation
When you walk through the demonstration it might seem like a lot of hassle and extra steps to go through before data is flowing and we reach what is essentially the same state as in previous demonstrations, where we just published readings directly. Indeed, Greengrass is not intended for use with a single sensor. Imagine, however, that you are managing hundreds of sensors on a factory floor. The factory might be far away, or the gowning procedure might prohibit frequent visits, but even if your desk is right next to the manufacturing line, you still do not want to physically go there each time you deploy changes to sensor data streams, restart devices, or update software. Greengrass allows you to define functionality in the cloud and deploy it to your device with a click.<br>
Another important aspect of your IoT application to consider is cost. It is tempting to just send all raw data to storage in the cloud. Cloud storage is indeed inexpensive, but it is not free. What is worse, however, is the cost of compute. Cloud compute offers unprecedented flexibility, but it is expensive, so we generally want to use it to handle loads with varying intensity or low predictability, e.g. for hosting the application that uses data from the IoT setup. As an example of a case where you might quickly incur a large and unnecessary bill, imagine a set of vibration sensors. Vibration sensors are useful for predictive maintenance applications, since the patterns in vibrations from components like bearings and motors might be good predictors for the health of the component. An industrial vibration sensor might be able to sample acceleration thousands of times per second. If we were to store the data from just a few vibration sensors, we would quickly fill up enough storage to accomodate years worth of data from other sources like factory floor temperature and humidity. Furthermore, since it is not the accelleration itself but characteristics of the vibrations we are interested in, each time we use the data we would have to do signal processing and recalculate features. If we do that using cloud compute, we will work up quite a bill. The financially and environmentally responsible way to implement vibration sensors is to do the signal processing as close to the sampling point as possible and then only store the calculated features. We still want the flexibility of developing in the cloud and deploying to a remote device, however. While we will not work with signal processing in this demonstration, we will create an example of data transformation and deploy it from the cloud to the Raspberry Pi using Greengrass.<br>
Conceptually, the setup for this demonstration is a bit different from that of the three previous demonstrations. The hardware is exactly the same, however. The difference is that, in previous demonstrations, our Raspberry Pi acted the part of a microcontroller and essentially did not do a lot of work. In this demonstration, we will make use of the compute available on the Raspberry Pi, install Greengrass, and use it to manage the sensor. To demonstrate the concept of edge calculations, we will create a transformation that corrects for the fact that the temperature sensor is right next the CPU of our PI.
<div align="center">
	<img width=500 src="images/hardware_setup.jpg" alt="iot setup">
	<br>
</div>

Notice that the BME680 is right next to the CPU. The edge calculation we make will attempt to correct the temperature reading from the BME680 by substracting an amount based on the current CPU temperature.
# Installing and Configuring Greengrass
The AWS Greengrass service consists of two main elements. Greengrass Core is a piece of software that is installed on your gateway device, in our case, the Raspberry Pi. The software is configured to communicate with Greengrass in the IoT console, which constitutes the other element.<br>
The process of installing Greengrass depends a lot on your device and its operating system, but the docs contain a [general guide](https://docs.aws.amazon.com/greengrass/latest/developerguide/module2.html "install Greengrass"). I used apt to install Greengrass on the Pi. When following this guide, you will
- [Register the Greengrass Core](https://docs.aws.amazon.com/greengrass/latest/developerguide/gg-config.html) in AWS IoT. Remember to download the package with security resources onto your device
- [Download](https://docs.aws.amazon.com/greengrass/latest/developerguide/what-is-gg.html#gg-core-download-tab "ggc software") the packaged software for your specific device and operating system
- Set up the user group (ggc_group) and user (ggc_user) that Greengrass Core will assume on your device
- [Unpack software](https://docs.aws.amazon.com/greengrass/latest/developerguide/gg-device-start.html) and install certificates
- Download and install the root CA certificate
Once you have done all these steps, you might want to check that you have all the dependencies you need by running the Greengrass dependency checker:
```bash
mkdir greengrass-dependency-checker-GGCv1.10.x
cd greengrass-dependency-checker-GGCv1.10.x
wget https://github.com/aws-samples/aws-greengrass-samples/raw/master/greengrass-dependency-checker-GGCv1.10.x.zip
unzip greengrass-dependency-checker-GGCv1.10.x.zip
cd greengrass-dependency-checker-GGCv1.10.x
sudo ./check_ggc_dependencies | more
```
You might want to install the Java 8 runtime
```bash
sudo apt install openjdk-8-jdk
```
For this demonstration we will use Python 3.5 for the functions we deploy into Greengrass Core. Therefore we also need to make sure that the appropriate Python runtime is available to Greengrass core.