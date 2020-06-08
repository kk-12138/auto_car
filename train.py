#!/usr/bin/env python3

"""Train the model.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import datetime
import pathlib
import random
import matplotlib.pyplot as plt

import tensorflow as tf

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, Flatten, Dropout, MaxPooling2D
from tensorflow.keras import regularizers
# from tensorflow.python.client import device_lib

import image_dataset

print(tf.version.VERSION)

AUTOTUNE = tf.data.experimental.AUTOTUNE

# # Need to modify depending on your device.
# os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
# os.environ["CUDA_VISIBLE_DEVICES"]="0"
# print(device_lib.list_local_devices())

# Image size for training.
IMG_HEIGHT = 120
IMG_WIDTH  = 160

BATCH_SIZE = 128

# We use early stopping to avoid long and unnecessary training times,
# so you could set a larger epoch value.
EPOCHS     = 100

# The path for checkpoint callback.
checkpoint_path = "training/cp.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)

# The path for tensorboard log files.
log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

# Get the image dataset.
dataset = image_dataset.ImageDataset(img_path='./dataset', img_size=(120, 160)) # img_size: (h, w)

# Divide 80% of the dataset as the training dataset and the rest as the validation dataset.
dataset.create(train_set_ratio=0.8, val_set_ratio=0.2, batch_size=BATCH_SIZE)

print('Image count: ', dataset.img_count)

# Get the training and validation dataset.
train_ds = dataset.train_ds
val_ds   = dataset.val_ds

def create_model():
	"""Create the model.
	The model structure is based on NVIDIA 2016 <End to end learning for self-driving cars>.
	
	Returns:
		A initialized model.
	"""
	model = Sequential([
		Conv2D(filters=24, kernel_size=5, strides=2, padding='same', activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)),
		Conv2D(filters=36, kernel_size=5, strides=2, padding='same', activation='relu', kernel_regularizer=regularizers.l2(0.001)),
		Conv2D(filters=48, kernel_size=5, strides=2, padding='same', activation='relu', kernel_regularizer=regularizers.l2(0.001)),
		Conv2D(filters=64, kernel_size=3, padding='same', activation='relu', kernel_regularizer=regularizers.l2(0.001)),
		Conv2D(filters=64, kernel_size=3, padding='same', activation='relu', kernel_regularizer=regularizers.l2(0.001)),
		Flatten(),
		Dense(units=250, activation='relu', kernel_regularizer=regularizers.l2(0.001)),
		Dense(units=dataset.class_count, activation='softmax')
        Dense(units=dataset.class_count, activation='softmax')
	])

	model.compile(
		optimizer='adam',
		loss='sparse_categorical_crossentropy',
		metrics=['accuracy']
	)
	return model

# Create a model instance.
model = create_model()

# Display the model's architecture.
model.summary()

# Create checkpoint callback.
cp_callback = tf.keras.callbacks.ModelCheckpoint(
	filepath=checkpoint_path,
	monitor='val_loss',
	save_best_only=True,	# Set it true to save the best model at the end of training.
	save_weights_only=True,	# Only thee model's weights will be saved.
	mode='auto',	# In auto mode, the direction is automatically inferred from the name of the monitored quantity.
	verbose=1
)

# Create early stopping callback.
early_stop = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=15,	# The amount of epochs to check for improvement.
    verbose=1,
    restore_best_weights=True
)

# Create tensorboard callback.
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

# Total number of steps (batches of samples) before declaring one epoch finished and starting the next epoch. 
steps_per_epoch = tf.math.ceil(dataset.train_size/BATCH_SIZE).numpy()
print('Steps per epoch: ', steps_per_epoch)

# Use to solve unbalanced training data.
# 0: move_forward image label;
# 1: turn_left image label;
# 2: turn_right image label.
class_weight={0:0.2, 1:0.3, 2:0.5}

# Trains the model for a fixed number of epochs (iterations on a dataset).
history = model.fit(
	train_ds,
	steps_per_epoch=steps_per_epoch,
	epochs=EPOCHS,
	callbacks=[cp_callback, early_stop, tensorboard_callback],
	validation_data=val_ds,
	class_weight=class_weight,
	validation_steps=tf.math.ceil(dataset.val_size/BATCH_SIZE).numpy()
)

# Save the best model weights.
# Because 'restore_best_weights' is True in 'early_stop' callback,
# the model will restore weights from the epoch with the best value of the monitored quantity,
# therefore we just save the model at this time
model.save('best_model.h5')

print('Model training stoped at: ', early_stop.stopped_epoch)

# Visualize the training results:
print(history.history)
acc      = history.history['accuracy']
val_acc  = history.history['val_accuracy']
loss     = history.history['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(8, 8))

x_axis = range(len(acc))
plt.subplot(1, 2, 1)
plt.plot(x_axis, acc, label='Training Accuracy')
plt.plot(x_axis, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

x_axis = range(len(loss))
plt.subplot(1, 2, 2)
plt.plot(x_axis, loss, label='Training Loss')
plt.plot(x_axis, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()
