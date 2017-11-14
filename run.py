#IMPORTS------------------------------------------#
import sys
import getopt
import os
import numpy as np
import six.moves.urllib as urllib
import sys
import tarfile
import cv2
import tensorflow as tf
import zipfile

from collections import defaultdict
from io import StringIO
#from matplotlib import pyplot as plt
from PIL import Image

from utils import label_map_util
from utils import visualization_utils as vis_util

#CONST--------------------------------------------#
PATH_TO_CKPT = ''
PATH_TO_IMAGES = ''
PATH_TO_LABELS = ''
PATH_TO_OUTDIR = './'
NUM_CLASSES = 9
MIN_CONV = 0.5	

#MAIN---------------------------------------------#
def main(argv=None):
	PATH_TO_CKPT = ''
	PATH_TO_IMAGES = ''
	PATH_TO_LABELS = ''
	PATH_TO_OUTDIR = './'
	NUM_CLASSES = 9
	MIN_CONV = 0.5

	try:
		opts, args = getopt.getopt(argv[1:], 'hm:i:l:o:c:m:', ['help', 'model=', 'images=', 'labels=', 'outdir=', 'classes=', 'min='])
	except getopt.GetoptError:
		print argv[0] + ' --model= --images= --labels= --outdir= --classes= --min='
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print argv[0] + ' --model= --images= --labels='
			sys.exit()
		elif opt in ("-m", "--model"):
			PATH_TO_CKPT = arg
		elif opt in ("-i", "--images"):
			PATH_TO_IMAGES = arg
		elif opt in ("-l", "--labels"):
			PATH_TO_LABELS = arg
		elif opt in ("-l", "--outdir"):
			PATH_TO_OUTDIR = arg
		elif opt in ("-c", "--classes"):
			NUM_CLASSES = int(arg)
		elif opt in ("-m", "--min"):
			MIN_CONV = float(arg)

	detection_graph = tf.Graph()
	with detection_graph.as_default():
		od_graph_def = tf.GraphDef()
		with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
			serialized_graph = fid.read()
			od_graph_def.ParseFromString(serialized_graph)
			tf.import_graph_def(od_graph_def, name='')

	label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
	categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
	category_index = label_map_util.create_category_index(categories)

	def load_image_into_numpy_array(image):
		(im_width, im_height) = image.size
		rgb = Image.merge("RGB", [image, image, image])
		return np.array(rgb.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

	with detection_graph.as_default():
		with tf.Session(graph=detection_graph) as sess:
			# Definite input and output Tensors for detection_graph
			image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
			# Each box represents a part of the image where a particular object was detected.
			detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
			# Each score represent how level of confidence for each of the objects.
			# Score is shown on the result image, together with the class label.
			detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
			detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
			num_detections = detection_graph.get_tensor_by_name('num_detections:0')
			image_pathes = [f for f in os.listdir(PATH_TO_IMAGES) if os.path.isfile(os.path.join(PATH_TO_IMAGES, f))]
			for image_name in image_pathes:
				image = Image.open(os.path.join(PATH_TO_IMAGES, image_name))
				# the array based representation of the image will be used later in order to prepare the
				# result image with boxes and labels on it.
				image_np = load_image_into_numpy_array(image)
				# Expand dimensions since the model expects images to have shape: [1, None, None, 3]
				image_np_expanded = np.expand_dims(image_np, axis=0)
				# Actual detection.
				(boxes, scores, classes, num) = sess.run(
					[detection_boxes, detection_scores, detection_classes, num_detections],
					feed_dict={image_tensor: image_np_expanded})
				# Visualization of the results of a detection.
				vis_util.visualize_boxes_and_labels_on_image_array(
					image_np,
					np.squeeze(boxes),
					np.squeeze(classes).astype(np.int32),
					np.squeeze(scores),
					category_index,
					use_normalized_coordinates=True,
					min_score_thresh=MIN_CONV,
					line_thickness=1)
				out = os.path.join(PATH_TO_OUTDIR, image_name)
				print out
				cv2.imwrite(out, image_np)

if __name__ == '__main__':
	main(sys.argv[0:])