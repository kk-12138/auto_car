Hardware:<br>
--------
`Raspberry Pi`: 3 B+<br>

`PC`: with GTX 1060 for CUDA acceleration.<br>

Software:<br>
--------
Tensorflow 2.0<br>

Usage:<br>
--------
`1. Data collection`: Run `collect_data.py` on Raspberry Pi.<br>
	Use the keyboard to control the movement of the car,<br>
	and it will save the pictures captured by the camera to the corresponding folders according to the key values.<br>
	Each folder corresponds to a category (move forward, turn left, turn right).<br>

`2. Training`: Run `train.py` on your PC (Copy Raspberry's dataset folder to your PC first).<br>
	The model refers to an autopilot paper from NVIDIA in 2016.(https://images.nvidia.com/content/tegra/automotive/images/2016/solutions/pdf/end-to-end-dl-using-px.pdf)<br>
	Although the model of this paper is aimed at realistic road scenes, it is indeed a bit overkill for simple line-tracking cars (the model is too complicated, close to 500w model parameters).<br>
	But this model has strong adaptability and can be easily migrated to complex scenes.<br>
	
`3. Prediction`: Run `pilot_serv.py` on your PC, and then Run `pilot_client.py` on Raspberry Pi.<br>
	This model is too complicated for the line-tracking task, and the convolution operation on Raspberry is too inefficient.<br>
	Therefore, we collect images on Raspberry, and transfer images to the PC using network stream.<br>
	Then do the forward propagation of the neural network on the PC to calculate the movement direction.<br>
	Then send the prediction to Raspberry to control the car's movement.<br>
	After test it can reach a rate of about 20 frames.<br>
	
Tips:<br>
--------
`Track the workflow`: `tensorboard --logdir logs/`<br>
Use TensorBoard to track merics like loss and accuracy, visualize model graph, project embeddings to a lower dimensional space, and much more.<br>
![acc](https://github.com/kk-12138/auto_car/blob/master/.temp/acc.png)
![histogram](https://github.com/kk-12138/auto_car/blob/master/.temp/histogram.png)

`Visualize the result`:<br>
![result](https://github.com/kk-12138/auto_car/blob/master/.temp/result.png)

	
Known issues:<br>
--------
* The data is unbalanced.<br>
	The amount of data for the car going straight is much larger than the amount of data for turning.<br>
	In this way, the trained network will perform well in the prediction of the car going straight, but the prediction effect for turning will be poor.<br>
	`Solution`: Use TensorFlow's class_weight parameter to manually specify the weight ratio of each class,<br>
	so that the network pays more attention to the samples with smaller data volume.<br>

	`class_weight`: Optional dictionary mapping class indices (integers) to a weight (float) value,<br>
	used for weighting the loss function (during training only).<br>
	This can be useful to tell the model to "pay more attention" to samples from an under-represented class.<br>
