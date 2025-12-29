
import os

file_path = r'd:\Python\MultiTenant\apps\student_portal\views.py'

try:
    with open(file_path, 'rb') as f:
        content = f.read()
        
    print(f"File size: {len(content)} bytes")
    
    # Check for null bytes
    if b'\x00' in content:
        print("Null bytes detected!")
        # Clean the file
        clean_content = content.replace(b'\x00', b'')
        
        with open(file_path, 'wb') as f:
            f.write(clean_content)
        print("File cleaned.")
    else:
        print("No null bytes found.")

except Exception as e:
    print(f"Error: {e}")
