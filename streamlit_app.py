import streamlit as st
import cv2, os
import numpy as np

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
	cv2.imwrite(f'{dir}/images/{file.name}', opencv_image)
# =============================================================================


# Start the app in wide-mode
# st.set_page_config( layout="wide", page_title="my photos" )


# Starting random state
# random_state = 78

# Number of results to return
# top_k = 12


title_element = st.empty()
info_element = st.empty()

# if st.button("💥 Randomize image"):
#     m = sys.maxsize
#     random_state = random.randint(0, 2 ** 32 - 1)


# names = pd.read_csv("data/img_keys.csv")
# random_sample = names.sample(n=1, random_state=random_state)["unsplashID"]

# vector_idx = int(random_sample.index.values[0])
# target_unsplash_id = random_sample.values[0]

# url = f"https://unsplash.com/photos/{target_unsplash_id}"
title = f"CLIP+Unsplash image similarity"
info = '''
Explore the latent image space of CLIP via top 100K Unsplash photos.
Made with 💙 by [@metasemantic](https://twitter.com/metasemantic?lang=en) 
[[github](https://github.com/thoppe/streamlit-CLIP-Unsplash-explorer)]
'''.strip()
title_element.title(title)
info_element.write(info)

url = "http://localhost:8000/top_match"
# r = requests.get(url, params={"i": vector_idx, "top_k": top_k})
# matching_ids = r.json()

# Uses CSS Masonry from 
# https://w3bits.com/labs/css-masonry/

# unsplash_links = [target_unsplash_id,] + matching_ids

divs = [
    f"""
    <div class="brick">
    <a href="">
    <img src="https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg">
    </a>
    </div>
    """
    # for idx in unsplash_links
]
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
  <body>
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
