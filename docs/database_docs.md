Tagging is the process of giving names to individual faces.

- Table 1: (Name: class) Stores the class (in this case name of the face) and it's ID. There is an entry where ID=-1 and class=none upon creation of this table. This is the default class for a non-face image.
	- ID (Number): primary key
	- Class (Text)

- Table 2: (Name: all_images) Stores all complete_images and whether they are tagged or not.
	- image_path (Text): primary key
	- tagged (Bool): 0 -> Not tagged, 1-> Tagged

- Table 3: (Name: image_tags) Tagged images: This table contains the path to a complete image and the faces in it.
	- image_path (Text)
	- faces (Number): Only 1 face per entry. meaning for one complete_image with n faces, there would be n rows.

- Table 4: (Name: untagged_images) untagged images: This table contains path to individual face image and path to complete_image. Once all the faces are tagged for a particular image, then the tagged variable can be set to 1 in Table 1.
	- face_path (Text): PRIMARY KEY :path to individual cropped face image
	- complete_image_path (Text): path to corresponding complete image

- Table 5: (Name: tagged_faces): This table contains path to tagged face images and their respective class. This table will be used while training the classifier.
	- face_path (Text): primary key
	- class (Text)