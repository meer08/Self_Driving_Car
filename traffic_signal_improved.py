# -*- coding: utf-8 -*-
"""Traffic Signal Improved.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Pc2tOrclkE9_VGRJW7eyjeBbyft4WHAK
"""

!git clone https://bitbucket.org/jadslim/german-traffic-signs

import numpy as np
import matplotlib.pyplot as plt
import keras
from keras.models import Sequential
from keras.layers import Dense
from tensorflow.keras.optimizers import Adam 
from keras.utils.np_utils import to_categorical
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.layers import Flatten, Dropout
import pickle
import random
import pandas as pd

np.random.seed(0)
with open('german-traffic-signs/train.p', 'rb') as f:
    train_data=pickle.load(f)
with open('german-traffic-signs/valid.p', 'rb') as f:
    val_data=pickle.load(f)
with open('german-traffic-signs/test.p', 'rb') as f:
    test_data=pickle.load(f)
X_train, y_train = train_data['features'], train_data['labels']
X_val, y_val= val_data['features'], val_data['labels']
X_test, y_test = test_data['features'], test_data['labels']

print(X_train.shape)
print(X_val.shape)
print(X_test.shape)

data=pd.read_csv('german-traffic-signs/signnames.csv')
print(data)

num_of_samples=[]
cols=5
num_classes=43
fig,axs =plt.subplots(nrows=num_classes, ncols=cols, figsize=(5,50))
fig.tight_layout()
for i in range(cols):
    for j,row in data.iterrows():
        x_selected=X_train[y_train==j]
        axs[j][i].imshow(x_selected[random.randint(0,(len(x_selected)-1)), :, :], cmap=plt.get_cmap('gray'))
        if i==2:
            axs[j][i].set_title(str(j)+"-"+row['SignName'])
            num_of_samples.append(len(x_selected))

print(num_of_samples)
plt.figure(figsize=(12,4))
plt.bar(range(0,num_classes), num_of_samples)
plt.title("Distribution of the train dataset")
plt.xlabel("class number")
plt.ylabel("number of images")
plt.show()

import cv2
plt.imshow(X_train[1076])
plt.axis("off")
print(X_train[1076].shape)
print(y_train[1076])
def grayscale(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img

img = grayscale(X_train[1076])
plt.imshow(img, cmap="gray")
plt.axis("off")
print(img.shape)

def equalize(img):
    img=cv2.equalizeHist(img)
    return img

img=equalize(img)
plt.imshow(img,cmap="gray")
plt.axis("off")
print(img.shape)

def preprocessing(img):
    img = grayscale(img)
    img = equalize(img)
    img = img/255
    return img

X_train = np.array(list(map(preprocessing, X_train)))
X_test = np.array(list(map(preprocessing, X_test)))
X_val = np.array(list(map(preprocessing, X_val)))

plt.imshow(X_train[random.randint(0,len(X_train))-1], cmap='gray')

plt.imshow(X_test[random.randint(0,len(X_test))-1], cmap='gray')

plt.imshow(X_val[random.randint(0,len(X_val))-1], cmap='gray')

print(X_train.shape)
print(X_test.shape)
print(X_val.shape)

X_train = X_train.reshape(34799,32,32, 1) #adding a depth of 1
X_test = X_test.reshape(12630,32,32,1)
X_val = X_val.reshape(4410,32,32,1)

from keras.preprocessing.image import ImageDataGenerator
 
datagen = ImageDataGenerator(width_shift_range=0.1,
                            height_shift_range=0.1,
                            zoom_range=0.2,
                            shear_range=0.1,
                            rotation_range=10.)
datagen.fit(X_train)

batches = datagen.flow(X_train, y_train, batch_size = 15)
X_batch, y_batch = next(batches)
 
fig, axs = plt.subplots(1, 15, figsize=(20, 5))
fig.tight_layout()
 
for i in range(15):
    axs[i].imshow(X_batch[i].reshape(32, 32))
    axs[i].axis("off")
 
print(X_batch.shape)

y_train = to_categorical(y_train, 43)
y_test = to_categorical(y_test, 43)
y_val = to_categorical(y_val, 43)

"""#STEP 2(b): IMPROVED MODEL
##CHANGES:


1.   Changing learning rate
2.   Increased Number of Filters
3.   Adding more Convolutional layers
4.   Data Augmentation. 
"""

def modified_model():
    model=Sequential()
    model.add(Conv2D(60,(5,5), input_shape = (32,32,1), activation='relu'))
    model.add(Conv2D(60,(5,5), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))

    model.add(Conv2D(30,(3,3), activation='relu'))
    model.add(Conv2D(30,(3,3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    #model.add(Dropout(0.5))

    model.add(Flatten())
    model.add(Dense(500,activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation='softmax'))
    model.compile(Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])
    return model

model=modified_model()
print(model.summary())

history = model.fit(datagen.flow(X_train,y_train,batch_size=50), steps_per_epoch = X_train.shape[0]/50, epochs=10, validation_data=(X_val,y_val), shuffle=1)

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.legend(['training', 'validation'])
plt.title('loss')
plt.xlabel('epochs')

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.legend(['training', 'validation'])
plt.title('accuracy')
plt.xlabel('epochs')

score = model.evaluate(X_test, y_test, verbose=0)
print('Test Score: ', score[0])
print('Test Accuracy', score[1])

"""#STEP 3: TESTING"""

#FETCH THE IMAGE
import requests
from PIL import Image

#url = 'https://c8.alamy.com/comp/G667W0/road-sign-speed-limit-30-kmh-zone-passau-bavaria-germany-G667W0.jpg'

#url = 'https://previews.123rf.com/images/bwylezich/bwylezich1608/bwylezich160800375/64914157-german-road-sign-slippery-road.jpg'

#url = 'https://previews.123rf.com/images/pejo/pejo0907/pejo090700003/5155701-german-traffic-sign-no-205-give-way.jpg'

url = 'https://c8.alamy.com/comp/J2MRAJ/german-road-sign-bicycles-crossing-J2MRAJ.jpg'

r = requests.get(url, stream=True)
img = Image.open(r.raw)
plt.imshow(img, cmap=plt.get_cmap('gray'))

#PREPROCESSING
img = np.asarray(img)
img = cv2.resize(img, (32, 32))
img = preprocessing(img)
plt.imshow(img, cmap = plt.get_cmap('gray'))
print(img.shape)

#RESHAPING
img = img.reshape(1, 32, 32, 1)

#TESTING
print("predicted sign: "+ str( np.argmax(model.predict(img), axis=-1) ))