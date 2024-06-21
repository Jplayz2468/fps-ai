# double_fps.py
import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# Ensure the required library is installed
os.system('./setup.sh')

def load_model_and_weights(model_path, weights_path):
    # Manually compile the model after loading
    model = load_model(model_path, compile=False)
    if os.path.exists(weights_path):
        model.load_weights(weights_path)
    model.compile(optimizer='adam', loss='mse')  # Re-compile the model
    return model

def preprocess_frame(frame):
    frame = frame / 255.0
    return frame

def generate_intermediate_frame(model, prev_frame, next_frame):
    if prev_frame.shape != next_frame.shape:
        raise ValueError("The input frames must have the same dimensions.")
    
    prev_frame = preprocess_frame(prev_frame)
    next_frame = preprocess_frame(next_frame)
    
    input_data = np.concatenate((prev_frame, next_frame), axis=-1)
    input_data = np.expand_dims(input_data, axis=0)
    
    generated_frame = model.predict(input_data)[0]
    generated_frame = (generated_frame * 255).astype(np.uint8)
    
    return generated_frame

def double_video_fps(model, input_video_path, output_video_path):
    cap = cv2.VideoCapture(input_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps * 2, (width, height))

    ret, prev_frame = cap.read()
    frame_count = 0
    while ret:
        out.write(prev_frame)
        ret, next_frame = cap.read()
        if not ret:
            break
        generated_frame = generate_intermediate_frame(model, prev_frame, next_frame)
        out.write(generated_frame)
        prev_frame = next_frame
        frame_count += 1
    
    cap.release()
    out.release()
    print(f"Processed {frame_count} frames and saved to {output_video_path}")

if __name__ == "__main__":
    model_path = 'frame_interpolator.h5'
    weights_path = 'checkpoint.weights.h5'
    input_video_path = 'input.mp4'
    output_video_path = 'output_video_3.mp4'
    
    model = load_model_and_weights(model_path, weights_path)
    double_video_fps(model, input_video_path, output_video_path)