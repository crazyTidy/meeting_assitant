"""Token login test."""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_token_login():
    print("=" * 80)
    print("Token Login Test")
    print("=" * 80)
    print()

    # Step 1: Generate test tokens
    print("[Step 1] Generate test tokens")
    print("-" * 80)
    from app.utils.jwt_generator import generate_test_token

    token1 = generate_test_token(
        user_id='user-zhangsan',
        username='zhangsan',
        real_name='Zhang San',
        department_id='dept-rd',
        department_name='R&D',
        position='Senior Engineer'
    )
    print(f"Token1 (first 60 chars): {token1[:60]}...")

    token2 = generate_test_token(
        user_id='user-lisi',
        username='lisi',
        real_name='Li Si',
        department_id='dept-market',
        department_name='Marketing',
        position='Manager'
    )
    print(f"Token2 (first 60 chars): {token2[:60]}...")
    print()

    # Step 2: Login with token1
    print("[Step 2] Login with token1")
    print("-" * 80)
    login_resp = requests.post(f"{BASE_URL}/api/v1/users/login", json={"token": token1})
    print(f"Status: {login_resp.status_code}")
    if login_resp.status_code == 200:
        user = login_resp.json()['user']
        print(f"Success! User: {user['real_name']} ({user['department_name']})")
    else:
        print(f"Failed: {login_resp.text}")
    print()

    # Step 3: Get current user
    print("[Step 3] Get current user with token")
    print("-" * 80)
    me_resp = requests.get(f"{BASE_URL}/api/v1/users/me", headers={"Authorization": f"Bearer {token1}"})
    print(f"Status: {me_resp.status_code}")
    if me_resp.status_code == 200:
        user = me_resp.json()
        print(f"Success! User: {user['real_name']}")
    else:
        print(f"Failed: {me_resp.text}")
    print()

    # Step 4: Access meetings
    print("[Step 4] Access meeting list")
    print("-" * 80)
    mtg_resp = requests.get(f"{BASE_URL}/api/v1/meetings/", headers={"Authorization": f"Bearer {token1}"})
    print(f"Status: {mtg_resp.status_code}")
    if mtg_resp.status_code == 200:
        data = mtg_resp.json()
        print(f"Success! Total meetings: {data['total']}")
    else:
        print(f"Failed: {mtg_resp.text}")
    print()

    # Step 5: Test invalid token
    print("[Step 5] Test invalid token")
    print("-" * 80)
    bad_resp = requests.post(f"{BASE_URL}/api/v1/users/login", json={"token": "invalid"})
    print(f"Status: {bad_resp.status_code} (expected 401)")
    print()

    print("=" * 80)
    print("Test Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_token_login()
