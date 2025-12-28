import os
import glob
import re
from collections import defaultdict

BASE_DIR = r"d:/Python/MultiTenant/apps"

def find_duplicates():
    serializers = defaultdict(list)
    
    # Find all serializer files
    files = glob.glob(os.path.join(BASE_DIR, "**", "api", "serializers.py"), recursive=True)
    
    class_pattern = re.compile(r"class\s+(\w+)\(serializers\.ModelSerializer\):")
    
    for file_path in files:
        app_name = file_path.split(os.sep)[-3]
        
        with open(file_path, 'r') as f:
            content = f.read()
            matches = class_pattern.findall(content)
            
            for class_name in matches:
                serializers[class_name].append(app_name)
    
    # Print Duplicates
    duplicates_found = False
    for class_name, apps in serializers.items():
        if len(apps) > 1:
            duplicates_found = True
            print(f"Duplicate: {class_name} found in {apps}")

    if not duplicates_found:
        print("No duplicates found.")

if __name__ == "__main__":
    find_duplicates()
