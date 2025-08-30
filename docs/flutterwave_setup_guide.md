# Flutterwave Setup Guide for Signova

## Getting Started

This guide will help you set up and test the Flutterwave payment integration for Signova.

### Step 1: Create a Flutterwave Account

1. Go to [Flutterwave's website](https://flutterwave.com) and sign up for an account
2. Complete the verification process to activate your account
3. Navigate to the Dashboard to access your API keys

### Step 2: Get Your API Keys

1. In your Flutterwave Dashboard, go to **Settings** > **API Keys & Webhooks**
2. You'll find your **Public Key** and **Secret Key** for both test and live environments
3. For development, use the **Test** keys

### Step 3: Configure Signova

1. Open your `.env` file in the Signova project root
2. Update the following settings with your Flutterwave API keys:

```
# Flutterwave Configuration
FLW_SECRET_KEY=FLWSECK_TEST-your-flutterwave-secret-key-here
FLW_PUBLIC_KEY=FLWPUBK_TEST-your-flutterwave-public-key-here
FLUTTERWAVE_ENABLED=True
FLW_WEBHOOK_HASH=your-webhook-hash-here
```

### Step 4: Set Up Webhooks (Optional)

1. In your Flutterwave Dashboard, go to **Settings** > **API Keys & Webhooks**
2. Add a new webhook URL: `https://your-domain.com/payment/webhook/`
3. Copy the webhook hash and add it to your `.env` file as `FLW_WEBHOOK_HASH`

### Step 5: Test the Integration

#### Using the Test Script

Run the provided test script to verify your Flutterwave API connection:

```bash
python scripts/test_flutterwave_connection.py
```

If successful, you should see a confirmation message and a list of banks for Rwanda.

#### Testing Payments

For testing payments, use Flutterwave's test cards:

| Card Type | Card Number         | CVV | Expiry Date | PIN  | OTP  |
|-----------|---------------------|-----|-------------|------|------|
| Visa      | 4187427415564246    | 828 | 09/32       | 3310 | 12345 |
| Mastercard| 5531886652142950    | 564 | 09/32       | 3310 | 12345 |

For MTN Mobile Money testing, follow the prompts in the test environment.

### Step 6: Go Live

When you're ready to accept real payments:

1. Complete Flutterwave's verification process for your business
2. Switch to live API keys in your `.env` file:

```
FLW_SECRET_KEY=FLWSECK-your-live-secret-key-here
FLW_PUBLIC_KEY=FLWPUBK-your-live-public-key-here
```

3. Update your webhook URL in the Flutterwave Dashboard to your production domain

## Troubleshooting

### Common Issues

1. **API Keys Not Working**
   - Ensure you've copied the keys correctly with no extra spaces
   - Check that you're using the right environment keys (test vs. live)

2. **Payment Verification Fails**
   - Check your server logs for detailed error messages
   - Verify that your Secret Key is correctly set in the `.env` file

3. **Webhook Not Received**
   - Ensure your webhook URL is publicly accessible
   - Check that the webhook URL is correctly configured in the Flutterwave Dashboard

### Getting Help

If you encounter issues with the Flutterwave integration:

1. Check the [Flutterwave API Documentation](https://developer.flutterwave.com/docs)
2. Contact Flutterwave support through their [Support Portal](https://support.flutterwave.com)
3. Review the implementation details in `signova_app/payment.py` and `static/js/flutterwave.js`