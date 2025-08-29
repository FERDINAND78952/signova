import os
import time
import threading
import csv
import copy
from collections import deque
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.views.static import serve

# Conditionally import ML dependencies
ML_IMPORTS_AVAILABLE = False

# Check if ML features should be disabled
is_render = os.environ.get('RENDER', 'False').lower() == 'true'
disable_tensorflow = os.environ.get('DISABLE_TENSORFLOW', 'False').lower() == 'true'
disable_ml = os.environ.get('SIGNOVA_DISABLE_ML', 'False').lower() == 'true'

# Skip ML imports if we're on Render or if ML is explicitly disabled
if not (is_render or disable_tensorflow or disable_ml):
    try:
        # Import lightweight dependencies first
        import cv2 as cv
        import numpy as np
        
        # Try to import MediaPipe (less memory intensive than TensorFlow)
        import mediapipe as mp
        
        # Only import TensorFlow if explicitly allowed
        try:
            # Set TensorFlow log level to suppress warnings
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
            # Limit TensorFlow memory usage
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
            # Import application modules
            from app3 import (
                KeyPointClassifier, PointHistoryClassifier, CvFpsCalc, AudioTranslator,
                SentenceRecorder, calc_bounding_rect, calc_landmark_list, pre_process_landmark,
                pre_process_point_history, draw_landmarks, draw_bounding_rect, draw_info_text,
                draw_point_history, draw_info, draw_sentence_info
            )
            ML_IMPORTS_AVAILABLE = True
        except ImportError:
            # TensorFlow not available, but we might still have OpenCV and MediaPipe
            pass
    except ImportError:
        # For web deployment without ML dependencies
        pass

# Global variables for video processing
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
VIDEO_DIR = os.path.join(settings.MEDIA_ROOT, 'videos')
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

# Home page view
def index(request):
    # Check if we're on Render and add a small delay to prevent worker timeout
    import os
    if os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
        # Add a small delay to prevent worker timeout during initial load
        time.sleep(0.1)
    return render(request, 'modern_index.html')

# Modern landing page view
def modern_landing(request):
    return render(request, 'modern_landing.html')

# Landing page view
def landing(request):
    return render(request, 'signova_landing.html')

# Translate page view
def translate(request):
    return render(request, 'modern_translate.html')

# Learn page view
def learn(request):
    videos = [os.path.splitext(os.path.basename(v))[0] for v in VIDEO_FILES.values()]
    return render(request, 'modern_learn.html', {'videos': videos})

# Learning module view
def learning_module(request):
    return render(request, 'learning_module.html')

# Dashboard view
@login_required
def dashboard(request):
    # Pass the current user to the template context
    context = {
        'current_user': request.user
    }
    return render(request, 'dashboard.html', context)

# Signup view
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Account created for {username}!')
                    return redirect('index')
                else:
                    messages.error(request, 'Authentication failed after account creation. Please try logging in.')
                    return redirect('login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

# Video feed generator function
def gen_frames():
    global frame_buffer, frame_lock
    
    if not ML_IMPORTS_AVAILABLE:
        # If ML imports are not available, return a static message frame
        while True:
            # Create a blank frame with a message
            import numpy as np
            try:
                import cv2 as cv
                frame = np.zeros((480, 640, 3), np.uint8)
                cv.putText(frame, "ML features not available in web mode", (50, 240), 
                          cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                ret, buffer = cv.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
            except ImportError:
                # If even cv2 is not available, return a simple error message
                frame_bytes = b'ML features not available in web mode'
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(1.0)  # Slow refresh rate for static message
    else:
        # Normal operation with ML imports
        while True:
            with frame_lock:
                if frame_buffer is not None:
                    frame = frame_buffer.copy()
                else:
                    # Create a blank frame if no frame is available
                    frame = np.zeros((480, 640, 3), np.uint8)
                    # Add helpful message on blank frame
                    cv.putText(frame, "Camera initializing...", (50, 240), cv.FONT_HERSHEY_SIMPLEX, 
                              1, (255, 255, 255), 2, cv.LINE_AA)
                    cv.putText(frame, "Please wait or check camera permissions", (50, 280), 
                              cv.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1, cv.LINE_AA)
            
            # Encode the frame as JPEG
            ret, buffer = cv.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.033)  # ~30 FPS

# Video feed view
def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

# Start camera API endpoint
@csrf_exempt
def start_camera(request):
    global camera, processing_thread, should_stop, audio_translator, sentence_recorder
    
    if not ML_IMPORTS_AVAILABLE:
        # Return a message indicating ML features are not available in web mode
        return JsonResponse({
            'status': 'error',
            'message': 'ML features are not available in web deployment mode'
        })
    
    if camera is None:
        try:
            camera = cv.VideoCapture(0)
            camera.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
            camera.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
            
            # Initialize audio and sentence recorder
            audio_translator = AudioTranslator(rate=150)
            sentence_recorder = SentenceRecorder(audio_translator)
            
            # Start processing thread
            should_stop = False
            processing_thread = threading.Thread(target=process_frames)
            processing_thread.daemon = True
            processing_thread.start()
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to initialize camera: {str(e)}'
            })
        
        return JsonResponse({'status': 'success', 'message': 'Camera started'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Camera already running'})

# Stop camera API endpoint
@csrf_exempt
def stop_camera(request):
    global camera, processing_thread, should_stop
    
    if not ML_IMPORTS_AVAILABLE:
        return JsonResponse({
            'status': 'error',
            'message': 'ML features are not available in web deployment mode'
        })
    
    if camera is not None:
        should_stop = True
        if processing_thread is not None:
            processing_thread.join(timeout=1.0)
        
        camera.release()
        camera = None
        
        return JsonResponse({'status': 'success', 'message': 'Camera stopped'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Camera not running'})

# Clear sentence API endpoint
@csrf_exempt
def clear_sentence(request):
    global sentence_recorder
    
    if not ML_IMPORTS_AVAILABLE:
        return JsonResponse({
            'status': 'error',
            'message': 'ML features are not available in web deployment mode'
        })
    
    if sentence_recorder is not None:
        sentence_recorder.current_sentence = []
        return JsonResponse({'status': 'success', 'message': 'Sentence cleared'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Sentence recorder not initialized'})

# Speak sentence API endpoint
@csrf_exempt
def speak_sentence(request):
    global sentence_recorder
    
    if not ML_IMPORTS_AVAILABLE:
        return JsonResponse({
            'status': 'error',
            'message': 'ML features are not available in web deployment mode'
        })
    
    if sentence_recorder is not None:
        sentence_recorder.speak_sentence()
        return JsonResponse({'status': 'success', 'message': 'Speaking sentence'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Sentence recorder not initialized'})

# Get recognized signs API endpoint
@csrf_exempt
def get_recognized_signs(request):
    global sentence_recorder, recognized_signs, signs_lock
    
    if not ML_IMPORTS_AVAILABLE:
        return JsonResponse({
            'status': 'error',
            'message': 'ML features are not available in web deployment mode'
        })
    
    if sentence_recorder is not None:
        with signs_lock:
            signs_copy = recognized_signs.copy() if recognized_signs else []
        
        return JsonResponse({
            'status': 'success',
            'signs': signs_copy,
            'current_sentence': sentence_recorder.get_current_sentence()
        })
    else:
        return JsonResponse({'status': 'error', 'message': 'Sentence recorder not initialized'})

# Health check endpoint for deployment monitoring
def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'Service is running'
    })

# Set language API endpoint
@csrf_exempt
def set_language(request):
    global sentence_recorder
    
    if not ML_IMPORTS_AVAILABLE:
        return JsonResponse({
            'status': 'error',
            'message': 'ML features are not available in web deployment mode'
        })
    
    if request.method == 'POST':
        language = request.POST.get('language', 'english')
        
        if sentence_recorder is not None:
            sentence_recorder.set_language(language)
            return JsonResponse({'status': 'success', 'message': f'Language set to {language}'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Sentence recorder not initialized'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# About page view
def about(request):
    return render(request, 'about.html')

# Contact page view
def contact(request):
    return render(request, 'contact.html')

# Terms of Service page view
def terms_of_service(request):
    return render(request, 'terms_of_service.html')

# Privacy Policy page view
def privacy_policy(request):
    return render(request, 'privacy_policy.html')

# Health check endpoint for Render
def health_check(request):
    """Simple health check endpoint for Render deployment monitoring"""
    return HttpResponse("OK", content_type="text/plain")

# Serve video files
def serve_video(request, video_name):
    # Map the video name to the actual file path
    video_path = None
    for key, path in VIDEO_FILES.items():
        if key == video_name.lower():
            video_path = path
            break
    
    if not video_path or not os.path.exists(video_path):
        # Return a 404 response if the video doesn't exist
        from django.http import Http404
        raise Http404(f"Video '{video_name}' not found")
    
    # Serve the video file
    return serve(request, os.path.basename(video_path), os.path.dirname(video_path))

# Process frames function for ML processing
def process_frames():
    global camera, frame_buffer, frame_lock, should_stop, recognized_signs, signs_lock, sentence_recorder
    
    if not ML_IMPORTS_AVAILABLE:
        return
    
    try:
        # Initialize MediaPipe hands module
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )
        
        # Initialize classifiers
        keypoint_classifier = KeyPointClassifier()
        point_history_classifier = PointHistoryClassifier()
        
        # Read labels
        with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
            keypoint_classifier_labels = [row[0] for row in csv.reader(f)]
        with open('model/point_history_classifier/point_history_classifier_label.csv', encoding='utf-8-sig') as f:
            point_history_classifier_labels = [row[0] for row in csv.reader(f)]
        
        # Initialize variables
        point_history = deque(maxlen=16)
        finger_gesture_history = deque(maxlen=16)
        
        while not should_stop:
            # Read frame from camera
            ret, frame = camera.read()
            if not ret:
                continue
            
            # Process frame with MediaPipe
            frame = cv.flip(frame, 1)  # Mirror display
            debug_image = copy.deepcopy(frame)
            
            # Convert to RGB for MediaPipe
            frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            
            # Update frame buffer with processed frame
            with frame_lock:
                frame_buffer = debug_image
            
            # Sleep to reduce CPU usage
            time.sleep(0.01)
    except Exception as e:
        print(f"Error in process_frames: {str(e)}")
    finally:
        if 'hands' in locals():
            hands.close()
