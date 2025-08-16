import os
import sys
import time
import threading
import copy
import cv2 as cv
import numpy as np
import pyttsx3
import mediapipe as mp
import secrets
from datetime import datetime, timedelta
from collections import deque, Counter
from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Import from app3.py
from app3 import (
    KeyPointClassifier, PointHistoryClassifier, CvFpsCalc, AudioTranslator,
    SentenceRecorder, calc_bounding_rect, calc_landmark_list, pre_process_landmark,
    pre_process_point_history, draw_landmarks, draw_bounding_rect, draw_info_text,
    draw_point_history, draw_info, draw_sentence_info
)

# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signova.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.email}>'

# Progress model for tracking user learning
class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sign_name = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    practice_count = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref=db.backref('progress', lazy=True))

# Global variables
camera = None
processing_thread = None
should_stop = False
frame_buffer = None
frame_lock = threading.Lock()
recognized_signs = []
signs_lock = threading.Lock()
audio_translator = None
sentence_recorder = None

# Video paths for learning module
VIDEO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
VIDEO_FILES = {
    'hello': os.path.join(VIDEO_DIR, 'Hello.mp4'),
    'how_are_you': os.path.join(VIDEO_DIR, 'HowAreYou.mp4'),
    'forget': os.path.join(VIDEO_DIR, 'Forget.mp4'),
    'remember': os.path.join(VIDEO_DIR, 'Remember.mp4'),
    'i_want': os.path.join(VIDEO_DIR, 'Iwant.mp4'),
    'my_name_is': os.path.join(VIDEO_DIR, 'MyNameIs.mp4'),
    'thank_you': os.path.join(VIDEO_DIR, 'ThankYou.mp4'),
    'same_to_you': os.path.join(VIDEO_DIR, 'SameToYou.mp4'),
    'you': os.path.join(VIDEO_DIR, 'You.mp4')
}

# Login required decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Optimize database query with specific columns only
        user = User.query.options(db.load_only(User.id, User.first_name, User.last_name, User.password)).filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            # Store minimal data in session
            session['user_id'] = user.id
            session['first_name'] = user.first_name
            session['last_name'] = user.last_name
            
            # Update last login time in a separate thread to avoid blocking
            def update_login_time(user_id):
                with app.app_context():
                    user = User.query.get(user_id)
                    if user:
                        user.last_login = datetime.utcnow()
                        db.session.commit()
            
            threading.Thread(target=update_login_time, args=(user.id,)).start()
            
            # Set session expiry if remember me is not checked
            if not remember:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(hours=1)
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form data
        if not all([first_name, last_name, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
        
        # Check if user already exists - optimize query to only check email
        existing_user = db.session.query(User.id).filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        # Create new user with optimized password hashing
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Main routes
@app.route('/')
def index():
    return render_template('signova_landing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route('/original')
def original_index():
    return render_template('index.html')

@app.route('/modern')
def modern_index():
    return render_template('modern_index.html')

@app.route('/landing')
def landing():
    return render_template('signova_landing.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user data
    user = User.query.get(session['user_id'])
    
    # Get user progress
    progress = Progress.query.filter_by(user_id=user.id).all()
    
    # Calculate stats
    signs_learned = len([p for p in progress if p.completed])
    total_practice = sum(p.practice_count for p in progress)
    
    return render_template('dashboard.html', 
                           current_user=user, 
                           signs_learned=signs_learned,
                           total_practice=total_practice)

@app.route('/learning_module')
@login_required
def learning_module():
    # Get user data
    user = User.query.get(session['user_id'])
    
    # Get user progress data for learning module
    progress_data = Progress.query.filter_by(user_id=session['user_id']).all()
    
    return render_template('learning_module.html', user=user, progress_data=progress_data)

@app.route('/learn')
def learn():
    return render_template('learn.html', videos=list(VIDEO_FILES.keys()))

@app.route('/modern/learn')
def modern_learn():
    return render_template('modern_learn.html', videos=list(VIDEO_FILES.keys()))

@app.route('/translate')
def translate():
    return render_template('translate.html')

@app.route('/modern/translate')
def modern_translate():
    return render_template('modern_translate.html')

@app.route('/video/<video_name>')
def video(video_name):
    if video_name in VIDEO_FILES:
        video_path = VIDEO_FILES[video_name]
        def generate_video():
            cap = cv.VideoCapture(video_path)
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break
                ret, buffer = cv.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                time.sleep(0.03)  # Control frame rate
            cap.release()
        return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return "Video not found", 404

@app.route('/video_feed')
def video_feed():
    def generate():
        global frame_buffer
        while True:
            with frame_lock:
                if frame_buffer is not None:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer + b'\r\n')
            time.sleep(0.03)  # Control frame rate
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_camera')
def start_camera():
    global camera, processing_thread, should_stop, audio_translator, sentence_recorder
    
    if camera is not None or (processing_thread is not None and processing_thread.is_alive()):
        return jsonify({"status": "Camera already running"})
    
    should_stop = False
    camera = cv.VideoCapture(0)  # Use default camera
    camera.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Initialize audio translator and sentence recorder
    audio_translator = AudioTranslator(rate=150)
    sentence_recorder = SentenceRecorder(audio_translator)
    
    # Start processing in a separate thread
    processing_thread = threading.Thread(target=process_camera_feed)
    processing_thread.daemon = True
    processing_thread.start()
    
    return jsonify({"status": "Camera started"})

@app.route('/stop_camera')
def stop_camera():
    global camera, should_stop, processing_thread
    
    should_stop = True
    if processing_thread is not None:
        processing_thread.join(timeout=1.0)
    
    if camera is not None:
        camera.release()
        camera = None
    
    return jsonify({"status": "Camera stopped"})

@app.route('/get_recognized_signs')
def get_recognized_signs():
    global recognized_signs
    language = request.args.get('language', 'english')
    
    with signs_lock:
        signs = recognized_signs.copy()
        current_sentence = sentence_recorder.get_current_sentence() if sentence_recorder else ""
        translated_sentence = ""
        
        if sentence_recorder and current_sentence:
            translated_sentence = sentence_recorder.get_translation(current_sentence, language)
        
        # Add confidence information for the latest sign
        confidence = 0
        if signs and len(signs) > 0:
            # In a real implementation, this would come from the model
            # Here we're simulating with a random high confidence
            confidence = round(max(75, min(99, 85 + np.random.randint(-10, 10))), 1)
    
    return jsonify({
        "signs": signs,
        "current_sentence": current_sentence,
        "translated_sentence": translated_sentence,
        "confidence": confidence,
        "language": language
    })

@app.route('/clear_sentence')
def clear_sentence():
    global sentence_recorder
    if sentence_recorder:
        sentence_recorder.clear_sentence()
    return jsonify({"status": "Sentence cleared"})

@app.route('/speak_sentence')
def speak_sentence():
    global sentence_recorder
    if sentence_recorder:
        sentence_recorder.speak_sentence()
    return jsonify({"status": "Speaking sentence"})

@app.route('/set_language', methods=['POST'])
def set_language():
    global sentence_recorder
    data = request.json
    language = data.get('language', 'english')
    
    if sentence_recorder:
        sentence_recorder.set_language(language)
        current_sentence = sentence_recorder.get_current_sentence()
        translated_sentence = sentence_recorder.get_translation(current_sentence, language)
        
        return jsonify({
            "status": "Language set to " + language,
            "current_sentence": current_sentence,
            "translated_sentence": translated_sentence
        })
    
    return jsonify({"status": "Error: Sentence recorder not initialized"})

@app.route('/get_translation')
def get_translation():
    global sentence_recorder
    language = request.args.get('language', 'english')
    
    if sentence_recorder:
        current_sentence = sentence_recorder.get_current_sentence()
        translated_sentence = sentence_recorder.get_translation(current_sentence, language)
        
        return jsonify({
            "current_sentence": current_sentence,
            "translated_sentence": translated_sentence,
            "language": language
        })
    
    return jsonify({"status": "Error: Sentence recorder not initialized"})

def process_camera_feed():
    global camera, should_stop, frame_buffer, recognized_signs, audio_translator, sentence_recorder

    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )
    
    # Initialize classifiers
    keypoint_classifier = KeyPointClassifier()
    point_history_classifier = PointHistoryClassifier()
    cv_fps_calc = CvFpsCalc(buffer_len=10)
    
    # Load labels
    import csv
    with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
        keypoint_classifier_labels = [row[0] for row in csv.reader(f)]
    
    with open('model/point_history_classifier/point_history_classifier_label.csv', encoding='utf-8-sig') as f:
        point_history_classifier_labels = [row[0] for row in csv.reader(f)]
    
    # Initialize variables
    point_history = deque([[0, 0] for _ in range(16)], maxlen=16)
    last_gesture_time = time.time()
    
    while not should_stop:
        if camera is None:
            break
            
        ret, image = camera.read()
        if not ret:
            continue
        
        fps = cv_fps_calc.get()
        
        # Flip the image horizontally for a later selfie-view display
        image = cv.flip(image, 1)
        debug_image = copy.deepcopy(image)
        
        # Convert the BGR image to RGB
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        
        # Process the image and detect hands
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        
        # Process hand landmarks if detected
        if results.multi_hand_landmarks:
            last_gesture_time = time.time()
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                # Calculate bounding rectangle
                brect = calc_bounding_rect(debug_image, hand_landmarks)
                
                # Landmark calculation
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)
                
                # Conversion to relative coordinates / normalized coordinates
                pre_processed_landmark_list = pre_process_landmark(landmark_list)
                pre_processed_point_history_list = pre_process_point_history(debug_image, point_history)
                
                # Classification
                try:
                    hand_sign_id, confidence = keypoint_classifier(pre_processed_landmark_list)
                    hand_sign_id = int(hand_sign_id)
                    if not 0 <= hand_sign_id < len(keypoint_classifier_labels):
                        hand_sign_id = 0  # Default to "None"
                except Exception as e:
                    print(f"Classification error: {e}")
                    hand_sign_id = 0
                    confidence = 0.0
                
                # Update point history
                if confidence > 0.7 and len(landmark_list) > 8:
                    point_history.append(landmark_list[8] if hand_sign_id == 2 else [0, 0])
                else:
                    point_history.append([0, 0])
                
                # Add recognized sign to the list if confidence is high enough
                if 0 <= hand_sign_id < len(keypoint_classifier_labels):
                    recognized_word = keypoint_classifier_labels[hand_sign_id]
                    if recognized_word not in ["None", "Point"]:
                        if sentence_recorder.add_word(recognized_word):
                            with signs_lock:
                                recognized_signs.append(recognized_word)
                                # Keep only the last 10 signs
                                if len(recognized_signs) > 10:
                                    recognized_signs.pop(0)
                
                # Draw landmarks and information
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
        
        # Draw point history and other information
        debug_image = draw_point_history(debug_image, point_history)
        debug_image = draw_info(debug_image, fps, 0, 0)
        debug_image = draw_sentence_info(
            debug_image, 
            sentence_recorder, 
            last_gesture_time,
            audio_translator.is_speaking
        )
        
        # Convert the image to JPEG
        ret, buffer = cv.imencode('.jpg', debug_image)
        if ret:
            with frame_lock:
                frame_buffer = buffer.tobytes()
    
    # Clean up
    if hands:
        hands.close()
    if camera:
        camera.release()

# Create database tables
def create_tables():
    db.create_all()

# Initialize database with some default data
def init_db():
    # Check if database is already initialized
    if User.query.first() is None:
        # Create admin user
        admin = User(
            first_name='Admin',
            last_name='User',
            email='admin@signova.com',
            password=generate_password_hash('admin123')
        )
        db.session.add(admin)
        
        # Create demo user
        demo = User(
            first_name='Demo',
            last_name='User',
            email='demo@signova.com',
            password=generate_password_hash('demo123')
        )
        db.session.add(demo)
        
        # Add initial progress data for demo user
        for video in VIDEO_FILES.keys():
            progress = Progress(
                user_id=2,  # demo user id
                sign_name=video,
                completed=video in ['hello', 'thank_you'],
                completed_at=datetime.utcnow() if video in ['hello', 'thank_you'] else None,
                practice_count=5 if video in ['hello', 'thank_you'] else 0
            )
            db.session.add(progress)
        
        db.session.commit()
        print('Database initialized with default data')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_db()
    app.run(debug=True, threaded=True)