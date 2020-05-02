import greengrasssdk
import logging

client = greengrasssdk.client('airq-core')

REPUB_TOPIC = 'republish/temperature'

def get_topic(context):
    try:
        topic = context.client_context.custom['subject']
    except Exception as e:
        logging.error('Unable to read a topic. ' + repr(e))
    return topic

def function_handler(event, context):
    try:
        input_topic = get_input_topic(context)
        input_message = get_input_message(event)
        logging.info(event)
    except Exception as e:
        logging.error(e)
    client.publish(topic=REPUB_TOPIC, payload=event)
    return