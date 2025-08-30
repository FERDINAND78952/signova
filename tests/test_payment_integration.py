import os
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from signova_app.models import Subscription
from signova_app.payment import PAYMENT_PLANS, verify_flutterwave_transaction

User = get_user_model()

class FlutterwavePaymentTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Set up test client
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'FLW_SECRET_KEY': 'FLWSECK_TEST-test-secret-key',
            'FLW_PUBLIC_KEY': 'FLWPUBK_TEST-test-public-key',
            'FLUTTERWAVE_ENABLED': 'True',
            'FLW_WEBHOOK_HASH': 'test-webhook-hash'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        self.env_patcher.stop()
    
    def test_payment_plans_exist(self):
        """Test that payment plans are properly defined"""
        self.assertIn('free', PAYMENT_PLANS)
        self.assertIn('advanced', PAYMENT_PLANS)
        self.assertIn('pro', PAYMENT_PLANS)
        
        # Check free plan details
        self.assertEqual(PAYMENT_PLANS['free']['amount'], 0)
        
        # Check advanced plan details
        self.assertEqual(PAYMENT_PLANS['advanced']['amount'], 30000)
        self.assertEqual(PAYMENT_PLANS['advanced']['duration'], 30)
        
        # Check pro plan details
        self.assertEqual(PAYMENT_PLANS['pro']['amount'], 60000)
        self.assertEqual(PAYMENT_PLANS['pro']['duration'], 30)
    
    def test_free_plan_activation(self):
        """Test that free plan can be activated without payment"""
        # Get initial subscription count
        initial_count = Subscription.objects.count()
        
        # Submit request to activate free plan
        response = self.client.post(
            reverse('initiate_payment'),
            {'plan': 'free'}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment_success.html')
        
        # Check that subscription was created
        self.assertEqual(Subscription.objects.count(), initial_count + 1)
        
        # Check subscription details
        subscription = Subscription.objects.get(user=self.user)
        self.assertEqual(subscription.plan, 'free')
        self.assertTrue(subscription.is_active)
    
    @patch('signova_app.payment.verify_flutterwave_transaction')
    def test_paid_plan_verification(self, mock_verify):
        """Test verification of paid plan subscription"""
        # Mock successful verification response
        mock_verify.return_value = {
            'status': 'success',
            'data': {
                'amount': 30000,
                'currency': 'RWF',
                'tx_ref': 'test-tx-ref',
                'flw_ref': 'test-flw-ref'
            }
        }
        
        # Submit request with transaction details
        response = self.client.post(
            reverse('initiate_payment'),
            {
                'plan': 'advanced',
                'tx_ref': 'test-tx-ref',
                'transaction_id': 'test-transaction-id',
                'amount': '30000'
            }
        )
        
        # Check that verification was called
        mock_verify.assert_called_once_with('test-transaction-id')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Check subscription details
        subscription = Subscription.objects.get(user=self.user)
        self.assertEqual(subscription.plan, 'advanced')
        self.assertTrue(subscription.is_active)
        self.assertEqual(subscription.transaction_id, 'test-transaction-id')
    
    @patch('requests.get')
    def test_transaction_verification(self, mock_get):
        """Test the transaction verification function"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'success',
            'message': 'Transaction verified',
            'data': {
                'status': 'successful',
                'amount': 30000,
                'currency': 'RWF',
                'tx_ref': 'test-tx-ref',
                'flw_ref': 'test-flw-ref'
            }
        }
        mock_get.return_value = mock_response
        
        # Call verification function
        result = verify_flutterwave_transaction('test-transaction-id')
        
        # Check result
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['amount'], 30000)

if __name__ == '__main__':
    unittest.main()