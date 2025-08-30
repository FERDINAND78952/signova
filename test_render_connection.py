import requests
import sys
import json

def test_connection(url):
    """Test connection to a URL with detailed error reporting"""
    print(f"Testing connection to: {url}")
    
    try:
        # Make request with extended timeout and detailed headers
        headers = {
            'User-Agent': 'SignovaConnectionTest/1.0',
            'Accept': 'text/html,application/json,*/*',
            'Connection': 'keep-alive'
        }
        
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        
        # Print response content (truncated if too large)
        content = response.text[:500]
        print(f"Response Content (truncated): {content}")
        
        if response.status_code == 200:
            print("✅ Connection successful!")
            return True
        else:
            print(f"❌ Connection failed with status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    # Default URL to test
    url = "https://signova.onrender.com/health-check/"
    
    # Allow custom URL from command line
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    test_connection(url)