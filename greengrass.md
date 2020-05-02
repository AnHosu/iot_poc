# Using Greengrass to Connect Things
It is time to create an edge, to take advantage of the compute that is available right where the data is gathered. Even if you use the AWS IoT services, there are several ways and plenty of 3<sup>rd</sup> party software you could apply for device management and creating an edge. The AWS offering is Greengrass, a piece of software running on your device and an accompanying cloud service. In this demonstration, we introduce key concepts in the context of an IoT edge using Greengrass.<br>
In this demonstration we will
- Install AWS Greengrass Core on our Raspberry Pi
- Register the Pi as a Core Device in the AWS Greengrass console
- Connect a our sensor as a Thing through Greengrass, sending data to AWS IoT
- Define a calculation in the cloud and deploy it onto the edge
# Motivation
When you walk through the demonstration it might seem like a lot of hassle and extra steps to go through before data is flowing and we reach what is essentially the same state as in previous demonstrations, where we just [published](publishing.md) readings and [subscribed](pubsub.md) directly in the script that also queried our sensor. Indeed, Greengrass is not intended for use with a single sensor. Imagine, however, that you are managing hundreds of sensors on a factory floor. The factory might be far away, or the gowning procedure might prohibit frequent visits, but even if your desk is right next to the manufacturing line, you still do not want to physically go there each time you deploy changes to sensor data streams, restart devices, define new signal processing, or update software. Greengrass allows you to define functionality in the cloud and deploy it to your device with a click.<br>
Another important aspect of your IoT application to consider is cost. It is tempting to just send all raw data to storage in the cloud. Cloud storage is indeed inexpensive, but it is not free. What is worse, however, is the cost of compute. Cloud compute offers unprecedented flexibility, but it is expensive, so we generally want to use it to handle loads with varying intensity or low predictability, e.g. for hosting the application that uses data from the IoT setup. As an example of a case where you might quickly incur a large and unnecessary bill, imagine a set of vibration sensors. Vibration sensors are useful for predictive maintenance applications, since the patterns in vibrations from components like bearings and motors might be good predictors for the health of the component. An industrial grade vibration sensor might be able to sample acceleration thousands of times per second. If we were to store the data from just a few vibration sensors, we would quickly fill up enough storage to accomodate years worth of data from other sources like factory floor temperature and humidity. Furthermore, since it is not the accelleration itself but characteristics of the vibrations we are interested in, each time we use the data we would have to do signal processing and recalculate features. If we do that using cloud compute, we will work up quite a bill. The financially and environmentally responsible way to implement vibration sensors is to do the signal processing as close to the sampling point as possible and then only store the calculated features. We still want the flexibility of developing in the cloud and deploying to a remote device, however. While we will not work with signal processing in this demonstration, we will create an example of data transformation and deploy it from the cloud to the Raspberry Pi using Greengrass.<br>
Conceptually, the setup for this demonstration is a bit different from that of the three previous demonstrations. The hardware is exactly the same but, in previous demonstrations, our Raspberry Pi acted the part of a microcontroller and essentially did not do a lot of work. In this demonstration, we will make use of the compute available on the Raspberry Pi, install Greengrass, and use it to manage the sensor. To demonstrate the concept of edge calculations, we will create a transformation that corrects for the fact that the temperature sensor is right next the CPU of our PI.
<div align="center">
	<img width=500 src="images/hardware_setup.jpg" alt="iot setup">
	<br>
</div>

Notice that the BME680 air quality sensor is right next to the CPU of the Pi. The edge calculation we make will attempt to correct the temperature reading from the BME680 by substracting an amount based on the current CPU temperature.
# Installing and Configuring Greengrass
The AWS Greengrass service consists of two main elements. Greengrass Core is a piece of software that is installed on your gateway device, in our case, the Raspberry Pi. The software is configured to communicate with Greengrass in the IoT console, which constitutes the other element.<br>
The process of installing Greengrass depends a lot on your device and its operating system, but the docs contain a [general guide](https://docs.aws.amazon.com/greengrass/latest/developerguide/module2.html "install Greengrass"). I used apt to install Greengrass on the Pi. When following this guide, you will
- [Register the Greengrass Core](https://docs.aws.amazon.com/greengrass/latest/developerguide/gg-config.html) in AWS IoT. Remember to download the package with certificates onto your device
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
If it is not already available on your device, you might want to install the Java 8 runtime
```bash
sudo apt install openjdk-8-jdk
```
For this demonstration we will use Python 3.7 for the functions we deploy into Greengrass Core. Therefore we also need to make sure that Python 3.7 is available to Greengrass core on the device.<br>
When all is set up and configured, you can start Greengrass by running
```bash
cd /greengrass/ggc/core/
sudo ./greengrassd start
```
Greengrass Core will need to be running on your device in order to establish a connection between Core and the cloud. You can walk through the [AWS hello world cases](https://docs.aws.amazon.com/greengrass/latest/developerguide/module3-I.html) to familiarise yourself with Greengrass. We are going to do many of the same things in this demonstration but in a slightly different order and using our hardware setup instead of simulated devices.
# Build a Greengrass Group
During the setup, we created a Greengrass Group. The Group will eventually consist of one core device (in our case the Pi) and all the things (e.g. our sensors) associated with the core. Right now our group only consists of the Core device. We need to associate our thing, the sensor, with the core. To do so, we follow the [guidelines](https://docs.aws.amazon.com/greengrass/latest/developerguide/device-group.html "register a thing in Greengrass"), and go to AWS IoT > Greengrass > Groups, choose the group we just created, go to Devices, and click "Add Device". The creation procedure is similar to the procedure for any other Thing registered in AWS IoT. Indeed, after registering the device, you will be able to find it under the AWS IoT > Manage tab. The key difference here is that the device is associated with the core device.<br>

<div align="center">
	<img width=500 src="images/greengrass_group.png" alt="iot setup">
	<br>
</div>

We will now proceed to setup up a script that connects to Greengrass Core and publishes readings from the sensor to a topic. The messages will never reach the cloud, however. Instead, the messages are published into the core device on a topic that only lives within the the Greengrass group. The logic is something along the lines of
```
setup sensor
connect to Greengrass core
while true
	get sensor values
	publish to local topic
```
You might notice that this logic is very similar to what we did in the case of simple [publishing](publishing.md), and indeed the two cases are very similar. The main difference is that we will set up and configure a client that connects to Greengrass Core rather than IoT Core. <br>
## Connecting a Device to Greengrass Core
We use the same MQTT client as always and, as usual, we will need a variety of resources to establish the right connection.
```python
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureCredentials(groupCA, privateKeyPath, certificatePath)
myAWSIoTMQTTClient.configureEndpoint(coreHost, corePort)
```
Let us discuss each of these resources in turn.
- ClientId could be anything allowed by the policy you created for your thing in the previous step. To keep down complexity, using the device ID is a prudent idea.
- privateKeyPath is the complete path to the key associated with the certificate created earlier for your thing.
- certificatePath is the complete path to the certificate for your thing that you created earlier.
- groupCA is the certificate authority for your Greengrass group and is used to authenticate that your thing is indeed connected to the intended Greengrass core when sending and receiving messages. In a moment we will walk through how to obtain this certificate. Note that this is *not* the root certificate authority used when communicating with AWS IoT Core.
- coreHost is the server running the Greengrass Core, i.e. your core device
- corePort is the port on which your thing will communicate with the core using the MQTT protocol. The default setting for when generating a new Greengrass Core is 8883, but you can [configure](https://docs.aws.amazon.com/greengrass/latest/developerguide/gg-core.html) this

The three first elements are realtively straight forward; you know these from when you created the thing and its certificate in the first place. The three remaining resources, however, require a bit of additional work. The group certificate is managed by AWS and by default it is rotated every 7 days. This requires a little bit of effort on our part when connecting things to the core, but is worth it for the free added security. Since the the Greengrass Core is connected to AWS, AWS also knows the host and port, and so while we are querying AWS for the group certificate, we can also retrieve these two pieces of information. This process of retrieving connection information is called core discovery and is the only time our thing will connect to AWS. Once connected to the core, all communication will be with it.<br>
To set up the discovery process, we need a special dicovery client that is also included in the AWS IoT SDK
```python
from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider

discoveryInfoProvider = DiscoveryInfoProvider()
discoveryInfoProvider.configureEndpoint(host)
discoveryInfoProvider.configureCredentials(rootCAPath, certificatePath, privateKeyPath)
discoveryInfoProvider.configureTimeout(10)
```
The discovery client is set up using the usual materials; the AWS IoT custom endpoint for your account, the AWS root certificate authority, the private key, and certificate for your thing. We also tell the client to wait a maximum of 10 seconds before timing out a connection attempt.<br>
The client can be used to send a discovery request to AWS and fetch connection information for the core. It works like this:
```python
# Returns list of AWSIoTPythonSDK.core.greengrass.discovery.models.DiscoveryInfo objects
discoveryInfo = discoveryInfoProvider.discover(thingName)
```
We provide the thing name of the thing for which we are looking up connection information. In most of your applications this is probably the same as your client name, but in this case it *has* to be the name of your thing as registered in AWS.<br>
If the request is successful, `discoveryInfo` will hold information about Greengrass groups that the device belongs to (a device can belong to several groups, but each group has exactly one core). Of interest to us are the certification authorities and the connection information, the lists of which can be accessed as such:
```python
# Returns list of AWSIoTPythonSDK.core.greengrass.discovery.models.CoreConnectivtyInfo objects
caList = discoveryInfo.getAllCas()
# Returns list of tuples (CA content, group ID)
coreList = discoveryInfo.getAllCores()
```
These are lists with each entry representing a core. If your device only belongs to a single Greengrass core, this list will only have one entry. We can get the certificate authority for the first available core like this
```python
groupId, ca = caList[0]
```
Each core might have several connection options so we might like to keep them in a list to loop over later
```python
coreInfo = coreList[0]
# Get a list of tuples (host, port)
coreConnectivityInfoList = coreInfo.connectivityInfoList
``` 
Now we have everything we need to have out thing automatically discover and connect to the Greengrass core:
```python
from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider
from AWSIoTPythonSDK.core.protocol.connection.cores import ProgressiveBackOffCore
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
# Configure client for gg core discovery
discoveryInfoProvider = DiscoveryInfoProvider()
discoveryInfoProvider.configureEndpoint(host)
discoveryInfoProvider.configureCredentials(rootCAPath, certificatePath, privateKeyPath)
discoveryInfoProvider.configureTimeout(10)
# Discover gg cores for the thing
discoveryInfo = discoveryInfoProvider.discover(thingName)
# Get connection info
caList = discoveryInfo.getAllCas()
coreList = discoveryInfo.getAllCores()
# Get info for the first core
groupId, ca = caList[0]
coreInfo = coreList[0]
coreConnectivityInfoList = coreInfo.connectivityInfoList
# Loop over and try connection with each set of host name and port
for connectionInfo in coreConnectivityInfoList:
	coreHost = connectionInfo.host
    corePort = connectionInfo.port
    myAWSIoTMQTTClient.configureEndpoint(coreHost, corePort)
    try:
        myAWSIoTMQTTClient.connect()
        break
    except BaseException as e:
        pass
```
This is the most condensed code needed to implement discovery, but in production you will want to add much more logging, error handling, retries for discoveries, and other frills. See the section below on Greengrass in production for a further discussion on how to improve the thing script for a real world scenario.
## Publishing and Subscribing in the Greengrass Group
Now that our thing is connected to the core in its Greengrass group we can start publishing data to a local topic. From the point of view of our thing, this works just like publishing to a topic on AWS IoT. Using the client we configured:
```python
myAWSIoTMQTTClient.publish(topic, messageJson, 1)
```
With this, we have everything needed to run our thing running. The [example script](greengrass_thing.py "example script") for this section summarises everything we have done so far but contains a bit more detail. It is based off of the [example](https://github.com/aws/aws-iot-device-sdk-python/blob/master/samples/greengrass/basicDiscovery.py "AWS IoT SDK basic discovery example") included with the AWS IoT SDK and was adapted to be used with our hardware setup. Note that the functionality in this script is running on the same Pi as the Greengrass software. In a real production setting, however, the two are likely to be seperate physical devices.<br>
Even assuming that the Greengrass core is running and the thing script is publishing values, not much is happening yet. If you go to the AWS IoT test test client in the console and subscribe to the topic that the thing is publishing to, there should be no values flowing in, as nothing is being sent there. In order for us to see data flowing into the cloud, we have to grab the data in Greengrass Core and pass it on to a new topic that is published to the cloud.<br>
The way this is done with Greengrass is by defining a Lambda function in AWS and deploying onto the core.
## Writing and Deploying Lambda Functions

## Calculations on the Edge
# Putting it Together
```bash
python3 greengrass_thing.py -e <AWS IoT custom endpoint> -r <root CA> -c <thing certificate> -k <private key> -id <client ID> -t <local topic>
```

# In Production
## Default vs Custom Core Config
Note that in the demonstration we just went for the default options when setting up the Greengrass core. This creates a new ploicy for the certificate attached to the core. The policy is extremely permissive and, while it works great for demonstration purposes, it might not be what we want in a production setting.<br>
The great thing about Greengrass is that we can define aggregations and handle the diversity of incoming data at the edge and then only publish to a set of neatly organised topics to the cloud.
## Handle certificate authority rotation
### Persisting connection information
## Make Greengrass Core run on boot
## Connection retries and progressive backoff logic
Imagine the following situation. You have a couple of hundred sensors that connect to one or a few Greengrass core devices, and all run off of the same power supply. At one point, the power supply is switched off, maybe it is maintenance maybe it is an error, but after a while power returns and your sensors and their controllers reboot. You set up the controllers such that they will automatically try to reconnect with the core. This is fine, but suddenly the core is getting hundreds of connection requests within a few seconds, so the controllers are receiving errors. Now, obviously there is nothing wrong with the core devices; they are just getting too many requests, so we will want the controllers to retry the connection before giving up. However, we do not want to have them all retry at the same time lest we repeat the story again. That is why we implement progressive backoff logic.<br>
...