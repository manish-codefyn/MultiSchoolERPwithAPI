import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User
from apps.auth.forms import ProfileUpdateForm

# Get a test user (non-superuser preferably)
try:
    user = User.objects.filter(is_superuser=False, tenant__isnull=False).first()
    if not user:
        print("No regular user found, trying superuser")
        user = User.objects.first()
        
    if not user:
        print("No users found at all!")
        exit()
        
    print(f"Testing with user: {user.email}")
    print(f"Current Phone: {user.phone_number}")

    # Create dummy image data
    image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    uploaded_file = SimpleUploadedFile(name='test_avatar.png', content=image_data, content_type='image/png')

    # Data similar to what might be submitted
    data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': user.phone_number or '+1234567890', # Ensure valid phone format
        'timezone': 'UTC',
        'language': 'en',
    }
    
    files = {
        'avatar': uploaded_file
    }

    form = ProfileUpdateForm(data=data, files=files, instance=user)
    
    if form.is_valid():
        print("Form IS VALID!")
        # Don't save to avoid cluttering DB? Or save to test complete flow?
        # user = form.save()
        # print(f"Saved avatar URL: {user.avatar.url}")
    else:
        print("Form IS INVALID!")
        print("Errors:", form.errors)
        
except Exception as e:
    print(f"An error occurred: {e}")
