"""
Created on Sat May 21 16:07:00 2020

@author: AnHosu

This is a simple example of a lambda function to be deployed
 to Greengrass core. It accompanies the demonstration at:
 https://github.com/AnHosu/iot_poc/blob/master/greengrass_ml.md
The lambda function republishes values to the local Shadow service.
"""
import greengrasssdk
import logging
import json
import time
import os

THING_NAME = os.environ["THING_NAME"]

client = greengrasssdk.client('iot-data')

def get_cpu_temperature():
    '''
    Gets the CPU temperature of a Raspberry Pi in deg. C
    '''
    try:
        f = open("/sys/class/thermal/thermal_zone0/temp")
        raw_temp = f.read()
        f.close()
        cpu_temp = float(raw_temp)/1000.0
    except Exception as e:
        logging.error('Unable to obtain CPU temperature. ' + repr(e))
    return cpu_temp

def get_topic(context):
    try:
        topic = context.client_context.custom['subject']
    except Exception as e:
        logging.error('Unable to read a topic. ' + repr(e))
    return topic
    
def get_temperature(event):
    try:
        temperature = float(event["temperature"])
    except Exception as e:
        logging.error('Unable to parse message body. ' + repr(e))
    return temperature

def function_handler(event, context):
    try:
        input_temperature = get_temperature(event)
        cpu_temps = []
        for _ in range(8):
            cpu_temps.append(get_cpu_temperature())
            time.sleep(1)
        avg_cpu_temp = sum(cpu_temps)/float(len(cpu_temps))
        # Compensated temperature
        comp_temp = 2*input_temperature - avg_cpu_temp
        message = {}
        message["state"] = { "reported" : {"temperature" : comp_temp,
                                            "pressure" : event["pressure"],
                                            "humidity" : event["humidity"],
                                            "message" : event["message"]}}
        logging.info(event)
        logging.info(message)
    except Exception as e:
        logging.error(e)
    client.update_thing_shadow(thingName=THING_NAME, payload=json.dumps(message))
    return