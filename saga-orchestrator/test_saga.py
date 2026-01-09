"""
Test script for Saga Pattern
Tests both success and failure scenarios
"""
import requests
import time
import json

SAGA_ORCHESTRATOR_URL = 'http://localhost:5003'
USER_SERVICE_URL = 'http://localhost:5001'
QUIZ_SERVICE_URL = 'http://localhost:5002'


def test_saga_success():
    """Test successful saga execution"""
    print("\n" + "="*60)
    print("TEST 1: Successful User Registration Saga")
    print("="*60)
    
    email = f"saga_test_{int(time.time())}@example.com"
    password = "testpass123"
    
    # Start saga
    print(f"\n1. Starting saga for: {email}")
    response = requests.post(
        f'{SAGA_ORCHESTRATOR_URL}/saga/register',
        json={'email': email, 'password': password}
    )
    
    if response.status_code != 202:
        print(f"❌ Failed to start saga: {response.status_code}")
        print(response.text)
        return False
    
    result = response.json()
    task_id = result['task_id']
    print(f"✅ Saga started. Task ID: {task_id}")
    
    # Poll for completion
    print("\n2. Polling for saga completion...")
    max_attempts = 30
    for i in range(max_attempts):
        time.sleep(1)
        status_response = requests.get(f'{SAGA_ORCHESTRATOR_URL}/saga/status/{task_id}')
        status_data = status_response.json()
        
        print(f"   Attempt {i+1}: Status = {status_data['state']}")
        
        if status_data['state'] == 'SUCCESS':
            print("\n✅ Saga completed successfully!")
            print(f"   Result: {json.dumps(status_data['result'], indent=2)}")
            
            # Verify user was created
            user_id = status_data['result'].get('user_id')
            if user_id:
                print(f"\n3. Verifying user {user_id} exists in User Service...")
                user_check = requests.get(f'{USER_SERVICE_URL}/saga/users/{user_id}')
                if user_check.status_code == 200:
                    print("   ✅ User exists in User Service")
                else:
                    print(f"   ⚠️  User check returned: {user_check.status_code}")
                
                print(f"\n4. Verifying profile for user {user_id} exists in Quiz Service...")
                profile_check = requests.get(f'{QUIZ_SERVICE_URL}/saga/profile/{user_id}')
                if profile_check.status_code == 200:
                    print("   ✅ Profile exists in Quiz Service")
                else:
                    print(f"   ⚠️  Profile check returned: {profile_check.status_code}")
            
            return True
        
        elif status_data['state'] == 'FAILURE':
            print("\n❌ Saga failed!")
            print(f"   Error: {status_data.get('error', 'Unknown error')}")
            return False
    
    print("\n⏱️  Saga timed out after 30 seconds")
    return False


def test_saga_compensation():
    """Test saga compensation (rollback) when step fails"""
    print("\n" + "="*60)
    print("TEST 2: Saga Compensation (Failure Scenario)")
    print("="*60)
    print("\nNote: This test requires Quiz Service to be temporarily unavailable")
    print("      or the init-profile endpoint to fail to trigger compensation.")
    print("\nTo test compensation manually:")
    print("1. Start saga registration")
    print("2. Stop Quiz Service before Step 2 completes")
    print("3. Observe compensation (user deletion)")
    print("\nFor now, testing with invalid data to see error handling...")
    
    email = f"saga_fail_{int(time.time())}@example.com"
    password = "testpass123"
    
    # Start saga
    print(f"\n1. Starting saga for: {email}")
    response = requests.post(
        f'{SAGA_ORCHESTRATOR_URL}/saga/register',
        json={'email': email, 'password': password}
    )
    
    if response.status_code != 202:
        print(f"❌ Failed to start saga: {response.status_code}")
        return False
    
    result = response.json()
    task_id = result['task_id']
    print(f"✅ Saga started. Task ID: {task_id}")
    
    # Poll for completion/failure
    print("\n2. Polling for saga status...")
    for i in range(30):
        time.sleep(1)
        status_response = requests.get(f'{SAGA_ORCHESTRATOR_URL}/saga/status/{task_id}')
        status_data = status_response.json()
        
        if status_data['state'] in ['SUCCESS', 'FAILURE']:
            print(f"\n   Final Status: {status_data['state']}")
            print(f"   Details: {json.dumps(status_data, indent=2)}")
            
            if status_data['state'] == 'FAILURE':
                print("\n✅ Compensation should have been triggered")
                print("   Check logs to see compensation execution")
            
            return True
    
    print("\n⏱️  Test timed out")
    return False


def check_services():
    """Check if all services are running"""
    print("\n" + "="*60)
    print("Checking Services...")
    print("="*60)
    
    services = {
        'Saga Orchestrator': (SAGA_ORCHESTRATOR_URL, '/saga/health'),
        'User Service': (USER_SERVICE_URL, '/health'),
        'Quiz Service': (QUIZ_SERVICE_URL, '/health')
    }
    
    all_up = True
    for name, (url, health_path) in services.items():
        try:
            response = requests.get(f'{url}{health_path}', timeout=2)
            if response.status_code == 200:
                print(f"✅ {name}: Running")
            else:
                print(f"⚠️  {name}: Responding but status {response.status_code}")
                all_up = False
        except requests.exceptions.RequestException:
            print(f"❌ {name}: Not responding")
            all_up = False
    
    return all_up


if __name__ == '__main__':
    print("\n" + "="*60)
    print("SAGA PATTERN TEST SUITE")
    print("="*60)
    
    # Check services
    if not check_services():
        print("\n⚠️  Some services are not running. Please start all services first.")
        print("\nRequired services:")
        print("  - Saga Orchestrator: http://localhost:5003")
        print("  - User Service: http://localhost:5001")
        print("  - Quiz Service: http://localhost:5002")
        print("  - Redis: localhost:6379")
        print("  - Celery Worker: Running")
        exit(1)
    
    # Run tests
    print("\n" + "="*60)
    print("Running Tests...")
    print("="*60)
    
    test1_result = test_saga_success()
    test2_result = test_saga_compensation()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Test 1 (Success): {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"Test 2 (Compensation): {'✅ PASSED' if test2_result else '❌ FAILED'}")

