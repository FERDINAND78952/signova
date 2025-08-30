# Signova Payment Integration Guide

## Overview

This document provides a comprehensive guide for setting up and managing payment integrations in the Signova application. Currently, the application supports Flutterwave for payment processing and MTN Mobile Money as a payment method.

## Configuration

### Environment Variables

The following environment variables need to be set in your `.env` file:

```
# Flutterwave Configuration
FLW_SECRET_KEY=FLWSECK_TEST-your-flutterwave-secret-key-here  # Replace with your actual secret key
FLW_PUBLIC_KEY=FLWPUBK_TEST-your-flutterwave-public-key-here  # Replace with your actual public key
FLUTTERWAVE_ENABLED=True  # Set to False to disable Flutterwave integration
FLW_WEBHOOK_HASH=your-webhook-hash-here  # For webhook verification

# MTN Mobile Money Configuration
MTN_ENABLED=True  # Set to False to disable MTN Mobile Money
MTN_API_KEY=your-mtn-api-key-here
MTN_API_SECRET=your-mtn-api-secret-here
```

### Test vs. Production Keys

- For development and testing, use Flutterwave test keys (prefixed with `FLWSECK_TEST-` and `FLWPUBK_TEST-`)
- For production, use live keys (prefixed with `FLWSECK-` and `FLWPUBK-`)

## Payment Flow

1. User selects a subscription plan
2. User chooses a payment method (Card or MTN Mobile Money)
3. Payment is initiated through Flutterwave
4. User completes payment on Flutterwave's interface
5. User is redirected back to Signova
6. Payment is verified and subscription is activated

## Implementation Details

### Backend (Django)

The payment processing is handled in `signova_app/payment.py`, which includes:

- `initiate_payment`: Initiates a payment for a subscription plan
- `verify_flutterwave_transaction`: Verifies a completed transaction with Flutterwave API
- `payment_callback`: Handles the callback from Flutterwave after payment
- `webhook_handler`: Processes webhook notifications from Flutterwave

### Frontend (JavaScript)

The frontend integration is handled in `static/js/flutterwave.js` and `static/js/payment.js`, which include:

- `initFlutterwavePayment`: Initializes the Flutterwave payment buttons
- `makeFlutterwavePayment`: Handles the payment process using Flutterwave's inline JS
- `initPaymentMethodSelectors`: Manages payment method selection UI

## Payment Plans

The application defines several subscription plans in `signova_app/payment.py`:

- **Free Plan**: Basic access to Signova features (0 RWF)
- **Advanced Plan**: Enhanced learning experience (30,000 RWF for 30 days)
- **Pro Plan**: Complete professional package (60,000 RWF for 30 days)

## Testing Payments

For testing payments with Flutterwave:

1. Use test cards provided by Flutterwave in their documentation
2. For MTN Mobile Money testing, follow Flutterwave's test documentation

## Webhook Integration

Flutterwave can send webhook notifications for payment events. To set up webhooks:

1. Configure your webhook URL in the Flutterwave dashboard (e.g., `https://yourdomain.com/payment/webhook/`)
2. Set the `FLW_WEBHOOK_HASH` in your `.env` file to the hash provided by Flutterwave
3. Ensure the webhook handler in `payment.py` is properly configured to process these notifications

## Troubleshooting

### Common Issues

1. **Payment Verification Fails**: Ensure your API keys are correct and that you're using the right environment (test vs. production)
2. **Webhook Not Received**: Check your webhook URL configuration in the Flutterwave dashboard
3. **MTN Mobile Money Not Working**: Verify that MTN Mobile Money is enabled in your Flutterwave account and that the `MTN_ENABLED` setting is `True`

## Resources

- [Flutterwave API Documentation](https://developer.flutterwave.com/docs)
- [Flutterwave Python Library (rave_python)](https://github.com/Flutterwave/rave-python)
- [MTN Mobile Money API Documentation](https://momodeveloper.mtn.com/)