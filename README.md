# Signova - Sign Language Translator

## Overview
Signova is a web application that translates sign language using computer vision and machine learning. It includes features for learning sign language, real-time translation, and tracking user progress.

## Migration from Flask to Django
This project has been migrated from Flask to Django for improved scalability, security, and maintainability.

## Features
- Real-time sign language translation
- Learning modules for sign language
- User progress tracking
- Subscription tiers (Free, Advanced, Pro)
- Mobile Money payment integration
- Kinyarwanda signs integration

## Tech Stack
- Django 5.0
- TensorFlow
- OpenCV
- MediaPipe
- MySQL/MariaDB (via XAMPP)
- HTML/CSS/JavaScript

## Local Development Setup

### Prerequisites
- Python 3.10+
- XAMPP (for MySQL database)
- Git

### Installation Steps

1. Clone the repository:
   ```
   git clone <repository-url>
   cd signova-web
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements_django.txt
   ```

4. Set up the database in XAMPP:
   - Start XAMPP and ensure MySQL service is running
   - Create a database named `signova_db`
   - Update the database settings in `signova/settings.py` to use MySQL

5. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Access the application at http://localhost:8000

## Deployment on Render

1. Create a Render account at https://render.com

2. Connect your GitHub repository to Render

3. Create a new Web Service with the following settings:
   - Build Command: `pip install -r requirements_django.txt`
   - Start Command: `gunicorn signova.wsgi:application`

4. Add environment variables:
   - `DJANGO_SETTINGS_MODULE`: signova.settings
   - `SECRET_KEY`: (generate a secure random key)
   - `RENDER`: true

5. Create a MySQL database on Render or use an external database service

6. Add the database connection string as an environment variable:
   - `DATABASE_URL`: (your database connection string)

7. Deploy the application

## License
This project is licensed under the MIT License - see the LICENSE file for details.