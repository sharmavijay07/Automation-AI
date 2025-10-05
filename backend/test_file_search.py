"""
Quick Test Script for File Search
Tests if apple.pdf in Downloads can be found
"""

import os

# Test search locations
user_profile = os.environ.get('USERPROFILE', '')
print(f"User Profile: {user_profile}")

downloads = os.path.join(user_profile, 'Downloads')
print(f"Downloads Path: {downloads}")
print(f"Downloads exists: {os.path.exists(downloads)}")

# Test file path
test_file = os.path.join(downloads, 'apple.pdf')
print(f"\nTest File Path: {test_file}")
print(f"File exists: {os.path.exists(test_file)}")

# Test os.walk search (what we're now using)
if os.path.exists(downloads):
    print(f"\nSearching in Downloads with os.walk...")
    found_files = []
    max_depth = 3
    
    for root, dirs, files in os.walk(downloads):
        depth = root[len(downloads):].count(os.sep)
        if depth >= max_depth:
            dirs[:] = []
            continue
        
        for filename in files:
            if 'apple.pdf' in filename.lower():
                file_path = os.path.join(root, filename)
                found_files.append(file_path)
                print(f"✅ FOUND: {filename}")
                print(f"   Path: {file_path}")
                print(f"   Depth: {depth}")
    
    print(f"\nTotal files found: {len(found_files)}")
    
    if not found_files:
        print("❌ No files found. Checking if file exists at expected location...")
        if os.path.exists(test_file):
            print(f"⚠️  File exists but wasn't found in search!")
            print(f"   This shouldn't happen. Debug needed.")
        else:
            print(f"ℹ️  File doesn't exist at: {test_file}")
            print(f"   Please create it or check the actual location.")
else:
    print(f"❌ Downloads folder doesn't exist: {downloads}")

# List what's actually in Downloads
print(f"\n--- Files in Downloads (top level) ---")
try:
    items = os.listdir(downloads)
    pdf_files = [f for f in items if f.lower().endswith('.pdf')]
    print(f"PDF files found: {len(pdf_files)}")
    for pdf in pdf_files[:10]:  # Show first 10
        print(f"  - {pdf}")
except Exception as e:
    print(f"Error listing Downloads: {e}")
