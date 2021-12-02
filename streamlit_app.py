import streamlit as st
import cv2, os
import numpy as np
import pathlib, base64
import main

def img_to_bytes(img_path):
	img_bytes = pathlib.Path(img_path).read_bytes()
	encoded = base64.b64encode(img_bytes).decode()
	return f"data:image/png;base64,{encoded}"

st.set_page_config( layout="wide", page_title="My Photos")

st.title("My Photos")


search_query = st.text_input("Enter your search query")
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
	
# =============================================================================

images = os.listdir("images")
dir = os.getcwd()

divs = []

for i in images:

  divs.append(
      f"""
      <div class="brick">
      <a href="">
      <img src="{img_to_bytes(f"images/{i}")}">
      </a>
      </div>
      """
  )

divs = "\n".join(divs)

with open("css/labs.css") as FIN:
		css0 = FIN.read()

with open("css/masonry.css") as FIN:
		css1 = FIN.read()


html = """
<html>
	<base target="_blank" />
	<head>
		<style> %s </style>
		<style> %s </style>
	</head>
	<body style="background-color: rgb(14, 17, 23)">
	<h1 style="color: black"> <?php echo getcwd(); ?> </h1>
	<div class="masonry">
	%s
	</div>
	</body>
</html>
""" % (
		css0,
		css1,
		divs,
)

st.components.v1.html(html, height=2400, scrolling=True)
