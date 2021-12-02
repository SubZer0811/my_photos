import streamlit as st
import cv2, os
import numpy as np
import pathlib, base64
import sqlite3 as sl
import db
# import tensorflow
# import utils

con = sl.connect(db.DB_PATH)
cursor = con.cursor()

def img_to_bytes(img_path):
	img_bytes = pathlib.Path(img_path).read_bytes()
	encoded = base64.b64encode(img_bytes).decode()
	return f"data:image/png;base64,{encoded}"

st.set_page_config( layout="wide", page_title="My Photos")

st.title("My Photos")
search_word = st.text_input("Search")
uploaded_files = st.file_uploader("Choose image file(s)", type=[".png", ".jpg", ".jpeg", ".gif", ".tiff"], accept_multiple_files=True)


for file in uploaded_files:
	# Convert the file to an opencv image.
	file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
	opencv_image = cv2.imdecode(file_bytes, 1)

	# Now do something with the image! For example, let's display it:
	st.image(opencv_image, channels="BGR")
	dir = os.getcwd()
	filename = f'{dir}/images/{file.name}'
	cv2.imwrite(filename, opencv_image)
	utils.add_image(filename)
# =============================================================================

images = os.listdir("images")
dir = os.getcwd()

divs = []

if search_word:
	query = f"SELECT DISTINCT image_path FROM class JOIN image_tags WHERE class.ID == image_tags.face and class.class LIKE '{search_word.lower()}%'";
	cursor.execute(query)
	images = cursor.fetchall()
	divs =[]
	for i in images:
		divs.append(
			f"""
			<div class="brick">
			<img src="{img_to_bytes(f"{i[0]}")}">
			</div>
			"""
		)

else:

	for i in images:
		divs.append(
			f"""
			<div class="brick">
			<img src="{img_to_bytes(f"images/{i}")}">
			</div>
			"""
		)

divs = "\n".join(divs)

with open("css/labs.css") as FIN:
		css0 = FIN.read()

with open("css/masonry.css") as FIN:
		css1 = FIN.read()

with open("css/img_enlarge.css") as FIN:
		css2 = FIN.read()

with open("js/script.js") as FIN:
		script = FIN.read()

html = f"""<html>
	<base target="_blank" />
	<head>
		<style> {css0} </style>
		<style> {css1} </style>
		<style> {css2} </style>
	</head>
	<body style="background-color: rgb(14, 17, 23)">
	<h1 style="color: black"> <?php echo getcwd(); ?> </h1>
	<div class="masonry">
	{divs}
	<div id="myModal" class="modal">
  <span class="close">&times;</span>
  <img class="modal-content" id="img01">
  <div id="caption"></div>
</div>
<script> {script} </script>
	</div>
	</body>
</html>"""

st.components.v1.html(html, height=2400, scrolling=True)
