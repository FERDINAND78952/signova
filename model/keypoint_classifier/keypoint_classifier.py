import numpy as np
import csv
import os

# Check if we're on Render
RENDER_DEPLOYMENT = os.environ.get('RENDER_EXTERNAL_HOSTNAME') is not None

# Conditionally import TensorFlow
if not RENDER_DEPLOYMENT:
    try:
        import tensorflow as tf
    except ImportError:
        print("TensorFlow not available")
else:
    tf = None

class KeyPointClassifier:
    def __init__(
        self,
        model_path='model/keypoint_classifier/keypoint_classifier.tflite',
        num_threads=1,
    ):
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        
        # Only initialize TensorFlow if not on Render
        if not RENDER_DEPLOYMENT and tf is not None:
            try:
                self.interpreter = tf.lite.Interpreter(
                    model_path=model_path,
                    num_threads=num_threads
                )
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
            except Exception as e:
                print(f"Error initializing TensorFlow: {e}")
        
        # Load labels
        try:
            label_path = os.path.join(os.path.dirname(model_path), 'keypoint_classifier_label.csv')
            with open(label_path, encoding='utf-8-sig') as f:
                self.labels = [row[0] for row in csv.reader(f)]
        except Exception as e:
            print(f"Error loading labels: {e}")
            self.labels = []

    def __call__(self, landmark_list):
        # If we're on Render or TensorFlow is not available, return a default value
        if RENDER_DEPLOYMENT or self.interpreter is None:
            return 0  # Return default gesture (e.g., "Open" or "Unknown")
            
        try:
            input_details_tensor_index = self.input_details[0]['index']
            self.interpreter.set_tensor(
                input_details_tensor_index,
                np.array([landmark_list], dtype=np.float32))
            self.interpreter.invoke()

            output_details_tensor_index = self.output_details[0]['index']
            result = self.interpreter.get_tensor(output_details_tensor_index)
            result_index = np.argmax(np.squeeze(result))
            return result_index
        except Exception as e:
            print(f"Error in KeyPointClassifier inference: {e}")
            return 0  # Return default gesture on error

    def save_landmark(self, landmark_list, label, save_path='model/keypoint_classifier/keypoint.csv'):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'a', newline='') as f:
            writer = csv.writer(f)
            row = [label] + landmark_list
            writer.writerow(row)