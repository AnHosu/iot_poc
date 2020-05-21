"""
Created on Sat May 21 16:07:00 2020

@author: AnHosu

This is a simple example of a lambda function to be deployed
 to Greengrass core. It accompanies the demonstration at:
 https://github.com/AnHosu/iot_poc/blob/master/greengrass_ml.md
The lambda function republishes values 
"""
import greengrasssdk
import logging
import json

REPUB_TOPIC = 'republish/reading'

client = greengrasssdk.client('iot-data')

def get_topic(context):
    try:
        topic = context.client_context.custom['subject']
    except Exception as e:
        logging.error('Unable to read a topic. ' + repr(e))
    return topic

def function_handler(event, context):
    try:
        input_topic = get_topic(context)
        message = event
        message['input_topic'] = input_topic
        logging.info(event)
    except Exception as e:
        logging.error(e)
    client.publish(topic=REPUB_TOPIC, payload=json.dumps(message))
    return