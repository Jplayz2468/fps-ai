import os
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, UpSampling2D

def load_frames_from_all_subdirs(base_dir, max_side_length=420):
    frames = []
    for subdir, _, files in os.walk(base_dir):
        frame_files = sorted([f for f in files if f.endswith('.jpg')])
        for frame_file in frame_files:
            frame_path = os.path.join(subdir, frame_file)
            frame = cv2.imread(frame_path, cv2.IMREAD_COLOR)  # Ensure color image is loaded
            
            # Resize while maintaining aspect ratio
            height, width, _ = frame.shape  # Handle all three dimensions
            
            if height > width:
                new_height = max_side_length
                new_width = int(width * (max_side_length / height))
            else:
                new_width = max_side_length
                new_height = int(height * (max_side_length / width))
            
            frame = cv2.resize(frame, (new_width, new_height))
            
            # Pad the image to make it square
            delta_w = max_side_length - new_width
            delta_h = max_side_length - new_height
            top, bottom = delta_h // 2, delta_h - (delta_h // 2)
            left, right = delta_w // 2, delta_w - (delta_w // 2)
            color = [0, 0, 0]
            frame = cv2.copyMakeBorder(frame, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
            
            frames.append(frame)
    frames = np.array(frames)
    frames = frames.astype('float32') / 255.0
    return frames

def create_model(input_shape):
    model = Sequential([
        Conv2D(64, (3, 3), activation='relu', padding='same', input_shape=input_shape),
        MaxPooling2D((2, 2), padding='same'),
        Conv2D(32, (3, 3), activation='relu', padding='same'),
        MaxPooling2D((2, 2), padding='same'),
        Conv2D(16, (3, 3), activation='relu', padding='same'),
        UpSampling2D((2, 2)),
        Conv2D(32, (3, 3), activation='relu', padding='same'),
        UpSampling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu', padding='same'),
        Conv2D(3, (3, 3), activation='sigmoid', padding='same')  # Ensure 3 channels for RGB
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def preprocess(frames):
    X, y = [], []
    for i in range(1, len(frames) - 1):
        prev_frame = frames[i - 1]
        next_frame = frames[i + 1]
        target_frame = frames[i]
        X.append(np.concatenate((prev_frame, next_frame), axis=-1))
        y.append(target_frame)
    X = np.array(X)
    y = np.array(y)
    return X, y

def train_model(model, X, y, epochs=8, batch_size=32, steps_per_epoch=16):
    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.1, steps_per_epoch=steps_per_epoch)
    model.save('frame_interpolator2.h5')

if __name__ == "__main__":
    base_dir = 'frames'
    frames = load_frames_from_all_subdirs(base_dir)
    X, y = preprocess(frames)
    input_shape = X.shape[1:]
    model = create_model(input_shape)
    train_model(model, X, y)