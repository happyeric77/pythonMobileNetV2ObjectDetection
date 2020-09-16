#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/home/pi/Projects/py/ML/tensorflow/models/research:/home/pi/Projects/py/ML/tensorflow/models/research/slim:/home/pi/Projects/py/ML/tensorflow/models:/home/pi/Projects/py/ML/tensorflow/models/research/object_detection
export LINE_NOTIFY_TOKEN=9H60VvGBBaptohQd9VgI2SboJseX5ygpg7PirQYvzON

/home/pi/Projects/pyenv/ML/bin/python $(pwd)/detectionAPPservice_v1.py