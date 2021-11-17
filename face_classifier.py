from tensorflow.python.keras.applications.resnet import ResNet50
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
import tensorflow as tf
import cv2
import numpy as np
import db

# Find total number of classes in database
NUM_CLASSES = len(db.get_classes()) - 1

# Define size of input image to classifier
IMAGE_RESIZE = 224

def train():

	NUM_CLASSES = len(db.get_classes()) - 1
	model = Sequential()
	model.add(ResNet50(include_top = False, pooling='avg', weights='imagenet'))
	model.add(Dense(NUM_CLASSES, activation='softmax'))
	model.layers[0].trainable = False
	model.summary()

	rows = db.get_training_data()

	x_train = []
	y_train = []

	for row in rows:
		x_train.append(cv2.resize(cv2.imread(row[0]), (IMAGE_RESIZE, IMAGE_RESIZE)))
		one_hot_vector = [0] * NUM_CLASSES
		one_hot_vector[int(row[1])] = 1
		y_train.append(one_hot_vector)
	
	x_train = np.asarray(x_train)
	y_train = np.asarray(y_train)
	print(x_train.shape)
	print(y_train.shape)

	model.compile(	loss='binary_crossentropy',
					optimizer='ADAM',
					metrics=['accuracy'])
	model.fit(x_train, y_train, epochs=20)
	model.save_weights("classifier.h5")
	print("[+] Training process complete.")
	print("[+] New weights saved as 'classifier.h5'")

def test(img) -> list:
	global model
	return model.predict(np.asarray([img]))

print("[!] Loading Face Classification Model (resnet50)...")
NUM_CLASSES = len(db.get_classes()) - 1
model = Sequential()
model.add(ResNet50(include_top = False, pooling='avg', weights='imagenet'))
model.add(Dense(NUM_CLASSES, activation='softmax'))
model.layers[0].trainable = False
model.summary()

try:
	model.load_weights('classifier.h5')
except:
	print("[!] Weights mismath...")
	print("[!] Retraining weights...")
	train()
	model.load_weights('classifier.h5')
print("[+] Face Classification Model Loaded Successfully!")

test_image = cv2.resize(cv2.imread("faces/DSC_0405_3.png"), (IMAGE_RESIZE, IMAGE_RESIZE))
cv2.imshow("asdf", test_image)
print(model.predict(np.asarray([test_image])))