import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signova.settings')
import django
django.setup()

# Import the payment module
from signova_app.payment import verify_flutterwave_transaction
from django.conf import settings


class FlutterwaveIntegrationTest(unittest.TestCase):
    """Test cases for Flutterwave integration"""

    def test_flutterwave_keys_loaded(self):
        """Test that Flutterwave keys are loaded from environment variables"""
        # Check if the keys are loaded from settings
        self.assertIsNotNone(settings.FLW_SECRET_KEY)
        self.assertIsNotNone(settings.FLW_PUBLIC_KEY)
        
        # Check if the keys are not the default placeholder values
        self.assertNotEqual(settings.FLW_SECRET_KEY, 'FLWSECK_TEST-YOUR-SECRET-KEY-HERE')
        self.assertNotEqual(settings.FLW_PUBLIC_KEY, 'FLWPUBK_TEST-YOUR-PUBLIC-KEY-HERE')

    @patch('signova_app.payment.Rave')
    def test_verify_transaction(self, mock_rave):
        """Test transaction verification with mocked Rave"""
        # Mock the Rave instance and Card.verify method
        mock_rave_instance = MagicMock()
        mock_rave.return_value = mock_rave_instance
        
        mock_card = MagicMock()
        mock_rave_instance.Card = mock_card
        
        # Mock successful verification response
        mock_response = {
            'status': 'successful',
            'amount': 30000,
            'currency': 'RWF',
            'customer': {
                'email': 'test@example.com'
            }
        }
        mock_card.verify.return_value = mock_response
        
        # Call the function with a test transaction ID
        result = verify_flutterwave_transaction('test_transaction_id')
        
        # Assert the function returns the expected result
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['amount'], 30000)
        self.assertEqual(result['data']['currency'], 'RWF')
        self.assertEqual(result['data']['customer']['email'], 'test@example.com')


if __name__ == '__main__':
    unittest.main()