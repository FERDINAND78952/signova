import json
import uuid
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import Subscription
from datetime import datetime, timedelta
from django.utils import timezone

# Import Rave Python for Flutterwave
from rave_python import Rave, Misc, RaveExceptions

# Flutterwave API configuration
FLUTTERWAVE_SECRET_KEY = getattr(settings, 'FLW_SECRET_KEY', "FLWSECK_TEST-YOUR-SECRET-KEY-HERE")  # Replace with your secret key
FLUTTERWAVE_PUBLIC_KEY = getattr(settings, 'FLW_PUBLIC_KEY', "FLWPUBK_TEST-YOUR-PUBLIC-KEY-HERE")  # Replace with your public key
FLUTTERWAVE_API_URL = "https://api.flutterwave.com/v3"

# MTN Mobile Money configuration
MTN_ENABLED = getattr(settings, 'MTN_ENABLED', True)  # Enable MTN Mobile Money by default

# Define payment plans
PAYMENT_PLANS = {
    'free': {
        'name': 'Free Plan',
        'amount': 0,  # RWF
        'description': 'Basic access to Signova features',
        'duration': 365,  # days
    },
    'advanced': {
        'name': 'Advanced Plan',
        'amount': 30000,  # RWF
        'description': 'Enhanced learning experience with full access to learning materials',
        'duration': 30,  # days
    },
    'pro': {
        'name': 'Pro Plan',
        'amount': 60000,  # RWF
        'description': 'Complete professional package with offline translation capabilities',
        'duration': 30,  # days
    }
}

@login_required
def initiate_payment(request):
    """
    Initiates a Flutterwave payment for subscription using rave_python package
    or activates free plan without payment
    """
    if request.method == 'POST':
        plan_id = request.POST.get('plan')
        tx_ref = request.POST.get('tx_ref')
        transaction_id = request.POST.get('transaction_id')
        amount = request.POST.get('amount')
        
        # Check if plan is valid
        if plan_id not in PAYMENT_PLANS:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid plan selected'
            }, status=400)
            
        plan = PAYMENT_PLANS[plan_id]
        
        # Handle free plan activation without payment
        if plan_id == 'free':
            # Create or update subscription for free plan
            subscription, created = Subscription.objects.update_or_create(
                user=request.user,
                defaults={
                    'plan': plan_id,
                    'is_active': True,
                    'transaction_id': f"free-{str(uuid.uuid4())[:8]}",
                    'start_date': timezone.now(),
                    'end_date': timezone.now() + timedelta(days=PAYMENT_PLANS[plan_id]['duration'])
                }
            )
            
            return render(request, 'payment_success.html', {
                'plan': PAYMENT_PLANS[plan_id],
                'transaction_id': subscription.transaction_id,
                'is_free_plan': True
            })
        
        # If we have transaction details, it means payment was processed by Flutterwave JS
        if tx_ref and transaction_id:
            # Verify the transaction with Flutterwave API
            verification = verify_flutterwave_transaction(transaction_id)
            
            if verification.get('status') == 'success':
                # Update or create subscription
                subscription, created = Subscription.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'plan': plan_id,
                        'is_active': True,
                        'transaction_id': transaction_id,
                        'start_date': timezone.now(),
                        'end_date': timezone.now() + timedelta(days=PAYMENT_PLANS[plan_id]['duration'])
                    }
                )
                
                return render(request, 'payment_success.html', {
                    'plan': PAYMENT_PLANS[plan_id],
                    'transaction_id': transaction_id
                })
            else:
                # Payment verification failed
                return render(request, 'payment_failed.html', {
                    'error': verification.get('message', 'Payment verification failed')
                })
        
        # Initialize Rave for paid plans
        rave = Rave(FLUTTERWAVE_SECRET_KEY, production=not settings.DEBUG)
        
        # Generate transaction reference
        tx_ref = f"signova-{plan_id}-{str(uuid.uuid4())[:8]}"
        
        # For development/testing, we can simulate payment
        if settings.DEBUG and not getattr(settings, 'FLUTTERWAVE_ENABLED', False):
            return redirect(reverse('payment_success') + f'?tx_ref={tx_ref}&amount={plan["amount"]}')
        
        # Prepare payment data for frontend
        payment_data = {
            'public_key': FLUTTERWAVE_PUBLIC_KEY,
            'tx_ref': tx_ref,
            'amount': plan['amount'],
            'currency': 'RWF',
            'customer': {
                'email': request.user.email,
                'name': request.user.get_full_name() or request.user.username
            },
            'customizations': {
                'title': 'Signova Subscription',
                'description': plan['description'],
                'logo': request.build_absolute_uri('/static/images/signova-logo.svg')
            },
            'redirect_url': request.build_absolute_uri(reverse('payment_success'))
        }
        
        # Render the payment page with plans and payment data
        return render(request, 'payment.html', {
            'plans': PAYMENT_PLANS,
            'flutterwave_public_key': FLUTTERWAVE_PUBLIC_KEY,
            'payment_data': json.dumps(payment_data),
            'selected_plan': plan_id
        })
    
    # Render the payment page with plans
    return render(request, 'payment.html', {
        'plans': PAYMENT_PLANS,
        'flutterwave_public_key': FLUTTERWAVE_PUBLIC_KEY
    })

# Handle payment callback from Flutterwave using rave_python
@login_required
@csrf_exempt
def payment_callback(request):
    """
    Handles the payment callback from Flutterwave
    """
    # Get transaction details from the request
    tx_ref = request.GET.get('tx_ref')
    transaction_id = request.GET.get('transaction_id')
    status = request.GET.get('status')
    
    if not tx_ref:
        return redirect('dashboard')
    
    # If we have a transaction_id, verify with Flutterwave API
    if transaction_id and status == 'successful':
        # Initialize Rave
        rave = Rave(FLUTTERWAVE_SECRET_KEY, production=not settings.DEBUG)
        
        # Verify the transaction
        verification = verify_flutterwave_transaction(transaction_id)
        
        if verification.get('status') == 'success':
            # Get the amount from verification
            amount = verification.get('data', {}).get('amount', 0)
            
            # Determine plan based on amount
            plan_id = None
            for pid, plan in PAYMENT_PLANS.items():
                if plan['amount'] == float(amount):
                    plan_id = pid
                    break
            
            if not plan_id:
                plan_id = 'advanced'  # Default to advanced if amount doesn't match
            
            # Update or create subscription for the user
            if request.user.is_authenticated:
                subscription, created = Subscription.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'plan': plan_id,
                        'is_active': True,
                        'transaction_id': transaction_id,
                        'start_date': timezone.now(),
                        'end_date': timezone.now() + timedelta(days=PAYMENT_PLANS[plan_id]['duration'])
                    }
                )
                
                return render(request, 'payment_success.html', {
                    'plan': PAYMENT_PLANS[plan_id],
                    'transaction_id': transaction_id
                })
            else:
                # Handle case where user is not authenticated
                return redirect('login')
        else:
            # Payment verification failed
            return render(request, 'payment_failed.html', {
                'error': verification.get('message', 'Payment verification failed')
            })
    
    # For development/testing when Flutterwave is not enabled
    if settings.DEBUG and not getattr(settings, 'FLUTTERWAVE_ENABLED', False):
        amount = request.GET.get('amount')
        if amount:
            plan_id = 'advanced' if int(float(amount)) == PAYMENT_PLANS['advanced']['amount'] else 'pro'
            transaction_id = tx_ref
            
            # Update or create subscription
            if request.user.is_authenticated:
                subscription, created = Subscription.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'plan': plan_id,
                        'is_active': True,
                        'transaction_id': transaction_id,
                        'start_date': timezone.now(),
                        'end_date': timezone.now() + timedelta(days=PAYMENT_PLANS[plan_id]['duration'])
                    }
                )
                
                return render(request, 'payment_success.html', {
                    'plan': PAYMENT_PLANS[plan_id],
                    'transaction_id': transaction_id
                })
            else:
                return redirect('login')
    
    # If we get here, something went wrong
    return render(request, 'payment_failed.html')

# Handle webhook notifications from Flutterwave using rave_python
@csrf_exempt
def payment_webhook(request):
    """
    Webhook endpoint for Flutterwave payment notifications
    This endpoint should be registered in your Flutterwave dashboard
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    
    try:
        # Initialize Rave
        rave = Rave(FLUTTERWAVE_SECRET_KEY, production=not settings.DEBUG)
        
        # Parse the webhook data
        payload = json.loads(request.body)
        
        # Process the webhook based on event type
        event = payload.get('event')
        data = payload.get('data', {})
        
        if event == 'charge.completed' and data.get('status') == 'successful':
            # Get transaction details
            tx_ref = data.get('tx_ref')
            transaction_id = data.get('id')
            amount = data.get('amount')
            customer_email = data.get('customer', {}).get('email')
            
            # Find the user by email
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(email=customer_email)
                
                # Determine plan based on amount
                plan_id = None
                for pid, plan in PAYMENT_PLANS.items():
                    if plan['amount'] == float(amount):
                        plan_id = pid
                        break
                
                if not plan_id:
                    plan_id = 'advanced'  # Default to advanced if amount doesn't match
                
                # Update or create subscription
                subscription, created = Subscription.objects.update_or_create(
                    user=user,
                    defaults={
                        'plan': plan_id,
                        'is_active': True,
                        'transaction_id': transaction_id,
                        'start_date': timezone.now(),
                        'end_date': timezone.now() + timedelta(days=PAYMENT_PLANS[plan_id]['duration'])
                    }
                )
                
                # Log the successful payment
                print(f"Webhook: Subscription updated for {user.username}, plan: {plan_id}, tx_id: {transaction_id}")
                
            except User.DoesNotExist:
                # Log the error
                print(f"Webhook: User with email {customer_email} not found")
        
        return JsonResponse({'status': 'success'})
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        # Log the error
        print(f"Webhook error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def verify_flutterwave_transaction(transaction_id):
    """
    Verify a transaction with Flutterwave API using rave_python package
    Supports both card payments and MTN Mobile Money
    """
    # First try to use the rave_python package
    try:
        # Initialize Rave
        rave = Rave(FLUTTERWAVE_SECRET_KEY, production=not settings.DEBUG)
        
        # Try to verify as a card transaction first
        try:
            verification = rave.Card.verify(transaction_id)
            if verification:
                return {
                    'status': 'success',
                    'data': verification
                }
        except RaveExceptions.TransactionVerificationError:
            # If card verification fails, try mobile money verification
            try:
                verification = rave.MobileMoney.verify(transaction_id)
                if verification:
                    return {
                        'status': 'success',
                        'data': verification
                    }
            except Exception as mm_error:
                print(f"Error using Mobile Money verification: {str(mm_error)}")
                # Fall through to direct API call
    except Exception as e:
        print(f"Error using Rave verification: {str(e)}")
        # Fall back to direct API call if rave verification fails
    
    # Direct API call as fallback
    url = f"{FLUTTERWAVE_API_URL}/transactions/{transaction_id}/verify"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {FLUTTERWAVE_SECRET_KEY}'
    }
    
    try:
        # For development/testing when Flutterwave is not enabled
        if settings.DEBUG and not getattr(settings, 'FLUTTERWAVE_ENABLED', False):
            return {
                'status': 'success',
                'message': 'Transaction verified successfully',
                'data': {
                    'id': transaction_id,
                    'tx_ref': f"signova-{transaction_id}",
                    'amount': 30000,
                    'currency': 'RWF',
                    'status': 'successful'
                }
            }
        
        # Make API request to Flutterwave
        response = requests.get(url, headers=headers)
        return response.json()
        
    except Exception as e:
        # Log the error
        print(f"Flutterwave verification error: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }