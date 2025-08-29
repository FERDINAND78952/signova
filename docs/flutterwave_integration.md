# Flutterwave Integration Guide

## Overview

This document provides instructions for setting up and using Flutterwave payment integration in the Signova project.

## Prerequisites

- Flutterwave account (Test or Live)
- API keys from Flutterwave dashboard

## Installation

The following dependencies are required for Flutterwave integration:

```bash
pip install requests python-decouple rave_python
```

These are already included in the project's `requirements.txt` file.

## Configuration

### Environment Variables

Create or update your `.env` file with the following Flutterwave configuration:

```
# Flutterwave Configuration
FLW_SECRET_KEY=FLWSECK_TEST-your-flutterwave-secret-key-here
FLW_PUBLIC_KEY=FLWPUBK_TEST-your-flutterwave-public-key-here
FLUTTERWAVE_ENABLED=True
FLW_WEBHOOK_HASH=your-webhook-hash-here

# MTN Mobile Money Configuration (if using MTN Mobile Money)
MTN_ENABLED=True
MTN_API_KEY=your-mtn-api-key-here
MTN_API_SECRET=your-mtn-api-secret-here
```

Replace the placeholder values with your actual Flutterwave API keys.

### Django Settings

The project's `settings.py` file is already configured to load these environment variables using `python-decouple`:

```python
# Flutterwave Configuration
FLW_SECRET_KEY = config('FLW_SECRET_KEY', default='FLWSECK_TEST-YOUR-SECRET-KEY-HERE')
FLW_PUBLIC_KEY = config('FLW_PUBLIC_KEY', default='FLWPUBK_TEST-YOUR-PUBLIC-KEY-HERE')
FLUTTERWAVE_ENABLED = config('FLUTTERWAVE_ENABLED', default=DEBUG, cast=bool)

# Flutterwave Django Configuration
FLW_PRODUCTION = not DEBUG  # Use test mode in development
FLW_SANDBOX = DEBUG  # Use sandbox in development
FLW_REDIRECT_URL = 'payment_callback'  # URL name for payment callback
FLW_WEBHOOK_HASH = config('FLW_WEBHOOK_HASH', default='')  # Webhook hash for verification
```

## Usage

The Flutterwave integration is implemented in `signova_app/payment.py`. The main components are:

1. **Initiate Payment**: The `initiate_payment` function creates a payment session.
2. **Payment Callback**: The `payment_callback` function handles the response from Flutterwave.
3. **Verify Transaction**: The `verify_flutterwave_transaction` function verifies the payment status.

## Payment Methods

The integration supports the following payment methods:

1. **Card Payments**: Credit and debit cards
2. **MTN Mobile Money**: For mobile money payments in Rwanda

## Testing

To test the integration:

1. Use Flutterwave test cards for card payments
2. Use test phone numbers for MTN Mobile Money
3. Check the Flutterwave dashboard for transaction status

## Going Live

When ready to go live:

1. Replace test API keys with live API keys
2. Set `FLUTTERWAVE_ENABLED=True` in production
3. Update `FLW_PRODUCTION=True` in settings

## Troubleshooting

If you encounter issues:

1. Check the Flutterwave dashboard for transaction status
2. Verify API keys are correctly set in the `.env` file
3. Ensure the callback URL is correctly configured in the Flutterwave dashboard