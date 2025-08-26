#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import copy
import csv
import itertools
import os
import time
from collections import deque, Counter
import threading

import cv2 as cv
import mediapipe as mp
import numpy as np
import pyttsx3

# Check if we're on Render deployment
import os
RENDER_DEPLOYMENT = (os.environ.get('RENDER_EXTERNAL_HOSTNAME') is not None or 
                    os.environ.get('RENDER', 'False').lower() == 'true' or
                    os.environ.get('SIGNOVA_DISABLE_ML', 'False').lower() == 'true')

# Conditionally import TensorFlow
tf = None
if not RENDER_DEPLOYMENT:
    try:
        import tensorflow as tf
    except ImportError:
        print("TensorFlow not available")

# Import classifier classes
from model.keypoint_classifier.keypoint_classifier import KeyPointClassifier
from model.point_history_classifier.point_history_classifier import PointHistoryClassifier

class CvFpsCalc(object):
    def __init__(self, buffer_len=1):
        self._start_tick = cv.getTickCount()
        self._freq = 1000.0 / cv.getTickFrequency()
        self._difftimes = deque(maxlen=buffer_len)

    def get(self):
        current_tick = cv.getTickCount()
        different_time = (current_tick - self._start_tick) * self._freq
        self._start_tick = current_tick
        self._difftimes.append(different_time)
        fps = 1000.0 / (sum(self._difftimes) / len(self._difftimes))
        return round(fps, 2)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=780)
    parser.add_argument('--use_static_image_mode', action='store_true')
    parser.add_argument("--min_detection_confidence", type=float, default=0.7)
    parser.add_argument("--min_tracking_confidence", type=int, default=0.5)
    parser.add_argument("--speech_rate", type=int, default=150)
    parser.add_argument("--voice", type=str, default=None)
    return parser.parse_args()

class AudioTranslator:
    def __init__(self, rate=150, voice_id=None):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        if voice_id:
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if voice_id in voice.id:
                    self.engine.setProperty('voice', voice.id)
                    break
        self.is_speaking = False
        self.last_spoken_time = 0
        self.cooldown = 1.2  # Reduced cooldown for more responsive feedback
        self.speech_queue = deque(maxlen=5)  # Queue to manage multiple speech requests
        self.speech_thread = None
        self.active = True

    def speak(self, text):
        current_time = time.time()
        if not self.is_speaking and (current_time - self.last_spoken_time) > self.cooldown:
            self.is_speaking = True
            self.engine.say(text)
            if not self.speech_thread or not self.speech_thread.is_alive():
                self.speech_thread = threading.Thread(target=self._run_engine)
                self.speech_thread.daemon = True  # Make thread daemon so it exits when main program exits
                self.speech_thread.start()
        else:
            # Add to queue if we're currently speaking
            if text not in self.speech_queue:
                self.speech_queue.append(text)

    def _run_engine(self):
        try:
            self.engine.runAndWait()
        except RuntimeError:
            # Handle potential runtime errors from pyttsx3
            pass
        self.is_speaking = False
        self.last_spoken_time = time.time()
        
        # Process any queued speech items
        if self.speech_queue and self.active:
            next_text = self.speech_queue.popleft()
            self.is_speaking = True
            self.engine.say(next_text)
            self._run_engine()

    def stop(self):
        self.active = False
        self.engine.stop()
        self.speech_queue.clear()

class SentenceRecorder:
    def __init__(self, audio_translator):
        self.current_sentence = []
        self.sentence_history = []
        self.last_add_time = 0
        self.word_delay = 1.2  # Reduced delay for more responsive experience
        self.phrase_delay = 0.6  # Reduced delay for phrases
        self.audio = audio_translator
        self.current_language = 'english'  # Default language
        self.recent_signs = deque(maxlen=10)  # Track recent signs for better recognition
        self.confidence_threshold = 0.7  # Confidence threshold for sign recognition
        self.sign_counter = Counter()  # Count occurrences of signs for stability
        
        # English to Kinyarwanda translations
        self.english_to_kinyarwanda = {
            "Open": "Gufungura", 
            "Close": "Gufunga", 
            "Pointer": "Kwerekana", 
            "OK": "Nibyo",
            "A": "A", 
            "B": "B", 
            "C": "C", 
            "D": "D",
            "Good": "Byiza", 
            "Hello": "Muraho", 
            "Thank you": "Murakoze",
            "I am": "Ndi", 
            "Milk": "Amata", 
            "Tea": "Icyayi", 
            "Bread": "Ifunga",
            "Sorghum": "Uburo", 
            "Water": "Amazi", 
            "I know": "Ndabizi",
            "I don't understand": "Simbyumva", 
            "I want": "Nshaka", 
            "No": "Nta",
            "Hello well": "Muraho Neza", 
            "Thank you very much": "Murakoze Cyane",
            "I am Rwandan": "Ndi Umunyarwanda", 
            "I want water": "Ndashaka Amazi"
        }
        
        # RSL sign to English translations
        self.word_translations = {
            "Open": "Open", 
            "Close": "Close", 
            "Pointer": "Pointer", 
            "OK": "OK",
            "ASL A": "A", 
            "ASL B": "B", 
            "ASL C": "C", 
            "ASL D": "D",
            "Byiza": "Good", 
            "Muraho": "Hello", 
            "Murakoze": "Thank you",
            "Ndi": "I am", 
            "Amata": "Milk", 
            "Icyayi": "Tea", 
            "Ifunga": "Bread",
            "Uburo": "Sorghum", 
            "Amazi": "Water", 
            "Ndabizi": "I know",
            "Simbyumva": "I don't understand", 
            "Nshaka": "I want", 
            "Nta": "No",
            "Muraho_Neza": "Hello well", 
            "Murakoze_Cyane": "Thank you very much",
            "Ndi_Umunyarwanda": "I am Rwandan", 
            "Ndashaka_Amazi": "I want water",
            # Additional Kinyarwanda signs from the dataset
            "Akarere": "District",
            "Akazi": "Work",
            "Amakuru": "News",
            "Bayi": "Bye",
            "Bibi": "Grandmother",
            "Igihugu": "Country",
            "Neza": "Good",
            "Nyarugenge": "Nyarugenge",
            "Oya": "No",
            "Papa": "Father",
            "Umujyi wa kigali": "Kigali City",
            "Umurenge": "Sector",
            "Urakoze": "Thank you",
            "Yego": "Yes"
        }
        
        # Load Kinyarwanda signs data
        self.load_kinyarwanda_signs()

    def add_word(self, word, confidence=0.9):
        current_time = time.time()
        delay = self.phrase_delay if '_' in word else self.word_delay
        
        # Track recent signs for better recognition
        self.recent_signs.append(word)
        self.sign_counter[word] += 1
        
        # Only add words that meet confidence threshold and appear consistently
        if confidence >= self.confidence_threshold and current_time - self.last_add_time > delay:
            # Check if this sign has appeared multiple times recently for stability
            if self.sign_counter[word] >= 2 or confidence > 0.85:
                if '_' in word:
                    for w in word.split('_'):
                        display = self.word_translations.get(w, w)
                        self.current_sentence.append(display)
                        self.audio.speak(display)
                else:
                    display = self.word_translations.get(word, word)
                    self.current_sentence.append(display)
                    # Provide visual feedback that word was recognized
                    print(f"Recognized: {display} (confidence: {confidence:.2f})")
                    self.audio.speak(display)
                
                # Reset counter for this word after adding it
                self.sign_counter[word] = 0
                self.last_add_time = current_time
            return True
        return False
        
    def set_language(self, language):
        """Set the current language for translation"""
        self.current_language = language
        
    def get_translation(self, sentence, target_language):
        """Translate a sentence to the target language"""
        if not sentence or target_language == 'english':
            return sentence
            
        if target_language == 'kinyarwanda':
            words = sentence.split(' ')
            translated_words = [self.english_to_kinyarwanda.get(word, word) for word in words]
            return ' '.join(translated_words)
            
        return sentence

    def clear_sentence(self):
        if self.current_sentence:
            self.sentence_history.append(' '.join(self.current_sentence))
            self.current_sentence = []

    def backspace(self):
        if self.current_sentence:
            self.current_sentence.pop()

    def get_current_sentence(self):
        return ' '.join(self.current_sentence)

    def get_full_history(self):
        return '\n'.join(self.sentence_history)

    def speak_sentence(self):
        sentence = self.get_current_sentence()
        if sentence:
            self.audio.speak(sentence)
            
    def load_kinyarwanda_signs(self):
        """Load Kinyarwanda signs data from the dataset directory"""
        try:
            # Path to Kinyarwanda signs dataset
            kinyarwanda_signs_path = os.path.join('model', 'KinyarwandaSigns', 'Data')
            
            # Check if directory exists
            if os.path.exists(kinyarwanda_signs_path) and os.path.isdir(kinyarwanda_signs_path):
                print(f"Loading Kinyarwanda signs from {kinyarwanda_signs_path}")
                
                # Get all sign categories (folders)
                sign_categories = [d for d in os.listdir(kinyarwanda_signs_path) 
                                if os.path.isdir(os.path.join(kinyarwanda_signs_path, d))]
                
                # Add each sign category to translations
                for category in sign_categories:
                    # Convert folder name to proper case for display
                    display_name = category.replace('_', ' ').title()
                    
                    # Add to translations if not already present
                    if category not in self.word_translations:
                        self.word_translations[category] = display_name
                        
                        # Also add to Kinyarwanda translations if appropriate
                        if display_name not in self.english_to_kinyarwanda:
                            self.english_to_kinyarwanda[display_name] = category
                
                print(f"Successfully loaded {len(sign_categories)} Kinyarwanda sign categories")
            else:
                print(f"Warning: Kinyarwanda signs directory not found at {kinyarwanda_signs_path}")
        except Exception as e:
            print(f"Error loading Kinyarwanda signs: {str(e)}")
            # Continue without failing if there's an error loading signs

def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_array = np.empty((0, 2), int)
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_array = np.append(landmark_array, [np.array((landmark_x, landmark_y))], axis=0)
    x, y, w, h = cv.boundingRect(landmark_array)
    return [x, y, x + w, y + h]

def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    return [[min(int(landmark.x * image_width), image_width - 1),
             min(int(landmark.y * image_height), image_height - 1)]
            for landmark in landmarks.landmark]

def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)
    base_x, base_y = temp_landmark_list[0][0], temp_landmark_list[0][1]
    for landmark_point in temp_landmark_list:
        landmark_point[0] -= base_x
        landmark_point[1] -= base_y
    temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))
    max_value = max(map(abs, temp_landmark_list))
    return [n / max_value if max_value != 0 else 0 for n in temp_landmark_list]

def pre_process_point_history(image, point_history):
    """Improved version with empty history handling"""
    if not point_history or all(p == [0, 0] for p in point_history):
        return [0.0] * 32  # Return array of zeros matching expected input size
    
    image_width, image_height = image.shape[1], image.shape[0]
    temp_point_history = copy.deepcopy(point_history)
    
    # Find first non-zero point for base reference
    base_x, base_y = 0, 0
    for point in temp_point_history:
        if point[0] != 0 and point[1] != 0:
            base_x, base_y = point[0], point[1]
            break
    
    # Normalize points
    for point in temp_point_history:
        point[0] = (point[0] - base_x) / image_width if image_width > 0 else 0.0
        point[1] = (point[1] - base_y) / image_height if image_height > 0 else 0.0
    
    return list(itertools.chain.from_iterable(temp_point_history))

def logging_csv(number, mode, landmark_list, point_history_list):
    if mode == 1 and (0 <= number <= 9):
        with open('model/keypoint_classifier/keypoint.csv', 'a', newline="") as f:
            csv.writer(f).writerow([number, *landmark_list])
    elif mode == 2 and (0 <= number <= 9):
        with open('model/point_history_classifier/point_history.csv', 'a', newline="") as f:
            csv.writer(f).writerow([number, *point_history_list])

def draw_landmarks(image, landmark_point):
    if len(landmark_point) > 0:
        # Draw connections
        connections = [
            (2, 3), (3, 4), (5, 6), (6, 7), (7, 8),
            (9, 10), (10, 11), (11, 12), (13, 14),
            (14, 15), (15, 16), (17, 18), (18, 19),
            (19, 20), (0, 1), (1, 2), (2, 5), (5, 9),
            (9, 13), (13, 17), (17, 0)
        ]
        for start, end in connections:
            cv.line(image, tuple(landmark_point[start]), tuple(landmark_point[end]), (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[start]), tuple(landmark_point[end]), (255, 255, 255), 2)
        
        # Draw keypoints
        for idx, landmark in enumerate(landmark_point):
            radius = 8 if idx in [4, 8, 12, 16, 20] else 5
            cv.circle(image, tuple(landmark), radius, (255, 255, 255), -1)
            cv.circle(image, tuple(landmark), radius, (0, 0, 0), 1)
    return image

def draw_bounding_rect(use_brect, image, brect):
    if use_brect:
        cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]), (0, 0, 0), 1)
    return image

def draw_info_text(image, brect, handedness, hand_sign_text, finger_gesture_text):
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22), (0, 0, 0), -1)
    info_text = f"{handedness.classification[0].label[0:]}:{hand_sign_text}" if hand_sign_text else handedness.classification[0].label[0:]
    cv.putText(image, info_text, (brect[0] + 5, brect[1] - 4),
               cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)
    
    if finger_gesture_text:
        cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                   cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4, cv.LINE_AA)
        cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                   cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv.LINE_AA)
    return image

def draw_point_history(image, point_history):
    for idx, point in enumerate(point_history):
        if point[0] != 0 and point[1] != 0:
            cv.circle(image, tuple(point), 1 + int(idx / 2), (152, 251, 152), 2)
    return image

def draw_info(image, fps, mode, number):
    cv.putText(image, "FPS:" + str(fps), (10, 30), cv.FONT_HERSHEY_SIMPLEX,
               1.0, (0, 0, 0), 4, cv.LINE_AA)
    cv.putText(image, "FPS:" + str(fps), (10, 30), cv.FONT_HERSHEY_SIMPLEX,
               1.0, (255, 255, 255), 2, cv.LINE_AA)
    
    mode_string = ["Logging Key Point", "Logging Point History"]
    if 1 <= mode <= 2:
        cv.putText(image, "MODE:" + mode_string[mode - 1], (10, 90),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)
        if 0 <= number <= 9:
            cv.putText(image, "NUM:" + str(number), (10, 110),
                       cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)
    return image

def draw_sentence_info(image, sentence_recorder, last_gesture_time, is_audio_playing=False):
    text_color = (255, 255, 255)
    bg_color = (50, 50, 50)
    highlight_color = (0, 255, 255)
    instruction_color = (200, 200, 200)
    y_start = image.shape[0] - 150
    line_height = 25
    
    # Create overlay
    overlay = image.copy()
    cv.rectangle(overlay, (0, y_start - 25), (image.shape[1], image.shape[0]), bg_color, -1)
    cv.addWeighted(overlay, 0.7, image, 0.3, 0, image)
    
    # Draw current sentence
    current_sentence = sentence_recorder.get_current_sentence()
    if current_sentence:
        if time.time() - last_gesture_time < 0.5:
            text_size = cv.getTextSize(f"Sentence: {current_sentence}", 
                                     cv.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv.rectangle(image, (5, y_start - text_size[1] - 5),
                       (10 + text_size[0], y_start + 5), highlight_color, 2)
        
        cv.putText(image, f"Sentence: {current_sentence}", 
                  (10, y_start), 
                  cv.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2, cv.LINE_AA)
    
    # Draw instructions
    instructions = [
        "Space: Clear/Gusiba | Backspace: Delete/Gusiba ijambo",
        "'s': Size | 'a': Speak Sentence | 'v': List Voices",
        "'m': Muraho | 't': Murakoze | 'l': Toggle Language",
        "1-9: Amata(1), Icyayi(2), Ifunga(3), Uburo(4), Amazi(5)"
    ]
    
    if time.time() - last_gesture_time < 5:
        for i, instruction in enumerate(instructions):
            fade_factor = max(0.3, 1 - (time.time() - last_gesture_time - 3)/2)
            if fade_factor > 0.3:
                color = tuple(int(c * fade_factor) for c in instruction_color)
                cv.putText(image, instruction, 
                          (10, y_start + (i+1)*line_height), 
                          cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv.LINE_AA)
    
    # Audio indicator
    if is_audio_playing:
        cv.circle(image, (30, 70), 10, (0, 255, 0), -1)
        cv.putText(image, "Audio", (45, 75), 
                  cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
    
    return image

def select_mode(key, mode):
    number = -1
    if key == 110:  # n
        mode = 0
    elif key == 107:  # k
        mode = 1
    elif key == 104:  # h
        mode = 2
    elif key == 108:  # l
        mode = 3 if mode != 3 else 0
        
    if 48 <= key <= 57:  # 0-9
        number = key - 48
        
    gesture_map = {
        ord('o'): 0, ord('c'): 1, ord('p'): 2, ord('k'): 3,
        ord('a'): 4, ord('b'): 5, ord('d'): 6, ord('g'): 7
    }
    if key in gesture_map:
        number = gesture_map[key]
        mode = 1
        
    kinyarwanda_map = {
        ord('m'): 8, ord('t'): 9, ord('i'): 10,
        ord('1'): 11, ord('2'): 12, ord('3'): 13, ord('4'): 14,
        ord('5'): 15, ord('6'): 16, ord('7'): 17, ord('8'): 18, ord('9'): 19
    }
    if key in kinyarwanda_map:
        number = kinyarwanda_map[key]
        mode = 1
        
    return number, mode

def main():
    args = get_args()
    cap = cv.VideoCapture(args.device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, args.height)
    
    audio_translator = AudioTranslator(rate=args.speech_rate, voice_id=args.voice)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=args.use_static_image_mode,
        max_num_hands=2,
        min_detection_confidence=args.min_detection_confidence,
        min_tracking_confidence=args.min_tracking_confidence,
    )

    # Initialize classifiers
    keypoint_classifier = KeyPointClassifier()
    point_history_classifier = PointHistoryClassifier()
    sentence_recorder = SentenceRecorder(audio_translator)
    cv_fps_calc = CvFpsCalc(buffer_len=10)

    # Load labels
    with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
        keypoint_classifier_labels = [row[0] for row in csv.reader(f)]
    
    with open('model/point_history_classifier/point_history_classifier_label.csv', encoding='utf-8-sig') as f:
        point_history_classifier_labels = [row[0] for row in csv.reader(f)]

    # Initialize variables with proper defaults
    mode = 0
    number = 0
    display_scale = 1.0
    last_gesture_time = time.time()
    point_history = deque([[0, 0] for _ in range(16)], maxlen=16)  # Initialize with zeros
    audio_indicator_time = 0

    while True:
        fps = cv_fps_calc.get()
        key = cv.waitKey(10)
        
        if key == 27:  # ESC
            break
        elif key == ord(' '):
            sentence_recorder.clear_sentence()
        elif key == 8:  # Backspace
            sentence_recorder.backspace()
        elif key == ord('s'):
            display_scale = 1.0 if display_scale != 1.0 else 0.75
        elif key == ord('a'):
            sentence_recorder.speak_sentence()
            audio_indicator_time = time.time()
        elif key == ord('v'):
            voices = audio_translator.engine.getProperty('voices')
            print("Available voices:")
            for i, voice in enumerate(voices):
                print(f"{i}: {voice.name} ({voice.id})")
        else:
            new_number, new_mode = select_mode(key, mode)
            if new_number != -1:
                number = new_number
            if new_mode is not None:
                mode = new_mode

        ret, image = cap.read()
        if not ret:
            break
            
        image = cv.resize(image, (int(image.shape[1] * display_scale), 
                         int(image.shape[0] * display_scale)))
        image = cv.flip(image, 1)
        debug_image = copy.deepcopy(image)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        if results.multi_hand_landmarks:
            last_gesture_time = time.time()
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                results.multi_handedness):
                brect = calc_bounding_rect(debug_image, hand_landmarks)
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)
                pre_processed_landmark_list = pre_process_landmark(landmark_list)
                pre_processed_point_history_list = pre_process_point_history(debug_image, point_history)
                
                # Get classification results with error handling
                try:
                    hand_sign_id, confidence = keypoint_classifier(pre_processed_landmark_list)
                    hand_sign_id = int(hand_sign_id)
                    if not 0 <= hand_sign_id < len(keypoint_classifier_labels):
                        hand_sign_id = 0  # Default to "None"
                except Exception as e:
                    print(f"Classification error: {e}")
                    hand_sign_id = 0
                    confidence = 0.0
                
                # Only update point history if confidence is high enough
                if confidence > 0.7 and len(landmark_list) > 8:
                    point_history.append(landmark_list[8] if hand_sign_id == 2 else [0, 0])
                else:
                    point_history.append([0, 0])

                if 0 <= hand_sign_id < len(keypoint_classifier_labels):
                    recognized_word = keypoint_classifier_labels[hand_sign_id]
                    if recognized_word not in ["None", "Point"]:
                        if sentence_recorder.add_word(recognized_word):
                            audio_indicator_time = time.time()

                debug_image = draw_bounding_rect(True, debug_image, brect)
                debug_image = draw_landmarks(debug_image, landmark_list)
                debug_image = draw_info_text(
                    debug_image,
                    brect,
                    handedness,
                    keypoint_classifier_labels[hand_sign_id],
                    "",
                )
        else:
            point_history.append([0, 0])  # Append zeros when no hands detected

        debug_image = draw_point_history(debug_image, point_history)
        debug_image = draw_info(debug_image, fps, mode, number)
        debug_image = draw_sentence_info(
            debug_image, 
            sentence_recorder, 
            last_gesture_time,
            audio_translator.is_speaking or (time.time() - audio_indicator_time < 0.5)
        )
        
        cv.imshow('Hand Gesture Recognition', debug_image)

    cap.release()
    cv.destroyAllWindows()
    audio_translator.stop()

if __name__ == '__main__':
    main()