import os
import time
import threading
import cv2 as cv
import numpy as np
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate

# Import from app3.py (will need to be refactored for Django)
from app3 import (
    KeyPointClassifier, PointHistoryClassifier, CvFpsCalc, AudioTranslator,
    SentenceRecorder, calc_bounding_rect, calc_landmark_list, pre_process_landmark,
    pre_process_point_history, draw_landmarks, draw_bounding_rect, draw_info_text,
    draw_point_history, draw_info, draw_sentence_info
)

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
                cv.putText(frame, "Camera Off", (200, 240), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
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
    
    if camera is None:
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
        
        return JsonResponse({'status': 'success', 'message': 'Camera started'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Camera already running'})

# Stop camera API endpoint
@csrf_exempt
def stop_camera(request):
    global camera, processing_thread, should_stop
    
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
    
    if sentence_recorder is not None:
        sentence_recorder.current_sentence = []
        return JsonResponse({'status': 'success', 'message': 'Sentence cleared'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Sentence recorder not initialized'})

# Speak sentence API endpoint
@csrf_exempt
def speak_sentence(request):
    global sentence_recorder
    
    if sentence_recorder is not None:
        sentence_recorder.speak_sentence()
        return JsonResponse({'status': 'success', 'message': 'Speaking sentence'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Sentence recorder not initialized'})

# Get recognized signs API endpoint
@csrf_exempt
def get_recognized_signs(request):
    global sentence_recorder, recognized_signs, signs_lock
    
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

# Set language API endpoint
@csrf_exempt
def set_language(request):
    global sentence_recorder
    
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
