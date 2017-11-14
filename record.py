
import hashlib
import io
import logging
import os
import random
import re

from lxml import etree
import PIL.Image
import tensorflow as tf

from object_detection.utils import dataset_util
from object_detection.utils import label_map_util

flags = tf.app.flags
flags.DEFINE_string('index', '', 'Index.txt lists the file relations.')
flags.DEFINE_string('outdir', '', 'Path to directory to output TFRecords.')
flags.DEFINE_string('ratio', '30', 'How many percent shall be used for validation?')
FLAGS = flags.FLAGS

def dict_to_tf_example(data, img_path):
	with tf.gfile.GFile(img_path, 'rb') as fid:
		encoded_jpg = fid.read()
	encoded_jpg_io = io.BytesIO(encoded_jpg)
	image = PIL.Image.open(encoded_jpg_io)
	if image.format != 'JPEG':
		raise ValueError('Image format not JPEG')
	key = hashlib.sha256(encoded_jpg).hexdigest()

	width = int(data['size']['width'])
	height = int(data['size']['height'])

	xmin = []
	ymin = []
	xmax = []
	ymax = []
	classes_label = []
	classes_text = []
	if 'object' in data:
		for obj in data['object']:
			xmin.append(float(obj['bndbox']['xmin']) / width)
			ymin.append(float(obj['bndbox']['ymin']) / height)
			xmax.append(float(obj['bndbox']['xmax']) / width)
			ymax.append(float(obj['bndbox']['ymax']) / height)
			classes_label.append(int(obj['id']))
			classes_text.append(obj['name'].encode('utf8'))

	example = tf.train.Example(features=tf.train.Features(feature={
		'image/height': dataset_util.int64_feature(height),
		'image/width': dataset_util.int64_feature(width),
		'image/filename': dataset_util.bytes_feature(data['filename'].encode('utf8')),
		'image/source_id': dataset_util.bytes_feature(img_path.encode('utf8')),
		'image/key/sha256': dataset_util.bytes_feature(key.encode('utf8')),
		'image/encoded': dataset_util.bytes_feature(encoded_jpg),
		'image/format': dataset_util.bytes_feature('jpeg'.encode('utf8')),
		'image/object/bbox/xmin': dataset_util.float_list_feature(xmin),
		'image/object/bbox/xmax': dataset_util.float_list_feature(xmax),
		'image/object/bbox/ymin': dataset_util.float_list_feature(ymin),
		'image/object/bbox/ymax': dataset_util.float_list_feature(ymax),
		'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
		'image/object/class/label': dataset_util.int64_list_feature(classes_label)
	}))
	return example


def create_tf_record(output, index):
	"""Creates a TFRecord file from examples.

	Args:
	output: Path to where output file is saved.
	index: Index of file relations.
	"""
	goods = 0
	errs = 0
	writer = tf.python_io.TFRecordWriter(output)
	for idx, entry in enumerate(index):
		if not os.path.exists(entry[1]):
			print('Could not find {}, ignoring index entry.'.format(entry[1]))
			errs += 1
			continue
		with tf.gfile.GFile(entry[1], 'r') as fid:
			xml_str = fid.read()
		xml = etree.fromstring(xml_str)
		data = dataset_util.recursive_parse_xml_to_dict(xml)['annotation']

		tf_example = dict_to_tf_example(data, entry[0])
		writer.write(tf_example.SerializeToString())
		goods += 1

	writer.close()
	return goods, errs

def main(_):
	index = FLAGS.index
	ratio = max(0, min(100, 100 - int(FLAGS.ratio)))
	rejected = 0

	print('Reading from {}.'.format(index))
	with open(index) as fid:
		lines = fid.readlines()
	example_list = [line.split() for line in lines]

	if len(example_list) == 0:
		exit('invalid index file {}'.format(index))

	# Test images are not included in the downloaded data set, so we shall perform
	# our own split.
	random.seed(42)
	random.shuffle(example_list)
	num_examples = len(example_list)
	num_train = int(ratio * num_examples * 0.01)
	train_examples = example_list[:num_train]
	val_examples = example_list[num_train:]
	print('{0} training and {1} validation examples.'.format(len(train_examples), len(val_examples)))

	train_output_file = os.path.join(FLAGS.outdir, 'train.record')
	val_output_file = os.path.join(FLAGS.outdir, 'val.record')
	[train_goods, train_errs] = create_tf_record(train_output_file, train_examples)
	[val_goods, val_errs] = create_tf_record(val_output_file, val_examples)
	print('{} created with {} files. {} rejected'.format(train_output_file, train_goods, train_errs))
	print('{} created with {} files. {} rejected'.format(val_output_file, val_goods, val_errs))

if __name__ == '__main__':
  tf.app.run()
