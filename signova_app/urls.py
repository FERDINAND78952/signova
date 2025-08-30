from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.static import serve
from django.conf import settings
import os
from . import views
from .payment import initiate_payment, payment_callback, payment_webhook

urlpatterns = [
    path('', views.index, name='index'),
    path('modern/', views.index, name='modern'),
    path('modern_landing/', views.modern_landing, name='modern_landing'),
    path('landing/', views.landing, name='landing'),
    path('translate/', views.translate, name='translate'),
    path('learn/', views.learn, name='learn'),
    path('modern_learn/', views.learn, name='modern_learn'),
    path('learning_module/', views.learning_module, name='learning_module'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/modern_landing/', template_name='modern_landing.html', redirect_field_name=None, http_method_names=['get', 'post']), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
    # API endpoints
    path('video_feed/', views.video_feed, name='video_feed'),
    path('start_camera/', views.start_camera, name='start_camera'),
    path('health/', views.health_check, name='health_check'),
    path('stop_camera/', views.stop_camera, name='stop_camera'),
    path('clear_sentence/', views.clear_sentence, name='clear_sentence'),
    path('speak_sentence/', views.speak_sentence, name='speak_sentence'),
    path('get_recognized_signs/', views.get_recognized_signs, name='get_recognized_signs'),
    path('set_language/', views.set_language, name='set_language'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    
    # Video serving endpoint
    path('video/<str:video_name>/', views.serve_video, name='video'),
    
    # Payment endpoints
    path('payment/', initiate_payment, name='payment'),
    path('payment/success/', payment_callback, name='payment_success'),
    path('payment/webhook/', payment_webhook, name='payment_webhook')
]