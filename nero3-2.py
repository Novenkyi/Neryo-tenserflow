

pip install tensorflow

pip install keras

from google.colab import files

uploaded = files.upload()

from google.colab import drive
drive.mount('/content/gdrive')

!unzip sixClasses_T124_200.zip

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow import keras
from keras import optimizers
# %matplotlib inline
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from tensorflow.keras import utils
import pathlib
import os, shutil
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import glob
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image

classes = ['baso', 'blas', 'eosi', 'lymph', 'mono', 'neut']

zip_dir = 'sixClasses_T124_200'
base_dir = os.path.join(os.path.dirname(zip_dir), 'sixClasses_T124_200')

for c in classes:
  img_path = os.path.join(base_dir, c)
  images = glob.glob(img_path + '/*.jpg')
  print("{}: {} изображений".format(c, len(images)))
  train, val = images[:round(len(images)*0.8)], images[round(len(images)*0.8):]

  for t in train:
    if not os.path.exists(os.path.join(base_dir, 'train', c)):
      os.makedirs(os.path.join(base_dir, 'train', c))
    shutil.move(t, os.path.join(base_dir, 'train', c))

  for v in val:
    if not os.path.exists(os.path.join(base_dir, 'val', c)):
      os.makedirs(os.path.join(base_dir, 'val', c))
    shutil.move(v, os.path.join(base_dir, 'val', c))

train_dir = os.path.join(base_dir, 'train')
val_dir = os.path.join(base_dir, 'val')

#train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'val')

train_lymph_dir = os.path.join(train_dir, 'lymph')
train_blst_dir = os.path.join(train_dir, 'blasts')
train_mon_dir = os.path.join(train_dir, 'mono')
train_baso_dir = os.path.join(train_dir, 'baso')
train_eosi_dir = os.path.join(train_dir, 'eosi')
train_neut_dir = os.path.join(train_dir, 'neut')
validation_lymph_dir = os.path.join(validation_dir, 'lymph')
validation_blst_dir = os.path.join(validation_dir, 'blas')
validation_mon_dir = os.path.join(validation_dir, 'mono')
validation_baso_dir = os.path.join(validation_dir, 'baso')
validation_eosi_dir = os.path.join(validation_dir, 'eosi')
validation_neut_dir = os.path.join(validation_dir, 'neut')

num_lymph_tr = len(os.listdir(train_lymph_dir))
num_blst_tr = len(os.listdir(train_blst_dir))
num_mon_tr = len(os.listdir(train_mon_dir))
num_baso_tr = len(os.listdir(train_baso_dir))
num_eosi_tr = len(os.listdir(train_eosi_dir))
num_neut_tr = len(os.listdir(train_neut_dir))


num_lymph_val = len(os.listdir(validation_lymph_dir))
num_blst_val = len(os.listdir(validation_blst_dir))
num_mon_val = len(os.listdir(validation_mon_dir))
num_baso_val = len(os.listdir(validation_baso_dir))
num_eosi_val = len(os.listdir(validation_eosi_dir))
num_neut_val = len(os.listdir(validation_neut_dir))

total_train = num_mon_tr + num_blst_tr + num_lymph_tr + num_neut_tr + num_eosi_tr + num_baso_tr
total_val = num_lymph_val + num_blst_val + num_mon_val + num_neut_val + num_eosi_val + num_baso_val

BATCH_SIZE = 16
IMG_SHAPE = 200

train_image_generator = ImageDataGenerator(rescale=1./255)
validation_image_generator = ImageDataGenerator(rescale=1./255)

train_data_gen = train_image_generator.flow_from_directory(batch_size=BATCH_SIZE,
                                                          directory=train_dir,
                                                          shuffle=True,
                                                          target_size=(IMG_SHAPE,IMG_SHAPE),
                                                          class_mode='categorical')

val_data_gen = validation_image_generator.flow_from_directory(batch_size=BATCH_SIZE,
                                                              directory=val_dir,
                                                              shuffle=False,
                                                              target_size=(IMG_SHAPE,IMG_SHAPE),
                                                              class_mode='categorical')

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(IMG_SHAPE, IMG_SHAPE, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),

    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),

    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),

    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),

    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(3, activation='softmax')
])

model.compile(optimizer = 'adam',
              loss = tf.keras.losses.CategoricalCrossentropy(),
              metrics=['accuracy'])

model.summary()

#history = model.fit_generator(
#    train_data_gen,
#    steps_per_epoch=int(np.ceil(total_train / float(BATCH_SIZE))),
#    epochs=EPOCHS,
#    validation_data=val_data_gen,
#    validation_steps=int(np.ceil(total_val / float(BATCH_SIZE)))
#)

EPOCHS = 5
history = model.fit_generator(
    train_data_gen,
    steps_per_epoch=int(np.ceil(total_train / float(BATCH_SIZE))),
    epochs=EPOCHS,
    validation_data=val_data_gen,
    validation_steps=int(np.ceil(total_val / float(BATCH_SIZE)))
)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(EPOCHS)

plt.figure(figsize=(8,8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Точность на обучении')
plt.plot(epochs_range, val_acc, label='Точность на валидации')
plt.legend(loc='lower right')
plt.title('Точность на обучающих и валидационных данных')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Потери на обучении')
plt.plot(epochs_range, val_loss, label='Потери на валидации')
plt.legend(loc='upper right')
plt.title('Потери на обучающих и валидационных данных')
plt.savefig('./foo.png')
plt.show()

json_file = 'model2.json'
model_json = model.to_json()

with open(json_file, 'w') as f:
  f.write(model_json)

img_path = "3classes_classification/val/monocytes/f0000095.jpg"
img = image.load_img(img_path, target_size=(200, 200))
plt.imshow(img)
plt.show()

img_path = "3classes_classification/val/monocytes/f0000331.jpg"
img = image.load_img(img_path, target_size=(200, 200))

img_array = image.img_to_array(img)
img_batch = np.expand_dims(img_array, axis=0)


y_prob = model.predict(img_batch)
print(y_prob)
y_classes = y_prob.argmax(axis=-1)
print(y_classes)
