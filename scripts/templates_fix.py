import os

root_dir = r"d:\Python\MultiTenant\templates"
floatform_fix_count = 0
sub_usages = []
split_usages = []

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith(".html"):
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                original_content = content
                
                # Fix floatform -> floatformat
                if "|floatform" in content:
                    content = content.replace("|floatform", "|floatformat")
                    
                if content != original_content:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    floatform_fix_count += 1
                    print(f"Fixed floatform in: {filepath}")

                # Check for sub and split
                if "|sub:" in content or "|sub " in content:
                    sub_usages.append(filepath)
                
                if "|split:" in content or "|split " in content:
                    split_usages.append(filepath)

            except Exception as e:
                print(f"Error processing {filepath}: {e}")

print(f"\nTotal files with floatform fixed: {floatform_fix_count}")
print(f"\nFiles using 'sub' filter ({len(sub_usages)}):")
for f in sub_usages:
    print(f"- {f}")

print(f"\nFiles using 'split' filter ({len(split_usages)}):")
for f in split_usages:
    print(f"- {f}")
