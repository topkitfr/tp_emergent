#!/usr/bin/env python3
"""
Admin User Check - Use admin privileges to check user account status
"""

import requests
import json
import sys
import os

# Configuration - Use environment variable with fallback
BACKEND_URL = os.environ.get('BACKEND_URL', os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')) + '/api'
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
TARGET_USER_EMAIL = "steinmetzlivio@gmail.com"

# Rest of the file remains the same...
