#!/usr/bin/env python3
"""
Test script for BCM Authentication REST API endpoints
"""

import requests
import json
import sys

# Configuration
ODOO_URL = "http://localhost:8069"  # Change if needed
TEST_EMAIL = "admin"  # Default Odoo admin
TEST_PASSWORD = "admin"  # Default Odoo admin password

class AuthAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def test_endpoint(self, endpoint, method='POST', data=None, description=""):
        """Test a specific endpoint"""
        url = f"{self.base_url}{endpoint}"

        print(f"\n{'='*60}")
        print(f"Testing: {method} {endpoint}")
        print(f"Description: {description}")
        print(f"URL: {url}")

        try:
            if method == 'POST':
                response = self.session.post(url, json=data)
            else:
                response = self.session.get(url)

            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")

            try:
                response_data = response.json()
                print(f"Response: {json.dumps(response_data, indent=2)}")
                return response_data
            except json.JSONDecodeError:
                print(f"Response Text: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None

    def run_tests(self):
        """Run all authentication tests"""
        print("BCM Authentication API Test Suite")
        print("="*60)

        # Test 1: Check authentication status (before login)
        self.test_endpoint(
            '/api/auth/check',
            method='POST',
            description="Check auth status before login"
        )

        # Test 2: Login
        login_data = {
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD
        }
        login_response = self.test_endpoint(
            '/api/auth/login',
            method='POST',
            data=login_data,
            description="User login"
        )

        if not login_response or not login_response.get('success'):
            print("\n❌ Login failed. Cannot continue with authenticated tests.")
            return

        print("\n✅ Login successful!")

        # Test 3: Get current user
        self.test_endpoint(
            '/api/auth/me',
            method='POST',
            description="Get current authenticated user"
        )

        # Test 4: Check authentication status (after login)
        self.test_endpoint(
            '/api/auth/check',
            method='POST',
            description="Check auth status after login"
        )

        # Test 5: Refresh session
        self.test_endpoint(
            '/api/auth/refresh',
            method='POST',
            description="Refresh user session"
        )

        # Test 6: Logout
        self.test_endpoint(
            '/api/auth/logout',
            method='POST',
            description="User logout"
        )

        # Test 7: Check authentication status (after logout)
        self.test_endpoint(
            '/api/auth/check',
            method='POST',
            description="Check auth status after logout"
        )

def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = ODOO_URL

    print(f"Testing authentication endpoints at: {base_url}")

    tester = AuthAPITester(base_url)
    tester.run_tests()

    print(f"\n{'='*60}")
    print("Test completed!")
    print("\nTo test manually:")
    print(f"curl -X POST {base_url}/api/auth/login \\")
    print("  -H 'Content-Type: application/json' \\")
    print(f"  -d '{{\"email\":\"{TEST_EMAIL}\",\"password\":\"{TEST_PASSWORD}\"}}'")

if __name__ == "__main__":
    main()