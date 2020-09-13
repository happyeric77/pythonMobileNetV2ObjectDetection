#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/home/pi/Projects/py/ML/tensorflow/models/research:/home/pi/Projects/py/ML/tensorflow/models/research/slim:/home/pi/Projects/py/ML/tensorflow/models:/home/pi/Projects/py/ML/tensorflow/models/research/object_detection
export LINE_NOTIFY_TOKEN=9H60VvGBBaptohQd9VgI2SboJseX5ygpg7PirQYvzON

cd /home/pi/Projects/py/ML/tensorflow/models

/home/pi/Projects/pyenv/ML/bin/python /home/pi/Projects/py/ML/tensorflow/models/detectionAPP_v0_noCAM.py