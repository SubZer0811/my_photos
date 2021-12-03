import streamlit as st, cv2, os, numpy as np, pathlib, base64, sqlite3 as sl, db, utils

con = sl.connect(db.DB_PATH)
cursor = con.cursor()
st.set_page_config( layout="wide", page_title="My Photos")

CURRENT_PAGE = "home"

def img_to_bytes(img_path):
	img_bytes = pathlib.Path(img_path).read_bytes()
	encoded = base64.b64encode(img_bytes).decode()
	return f"data:image/png;base64,{encoded}"

def main_page():

	global CURRENT_PAGE

	if CURRENT_PAGE == "home":

		button_place = st.empty()
		if button_place.button('Tagging'):
			CURRENT_PAGE = "tagging"
			tagging()
			button_place.button('Back')
		
		st.title("My Photos")
		search_word = st.text_input("Search")
		uploaded_files = st.file_uploader("Choose image file(s)", type=[".png", ".jpg", ".jpeg", ".gif", ".tiff"], accept_multiple_files=True)

		for file in uploaded_files:
			# Convert the file to an opencv image.
			file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
			opencv_image = cv2.imdecode(file_bytes, 1)

			# Now do something with the image! For example, let's display it:
			st.image(opencv_image, channels="BGR")
			filename = f'./images/{file.name}'
			cv2.imwrite(filename, opencv_image)
			utils.add_image(filename)
		# =============================================================================

		query = "SELECT DISTINCT image_path FROM all_images" if not search_word else f"SELECT DISTINCT image_path FROM class JOIN image_tags WHERE class.ID == image_tags.face and class.class LIKE '{search_word.lower()}%'";
		cursor.execute(query)
		images = cursor.fetchall()

		divs =[]
		for i in images:
			divs.append(
				f"""
				<div class="brick">
				<img src="{img_to_bytes(i[0])}" alt="{os.path.basename(i[0])}">
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

		#   <span class="close" style="right: 30px !important;>&times;</span>

		st.components.v1.html(html, height=2000, scrolling=True)

def tagging():

	# option = st.selectbox("Who is this?",('1', '2', '3', 'new person'))
	# if option=='new person':
	# 	new_person = st.text_input('What is their name?')
	# if st.button('Confirm'):
	# 	st.write(new_person if option=='new person' else option)
	classes = db.get_classes()
	class_names = [ class_name for class_name,id in classes ]
	class_names.remove('none')

	print(class_names)
	query = "SELECT face_path FROM untagged_images"
	cursor.execute(query)
	images = cursor.fetchall()

	options = [ f'<option value="{class_name}">' for class_name in class_names ]
	options = '\n'.join(options)
	print(options)

	divs =[]
	for i in images:
		divs.append(
			f"""
			<div class="brick">
			<img src="{img_to_bytes(i[0])}" alt="{os.path.basename(i[0])}">
			<input type="text" name="city" list="classes">
				 <datalist id="classes">
					{options}
				</datalist>
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
		</div>
		</body>
	</html>"""

	#   <span class="close" style="right: 30px !important;>&times;</span>

	st.components.v1.html(html, height=2000, scrolling=True)

main_page()