"""
Created on Sat May 22 19:16:00 2020

@author: AnHosu

This is a simple example of a ML inference lambda to be deployed
 to Greengrass core. It accompanies the demonstration at:
 https://github.com/AnHosu/iot_poc/blob/master/greengrass_ml.md
The lambda function should be longlived and allowed access to the
 SavedModel resources.
"""
import greengrasssdk
import tensorflow as tf
import json
import time
import logging
import os

THING_NAME = os.environ["THING_NAME"]
STANDARDISER_PATH = "/ggml/tensorflow/standardiser"
MODEL_PATH = "/ggml/tensorflow/rain_predictor"
CLASSIFICATION_THRESHOLD = 0.5

# Load the model that standardises readings
loaded_standardiser = tf.saved_model.load(STANDARDISER_PATH)
inference_standardiser = loaded_standardiser.signatures["serving_default"]

# Load the model that predicts rain
loaded_predictor = tf.saved_model.load(MODEL_PATH)
inference_predictor = loaded_predictor.signatures["serving_default"]

client = greengrasssdk.client('iot-data')

def parse_shadow(thing_shadow):
    try:
        reported = thing_shadow["state"]["reported"]
        readings = [reported["pressure"],
                    reported["temperature"],
                    reported["humidity"]]
    except Exception as e:
        logging.error("Failed to parse thing_shadow: " + repr(e))
    return [readings] # Note predictor expects shape (observations X num_features)

shadow_update = {}
while True:
    try:
        # Get readings from local Shadow
        thing_shadow = client.get_thing_shadow(thingName=THING_NAME)
        # Put readings in a list in the right order
        readings = parse_shadow(thing_shadow=json.loads(thing_shadow["payload"]))
        # Standardise readings to create model features
        feature_tensor = inference_standardiser(tf.constant(readings))['x_prime']
        logging.info(feature_tensor)
        # Perform prediction
        raw_prediction = inference_predictor(feature_tensor)['y'].numpy()
        # Evaluate prediction
        prediction = (raw_prediction >= CLASSIFICATION_THRESHOLD).astype(int).tolist()[0][0]
        shadow_update["state"] = {"reported" : { "rain_prediction" : prediction } }
    except Exception as e:
        logging.error("Failed to do prediction: " + repr(e))
        
    client.update_thing_shadow(thingName=THING_NAME, payload=json.dumps(shadow_update))
    time.sleep(10) # Repeat every 10s

# The function handler here will not be called. Our Lambda function
#  should be long running and stay in the infinite loop above.
def function_handler(event, context):
    pass