import cv2 as cv2
import numpy as np
import os
import db
import sqlite3 as sl

FACES_PATH = "static/faces"
CLASSIFY_THRESH = 0.7

print("[!] Loading Face Detection Model (yolov3-tiny)...")
net = cv2.dnn.readNetFromDarknet('face-detect-yolov3-tiny.cfg', 'face-yolov3-tiny_41000.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
classes = ['faces']
colors = [(0, 255, 0)]
print("[+] Face Detection Model Loaded Successfully!")

import face_classifier as fc

def imshow (win_name, img):
	cv2.namedWindow(win_name, cv2.WND_PROP_FULLSCREEN | cv2.WINDOW_NORMAL)
	cv2.imshow(win_name,img)

def save_faces (img_path, debug=False) -> list:
	'''
	This function takes an image as input. The image is cropped into 
	sub-images containing only faces. All these sub-images are stored
	as a separate file. The file names are returned as an array.

	All new images of faces are saved in the format: untagged_<number>.png
	<number> is obtained by parsing through the faces diretory and finding 
	the maximum number and adding 1 to it.
	'''
	print(img_path)
	img = cv2.imread(img_path)

	blob = cv2.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
	r = blob[0, 0, :, :]

	net.setInput(blob)
	outputs = net.forward(ln)

	r0 = blob[0, 0, :, :]
	r = r0.copy()

	boxes = []
	confidences = []
	classIDs = []
	img_h, img_w = img.shape[:2]

	for output in outputs:
		for detection in output:
			scores = detection[5:]
			classID = np.argmax(scores)
			confidence = scores[classID]
			if confidence > 0.5:
				box = detection[:4] * np.array([img_w, img_h, img_w, img_h])
				(centerX, centerY, width, height) = box.astype("int")
				x = int(centerX - (width / 2))
				y = int(centerY - (height / 2))
				box = [x, y, int(width), int(height)]
				boxes.append(box)
				confidences.append(float(confidence))
				classIDs.append(classID)

	indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
	bbox = []
	if len(indices) > 0:
		for i in indices.flatten():
			(x, y) = (boxes[i][0], boxes[i][1])
			(w, h) = (boxes[i][2], boxes[i][3])
			bbox.append([x, y, w, h])

		faces = []
		for x, y, w, h in bbox:
			faces.append(img[y:min(y+h, img_h), x:min(x+w, img_w)].copy())

		if debug:
			for i, (x, y, w, h) in enumerate(bbox):		
				cv2.imshow(f"face {i}", img[y:min(y+h, img_h), x:min(x+w, img_w)])
				color = [int(c) for c in colors[classIDs[i]]]
				cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
				text = "{}: {:.4f}".format(classes[classIDs[i]], confidences[i])
				cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

	else:
		print("No faces!")
		return []
	
	file_num = 1
	img_name = os.path.basename(img_path).split('.')[0]
	new_file_names = []
	for face in faces:
		new_file_names.append(f"{FACES_PATH}/{img_name}_{file_num}.png")
		cv2.imwrite(f"{FACES_PATH}/{img_name}_{file_num}.png", face)
		file_num += 1

	if debug:
		imshow('window', img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	return new_file_names

def user_tag_brute (img, debug=False) -> str:
	'''
	This function takes a face image as input and requests the user
	to type the name of the person in the image. The same is returned.
	
	This function needs to be used if and only if the predictions 
	obtained from the classifier are not satisfactory i.e. below the 
	set threshold (CLASSIFY_THRESH).
	'''
	# img = cv2.imread(path_to_img)
	print("Press escape on the image window and then type name of the person in console.")
	cv2.imshow("Who is this?", img)
	cv2.waitKey(0)
	name = input("Enter the person in the image: ")

	return name.lower()

def add_image (img_path: str) -> None:
	'''
	This function takes an image, detects the faces and saves them as separate 
	files. 
	
	The following steps happen and need to be atomic. 
	Step-1: Add image_path to table:all_images with tagged=0.
	Step-2: Detect all faces, crop and save. Add cropped faces to the table: untagged_images.
	'''
	print("IMAGE ADDED AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

	con = sl.connect(db.DB_PATH)
	cursor = con.cursor()
	cursor.execute("begin")
	face_paths = []
	try:
		sql = "INSERT INTO all_images(image_path) VALUES (?)"
		cursor.execute(sql, (img_path,))

		sql = "INSERT INTO untagged_images(face_path, complete_image_path) VALUES (?, ?)"
		
		face_paths = save_faces(img_path)
		
		for face_path in face_paths:
			cursor.execute(sql, (face_path, img_path))
		con.commit()

	except con.Error as er:
		db.print_error(er)
		for face_path in face_paths:
			os.remove(face_path)
		
		con.rollback()

def tag_image (complete_img_path: str) -> None:
	'''
	This function takes a complete image as input and classifies all the faces in that image.
	Once all the faces are tagged, the tags are pushed onto the table: tagged_faces.
	It calls classify_face to infer from the classifier. If the best accuracy 
	is less than CLASSIFY_THRESH, then the user is asked to tag the face by 
	calling user_tag_brute.

	step-1: get all face images for given image. for each face image
		step-1a: classify
		step-1b: insert face class to image_tags table
		step-1c: insert face class to tagged_faces table
		step-1d: remove face image from untagged_images
	step-2: change bool value of tagged in all_images to 1
	'''

	con = sl.connect(db.DB_PATH)
	cursor = con.cursor()
	
	# face_classes is a dict with key as class id and value as class name
	face_classes = dict(db.get_classes())
	MAX_ID = len(face_classes)-1

	cursor.execute('begin')
	try:
		query = 'SELECT * FROM untagged_images WHERE complete_image_path = (?)'
		rows = cursor.execute(query, (complete_img_path,))
		face_paths = [i[0] for i in rows.fetchall()]
		print(face_paths)
		
		for face_path in face_paths:
			print(face_path)

			img = cv2.imread(face_path)
			
			class_acc = classify_face(img)
			if class_acc[list(class_acc.keys())[0]] < CLASSIFY_THRESH:
				face_class = user_tag_brute(img)
			else:
				face_class = list(class_acc.keys())[0]
			
			if face_class not in list(face_classes.keys()):
				query = 'INSERT INTO class(id, class) VALUES(?, ?)'
				cursor.execute(query, (MAX_ID, face_class))
				face_classes[face_class] = MAX_ID
				MAX_ID += 1

			query = 'INSERT INTO image_tags(image_path, face) VALUES(?, ?)'
			cursor.execute(query, (complete_img_path, face_classes[face_class]))
			query = 'INSERT INTO tagged_faces(face_path, class) VALUES(?, ?)'
			cursor.execute(query, (face_path, face_classes[face_class]))

		query = 'DELETE FROM untagged_images WHERE complete_image_path = (?)'
		cursor.execute(query, (complete_img_path,))
		query = 'UPDATE all_images SET tagged=1 WHERE image_path=(?);'
		cursor.execute(query, (complete_img_path,))
		con.commit()

	except con.Error as er:
		db.print_error(er)
		con.rollback()

def tag_all_faces() -> None:
	'''
	This function takes a complete image as input and classifies all the faces in that image.
	Once all the faces are tagged, the tags are pushed onto the table: tagged_faces.
	It calls classify_face to infer from the classifier. If the best accuracy 
	is less than CLASSIFY_THRESH, then the user is asked to tag the face by 
	calling user_tag_brute.

	step-1: get all face images for given image. for each face image
		step-1a: classify
		step-1b: insert face class to image_tags table
		step-1c: insert face class to tagged_faces table
		step-1d: remove face image from untagged_images
	step-2: change bool value of tagged in all_images to 1
	'''

	# if face_class not in list(face_classes.keys()):
	# 	query = 'INSERT INTO class(id, class) VALUES(?, ?)'
	# 	cursor.execute(query, (MAX_ID, face_class))
	# 	face_classes[face_class] = MAX_ID
	# 	MAX_ID += 1

	con = sl.connect(db.DB_PATH)
	cursor = con.cursor()

	face_classes = dict(db.get_classes())

	query = "SELECT face_path FROM untagged_images"
	rows = cursor.execute(query)
	face_paths = [i[0] for i in rows.fetchall()]
	print("FACE PATHS ", len(face_paths), face_paths)
	low_acc=[]

	for face_path in face_paths:

		img = cv2.imread(face_path)
		print("FACE PATH :",face_path, flush=True)
		class_acc = classify_face(img)
		acc_keys = list(class_acc.keys())
		max_acc_class = acc_keys[0] if len(acc_keys) else None

		if max_acc_class is not None and class_acc[max_acc_class] >= CLASSIFY_THRESH:

			cursor.execute('begin')

			try:

				face_class = max_acc_class
				print(face_class, face_classes[face_class])
				query = 'SELECT complete_image_path FROM untagged_images WHERE face_path = (?)'
				complete_img_path = cursor.execute(query, (face_path,)).fetchall()[0][0]
				print("QUERY 1 executed",flush=True)

				query = 'INSERT INTO image_tags(image_path, face) VALUES(?, ?)'
				print("THIS TIHNG", complete_img_path, face_classes[face_class])
				cursor.execute(query, (complete_img_path, face_classes[face_class]))
				print("QUERY 2 executed",flush=True)

				query = 'INSERT INTO tagged_faces(face_path, class) VALUES(?, ?)'
				cursor.execute(query, (face_path, face_classes[face_class]))
				print("QUERY 3 executed",flush=True)

				query = 'DELETE FROM untagged_images WHERE face_path = (?)'
				cursor.execute(query, (face_path,))
				print("QUERY 4 executed",flush=True)


				query = 'SELECT * FROM untagged_images WHERE complete_image_path = (?);'
				result = cursor.execute(query, (complete_img_path,)).fetchall()
				if not len(result):
					query = 'UPDATE all_images SET tagged=1 WHERE image_path=(?);'
					cursor.execute(query, (complete_img_path,))
					print("QUERY 5 executed",flush=True)

				con.commit()

			except:
				print("SQLITE ERROR :(")
				con.rollback()

		else:
			print(class_acc)
			low_acc.append(face_path)

	return low_acc

def update_tagged_status():
	''' This function looks at images with tagged = False and updates it to True if tagging was already done '''
	pass
	

def classify_face (img) -> dict:
	'''
	This function takes a cv Mat object image as input and attempts to classify it.
	It returns the top 5 class labels that the face belongs to along with their accuracies.
	'''
	results = fc.test(cv2.resize(img, (fc.IMAGE_RESIZE, fc.IMAGE_RESIZE))).tolist()[0]
	results = [(db.get_class_label(class_id), acc) for class_id, acc in enumerate(results)]
	results.sort(reverse=True, key=lambda x: x[1])
	
	return dict(results[:5])

# add_image('images/DSC_0406.JPG')
# tag_image('images/DSC_0406.JPG')

# print(dict(db.get_classes()))
# print(classify_face(cv2.imread('faces/DSC_0403_1.png')))