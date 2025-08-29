import json
import uuid
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import Subscription

# Flutterwave payment plans
PAYMENT_PLANS = {
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
    Initiates a Flutterwave payment for subscription
    """
    if request.method == 'POST':
        plan_id = request.POST.get('plan')
        
        if plan_id not in PAYMENT_PLANS:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid plan selected'
            }, status=400)
        
        plan = PAYMENT_PLANS[plan_id]
        tx_ref = f"signova-{uuid.uuid4().hex[:10]}"
        
        # For now, just simulate payment and redirect to success page
        # This is a temporary solution until Flutterwave integration is properly set up
        return redirect(reverse('payment_success') + f'?tx_ref={tx_ref}&amount={plan["amount"]}')
    
    return render(request, 'payment.html', {'plans': PAYMENT_PLANS})

@csrf_exempt
def payment_callback(request):
    """
    Handles the payment callback from Flutterwave
    """
    tx_ref = request.GET.get('tx_ref')
    amount = request.GET.get('amount')
    
    if not tx_ref or not amount:
        return redirect('dashboard')
    
    # For now, simulate a successful payment
    # In a real implementation, we would verify with Flutterwave API
    plan_id = 'advanced' if int(amount) == PAYMENT_PLANS['advanced']['amount'] else 'pro'
    transaction_id = tx_ref
    
    # Update or create subscription
    subscription, created = Subscription.objects.update_or_create(
        user=request.user,
        defaults={
            'plan': plan_id,
            'is_active': True,
            'transaction_id': transaction_id,
        }
    )
    
    return render(request, 'payment_success.html', {
        'plan': PAYMENT_PLANS[plan_id],
        'transaction_id': transaction_id
    })

@csrf_exempt
def payment_webhook(request):
    """
    Webhook endpoint for Flutterwave payment notifications
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    # For now, just return success as we're simulating payments
    return JsonResponse({'status': 'success'})