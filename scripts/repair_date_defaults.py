import os
import glob
import re

BASE_DIR = r"d:/Python/MultiTenant/apps"

def fix_datefield_defaults():
    files = glob.glob(os.path.join(BASE_DIR, "**", "models.py"), recursive=True)
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.splitlines()
        new_lines = []
        modified = False
        
        for line in lines:
            if "models.DateField" in line and "default=timezone.now" in line:
                # Carefully replace only the default arg if possible, 
                # but valid string replace is safer if we match specific context
                if "timezone.now" in line and "timezone.localdate" not in line:
                     new_line = line.replace("default=timezone.now", "default=timezone.localdate")
                     new_lines.append(new_line)
                     modified = True
                else:
                     new_lines.append(line)
            else:
                new_lines.append(line)
                
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_datefield_defaults()
