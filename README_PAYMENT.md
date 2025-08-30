# Signova Payment Integration

## Overview

This document provides instructions for setting up and using the payment integration in the Signova application. The application uses Flutterwave as the payment gateway and supports various payment methods including credit cards and MTN Mobile Money.

## Setup Instructions

### 1. Environment Configuration

The payment integration is configured through environment variables in the `.env` file. The following variables have been added to your `.env` file:

```
# Flutterwave Configuration
FLW_SECRET_KEY=FLWSECK_TEST-your-flutterwave-secret-key-here
FLW_PUBLIC_KEY=FLWPUBK_TEST-your-flutterwave-public-key-here
FLUTTERWAVE_ENABLED=True
FLW_WEBHOOK_HASH=your-webhook-hash-here

# MTN Mobile Money Configuration
MTN_ENABLED=True
MTN_API_KEY=your-mtn-api-key-here
MTN_API_SECRET=your-mtn-api-secret-here
```

**Important:** Replace the placeholder values with your actual Flutterwave API keys.

### 2. Testing the Integration

A test script has been provided to verify your Flutterwave API connection:

```bash
python scripts/test_flutterwave_connection.py
```

If you see a "401 Unauthorized" error, it means you need to replace the placeholder API keys with valid ones from your Flutterwave dashboard.

### 3. Running the Payment Test Server

To test the payment integration in development:

```bash
python scripts/run_payment_test_server.py
```

This will start the Django development server with payment integration enabled.

## Documentation

Detailed documentation has been created to help you understand and use the payment integration:

1. **Payment Integration Guide** (`docs/payment_integration_guide.md`): Comprehensive guide for setting up and managing payment integrations

2. **Flutterwave Setup Guide** (`docs/flutterwave_setup_guide.md`): Step-by-step instructions for setting up Flutterwave

3. **Flutterwave Integration** (`docs/flutterwave_integration.md`): Technical details of the Flutterwave integration

## Testing Payments

For testing payments with Flutterwave's test environment, use the following test cards:

| Card Type | Card Number         | CVV | Expiry Date | PIN  | OTP  |
|-----------|---------------------|-----|-------------|------|------|
| Visa      | 4187427415564246    | 828 | 09/32       | 3310 | 12345 |
| Mastercard| 5531886652142950    | 564 | 09/32       | 3310 | 12345 |

For MTN Mobile Money testing, follow the prompts in the test environment.

## Implementation Details

### Backend

The payment processing is implemented in `signova_app/payment.py`, which includes:

- Payment initiation
- Transaction verification
- Webhook handling
- Subscription management

### Frontend

The frontend integration is implemented in:

- `static/js/flutterwave.js`: Handles the Flutterwave payment integration
- `static/js/payment.js`: Manages the payment form and UI interactions
- `templates/payment.html`: The payment page template

## Going Live

When you're ready to accept real payments:

1. Complete Flutterwave's verification process for your business
2. Replace the test API keys with live ones in your `.env` file
3. Update your webhook URL in the Flutterwave dashboard to your production domain

## Support

If you encounter issues with the payment integration:

1. Check the [Flutterwave API Documentation](https://developer.flutterwave.com/docs)
2. Review the implementation details in the codebase
3. Contact Flutterwave support through their [Support Portal](https://support.flutterwave.com)