import os
import cv2
import time
import argparse
import multiprocessing
import numpy as np
import tensorflow as tf

from multiprocessing import Queue, Pool
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

class Classifier:
    def __init__(self, model='soda_modelv5', predicted_class_threshold=0.6):

        CWD_PATH = os.getcwd()
        
        # Path to frozen detection graph. This is the actual model that is used for the object detection.
        # The path to frozen_inference_graph.pb is:
        # ./desktop/object_detector_app/object_detection_ssd_mobilenet_v1_coco_11_06_2017/frozen_inference_graph.pb
        #MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
        self.MODEL_NAME = model
        self.PATH_TO_CKPT = os.path.join(CWD_PATH, 'object_detection', self.MODEL_NAME, 'frozen_inference_graph.pb')
        
        # List of the strings that is used to add correct label for each box.
        # The path for the label map is:
        self.PATH_TO_LABELS = os.path.join(CWD_PATH, 'object_detection', 'data', 'soda_label_map.pbtxt')
        
        self.NUM_CLASSES = 4
        
        # Loading label map
        self.label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        self.categories = label_map_util.convert_label_map_to_categories(self.label_map, max_num_classes=self.NUM_CLASSES,
                                                                    use_display_name=True)
        
        self.category_index = label_map_util.create_category_index(self.categories)
        self.predicted_class_threshold = predicted_class_threshold # The threshold it has to exceed to be added to predicted classes
        self.sess = None
        self.detection_graph = None
        self.worker()


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
        vis_util.visualize_boxes_and_labels_on_image_array(
            image_np,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=8)
        
        has_already_printed_sthg = False
    
        detected_classes = [] # Stores classes that exceed a particular threshould
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
    
    
    
    def predict(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return detect_objects(frame_rgb, self.sess, self.detection_graph)

'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-src', '--source', dest='video_source', type=int,
                        default=0, help='Device index of the camera.')
    parser.add_argument('-wd', '--width', dest='width', type=int,
                        default=1000, help='Width of the frames in the video stream.')
    parser.add_argument('-ht', '--height', dest='height', type=int,
                        default=500, help='Height of the frames in the videostream.')
    parser.add_argument('-num-w', '--num-workers', dest='num_workers', type=int,
                        default=2, help='Number of workers.')
    parser.add_argument('-q-size', '--queue-size', dest='queue_size', type=int,
                        default=5, help='Size of the queue.')
    args = parser.parse_args()
    """
    parser.add_argument('-wd', '--width', dest='width', type=int,
                        default=480, help='Width of the frames in the video stream.')
    parser.add_argument('-ht', '--height', dest='height', type=int,
                        default=360, help='Height of the frames in the video stream.')
    """

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(multiprocessing.SUBDEBUG)

    #input_q = Queue(maxsize=args.queue_size)
   # output_q = Queue(maxsize=args.queue_size)
    
    #pool = Pool(args.num_workers, worker, (input_q, output_q))

    #video_capture = WebcamVideoStream(src=args.video_source,
    #                                  width=args.width,
    #                                  height=args.height).start()
    # fps = FPS().start()

    while True:  # fps._numFrames < 120
        frame = video_capture.read()
        input_q.put(frame)

        t = time.time()

        output_rgb = cv2.cvtColor(output_q.get(), cv2.COLOR_RGB2BGR)
        cv2.imshow('Video', output_rgb)
        fps.update()

        print('[INFO] elapsed time: {:.2f}'.format(time.time() - t))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    fps.stop()
    print('[INFO] elapsed time (total): {:.2f}'.format(fps.elapsed()))
    print('[INFO] approx. FPS: {:.2f}'.format(fps.fps()))

    pool.terminate()
    #video_capture.stop()
    cv2.destroyAllWindows()'''

