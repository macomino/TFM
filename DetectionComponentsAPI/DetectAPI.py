from wsgiref.simple_server import make_server
import matplotlib
import tensorflow as tf
import cv2
import numpy as np
import os
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# Path to frozen detection graph .pb file, which contains the model that is used
# for object detection.
PATH_TO_CKPT = '../../notebooktest/output/frozen_inference_graph.pb'

# Path to label map file
PATH_TO_LABELS = os.path.join('../DatasetCreator/out','label_map.pbtxt')

# Path to image
PATH_TO_IMAGE = '../../diagram127.jpg'


# Number of classes the object detector can identify
NUM_CLASSES = 13

def init():

    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)

def diagramDetection(environ, start_response):



    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'Hello, world!']

if __name__ == '__main__':
    try:
        init()
        httpd = make_server('', 5050, diagramDetection)
        print('Serving on port 5050...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')
