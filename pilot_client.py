"""Get the prediction result and control the moving."""

import io
import socket
import struct
import time
import picamera

import car

# IP address and port number of the machine you runs the prediction.
SERV_ADDR = '192.168.0.103'
PORT      = 8000

# Create a car instance for moving control.
front_left_wheel = car.Wheel(pwm_pin=33, dir_pin_1=35, dir_pin_2=37,
							 pwm_freq=1500)
front_right_wheel = car.Wheel(pwm_pin=32, dir_pin_1=31, dir_pin_2=29,
							  pwm_freq=1500)
rear_left_wheel = car.Wheel(pwm_pin=40, dir_pin_1=38, dir_pin_2=36,
							pwm_freq=1500)
rear_right_wheel = car.Wheel(pwm_pin=15, dir_pin_1=13, dir_pin_2=11,
							 pwm_freq=1500)
my_car = car.Car(front_left_wheel, front_right_wheel,
				rear_left_wheel, rear_right_wheel)

# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server).
client_socket = socket.socket()
client_socket.connect((SERV_ADDR, PORT))

# Make a file-like object out of the connection.
connection = client_socket.makefile('rwb')

try:
	with picamera.PiCamera() as camera:
		# This is preview window size.
		camera.resolution = (480, 320)
		camera.framerate = 30

		# Camera warm-up time.
		time.sleep(2)
		start = time.time()
		count = 0
		stream = io.BytesIO()

		# Use the video-port for captures...
		for foo in camera.capture_continuous(stream, 'jpeg',
											 use_video_port=True):
			connection.write(struct.pack('<L', stream.tell()))
			connection.flush()
			stream.seek(0)
			connection.write(stream.read())
			count += 1

			# Reset the stream for the next capture
			stream.seek(0)
			stream.truncate()

			# Waiting for prediction.
			key = connection.read(1).decode('utf-8')

			# If the prediction is '0', control the car moving forward.
			if key == '0':
				print("Move forward")
				my_car.move_forward(4)

			# If the prediction is "1", the car is controlled to rotate to the left.
			elif key == '1':
				my_car.rotate_left(4)
				print("Turn left")

			# If the prediction is "2", the car is controlled to rotate to the right.
			elif key == '2':
				my_car.rotate_right(4)
				print("Turn right")  

	# Write a length of zero to the stream to signal we're done
	connection.write(struct.pack('<L', 0))

finally:
	connection.close()
	client_socket.close()
	finish = time.time()

print('Sent %d images in %d seconds at %.2ffps' % (
	count, finish-start, count / (finish-start)))
