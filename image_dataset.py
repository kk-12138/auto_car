"""Image dataset using pipeline and cache to achieve high performance.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf

import pathlib
import random
import matplotlib.pyplot as plt

AUTOTUNE = tf.data.experimental.AUTOTUNE

class ImageDataset(object):
	"""Class for image dataset.

	This dataset will provide functions for images:
	1. To be well shuffled.
	2. To be batched.
	3. Batches to be available as soon as possible.

	The sample usage of this class is like:

	'''
	dataset = ImageDataset(img_path='./dataset', img_size=(120, 160)) # img_size: (h, w)
	dataset.create(train_set_ratio=0.8, val_set_ratio=0.2, batch_size=32)

	print('Image count: ', dataset.img_count)

	train_ds = dataset.train_ds
	val_ds   = dataset.val_ds

	# Check the shapes and types of the dataset
	print(train_ds) # shapes: ((None, 120, 160, 3), (None,)), types: (tf.float32, tf.int32)

	# Take a quick look at a few pictures
	for ds in train_ds.take(1):
		plt.figure('image show')
		for i in range(15):
			plt.subplot(3, 5, i+1)
			plt.imshow(ds[0][i])
		plt.show()
	'''
	"""

	def __init__(self, img_path, img_size):
		"""Inits ImageDataset with image path and size."""
		data_root = pathlib.Path(img_path)
		self._img_size = img_size  # [IMG_HEIGHT, IMG_WIDTH]

		self._all_image_paths = list(data_root.glob('*/*'))  # a list of [PosixPath('dataset/turn_right/1573975293.9194663.png'), ...]
		self._all_image_paths = [str(path) for path in self._all_image_paths]  # a list of ['dataset/turn_right/1573974760.0789077.png', ...]
		random.shuffle(self._all_image_paths)  # Shuffle images.

		label_names = sorted(item.name for item in data_root.glob('*/') if item.is_dir())  # ['move_forward', 'turn_left', 'turn_right']
		label_to_index = dict((name, index) for index, name in enumerate(label_names))  # {'turn_left': 1, 'turn_right': 2, 'move_forward': 0}
		self._all_image_labels = [label_to_index[pathlib.Path(path).parent.name] for path in self._all_image_paths]

		self._img_count = len(self._all_image_paths)  # image count.
		self._class_count = len(label_names)  # class count.

	@property
	def img_count(self):
		"""Get image count."""
		return self._img_count

	@property
	def class_count(self):
		"""Get class count."""
		return self._class_count

	def _preprocess_image(self, img_raw):
		"""Decode image and perform data augmentation.
		
		Returns:
			A normalized image.
		"""
		img_tensor = tf.image.decode_jpeg(contents=img_raw, channels=3)  # Can be used for plt.imshow(img_tensor)
		img = tf.image.resize(images=img_tensor, size=self._img_size)

		# Should do some data augmentation here
		img /= 255.0  # Normalize to [0,1] range
		return img

	def _load_and_preprocess_image(self, path):
		"""Load images from path.
		
		Returns:
			Image raw data.
		"""
		img_raw = tf.io.read_file(path) # can't be used for plt.imshow(img_raw)
		return self._preprocess_image(img_raw)

	def _load_and_preprocess_from_path_label(self, path, label):
		"""Load and preprocess images.
		
		Returns:
			Image precessed and the label.
		"""
		return self._load_and_preprocess_image(path), label

	def create(self, train_set_ratio, val_set_ratio, batch_size):
		"""Create the dataset.

		Args:
			train_set_ratio: Percentage of training dataset.
			val_set_ratio: Pwecentage of validation dataset.
			batch_size: Batch size.
		"""
		# Creates a Dataset whose elements are slices of the given tensors.
		ds = tf.data.Dataset.from_tensor_slices((self._all_image_paths, self._all_image_labels))

		# Convert the image path to image data.
		image_label_ds = ds.map(self._load_and_preprocess_from_path_label)

		# Calculate training and validation images count.
		self._train_size = int(train_set_ratio*self._img_count)
		self._val_size   = int(val_set_ratio*self._img_count)

		# Create training and validation dataset.
		self._train_ds = image_label_ds.take(self._train_size)
		self._val_ds   = image_label_ds.skip(self._train_size).take(self._val_size)

		# cache calculations between epochs
		self._train_ds = self._train_ds.cache(filename='./cache.tf-data')

		# Shuffle and repeat images.
		self._train_ds = self._train_ds.shuffle(buffer_size=self._train_size, reshuffle_each_iteration=True).repeat()

		# Batch and prefetch for high performance fetch.
		self._train_ds = self._train_ds.batch(batch_size).prefetch(buffer_size=AUTOTUNE)

		# Validation data don't need to shuffle.
		self._val_ds = self._val_ds.batch(batch_size)
		self._val_ds = self._val_ds.prefetch(buffer_size=AUTOTUNE)

	@property
	def train_size(self):
		"""Get training data size."""
		return self._train_size

	@property
		"""Get validation data size."""
	def val_size(self):
		return self._val_size

	@property
	def train_ds(self):
		"""Get training dataset."""
		return self._train_ds

	@property
	def val_ds(self):
		"""Get validation dataset."""
		return self._val_ds

""" Sample code for reference """
if __name__ == '__main__':
	dataset = ImageDataset(img_path='./dataset', img_size=(120, 160))  # img_size: (h, w)
	dataset.create(train_set_ratio=0.8, val_set_ratio=0.2, batch_size=32)

	print('Image count: ', dataset.img_count)

	train_ds = dataset.train_ds
	val_ds   = dataset.val_ds

	# Check the shapes and types of the dataset
	print(train_ds)  # shapes: ((None, 120, 160, 3), (None,)), types: (tf.float32, tf.int32)

	# Take a quick look at a few pictures
	for ds in train_ds.take(1):
		plt.figure('image show')
		for i in range(15):
			plt.subplot(3, 5, i+1)
			plt.imshow(ds[0][i])
		plt.show()
