# GUI
## Pages

- [ ] Homepage:
	- Display all images.
	- Navbar to have upload button and search bar.

- [ ] Upload Page: Upload image(s).
	- get image path and call `add_image()`. This function should create faces images and store in `./faces`.
	- After uploading, redirect to Tagging faces page.

- [ ] Tagging faces: Tagging refers to labeling here.
	- implement the function `tag_image()` in the following way:
		- with `complete_image_path` we get all face_path (path to individual face images).
		- Classify all the face images. Display all face images with top accuracy less than `CLASSIFY_THRESH`.
		- Make user tag all these faces.
		- Submit.
		- If no faces to be tagged, then redirect to homepage.
		- Retrain the classifier when some **threshold** is reached.

- [ ] Search: Search for a face(s).
	- Given face class, find class id (would be a set).
	- Display all images containing class id.