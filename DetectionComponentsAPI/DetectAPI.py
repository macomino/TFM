from wsgiref.simple_server import make_server
import matplotlib
import tensorflow as tf
import cv2
import numpy as np
import os
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
import base64
import json


# Path to frozen detection graph .pb file, which contains the model that is used
# for object detection.
PATH_TO_CKPT = './frozen_inference_graph.pb'

# Path to label map file
PATH_TO_LABELS = './label_map.pbtxt'

# Number of classes the object detector can identify
NUM_CLASSES = 13

def processImage():

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

    # Input tensor is the image
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Output tensors are the detection boxes, scores, and classes
    # Each box represents a part of the image where a particular object was detected
    detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represents level of confidence for each of the objects.
    # The score is shown on the result image, together with the class label.
    detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
    detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

    # Number of objects detected
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    #image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    image = cv2.imread('tmp')
    image_expanded = np.expand_dims(image, axis=0)

    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: image_expanded})

    vis_util.visualize_boxes_and_labels_on_image_array(
        image,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=8,
        min_score_thresh=0.50)

    return cv2.imencode('.jpg', image)[1]


def diagramDetection(environ, start_response):

    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)

    with open("tmp", "wb") as fh:
        fh.write(base64.decodebytes(request_body))

    #bytesIn = base64.b64decode(request_body)
    #nparr = np.fromstring(bytesIn, np.uint8)
    #img = np.expand_dims(nparr, axis=0)
    #img = cv2.imdecode(nparr, cv2.COLOR_BGR2GRAY)

    img_bytes = processImage()
    #byte_string = img_bytes.encode('utf-8')
    image_processed =  base64.b64encode(img_bytes).decode("utf-8")

    #start_response('200 OK', [('Content-Type', 'image/jpeg;base64'), ('Access-Control-Allow-Origin','*')])
    #return [image_processed]

    start_response('200 OK', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin','*')])
    return [bytes('{"image":"'+str(image_processed)+'"}', 'utf8')]

if __name__ == '__main__':
    try:
        httpd = make_server('', 5050, diagramDetection)
        print('Serving on port 5050...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')
