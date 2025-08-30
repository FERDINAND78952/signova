#!/usr/bin/env python
"""
Test script to verify Flutterwave API connection
This script tests the connection to Flutterwave API using the configured API keys
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Get Flutterwave API keys from environment
FLW_SECRET_KEY = os.getenv('FLW_SECRET_KEY')
FLW_PUBLIC_KEY = os.getenv('FLW_PUBLIC_KEY')
FLUTTERWAVE_ENABLED = os.getenv('FLUTTERWAVE_ENABLED', 'True').lower() == 'true'

# Flutterwave API base URL
FLW_API_URL = "https://api.flutterwave.com/v3"

def test_flutterwave_connection():
    """Test connection to Flutterwave API"""
    print("\n=== Testing Flutterwave API Connection ===")
    
    # Check if Flutterwave is enabled
    if not FLUTTERWAVE_ENABLED:
        print("❌ Flutterwave integration is disabled. Set FLUTTERWAVE_ENABLED=True to enable.")
        return False
    
    # Check if API keys are set
    if not FLW_SECRET_KEY or not FLW_PUBLIC_KEY:
        print("❌ Flutterwave API keys are not set. Please check your .env file.")
        return False
    
    # Check if using test keys
    is_test = FLW_SECRET_KEY.startswith('FLWSECK_TEST-') and FLW_PUBLIC_KEY.startswith('FLWPUBK_TEST-')
    print(f"ℹ️ Using {'TEST' if is_test else 'LIVE'} environment")
    
    # Test API connection by getting banks list
    try:
        headers = {
            'Authorization': f'Bearer {FLW_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        
        # Get banks list for Rwanda
        response = requests.get(f"{FLW_API_URL}/banks/RW", headers=headers)
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                banks_count = len(data.get('data', []))
                print(f"✅ Successfully connected to Flutterwave API")
                print(f"ℹ️ Retrieved {banks_count} banks for Rwanda")
                return True
            else:
                print(f"❌ API request failed: {data.get('message')}")
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error connecting to Flutterwave API: {str(e)}")
    
    return False

def test_payment_verification(transaction_id):
    """Test payment verification with a transaction ID"""
    print("\n=== Testing Payment Verification ===")
    
    if not transaction_id:
        print("❌ No transaction ID provided")
        return False
    
    try:
        headers = {
            'Authorization': f'Bearer {FLW_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        
        # Verify transaction
        response = requests.get(f"{FLW_API_URL}/transactions/{transaction_id}/verify", headers=headers)
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Transaction verification API call successful")
            print(f"ℹ️ Status: {data.get('status')}")
            print(f"ℹ️ Message: {data.get('message')}")
            
            # Print transaction details if available
            if data.get('data'):
                tx_data = data.get('data')
                print(f"ℹ️ Transaction amount: {tx_data.get('amount')} {tx_data.get('currency')}")
                print(f"ℹ️ Transaction status: {tx_data.get('status')}")
                print(f"ℹ️ Payment method: {tx_data.get('payment_type')}")
            
            return True
        else:
            print(f"❌ Transaction verification failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error verifying transaction: {str(e)}")
    
    return False

if __name__ == "__main__":
    # Test API connection
    connection_success = test_flutterwave_connection()
    
    # Test transaction verification if a transaction ID is provided
    if connection_success and len(sys.argv) > 1:
        transaction_id = sys.argv[1]
        test_payment_verification(transaction_id)
    elif connection_success:
        print("\nℹ️ To test transaction verification, provide a transaction ID as an argument:")
        print("python test_flutterwave_connection.py <transaction_id>")