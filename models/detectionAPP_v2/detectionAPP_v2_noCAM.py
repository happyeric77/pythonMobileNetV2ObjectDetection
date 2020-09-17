import cv2
import numpy as np
import tensorflow as tf
import os, re
import datetime
import requests
from itertools import groupby
import cloudinary
from cloudinary import uploader
import subprocess as sp

class DetetionAPP:
    def __init__(self, model_dir):
        self.model_dir = model_dir
        CWD_PATH = model_dir
        print(os.getcwd())

        # Import utilites
        from utils import label_map_util
        from utils import visualization_utils as vis_util
        self.vis_util = vis_util

        # Name of the directory containing the object detection module we're using
        MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'

        # Path to frozen detection graph .pb file, which contains the model that is used
        # for object detection.
        PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

        # Path to label map file
        PATH_TO_LABELS = os.path.join(CWD_PATH,'research/object_detection/data','mscoco_label_map.pbtxt')

        # Number of classes the object detector can identify
        NUM_CLASSES = 90

        ## Load the label map.
        # Label maps map indices to category names, so that when the convolution
        # network predicts `5`, we know that this corresponds to `airplane`.
        # Here we use internal utility functions, but anything that returns a
        # dictionary mapping integers to appropriate string labels would be fine
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

        # Load the Tensorflow model into memory.
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.compat.v2.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            self.sess = tf.compat.v1.Session(graph=detection_graph)

        # Define input and output tensors (i.e. data) for the object detection classifier

        # Input tensor is the image
        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

        # Output tensors are the detection boxes, scores, and classes
        # Each box represents a part of the image where a particular object was detected
        self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

        # Each score represents level of confidence for each of the objects.
        # The score is shown on the result image, together with the class label.
        self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

        # Number of objects detected
        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        # Initialize frame rate calculation
        self.frame_rate_calc = 1
        self.freq = cv2.getTickFrequency()
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.cam_status = False
        self.camera = cv2.VideoCapture(0)
        self.humanExist = False
    
    def camera_stop(self):
        if self.cam_status == True and self.camera:
            camera.release()
            self.cam_status = False
            self.camera = None
            return 'Camera terminated'
        else: 
            return 'Camera is already "OFF", extra action no needed'

    def camera_cap(self, img_width=640, img_height=480):
    # Set up camera constants
    
        img_width = img_width
        img_height = img_height
        self.cam_status = True
        
        while True:

            t1 = cv2.getTickCount()

            # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
            # i.e. a single-column array, where each item in the column has the pixel RGB value
            ret, frame = self.camera.read()
            frame = cv2.resize(frame, (img_width, img_height))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_expanded = np.expand_dims(frame_rgb, axis=0)

            # Perform the actual detection by running the model with the image as input
            (boxes, scores, classes, num) = self.sess.run(
                [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
                feed_dict={self.image_tensor: frame_expanded})
                
            # Check how many object is detected
            nowTxt = datetime.datetime.now().strftime('%m-%d-%H%M%S')
            allBoxes = groupby([np.sum(i) for i in boxes[0] ], lambda x: x>0)
            boxCount = 0
            for (key, value) in allBoxes:
                if key == True:
                        boxCount = len(list(value))
                # print(key, list(value))
            print('detected object: ',  boxCount)

            acc_thres = 0.5
            # list the class name of detected project

            obj_list = []
            for i in range(boxCount):
                objectName = self.category_index[classes[0][i]]['name']
                if scores[0][i] > acc_thres:
                    print('high confidency level obj:', objectName, scores[0][i])
                    obj_list.append(objectName)
                else:
                    print('low confidency level obj:', objectName)
            
            print('*'*50)

            # Draw the results of the detection (aka 'visulaize the results')
            self.vis_util.visualize_boxes_and_labels_on_image_array(
                frame,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                self.category_index,
                use_normalized_coordinates=True,
                line_thickness=8,
                min_score_thresh=acc_thres)
                
            # Human Detection (& save img)
            if ('person' in obj_list) and (self.humanExist == False):
                self.humanExist = True
                imgPath = '{}/img/human_detected_{}.jpeg'.format(os.path.dirname(self.model_dir), nowTxt)

                cv2.imwrite(imgPath, frame)
                print(frame)

                # Send img out using LINE NOTIFY
                message = 'Somebody shows up here'
                token = os.environ['LINE_NOTIFY_TOKEN']
                def lineNotifyPicMessage(token, msg, pic):
                    headers = { "Authorization": "Bearer " + token}
                    payload = { 'message': msg }
                    files = {'imageFile': open(pic, 'rb')}
                    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload, files = files)
                    return r
                picURI = imgPath
                r = lineNotifyPicMessage(token, message, picURI)
            
            if ('person' not in obj_list) and (self.humanExist == True):
                self.humanExist = False
                print('person left')

            cv2.putText(frame,"FPS: {0:.2f}".format(self.frame_rate_calc),(30,50),self.font,1,(255,255,0),2,cv2.LINE_AA)

            # All the results have been drawn on the frame, so it's time to display it.
            # cv2.imshow('Object detector', frame)

            t2 = cv2.getTickCount()
            time1 = (t2-t1)/self.freq
            self.frame_rate_calc = 1/time1

            # Press 'q' to quit
            if cv2.waitKey(1) == ord('q'):
                break

            yield frame

        self.camera.release()
        self.cam_status = False
        # cv2.destroyAllWindows()
