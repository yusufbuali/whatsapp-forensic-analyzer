#!/usr/bin/env python3
"""
Test Authentication System
Quick script to test login, token validation, and protected endpoints
"""

import requests
import json
import sys

# API Base URL
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Default admin credentials (from .env)
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "ChangeThisSecurePassword123!"


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_health_check():
    """Test health check endpoint"""
    print_section("1. Testing Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✓ Health check passed!")
            return True
        else:
            print("✗ Health check failed!")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_login(username, password):
    """Test login endpoint"""
    print_section("2. Testing Login")

    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password},
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✓ Login successful!")
            print(f"Username: {data['user']['username']}")
            print(f"Role: {data['user']['role']}")
            print(f"Token Type: {data['token_type']}")
            print(f"Expires In: {data['expires_in']} seconds")
            print(f"Access Token: {data['access_token'][:50]}...")
            return data["access_token"]
        else:
            print(f"✗ Login failed!")
            print(f"Response: {response.json()}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def test_get_current_user(token):
    """Test protected endpoint - get current user"""
    print_section("3. Testing Protected Endpoint (GET /auth/me)")

    try:
        response = requests.get(
            f"{API_URL}/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✓ Successfully retrieved user info!")
            print(f"User ID: {data['id']}")
            print(f"Username: {data['username']}")
            print(f"Email: {data['email']}")
            print(f"Full Name: {data['full_name']}")
            print(f"Role: {data['role']}")
            print(f"Active: {data['is_active']}")
            return True
        else:
            print(f"✗ Failed to get user info!")
            print(f"Response: {response.json()}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_list_users(token):
    """Test admin endpoint - list users"""
    print_section("4. Testing Admin Endpoint (GET /auth/users)")

    try:
        response = requests.get(
            f"{API_URL}/auth/users", headers={"Authorization": f"Bearer {token}"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Successfully retrieved user list!")
            print(f"Total Users: {data['total']}")
            print(f"Users in Response: {len(data['users'])}")

            for user in data["users"]:
                print(f"  - {user['username']} ({user['role']}) - {user['email']}")

            return True
        else:
            print(f"✗ Failed to list users!")
            print(f"Response: {response.json()}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_unauthorized_access():
    """Test access without token"""
    print_section("5. Testing Unauthorized Access")

    try:
        response = requests.get(f"{API_URL}/auth/me")

        print(f"Status Code: {response.status_code}")

        if response.status_code == 403 or response.status_code == 401:
            print("✓ Correctly rejected unauthorized access!")
            return True
        else:
            print(f"✗ Should have rejected unauthorized access!")
            print(f"Response: {response.json()}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_invalid_token():
    """Test access with invalid token"""
    print_section("6. Testing Invalid Token")

    try:
        response = requests.get(
            f"{API_URL}/auth/me", headers={"Authorization": "Bearer invalid_token_12345"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 401:
            print("✓ Correctly rejected invalid token!")
            return True
        else:
            print(f"✗ Should have rejected invalid token!")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  WhatsApp Forensic Analyzer - Authentication System Test")
    print("=" * 80)
    print(f"\nTesting API at: {BASE_URL}")
    print(f"Username: {DEFAULT_USERNAME}")
    print(f"Password: {'*' * len(DEFAULT_PASSWORD)}")

    results = []

    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))

    # Test 2: Login
    token = test_login(DEFAULT_USERNAME, DEFAULT_PASSWORD)
    results.append(("Login", token is not None))

    if token:
        # Test 3: Get Current User
        results.append(("Get Current User", test_get_current_user(token)))

        # Test 4: List Users (Admin)
        results.append(("List Users (Admin)", test_list_users(token)))

    # Test 5: Unauthorized Access
    results.append(("Unauthorized Access", test_unauthorized_access()))

    # Test 6: Invalid Token
    results.append(("Invalid Token", test_invalid_token()))

    # Summary
    print_section("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Authentication system is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        sys.exit(1)
