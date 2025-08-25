import os
import numpy as np
import csv

# Check if we're on Render deployment
RENDER_DEPLOYMENT = os.environ.get('RENDER_EXTERNAL_HOSTNAME') is not None

# Conditionally import TensorFlow
tf = None
if not RENDER_DEPLOYMENT:
    try:
        import tensorflow as tf
    except ImportError:
        print("TensorFlow not available")
        pass

class PointHistoryClassifier(object):
    def __init__(
        self,
        model_path='model/point_history_classifier/point_history_classifier.tflite',
        score_th=0.5,
        invalid_value=0,
        num_threads=1,
    ):
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.score_th = score_th
        self.invalid_value = invalid_value
        
        # Only initialize TensorFlow if not on Render
        if not RENDER_DEPLOYMENT and tf is not None:
            try:
                self.interpreter = tf.lite.Interpreter(model_path=model_path,
                                                   num_threads=num_threads)
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
            except Exception as e:
                print(f"Error initializing TensorFlow: {e}")

    def __call__(self, point_history):
        # If we're on Render or TensorFlow is not available, return a default value
        if RENDER_DEPLOYMENT or self.interpreter is None:
            return 0  # Return default gesture (e.g., "Open" or "Unknown")
            
        try:
            input_details_tensor_index = self.input_details[0]['index']
            self.interpreter.set_tensor(
                input_details_tensor_index,
                np.array([point_history], dtype=np.float32))
            self.interpreter.invoke()
            output_details_tensor_index = self.output_details[0]['index']
            result = self.interpreter.get_tensor(output_details_tensor_index)
            result_index = np.argmax(np.squeeze(result))
            # Check confidence threshold
            if np.squeeze(result)[result_index] < self.score_th:
                result_index = self.invalid_value
            return result_index
        except Exception as e:
            print(f"Error in PointHistoryClassifier inference: {e}")
            return 0  # Return default gesture on error

    def save_point_history(self, point_history, label, save_path='dataset/point_history.csv'):
        """Append new point history with label to dataset."""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'a', newline='') as f:
            writer = csv.writer(f)
            row = [label] + point_history
            writer.writerow(row)
