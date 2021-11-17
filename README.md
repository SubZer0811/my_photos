# my_photos
## Introduction

This repository tries to mimic the searching of faces like in Apple photos and Google photos. A supervised learning strategy is used as opposed to the semi-supervised learning strategy used by Apple and Google.

## Setup Environment
Make sure to setup an environment before doing anything with this repository for the sake of maintaining dependencies and not installing or uninstalling unwanted modules.
- Create the environment:
```
virtualenv face-detect
```
- Activate the environment:
```
source face-detect/bin/activate
```
- Install dependencies:
```
pip3 install -r requirements.txt
```
- Deactivate environment:
```
deactivate
```

## Working
All the faces in an image are detected (using yolov3-tiny), cropped and saved.
All the copped face images are first classified by the [classifier](docs/classifier.md). Depending on whether the accuracy of the topmost prediction is greater than a certain threshold, the face image is made to be tagged by the user.

## Database and Classifier
Details of the database can be found [here](docs/database_docs.md).<br>
Details of the classifier can be found [here](docs/classifier.md).