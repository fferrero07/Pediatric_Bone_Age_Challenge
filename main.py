from keras.applications.inception_v3 import InceptionV3
# from keras import backend as K
from keras.layers import Flatten, Dense, Input
from keras.models import Model
from keras.optimizers import Adam, RMSprop
# from keras.preprocessing import image
from six.moves import cPickle
import keras
import matplotlib.pyplot as plt
import numpy as np
import os

np.random.seed(1671)  # for reproducibility
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# network and training
EPOCHS = 3
BATCH_SIZE = 32
VERBOSE = 1
NB_CLASSES = 10   # number of outputs = number of digits
# OPTIMIZER = Adam()
OPTIMIZER = RMSprop()
N_HIDDEN = 128
VALIDATION_SPLIT = 0.2  # how much TRAIN is reserved for VALIDATION
DROPOUT = 0.3

# Load data
print('...loading training data')
f = open((os.path.join(__location__, 'data.pkl')), 'rb')
x = cPickle.load(f)
f.close()

f = open((os.path.join(__location__, 'data_age.pkl')), 'rb')
y = cPickle.load(f)
f.close()

x = np.asarray(x, dtype=np.float32)
y = np.asarray(y)

x /= 255.

x_final = []
y_final = []

# Shuffle images and split into train, validation and test sets
random_no = np.random.choice(x.shape[0], size=x.shape[0], replace=False)
for i in random_no:
    x_final.append(x[i, :, :, :])
    y_final.append(y[i])

x_final = np.asarray(x_final)
y_final = np.asarray(y_final)


k = 2  # Decides split count
x_test = x_final[:k, :, :, :]
y_test = y_final[:k]
x_valid = x_final[k:2 * k, :, :, :]
y_valid = y_final[k:2 * k]
x_train = x_final[2 * k:, :, :, :]
y_train = y_final[2 * k:]

print('x_train shape:' + str(x_train.shape))
print('y_train shape:' + str(y_train.shape))
print('x_valid shape:' + str(x_valid.shape))
print('y_valid shape:' + str(y_valid.shape))
print('x_test shape:' + str(x_test.shape))
print('y_test shape:' + str(y_test.shape))

# Using InceptionV3 with pretrained weights from Imagenet
base_model = InceptionV3(weights='imagenet', include_top=False)
input = Input(shape=(224, 224, 3))
output_vgg16 = base_model(input)
x = Flatten()(output_vgg16)
x = Dense(512, activation='relu')(x)
predictions = Dense(1)(x)

model = Model(inputs=input, outputs=predictions)

model.compile(
    optimizer=OPTIMIZER,
    loss='categorical_crossentropy',
    metrics=['MAE', 'accuracy']
)

# Save weights after every epoch
checkpoint = keras.callbacks.ModelCheckpoint(
    filepath='weights/weights.{epoch:02d}-{val_loss:.2f}.hdf5',
    save_weights_only=True,
    period=1)

history = model.fit(
    x_train, y_train,
    batch_size=BATCH_SIZE,
    epochs=EPOCHS,
    verbose=VERBOSE,
    validation_split=VALIDATION_SPLIT,
    validation_data=(x_valid, y_valid),
    callbacks=[checkpoint]
)

model.save_weights("model.h5")

score = model.evaluate(x_test, y_test, batch_size=BATCH_SIZE, verbose=VERBOSE)
print('\nTest loss:', score[0])
print('Test MAE:', score[1])
print('Test accuracy:', score[2])

# list all data in history
print(history.history.keys())
# summarize history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

with open('history.pkl', 'wb') as f:
    cPickle.dump(history.history, f)
f.close()
