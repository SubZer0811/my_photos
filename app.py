#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, send_from_directory, session, flash, url_for
import streamlit as st, cv2, os, numpy as np, pathlib, base64, sqlite3 as sl, db, utils, json, face_classifier
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345678'
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tiff'}

# @app.route('/')
@app.route('/', methods=['GET', 'POST'])
def home_page():

	utils.tag_all_faces()

	search = request.args.get('q')
	search = '' if search is None else search

	con = sl.connect(db.DB_PATH)
	cursor = con.cursor()
	# query = "SELECT DISTINCT image_path FROM all_images" if search=='' else f"SELECT DISTINCT image_path FROM class JOIN image_tags WHERE class.ID == image_tags.face and class.class LIKE '{search.lower()}%'"
	query = "SELECT image_tags.image_path, class.class FROM all_images JOIN image_tags JOIN class where image_tags.image_path=all_images.image_path and image_tags.face=class.id"
	cursor.execute(query)
	result = cursor.fetchall()

	tags = {}
	for image,tag in result:
		tags[image] = tags.get(image,[]) + [tag,]

	print(tags)

	divs =[]
	for image in tags.keys():
		divs.append(
			f"""
			<div class="brick">
			<img src="{image}" alt="{os.path.basename(image)} - {', '.join(tags[image])}">
			</div>
			"""
		)

	divs = "\n".join(divs)

	divs = "<h3 style='color: white'> No images found </h3>" if divs == '' else divs

	# if request.method == 'POST':

	count = 0
	print("HEREEEEEEEEEEEEEEEEEEEEEEEEEEEE")

	files = request.files.getlist('file')
	print(files)

	for file in files :
		print("UPLOOOOOOOOOOOOOOOOOOOOOOOOOOOAD")

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			file.save(filename)
			count+=1
			utils.add_image(filename)

	return render_template('home.html', search=search, divs=divs)

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/tagging', methods=['GET', 'POST'])
def tagging():

	con = sl.connect(db.DB_PATH)
	cursor = con.cursor()

	classes = db.get_classes()
	class_names = [ class_name for class_name,id in classes ]
	class_names.remove('none')

	print(class_names)
	# query = "SELECT face_path FROM untagged_images"
	# cursor.execute(query)
	images = utils.tag_all_faces()
	print("FACE IMAGE LIST",images)

	classes = db.get_classes()
	print(classes)

	class_names = [class_name for class_name,id in classes]
	class_names.remove('none')
	options = [ f'<option value="{class_name}">' for class_name in class_names ]
	options = '\n'.join(options)
	print(options)
	divs =[]
	for i in images:
		divs.append(
			f"""
			<div class="brick">
			<img src="{i}" alt="{os.path.basename(i)}" height="256" width="auto">
			<input list="classes" name="class" id="{i}">
			<datalist id="classes">
				{options}
			</datalist>
			</div>
			"""
		)

	divs = "\n".join(divs)
	divs = "<h3 style='color: white'> All images tagged </h3>" if divs == '' else divs

	return render_template('tagging.html', divs=divs)


@app.route('/tagging_final', methods=['POST'])
def get_post_javascript_data():

	jsdata=request.form.get("javascript_data")
	tags = json.loads(jsdata)

	con = sl.connect(db.DB_PATH)
	cursor = con.cursor()

	face_classes = dict(db.get_classes())
	MAX_ID = len(face_classes)-1

	for face_path, class_name in tags:

		class_id = cursor.execute(f"SELECT id FROM class where class = '{class_name}'").fetchall()
		cursor.execute('begin')

		try:

			if len(class_id)==0: # new class to be created

				query = 'INSERT INTO class(id, class) VALUES(?, ?)'
				cursor.execute(query, (MAX_ID, class_name))
				print("QUERY 0 executed",flush=True)
				face_classes[class_name] = MAX_ID
				class_id = MAX_ID
				MAX_ID += 1

			else:

				class_id=class_id[0][0]

			query = 'SELECT complete_image_path FROM untagged_images WHERE face_path = (?)'
			complete_img_path = cursor.execute(query, (face_path,)).fetchall()[0][0]
			print("QUERY 1 executed",flush=True)

			query = 'INSERT INTO image_tags(image_path, face) VALUES(?, ?)'
			cursor.execute(query, (complete_img_path, class_id))
			print("QUERY 2 executed",flush=True)

			query = 'INSERT INTO tagged_faces(face_path, class) VALUES(?, ?)'
			cursor.execute(query, (face_path, class_id))
			print("QUERY 3 executed",flush=True)

			query = 'DELETE FROM untagged_images WHERE face_path = (?)'
			cursor.execute(query, (face_path,))
			print("QUERY 4 executed",flush=True)


			# cursor.execute('begin')

					
			query = 'SELECT * FROM untagged_images WHERE complete_image_path = (?);'
			result = cursor.execute(query, (complete_img_path,)).fetchall()
			if len(result)==0:
				query = 'UPDATE all_images SET tagged=1 WHERE image_path=(?);'
				cursor.execute(query, (complete_img_path,))

			con.commit()

		except:
			print("SQLITE ERROR 2")
			con.rollback()

	return "done"

@app.route('/train', methods=['POST'])
def train():
	face_classifier.train()
	return "done"

if __name__ == '__main__':
	app.debug = True
	app.run(host="0.0.0.0",port=4000)

# terminate called without an active exception