"""Car for moving control."""

import time
import RPi.GPIO as GPIO

# Different speeds under the same control signal due to hardware differences,
# should modify depending on your hardware.
LEFT_FR_BIAS = 1  # Speed difference between two left wheels.
RIGHT_FR_BIAS = 1  # Speed difference between two right wheels.
LEFT_RIGHT_BIAS = 0.2  # Speed difference between left and right wheels.

class Wheel:
	"""Class for wheel.
	
	Use raspberry GPIO to control the rotation of the wheel.
	"""

	def __init__(self, pwm_pin, dir_pin_1, dir_pin_2, pwm_freq):
		"""Inits Wheel with PWM and dirction control pin."""
		self._pwm_pin = pwm_pin  # PWM input pin.
		self._dir_pin_1 = dir_pin_1  # GPIO number to control the direction of rotation of the wheel.
		self._dir_pin_2 = dir_pin_2  # GPIO number to control the direction of rotation of the wheel.
		self._pwm_freq = pwm_freq  # PWM cycle.

		self._last_dir = 's'  # Last rotation direction of this wheel. 's' indicates stop.
		self._last_dc_val = 0  # Last duty cycle value.
		self._current_dc_val = 0  # Current duty cycle value.

		GPIO.setmode(GPIO.BOARD)

		# Set the direction control GPIO output mode.
		GPIO.setup(self._pwm_pin, GPIO.OUT)
		GPIO.setup(self._dir_pin_1, GPIO.OUT)
		GPIO.setup(self._dir_pin_2, GPIO.OUT)

		# Inits PWM pin.
		self._motor_pwm = GPIO.PWM(self._pwm_pin, self._pwm_freq)  # pwm_freq: Hz
		self._motor_pwm.start(0)  # Set duty cycle to 0.

	def clockwise_rotate(self, speed):
		"""Control the wheel to turn clockwise.

		Args:
			speed: PWM duty cycle.
		"""
		if self._last_dir != 'c':  # "c" indicates that the last rotation of this wheel was clockwise.
			GPIO.output(self._dir_pin_1, GPIO.HIGH)
			GPIO.output(self._dir_pin_2, GPIO.LOW)
			self._last_dir = 'c'

		self._current_dc_val = speed
		if self._current_dc_val != self._last_dc_val:
			self._motor_pwm.ChangeDutyCycle(speed)  # 0.0 - 100.0
			self._last_dc_val = self._current_dc_val

	def anticlockwise_rotate(self, speed):
		"""Control the wheel to turn anticlockwise.

		Args:
			speed: PWM duty cycle.
		"""
		if self._last_dir != 'a':  # "a" indicates that the last rotation of this wheel was anticlockwise.
			GPIO.output(self._dir_pin_1, GPIO.LOW)
			GPIO.output(self._dir_pin_2, GPIO.HIGH)
			self._last_dir = 'a'

		self._current_dc_val = speed
		if self._current_dc_val != self._last_dc_val:
			self._motor_pwm.ChangeDutyCycle(speed)  # 0.0 - 100.0
			self._last_dc_val = self._current_dc_val

	def stop(self):
		"""Stop the wheel from turning."""
		GPIO.output(self._dir_pin_1, GPIO.HIGH)
		GPIO.output(self._dir_pin_2, GPIO.HIGH)
		self._last_dir = 's'
		# self._motor_pwm.ChangeDutyCycle(0)


class Car:
	"""Class for car movement control.
	
	The sample usage of this class is like:

	'''
	front_left_wheel = Wheel(pwm_pin=33, dir_pin_1=35, dir_pin_2=37,
							 pwm_freq=1500)
	front_right_wheel = Wheel(pwm_pin=32, dir_pin_1=31, dir_pin_2=29,
							  pwm_freq=1500)
	rear_left_wheel = Wheel(pwm_pin=40, dir_pin_1=38, dir_pin_2=36,
							pwm_freq=1500)
	rear_right_wheel = Wheel(pwm_pin=15, dir_pin_1=13, dir_pin_2=11,
							 pwm_freq=1500)

	my_car = Car(front_left_wheel, front_right_wheel,
					rear_left_wheel, rear_right_wheel)

	my_car.move_forward(4)
	print('forward')
	time.sleep(4)
	my_car.rotate_left(4)
	print('left')
	time.sleep(4)
	my_car.rotate_right(4)
	print('right')
	time.sleep(4)

	GPIO.cleanup()
	'''
	"""

	def __init__(self, front_left_wheel, front_right_wheel,
				 rear_left_wheel, rear_right_wheel):
		"""Inits Car with 4 wheels."""
		self._front_left_wheel = front_left_wheel
		self._front_right_wheel = front_right_wheel
		self._rear_left_wheel = rear_left_wheel
		self._rear_right_wheel = rear_right_wheel

	def move_forward(self, speed):
		"""Control the car to move forward.

		Args:
			speed: PWM duty cycle.
		"""
		# You should modify the bias of 4 wheels depending on your hardware.
		self._front_left_wheel.anticlockwise_rotate(speed + LEFT_FR_BIAS + LEFT_RIGHT_BIAS)
		self._front_right_wheel.clockwise_rotate(speed + RIGHT_FR_BIAS)
		self._rear_left_wheel.anticlockwise_rotate(speed + LEFT_RIGHT_BIAS)
		self._rear_right_wheel.clockwise_rotate(speed)

	def move_reverse(self, speed):
		"""Control the car to move reverse.

		Args:
			speed: PWM duty cycle.
		"""
		# You should modify the bias of 4 wheels depending on your hardware.
		self._front_left_wheel.clockwise_rotate(speed + LEFT_FR_BIAS + LEFT_RIGHT_BIAS)
		self._front_right_wheel.anticlockwise_rotate(speed + RIGHT_FR_BIAS)
		self._rear_left_wheel.clockwise_rotate(speed + LEFT_RIGHT_BIAS)
		self._rear_right_wheel.anticlockwise_rotate(speed)

	def turn_left(self, speed):
		"""Control the car to turn left.

		Args:
			speed: PWM duty cycle.
		"""
		# You should modify the bias of 4 wheels depending on your hardware.
		self._front_left_wheel.anticlockwise_rotate(1 + LEFT_FR_BIAS + LEFT_RIGHT_BIAS)
		self._front_right_wheel.clockwise_rotate(speed + RIGHT_FR_BIAS)
		self._rear_left_wheel.anticlockwise_rotate(1 + LEFT_RIGHT_BIAS)
		self._rear_right_wheel.clockwise_rotate(speed)

	def turn_right(self, speed):
		"""Control the car to turn right.

		Args:
			speed: PWM duty cycle.
		"""
		# You should modify the bias of 4 wheels depending on your hardware.
		self._front_left_wheel.anticlockwise_rotate(speed + LEFT_FR_BIAS + LEFT_RIGHT_BIAS)
		self._front_right_wheel.clockwise_rotate(1 + RIGHT_FR_BIAS)
		self._rear_left_wheel.anticlockwise_rotate(speed + LEFT_RIGHT_BIAS)
		self._rear_right_wheel.clockwise_rotate(1)

	def rotate_left(self, speed):
		"""Control the car to rotate left.

		Args:
			speed: PWM duty cycle.
		"""
		# You should modify the bias of 4 wheels depending on your hardware.
		self._front_left_wheel.clockwise_rotate(speed + LEFT_FR_BIAS + LEFT_RIGHT_BIAS)
		self._front_right_wheel.clockwise_rotate(speed + RIGHT_FR_BIAS)
		self._rear_left_wheel.clockwise_rotate(speed + 1 + LEFT_RIGHT_BIAS)
		self._rear_right_wheel.clockwise_rotate(speed)

	def rotate_right(self, speed):
		"""Control the car to roate right.

		Args:
			speed: PWM duty cycle.
		"""
		# You should modify the bias of 4 wheels depending on your hardware.
		self._front_left_wheel.anticlockwise_rotate(speed + LEFT_FR_BIAS + LEFT_RIGHT_BIAS)
		self._front_right_wheel.anticlockwise_rotate(speed + RIGHT_FR_BIAS)
		self._rear_left_wheel.anticlockwise_rotate(speed + 1 + LEFT_RIGHT_BIAS)
		self._rear_right_wheel.anticlockwise_rotate(speed)

	def stop(self):
		"""Stop the car from moving."""
		self._front_left_wheel.stop()
		self._front_right_wheel.stop()
		self._rear_left_wheel.stop()
		self._rear_right_wheel.stop()
