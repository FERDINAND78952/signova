import numpy as np
import tensorflow as tf
import csv
import os

class KeyPointClassifier:
    def __init__(
        self,
        model_path='model/keypoint_classifier/keypoint_classifier.tflite',
        num_threads=1,
    ):
        self.interpreter = tf.lite.Interpreter(
            model_path=model_path,
            num_threads=num_threads
        )
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Load labels
        label_path = os.path.join(os.path.dirname(model_path), 'keypoint_classifier_label.csv')
        with open(label_path, encoding='utf-8-sig') as f:
            self.labels = [row[0] for row in csv.reader(f)]

    def __call__(self, landmark_list):
        input_details_tensor_index = self.input_details[0]['index']
        self.interpreter.set_tensor(
            input_details_tensor_index,
            np.array([landmark_list], dtype=np.float32))
        self.interpreter.invoke()
        
        output_details_tensor_index = self.output_details[0]['index']
        result = self.interpreter.get_tensor(output_details_tensor_index)
        result_index = np.argmax(np.squeeze(result))
        
        confidence = np.max(np.squeeze(result))
        return result_index, confidence

    def save_landmark(self, landmark_list, label, save_path='model/keypoint_classifier/keypoint.csv'):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'a', newline='') as f:
            writer = csv.writer(f)
            row = [label] + landmark_list
            writer.writerow(row)