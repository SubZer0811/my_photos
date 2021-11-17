# Face Classifier
## Model
```
__________________________________________
Layer (type)                 Output Shape 
==========================================
resnet50 (Functional)        (None, 2048) 
__________________________________________
dense (Dense)                (None, N)    
==========================================
__________________________________________
```
- `resnet50` is the main classifier that is being used. The `resnet50` layer uses `imagenet`'s trained weights and is frozen that is, the `resnet50` layer is not trainable. `resnet50` has an output of 2048 dimensional feature vector.
- The final layer has `N` neurons where `N` stands for the total number of classes (total number of face classes). This is the only layer that is trained.
- This process of using `resnet50` as a feature extractor and changing the last layer is called transfer learning.
- The input the network is a 224x224x3 image. The dimensions of the image can be changed by altering the `IMAGE_RESIZE` constant in `face_classifier.py`.