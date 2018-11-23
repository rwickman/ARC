import os
import cv2
import time
import argparse
import multiprocessing
import numpy as np
import tensorflow as tf
import time

from multiprocessing import Queue, Pool
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

class ObjectClassifier:
    def __init__(self, model='coke2_model', predicted_class_threshold=0.90):

        #CWD_PATH = os.getcwd()
        
        # Path to frozen detection graph. This is the actual model that is used for the object detection.
        # The path to frozen_inference_graph.pb is:
        # ./desktop/object_detector_app/object_detection_ssd_mobilenet_v1_coco_11_06_2017/frozen_inference_graph.pb
        #MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
        self.MODEL_NAME = model

        # These paths should dynamic
        self.PATH_TO_CKPT = os.path.join('/home/pi/ARC/', self.MODEL_NAME, 'frozen_inference_graph.pb')
        
        # List of the strings that is used to add correct label for each box.
        # The path for the label map is:
        self.PATH_TO_LABELS = '/home/pi/ARC/coke_label_map.pbtxt'
        
        self.NUM_CLASSES = 1
        
        # Loading label map
        self.label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        self.categories = label_map_util.convert_label_map_to_categories(self.label_map, max_num_classes=self.NUM_CLASSES,
                                                                    use_display_name=True)
        self.category_index = label_map_util.create_category_index(self.categories)
        self.predicted_class_threshold = predicted_class_threshold # The threshold it has to exceed to be added to predicted classes
        self.sess = None
        self.detection_graph = None
        self.worker()
        self.detected_classes = []
        self.frame = None
        self.isNewFrame = False 
        self.on = True


    def run_threaded(self, frame):
        self.frame = frame
        self.isNewFrame = True
        return self.detected_classes

    def detect_objects(self,image_np):
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
    
        # Each box represents a part of the image where a particular object was detected.
        boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
    
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
    
        # Actual detection.
        (boxes, scores, classes, num_detections) = self.sess.run(
            [boxes, scores, classes, num_detections],
            feed_dict={image_tensor: image_np_expanded})
    
        # Visualization of the results of a detection.
        """
        vis_util.visualize_boxes_and_labels_on_image_array(
            image_np,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=8)
        """
        has_already_printed_sthg = False
    
        detected_classes = [] # Stores classes that exceed a particular threshold
        for index,value in enumerate(classes[0]):
            class_name = self.category_index[classes[0][0]]['name']
            if scores[0,index] > self.predicted_class_threshold:
                detected_classes.append(class_name)
        return detected_classes
    
    
    def worker(self):
        # Load a (frozen) Tensorflow model into memory.
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
    
            config = tf.ConfigProto()
            config.gpu_options.allow_growth = True
            self.sess = tf.Session(graph=self.detection_graph, config=config)
    
    
    
    def update(self):
        while self.on:
            time.sleep(0.01) # random delay that should in the future be based on the framerate
            if self.isNewFrame and self.frame is not None:
                print("About to try to detect image")
                frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                self.isNewFrame = False
                self.detected_classes = self.detect_objects(frame_rgb)
                if self.detected_classes:
                    print("DETECTED CLASSES: ", self.detected_classes)

