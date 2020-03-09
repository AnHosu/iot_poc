# AWS Shadow Service Demonstration
The AWS IoT thing shadow service offers a lot of functionality and the possible applications are numerous and diverse. You can read all about the functions and possible applications in the [documentation](https://docs.aws.amazon.com/iot/latest/developerguide/iot-device-shadows.html "AWS thing shadow docs"). In this case we will not exemplify all of the functionality, rather we will get started using shadows with an example that is as simple in functionality as possible. Once we are done with this case we will not have built all that is possible with shadows but we will have come far enough to start understanding advanced functions and applications work.<br>
We will try to do something like this
```
Prepare the sensor
Set up connection to AWS
while true
    get a sensor reading
    update the shadow
    confirm that the shadow was updated
```
We will then look at the shadow document using the AWS IoT test functionality.
# The Shadow Document
The shadow of a thing is a JSON document containing predetermined fields. An example of a shadow document could be
```json
{
    "state":{
      "reported":{
        "value": 27.87
      }
    },
    "metadata":{
      "reported":{
        "value":{
          "timestamp":1583755496
        }
      }
    },
    "version":4,
    "timestamp":1583755643
}
```
Let us walk through each of the fields one at a time.<br>
`state` holds the current values of the thing. The `reported` field should hold the current values as reported by the device itself. It can hold any number of reporting fields and a field can be an array.<br>
Besides `reported` the `state` field can also hold a `desired` field which can hold desired values as requested by an application or another device. This could be useful if you are doing a case with automation or maybe a home IoT project.<br>
This could be the state of a thing consisting of a valve and a flow meter where an application or maybe a user has just requested a new state:
```json
    "state":{
      "reported":{
        "flow": 15.04,
        "valve_state": "open"
      },
      "desired":{
          "flow": 0,
          "valve_state": "closed"
      }
    }
```
We will not use the desired field for this demonstration. We will just report the latest temperature
```json
    "state":{
      "reported":{
        "temperature": 21.6
      }
    }
```
The `metadata`field holds information on when each of the values in the `state` field were updated. The information is given as a UTC timestamp, representing when the value was last updated.<br>

You can read more about the shadow document in the [developer guide](https://docs.aws.amazon.com/iot/latest/developerguide/device-shadow-document.html "Shadow document developer guide")
# Topics and Policies for Shadows