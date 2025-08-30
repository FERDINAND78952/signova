#!/usr/bin/env python
"""
Script to run Django development server with payment integration enabled
This script sets up the necessary environment variables and runs the server
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set environment variables for payment testing
os.environ['FLUTTERWAVE_ENABLED'] = 'True'
os.environ['DEBUG'] = 'True'

# Check if Flutterwave keys are set
flw_secret_key = os.getenv('FLW_SECRET_KEY')
flw_public_key = os.getenv('FLW_PUBLIC_KEY')

if not flw_secret_key or not flw_public_key:
    print("\n❌ Flutterwave API keys are not set in your .env file.")
    print("Please set FLW_SECRET_KEY and FLW_PUBLIC_KEY before running this script.")
    sys.exit(1)

# Print configuration info
print("\n=== Signova Payment Test Server ===")
print("ℹ️ Starting Django development server with payment integration enabled")
print(f"ℹ️ Using {'TEST' if flw_secret_key.startswith('FLWSECK_TEST-') else 'LIVE'} Flutterwave environment")

# Run Django development server
try:
    print("\n🚀 Starting server at http://127.0.0.1:8000/")
    print("ℹ️ Visit http://127.0.0.1:8000/payment/ to test payment integration")
    print("ℹ️ Press Ctrl+C to stop the server\n")
    
    # Run the Django development server
    subprocess.run([sys.executable, 'manage.py', 'runserver'])
    
except KeyboardInterrupt:
    print("\n✅ Server stopped")
except Exception as e:
    print(f"\n❌ Error starting server: {str(e)}")