"""Receive images from raspberry and predict the direction the car should move."""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import io
import time
import socket
import struct
import numpy as np
import cv2

import tensorflow as tf
from tensorflow import keras

# Image size input to the model.
IMG_HEIGHT = 120
IMG_WIDTH  = 160

# Load the model for prediction.
model = keras.models.load_model('best_model.h5')

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces).
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it.
connection = server_socket.accept()[0].makefile('rwb')

try:
	while True:
		# Read the length of the image as a 32-bit unsigned int. If the
		# length is zero, quit the loop.
		image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]

		if not image_len:
			break

		# Construct a stream to hold the image data and read the image
		# data from the connection.
		image_stream = io.BytesIO()
		image_stream.write(connection.read(image_len))

		# Rewind the stream, open it as an image with OpenCV and do some
		# processing on it.
		image_stream.seek(0)

		# Convert the stream to image array.
		img_array = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)

		# Decode the image array.
		image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
		cv2.imshow('image', image)

		# Process the image for prediction.
		image = tf.image.resize(images=image, size=[IMG_HEIGHT, IMG_WIDTH])
		image /= 255.0  # Normalize to [0,1] range.

		start = time.time()

		# Start prediction.
		prediction = model.predict(tf.expand_dims(image, axis=0))

		print(time.time() - start)  # Time used by prediction.

		# Get the best result from the prediction.
		key = np.argmax(prediction)

		# Sent the result to raspberry for moving control.
		connection.write(str(key).encode('utf-8'))
		connection.flush()

		# When you press the 'q' key, quit prediction.
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

finally:
	connection.close()
	server_socket.close()
