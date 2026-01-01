import os
import django
from django.urls import resolve, reverse
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

def check_url():
    path = '/api/v1/auth/api-login/'
    print("\n--- Checking default URL Conf (config.urls) ---")
    try:
        resolver_match = resolve(path, urlconf='config.urls')
        print(f"Resolved to view: {resolver_match.func}")
        print("SUCCESS! URL is valid in config.urls.")
    except Exception as e:
        print(f"FAILED to resolve in config.urls: {e}")

    print("\n--- Checking Public URL Conf (config.urls_public) ---")
    try:
        resolver_match = resolve(path, urlconf='config.urls_public')
        print(f"Resolved to view: {resolver_match.func}")
        print("SUCCESS! URL is valid in config.urls_public.")
    except Exception as e:
        print(f"FAILED to resolve in config.urls_public: {e}")

    # Check reverse
    try:
        url = reverse('api_login')
        print(f"Reversed 'api_login' to: {url}")
    except Exception as e:
        print(f"FAILED to reverse 'api_login': {e}")

if __name__ == "__main__":
    check_url()
