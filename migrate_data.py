import os
import sys
import sqlite3
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signova.settings')
django.setup()

# Import Django models
from django.contrib.auth.models import User
from signova_app.models import Progress, Subscription
from django.utils import timezone

def migrate_users_from_sqlite():
    print("Starting migration of users from SQLite to Django...")
    
    # Connect to SQLite database
    sqlite_conn = sqlite3.connect('instance/signova.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get all users from SQLite
    sqlite_cursor.execute('SELECT id, first_name, last_name, email, password, created_at FROM user')
    users = sqlite_cursor.fetchall()
    
    # Create users in Django
    for user_id, first_name, last_name, email, password_hash, created_at in users:
        try:
            # Check if user already exists
            if not User.objects.filter(email=email).exists():
                # Create Django user
                django_user = User.objects.create(
                    username=email,  # Using email as username
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    date_joined=created_at if created_at else timezone.now()
                )
                
                # Set password directly (this is a hashed password from Flask)
                django_user.password = password_hash
                django_user.save()
                
                # Create default subscription
                Subscription.objects.create(
                    user=django_user,
                    plan='free',
                    start_date=timezone.now(),
                    is_active=True
                )
                
                print(f"Created user: {email}")
            else:
                print(f"User already exists: {email}")
        except Exception as e:
            print(f"Error creating user {email}: {str(e)}")
    
    print("User migration completed.")

def migrate_progress_from_sqlite():
    print("Starting migration of progress data from SQLite to Django...")
    
    # Connect to SQLite database
    sqlite_conn = sqlite3.connect('instance/signova.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get all progress records from SQLite
    sqlite_cursor.execute('SELECT id, user_id, sign_name, completed, completed_at, practice_count FROM progress')
    progress_records = sqlite_cursor.fetchall()
    
    # Create progress records in Django
    for _, user_id, sign_name, completed, completed_at, practice_count in progress_records:
        try:
            # Get corresponding Django user
            sqlite_cursor.execute('SELECT email FROM user WHERE id = ?', (user_id,))
            user_email = sqlite_cursor.fetchone()[0]
            
            django_user = User.objects.get(email=user_email)
            
            # Create progress record
            Progress.objects.create(
                user=django_user,
                sign_name=sign_name,
                completed=bool(completed),
                completed_at=completed_at if completed_at else None,
                practice_count=practice_count or 0
            )
            
            print(f"Migrated progress for {user_email}: {sign_name}")
        except Exception as e:
            print(f"Error migrating progress: {str(e)}")
    
    print("Progress migration completed.")

if __name__ == "__main__":
    print("Starting data migration from Flask (SQLite) to Django (MySQL)...")
    
    # Run migrations
    migrate_users_from_sqlite()
    migrate_progress_from_sqlite()
    
    print("Migration completed successfully!")