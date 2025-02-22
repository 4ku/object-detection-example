import argparse
import numpy as np
import cv2

from models import MODELS

parser = argparse.ArgumentParser(description='Object detection using Tensoflow API.')
parser.add_argument('--path', nargs='?', default='input/mall.mp4', help="Path to input video file or put 0 if you want to use camera")
parser.add_argument('--model', nargs='?', default='EfficientDet D1 640x640', help="Model name. List of all available models you can find in models.py.")
args = parser.parse_args()
args.path = int(args.path) if args.path.isdigit() else args.path

import tensorflow as tf
import tensorflow_hub as hub
tf.get_logger().setLevel('ERROR')

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils

PATH_TO_LABELS = './models/research/object_detection/data/mscoco_label_map.pbtxt'
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

hub_model = hub.load(MODELS[args.model])
hub_model = tf.function(hub_model)


video_capture = cv2.VideoCapture(args.path)
out = cv2.VideoWriter('output/output.avi',cv2.VideoWriter_fourcc(*"MJPG"), 15, (800,600))

while True:
    re,frame = video_capture.read()
    frame = np.expand_dims(cv2.resize(frame, (800,600)), axis=0)
    results = hub_model(frame)
    result = {key:value.numpy() for key,value in results.items()}

    #Get only person class
    idx = result['detection_classes'][0] == 1
    boxes = result['detection_boxes'][0][idx]
    classes = result['detection_classes'][0][idx]
    scores = result['detection_scores'][0][idx]

    label_id_offset = 0

    viz_utils.visualize_boxes_and_labels_on_image_array(
          frame[0],
          boxes,
          (classes + label_id_offset).astype(int),
          scores,
          category_index,
          use_normalized_coordinates=True,
          max_boxes_to_draw=100,
          min_score_thresh=.40,
          agnostic_mode=False)

    out.write(frame[0])
    cv2.imshow('Person detection', frame[0])
    if cv2.waitKey(1) & 0xFF == 27:
        break

video_capture.release()
out.release()
cv2.destroyAllWindows()
