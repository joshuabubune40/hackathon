import os
import numpy as np
import cv2
import keras
from tensorflow.keras.utils import Sequence
from tensorflow.keras.layers import Input, Dense, Reshape, Flatten, Conv2D, Conv2DTranspose
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

class ImageDataGenerator(Sequence):
    def __init__(self, folder, batch_size, img_size, **kwargs):
        self.folder = folder
        self.batch_size = batch_size
        self.img_size = img_size
        self.image_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(('.jpg', '.jpeg', '.png'))]
        self.on_epoch_end()
        super().__init__(**kwargs)  # Call the base class constructor

    def __len__(self):
        return int(np.floor(len(self.image_files) / self.batch_size))

    def __getitem__(self, index):
        batch_files = self.image_files[index * self.batch_size:(index + 1) * self.batch_size]
        images = [cv2.imread(f, cv2.IMREAD_GRAYSCALE) for f in batch_files]
        images = [cv2.resize(img, self.img_size) for img in images]
        images = np.array(images).astype('float32') / 255.0
        images = np.expand_dims(images, axis=-1)
        return images, images

    def on_epoch_end(self):
        np.random.shuffle(self.image_files)

# Define parameters
img_size = (200, 200)
batch_size = 32
data_dir = 'path/to/your/resized/images'

# Create data generators
train_generator = ImageDataGenerator(data_dir, batch_size, img_size)
test_generator = ImageDataGenerator(data_dir, batch_size, img_size)  # Assuming you use the same dir for testing

# Creating the Autoencoder Model
input_shape = (200, 200, 1)
latent_dim = 128

# Encoder
inputs = Input(shape=input_shape)
x = Conv2D(32, kernel_size=3, strides=2, activation='relu', padding='same')(inputs)
x = Conv2D(64, kernel_size=3, strides=2, activation='relu', padding='same')(x)
x = Flatten()(x)
latent_repr = Dense(latent_dim)(x)

# Decoder
x = Dense(50 * 50 * 64)(latent_repr)
x = Reshape((50, 50, 64))(x)
x = Conv2DTranspose(32, kernel_size=3, strides=2, activation='relu', padding='same')(x)
decoded = Conv2DTranspose(1, kernel_size=3, strides=2, activation='sigmoid', padding='same')(x)

# Autoencoder model
autoencoder = Model(inputs, decoded)

# Compiling the Autoencoder Model
autoencoder.compile(optimizer=Adam(learning_rate=0.0002), loss='binary_crossentropy')

# Adding Early Stopping
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Training the Autoencoder
epochs = 20

history = autoencoder.fit(train_generator, validation_data=test_generator, epochs=epochs, callbacks=[early_stopping])

autoencoder.save('denoising_autoencoder_200.keras')
