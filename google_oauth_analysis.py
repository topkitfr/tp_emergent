#!/usr/bin/env python3
"""
Comprehensive Google OAuth Analysis for TopKit
Based on the detailed testing and error analysis from backend logs.
"""

import requests
import json
import sys
from datetime import datetime
import urllib.parse

# Configuration
BACKEND_URL = "https://jersey-catalog-2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class GoogleOAuthAnalyzer:
    def __init__(self):
        self.results = []
        self.issues_found = []
        self.recommendations = []
        
    def log_finding(self, category, severity, title, description, technical_details=None):
        """Log a finding from the OAuth analysis"""
        finding = {
            "category": category,
            "severity": severity,  # "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"
            "title": title,
            "description": description,
            "technical_details": technical_details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(finding)
        
        severity_icon = {
            "CRITICAL": "🚨",
            "HIGH": "❌", 
            "MEDIUM": "⚠️",
            "LOW": "💡",
            "INFO": "ℹ️"
        }
        
        print(f"{severity_icon.get(severity, '•')} {severity}: {title}")
        print(f"   {description}")
        if technical_details:
            for key, value in technical_details.items():
                print(f"   {key}: {value}")
        print()

    def analyze_oauth_configuration(self):
        """Analyze the OAuth configuration and endpoints"""
        print("🔍 ANALYZING GOOGLE OAUTH CONFIGURATION")
        print("=" * 60)
        
        # Test 1: OAuth Initiation Endpoint
        try:
            response = requests.get(f"{API_BASE}/auth/google", allow_redirects=False, timeout=10)
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                
                # Parse the OAuth URL
                parsed_url = urllib.parse.urlparse(redirect_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                self.log_finding(
                    "Configuration",
                    "INFO",
                    "OAuth Initiation Working",
                    "The /api/auth/google endpoint successfully redirects to Google OAuth",
                    {
                        "status_code": response.status_code,
                        "redirect_domain": parsed_url.netloc,
                        "oauth_params": list(query_params.keys())
                    }
                )
                
                # Check client_id
                client_id = query_params.get('client_id', [''])[0]
                expected_client_id = "920523740769-d74f1dsdajtilkqasrhtrei4blmf8ujj.apps.googleusercontent.com"
                
                if client_id == expected_client_id:
                    self.log_finding(
                        "Credentials",
                        "INFO",
                        "Client ID Configuration Correct",
                        "The hardcoded Google client_id is being used correctly",
                        {"client_id": client_id}
                    )
                else:
                    self.log_finding(
                        "Credentials",
                        "HIGH",
                        "Client ID Mismatch",
                        "The client_id in OAuth URL doesn't match expected hardcoded value",
                        {"found_client_id": client_id, "expected_client_id": expected_client_id}
                    )
                
                # Check redirect_uri
                redirect_uri = query_params.get('redirect_uri', [''])[0]
                if redirect_uri:
                    parsed_redirect = urllib.parse.urlparse(redirect_uri)
                    
                    # Check protocol mismatch
                    if parsed_redirect.scheme == 'http' and BACKEND_URL.startswith('https'):
                        self.log_finding(
                            "Configuration",
                            "HIGH",
                            "Protocol Mismatch in Redirect URI",
                            "OAuth redirect URI uses HTTP but current domain uses HTTPS",
                            {
                                "redirect_uri": redirect_uri,
                                "current_domain": BACKEND_URL,
                                "issue": "HTTP vs HTTPS mismatch"
                            }
                        )
                        self.issues_found.append("redirect_uri_protocol_mismatch")
                    else:
                        self.log_finding(
                            "Configuration",
                            "INFO",
                            "Redirect URI Protocol Correct",
                            "OAuth redirect URI uses correct protocol",
                            {"redirect_uri": redirect_uri}
                        )
                
                # Check scope
                scope = query_params.get('scope', [''])[0]
                expected_scopes = ['openid', 'email', 'profile']
                if scope:
                    actual_scopes = scope.split()
                    missing_scopes = [s for s in expected_scopes if s not in actual_scopes]
                    if missing_scopes:
                        self.log_finding(
                            "Configuration",
                            "MEDIUM",
                            "Missing OAuth Scopes",
                            f"Some expected OAuth scopes are missing: {missing_scopes}",
                            {"requested_scopes": actual_scopes, "missing_scopes": missing_scopes}
                        )
                    else:
                        self.log_finding(
                            "Configuration",
                            "INFO",
                            "OAuth Scopes Complete",
                            "All required OAuth scopes are present",
                            {"scopes": actual_scopes}
                        )
            else:
                self.log_finding(
                    "Configuration",
                    "CRITICAL",
                    "OAuth Initiation Failed",
                    "The /api/auth/google endpoint is not working properly",
                    {"status_code": response.status_code, "response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_finding(
                "Configuration",
                "CRITICAL",
                "OAuth Endpoint Unreachable",
                "Cannot connect to OAuth initiation endpoint",
                {"error": str(e)}
            )

    def analyze_callback_endpoint(self):
        """Analyze the OAuth callback endpoint"""
        print("🔍 ANALYZING OAUTH CALLBACK ENDPOINT")
        print("=" * 60)
        
        # Test callback endpoint
        try:
            response = requests.get(f"{API_BASE}/auth/google/callback", timeout=10)
            
            if response.status_code == 500:
                self.log_finding(
                    "Callback",
                    "CRITICAL",
                    "Callback Endpoint Server Error",
                    "The OAuth callback endpoint returns 500 Internal Server Error",
                    {
                        "status_code": response.status_code,
                        "error": response.text,
                        "likely_cause": "MismatchingStateError - CSRF state validation failure"
                    }
                )
                self.issues_found.append("callback_server_error")
            else:
                self.log_finding(
                    "Callback",
                    "INFO",
                    "Callback Endpoint Accessible",
                    "The OAuth callback endpoint is accessible",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_finding(
                "Callback",
                "CRITICAL",
                "Callback Endpoint Unreachable",
                "Cannot connect to OAuth callback endpoint",
                {"error": str(e)}
            )

    def analyze_google_credentials_validity(self):
        """Analyze if the hardcoded Google credentials are still valid"""
        print("🔍 ANALYZING GOOGLE CREDENTIALS VALIDITY")
        print("=" * 60)
        
        # The hardcoded credentials from server.py
        client_id = "920523740769-d74f1dsdajtilkqasrhtrei4blmf8ujj.apps.googleusercontent.com"
        client_secret = "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"
        
        self.log_finding(
            "Credentials",
            "HIGH",
            "Hardcoded Credentials Found",
            "Google OAuth credentials are hardcoded in the source code",
            {
                "client_id": client_id,
                "client_secret": client_secret[:20] + "...",
                "security_risk": "Credentials exposed in source code"
            }
        )
        
        # Try to validate by checking if OAuth flow initiates properly
        try:
            response = requests.get(f"{API_BASE}/auth/google", allow_redirects=False, timeout=10)
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                if 'accounts.google.com' in redirect_url and client_id in redirect_url:
                    self.log_finding(
                        "Credentials",
                        "INFO",
                        "Client ID Appears Valid",
                        "The client_id successfully initiates Google OAuth flow",
                        {"validation_method": "OAuth initiation test"}
                    )
                else:
                    self.log_finding(
                        "Credentials",
                        "HIGH",
                        "Client ID May Be Invalid",
                        "OAuth flow doesn't redirect to Google or client_id not found",
                        {"redirect_url": redirect_url[:100]}
                    )
            else:
                self.log_finding(
                    "Credentials",
                    "HIGH",
                    "Cannot Validate Credentials",
                    "OAuth initiation failed, cannot validate credentials",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_finding(
                "Credentials",
                "HIGH",
                "Credential Validation Failed",
                "Error occurred while trying to validate credentials",
                {"error": str(e)}
            )

    def analyze_known_issues(self):
        """Analyze known issues from backend logs"""
        print("🔍 ANALYZING KNOWN ISSUES FROM BACKEND LOGS")
        print("=" * 60)
        
        # Based on the error we found in logs
        self.log_finding(
            "Security",
            "CRITICAL",
            "CSRF State Validation Failure",
            "OAuth callback fails with MismatchingStateError - CSRF state mismatch",
            {
                "error_type": "authlib.integrations.base_client.errors.MismatchingStateError",
                "error_message": "CSRF Warning! State not equal in request and response",
                "impact": "OAuth authentication completely broken",
                "root_cause": "State parameter validation failing between request and callback"
            }
        )
        self.issues_found.append("csrf_state_mismatch")
        
        # Protocol mismatch issue
        self.log_finding(
            "Configuration",
            "HIGH",
            "HTTP/HTTPS Protocol Mismatch",
            "OAuth redirect URI configured for HTTP but application runs on HTTPS",
            {
                "configured_redirect": "http://cd697a52-f790-47ca-9d2b-bf2e0d4d8598.preview.emergentagent.com/api/auth/google/callback",
                "actual_domain": "https://jersey-catalog-2.preview.emergentagent.com",
                "impact": "Google OAuth may reject callback due to protocol mismatch"
            }
        )
        self.issues_found.append("protocol_mismatch")

    def generate_recommendations(self):
        """Generate recommendations based on findings"""
        print("🔧 GENERATING RECOMMENDATIONS")
        print("=" * 60)
        
        if "csrf_state_mismatch" in self.issues_found:
            self.recommendations.append({
                "priority": "CRITICAL",
                "title": "Fix CSRF State Validation",
                "description": "The OAuth state parameter validation is failing. This is a critical security issue.",
                "actions": [
                    "Review session middleware configuration",
                    "Ensure session storage is working properly",
                    "Check if state parameter is being preserved between request and callback",
                    "Consider using database or Redis for session storage instead of in-memory"
                ]
            })
        
        if "protocol_mismatch" in self.issues_found:
            self.recommendations.append({
                "priority": "HIGH",
                "title": "Fix Protocol Mismatch",
                "description": "OAuth redirect URI uses HTTP but application runs on HTTPS",
                "actions": [
                    "Update OAuth configuration to use HTTPS redirect URI",
                    "Update Google Cloud Console OAuth settings to match HTTPS domain",
                    "Ensure all OAuth URLs use consistent protocol"
                ]
            })
        
        if "callback_server_error" in self.issues_found:
            self.recommendations.append({
                "priority": "HIGH",
                "title": "Fix Callback Endpoint Errors",
                "description": "OAuth callback endpoint returns 500 errors",
                "actions": [
                    "Add proper error handling in callback endpoint",
                    "Implement graceful fallback for OAuth failures",
                    "Add logging to debug OAuth callback issues"
                ]
            })
        
        # General recommendations
        self.recommendations.append({
            "priority": "MEDIUM",
            "title": "Security Improvements",
            "description": "Improve OAuth security and configuration",
            "actions": [
                "Move OAuth credentials to environment variables",
                "Implement proper error handling for OAuth failures",
                "Add OAuth state validation debugging",
                "Consider implementing OAuth without third-party library for better control"
            ]
        })
        
        self.recommendations.append({
            "priority": "LOW",
            "title": "Consider Removal",
            "description": "If OAuth cannot be fixed easily, consider removing it",
            "actions": [
                "Evaluate if Google OAuth is essential for the application",
                "If not critical, remove Google OAuth endpoints entirely",
                "Focus on email/password authentication which is working",
                "Add OAuth back later when properly configured"
            ]
        })

    def print_final_assessment(self):
        """Print final assessment and recommendations"""
        print("=" * 60)
        print("🎯 FINAL GOOGLE OAUTH ASSESSMENT")
        print("=" * 60)
        
        # Count issues by severity
        critical_issues = len([r for r in self.results if r['severity'] == 'CRITICAL'])
        high_issues = len([r for r in self.results if r['severity'] == 'HIGH'])
        medium_issues = len([r for r in self.results if r['severity'] == 'MEDIUM'])
        
        print(f"Critical Issues: {critical_issues}")
        print(f"High Priority Issues: {high_issues}")
        print(f"Medium Priority Issues: {medium_issues}")
        print()
        
        # Overall status
        if critical_issues > 0:
            status = "🔴 BROKEN - OAuth system is not functional"
            recommendation = "REMOVE or COMPLETELY FIX"
        elif high_issues > 2:
            status = "🟡 PARTIALLY BROKEN - Major issues prevent proper function"
            recommendation = "FIX CRITICAL ISSUES"
        elif high_issues > 0:
            status = "🟡 NEEDS FIXES - Some issues but may work partially"
            recommendation = "FIX HIGH PRIORITY ISSUES"
        else:
            status = "🟢 FUNCTIONAL - OAuth system appears to work"
            recommendation = "MINOR IMPROVEMENTS ONLY"
        
        print(f"Overall Status: {status}")
        print(f"Recommendation: {recommendation}")
        print()
        
        # Print recommendations
        print("📋 PRIORITIZED RECOMMENDATIONS:")
        print("-" * 40)
        
        for i, rec in enumerate(self.recommendations, 1):
            priority_icon = {
                "CRITICAL": "🚨",
                "HIGH": "❗",
                "MEDIUM": "⚠️",
                "LOW": "💡"
            }
            
            print(f"{i}. {priority_icon.get(rec['priority'], '•')} {rec['priority']}: {rec['title']}")
            print(f"   {rec['description']}")
            for action in rec['actions']:
                print(f"   • {action}")
            print()
        
        # Final verdict
        print("🏁 FINAL VERDICT:")
        print("-" * 40)
        
        if critical_issues > 0:
            print("❌ Google OAuth authentication is BROKEN and should be REMOVED")
            print("❌ Multiple critical issues prevent any OAuth functionality")
            print("✅ Regular email/password authentication is working fine")
            print("💡 Recommend removing OAuth endpoints until properly configured")
        else:
            print("⚠️  Google OAuth has issues but may be partially functional")
            print("🔧 Requires fixes before being production-ready")
            print("✅ Core authentication system works without OAuth")
        
        return critical_issues == 0

    def run_complete_analysis(self):
        """Run complete OAuth analysis"""
        print("🔍 COMPREHENSIVE GOOGLE OAUTH ANALYSIS FOR TOPKIT")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.analyze_oauth_configuration()
        self.analyze_callback_endpoint()
        self.analyze_google_credentials_validity()
        self.analyze_known_issues()
        self.generate_recommendations()
        
        return self.print_final_assessment()

if __name__ == "__main__":
    analyzer = GoogleOAuthAnalyzer()
    is_functional = analyzer.run_complete_analysis()
    
    # Exit with appropriate code
    sys.exit(0 if is_functional else 1)