
import os

file_path = r'd:\Python\MultiTenant\apps\student_portal\urls.py'

try:
    with open(file_path, 'rb') as f:
        content = f.read()
        
    print(f"File size: {len(content)} bytes")
    
    # Check for null bytes
    if b'\x00' in content:
        print("Null bytes detected!")
        # Clean the file
        clean_content = content.replace(b'\x00', b'')
        
        # Check if it looks like UTF-16
        if content.startswith(b'\xff\xfe') or content.startswith(b'\xfe\xff'):
             print("BOM detected. Re-encoding...")
             try:
                decoded = content.decode('utf-16')
                clean_content = decoded.encode('utf-8')
             except:
                pass

        with open(file_path, 'wb') as f:
            f.write(clean_content)
        print("File cleaned.")
    else:
        print("No null bytes found. Checking for other issues.")
        try:
            content.decode('utf-8')
            print("File is valid UTF-8.")
        except UnicodeDecodeError as e:
            print(f"UTF-8 Decode Error: {e}")

except Exception as e:
    print(f"Error: {e}")
