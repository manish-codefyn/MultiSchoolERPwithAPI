import os

root_dir = r"d:\Python\MultiTenant\templates"
fix_count = 0

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith(".html"):
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                original_content = content
                
                if "|floatformatat" in content:
                    content = content.replace("|floatformatat", "|floatformat")
                    
                if content != original_content:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    fix_count += 1
                    print(f"Fixed floatformatat in: {filepath}")

            except Exception as e:
                print(f"Error processing {filepath}: {e}")

print(f"\nTotal files fixed: {fix_count}")
