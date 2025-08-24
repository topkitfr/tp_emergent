#!/usr/bin/env python3
"""
Script to fix all hardcoded URLs in email service files
"""
import os
import re

def fix_hardcoded_urls():
    """Fix hardcoded URLs in all backend email service files"""
    
    email_files = [
        '/app/backend/email_service.py',
        '/app/backend/email_service_marketing.py', 
        '/app/backend/email_service_community.py',
        '/app/backend/email_service_extended.py'
    ]
    
    # Pattern to match hardcoded URLs
    url_pattern = r'https://topkit-ui-fix\.preview\.emergentagent\.com'
    replacement = '{os.environ.get("FRONTEND_URL", "https://topkit-ui-fix.preview.emergentagent.com")}'
    
    for file_path in email_files:
        if os.path.exists(file_path):
            print(f"Fixing URLs in {file_path}")
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Find all hardcoded URLs and replace them
            lines = content.split('\n')
            modified = False
            
            for i, line in enumerate(lines):
                # Skip lines that already use environment variables
                if 'os.environ.get(' in line and 'FRONTEND_URL' in line:
                    continue
                    
                # Replace hardcoded URLs with environment variable
                if 'https://topkit-ui-fix.preview.emergentagent.com' in line:
                    # Handle different cases
                    if 'href="https://topkit-ui-fix.preview.emergentagent.com"' in line:
                        lines[i] = line.replace(
                            'href="https://topkit-ui-fix.preview.emergentagent.com"',
                            f'href="{{{replacement}}}"'
                        )
                        modified = True
                    elif 'href="https://topkit-ui-fix.preview.emergentagent.com/' in line:
                        # Extract the path after the domain
                        path_match = re.search(r'href="https://topkit-ui-fix\.preview\.emergentagent\.com(/[^"]*)"', line)
                        if path_match:
                            path = path_match.group(1)
                            lines[i] = line.replace(
                                f'href="https://topkit-ui-fix.preview.emergentagent.com{path}"',
                                f'href="{{{replacement}}}{path}"'
                            )
                            modified = True
                    elif ': https://topkit-ui-fix.preview.emergentagent.com/' in line:
                        # Handle text URLs like "Notre guide : https://..."
                        path_match = re.search(r': https://topkit-ui-fix\.preview\.emergentagent\.com(/\S+)', line)
                        if path_match:
                            path = path_match.group(1)
                            lines[i] = line.replace(
                                f': https://topkit-ui-fix.preview.emergentagent.com{path}',
                                f': {{{replacement}}}{path}'
                            )
                            modified = True
            
            if modified:
                # Write back the modified content
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                print(f"✅ Fixed URLs in {file_path}")
            else:
                print(f"ℹ️ No changes needed in {file_path}")
        else:
            print(f"❌ File not found: {file_path}")

if __name__ == "__main__":
    fix_hardcoded_urls()
    print("🎉 All hardcoded URLs fixed!")