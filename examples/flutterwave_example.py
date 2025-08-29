# Example script for using Flutterwave in a Django view

import uuid
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from rave_python import Rave

# Example view for initiating a payment
@login_required
def example_payment(request):
    # Get Flutterwave keys from settings
    flw_public_key = settings.FLW_PUBLIC_KEY
    flw_secret_key = settings.FLW_SECRET_KEY
    
    # Generate a unique transaction reference
    tx_ref = f"example-{str(uuid.uuid4())[:8]}"
    
    # Payment details
    amount = 1000  # Amount in RWF
    currency = "RWF"
    payment_plan = "Basic Plan"
    description = "Example payment for testing"
    
    # Customer information
    customer_email = request.user.email
    customer_name = request.user.get_full_name() or request.user.username
    
    # Prepare payment data for frontend
    payment_data = {
        'public_key': flw_public_key,
        'tx_ref': tx_ref,
        'amount': amount,
        'currency': currency,
        'customer': {
            'email': customer_email,
            'name': customer_name
        },
        'customizations': {
            'title': 'Example Payment',
            'description': description,
            'logo': request.build_absolute_uri('/static/images/logo.png')
        },
        'redirect_url': request.build_absolute_uri(reverse('payment_callback'))
    }
    
    # Render the payment page
    return render(request, 'payment.html', {
        'payment_data': payment_data,
        'flutterwave_public_key': flw_public_key,
        'plan_name': payment_plan,
        'amount': amount,
        'currency': currency
    })

# Example function for verifying a transaction
def example_verify_transaction(transaction_id):
    # Initialize Rave with secret key
    rave = Rave(settings.FLW_SECRET_KEY, production=not settings.DEBUG)
    
    try:
        # Try to verify as a card transaction
        verification = rave.Card.verify(transaction_id)
        if verification:
            return {
                'status': 'success',
                'data': verification
            }
    except Exception as e:
        # If card verification fails, try mobile money verification
        try:
            verification = rave.MobileMoney.verify(transaction_id)
            if verification:
                return {
                    'status': 'success',
                    'data': verification
                }
        except Exception as mm_error:
            return {
                'status': 'error',
                'message': str(mm_error)
            }
    
    return {
        'status': 'error',
        'message': 'Transaction verification failed'
    }

# Example callback function
@login_required
def example_payment_callback(request):
    # Get transaction details from the request
    tx_ref = request.GET.get('tx_ref')
    transaction_id = request.GET.get('transaction_id')
    status = request.GET.get('status')
    
    if not tx_ref or not transaction_id:
        return redirect('dashboard')
    
    if status == 'successful':
        # Verify the transaction
        verification = example_verify_transaction(transaction_id)
        
        if verification.get('status') == 'success':
            # Process successful payment
            # Update user subscription, database records, etc.
            return render(request, 'payment_success.html', {
                'transaction_id': transaction_id
            })
    
    # Payment failed
    return render(request, 'payment_failed.html', {
        'error': 'Payment verification failed'
    })