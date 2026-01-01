import requests

def test_options():
    url = "http://127.0.0.1:8000/api/v1/auth/api-login/"
    print(f"Testing OPTIONS request to: {url}")
    
    try:
        response = requests.options(url)
        print(f"Status Code: {response.status_code}")
        print("Headers:")
        for k, v in response.headers.items():
            print(f"  {k}: {v}")
            
        if response.status_code == 200:
            print("\nSUCCESS: The endpoint accepts OPTIONS requests.")
        else:
            print(f"\nFAILURE: Received status {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_options()
