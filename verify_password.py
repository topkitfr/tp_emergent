#!/usr/bin/env python3
import bcrypt

# Hash from database
stored_hash = '$2b$12$I.Holw2XswnhfZSWEJm2k.UX/BZXCvbiWHUCpl6LYcZu3bdDJFqhW'
test_password = 'TopKitBeta2025!'

# Verify password
is_valid = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))

print(f"Password verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
print(f"Test password: {test_password}")
print(f"Stored hash: {stored_hash}")