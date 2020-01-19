#!/usr/bin/env python3

"""Use the keyboard to control the car movement and automatically save labelled pictures.
"""

import time
import threading

import pygame
import cv2 as cv

import car

def cam_init(dev_nu=0, view_width=320, view_height=240, fps=30):
	"""Initialize the camera with the parameters.

	Args:
		dev_nu: The device name of camera in /dev/, usually 0.
		view_width: The width of the preview window when you control the car moving.
		view_height: The height of the preview window when you control the car moving.
		fps: Frames per second of the camera.

	Returns:
		A initialized camera object.
	"""
	# Opens the camera for video capturing.
	camera = cv.VideoCapture(dev_nu)
	if not camera.isOpened():
		print("Can't open camera")
		exit()

	print("Original fps is: %d" % camera.get(cv.CAP_PROP_FPS))

	# Set the width of the frames in the video stream.
	camera.set(cv.CAP_PROP_FRAME_WIDTH, view_width)
	# Set the height of the frames in the video stream.
	camera.set(cv.CAP_PROP_FRAME_HEIGHT, view_height)

	# Set the framrate, it may fail, you should check the result.
	ret = camera.set(cv.CAP_PROP_FPS, fps)
	if ret:
		print("Set fps %d success" % fps)
	else:
		print("This camera doesn't support fps settings")	

	return camera

def keyboard_init():
	"""Initialize the keyboard to capture key events.

	Returns:
		A initialized keyborad object.
	"""
	pygame.init()

	# Set the window size of key press capturer.
	# When you start capturing key events, make sure the mouse arrow falls in this window.
	pygame.display.set_mode((50, 50))
	return pygame

def car_init():
	"""Initialize the car to control it moving.

	Returns:
		A initialized car object.
	"""
	# Creates 4 wheels with GPIO and PWM configurations to make up the car.
	front_left_wheel = car.Wheel(pwm_pin=33, dir_pin_1=35, dir_pin_2=37,
								 pwm_freq=1500)
	front_right_wheel = car.Wheel(pwm_pin=32, dir_pin_1=31, dir_pin_2=29,
								  pwm_freq=1500)
	rear_left_wheel = car.Wheel(pwm_pin=40, dir_pin_1=38, dir_pin_2=36,
								pwm_freq=1500)
	rear_right_wheel = car.Wheel(pwm_pin=15, dir_pin_1=13, dir_pin_2=11,
								 pwm_freq=1500)

	# Make up the car with the wheels.
	my_car = car.Car(front_left_wheel, front_right_wheel,
					rear_left_wheel, rear_right_wheel)
	return my_car

def car_control(keyboard, car):
	"""Control the movement of the car using keyboard.

	Args:
		keyboard: Keyboard to handle key events.
		car: Car object to control the movement.
	"""
	# A key flag indicating which key has been pressed.
	# This key flag will be used to classify the images.
	global key_flag

	# Start handle the key enents in this infinite loop.
	while True:
		for event in keyboard.event.get():

			# Capture key press events.
			if event.type == keyboard.KEYDOWN:

				# Get the key value.
				key_input = keyboard.key.get_pressed()

				# When you press the up arrow key, control the car to move forward.
				if key_input[keyboard.K_UP]:
					# Sets the PWM value to the car.
					car.move_forward(4)
					key_flag = 'f'	# Update the key flag.
					print('Move forward')

				# When you press the left arrow key, control the car to turn left.
				elif key_input[keyboard.K_LEFT]:
					# Sets the PWM value to the car.
					car.rotate_left(4)
					key_flag = 'l'	# Update the key flag.
					print('Ture left')

				# When you press the right arrow key, control the car to turn right.
				elif key_input[keyboard.K_RIGHT]:
					# Sets the PWM value to the car.
					car.rotate_right(4)
					key_flag = 'r'	# Update the key flag.
					print('Ture right')

			# Capture key up events.
			# After releasing the key, control the car to stop moving.
			elif event.type == keyboard.KEYUP:
				# Stop the car.
				car.stop()
				key_flag = 's'	# Update the key flag.
				print('Stop')

			# Quit key events loop.
			elif event.type == keyboard.QUIT:
				raise SystemExit

def capture_img(camera, path, img_size):
	"""Capture the image and save it to the corresponding folder based on the key flag.

	Args:
		camera: The camera object to capture images.
		path: The image file save path.
		img_size: The tuple of image size.
	"""
	# The key flag used to classify the images.
	global key_flag

	while True:
		# Capture frame-by-frame
		ret, frame = camera.read()

		# If frame is read correctly ret is True
		if not ret:
			print("Can't receive frame. Exiting ....")
			break

		# Preview the image.
		cv.imshow('image', frame)

		# Core operation on the frame
		img_resized = cv.resize(frame, img_size)

		# If the key flag at this time is f(forward), save the image to the move_forward folder.
		if key_flag == 'f':
			cv.imwrite(path + 'move_forward/' + str(time.time()) + '.jpg', img_resized)

		# If the key flag at this time is l(left), save the image to the turn_left folder.
		elif key_flag == 'l':
			cv.imwrite(path + 'move_left/' + str(time.time()) + '.jpg', img_resized)

		# If the key flag at this time is r(right), save the image to the turn_right folder.
		elif key_flag == 'r':
			cv.imwrite(path + 'move_right/' + str(time.time()) + '.jpg', img_resized)

		# When you press the 'q' key, quit image capture.
		if cv.waitKey(1) & 0xff == ord('q'):
			break

	# When everything done, release the capture
	camera.release()

if __name__ == '__main__':
	# Initialize the key flag to s(stop).
	key_flag = 's'

	# Initialize camera, keyboaard and the car.
	camera   = cam_init()
	keyboard = keyboard_init()
	my_car   = car_init()

	# Create 2 threads to handle keypress and image capture tasks in parallel.
	controller = threading.Thread(target=car_control, args=(keyboard, my_car,))
	capturer   = threading.Thread(target=capture_img, args=(camera, './dataset/', (160, 120),))

	# Start the car control thread.
	controller.start()

	# Start the image capture thread.
	capturer.start()

	# Block the main thread until the child thread exits.
	controller.join()
	capturer.join()
