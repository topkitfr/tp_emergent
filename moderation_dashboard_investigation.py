#!/usr/bin/env python3
"""
TopKit Moderation Dashboard Bug Investigation - CRITICAL ISSUE

**USER REPORT - MODERATION DASHBOARD DISCREPANCY:**
1. Overview tab shows "30 Pending Review" 
2. Pending Review tab shows "All Caught Up! No contributions pending review"  
3. User created a brand contribution but can't see it anywhere
4. Clear mismatch between stats and actual displayed data

**INVESTIGATION FOCUS:**
1. **Moderation Stats API**: Test GET /api/contributions-v2/admin/moderation-stats
2. **Pending Contributions API**: Test GET /api/contributions-v2/?status=pending_review vs GET /api/contributions-v2/?status=pending
3. **Recent Brand Contribution**: Check contributions_v2 collection for recent brand submissions
4. **API Endpoint Discrepancy**: Compare results between different contribution endpoints
5. **Status Value Investigation**: List all unique status values in contributions_v2 collection

**AUTHENTICATION:** emergency.admin@topkit.test / EmergencyAdmin2025!

**EXPECTED TO FIND:**
- Root cause of the 30 vs 0 discrepancy
- The missing brand contribution
- Inconsistent status values or API endpoint issues
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
from collections import Counter

# Configuration
BACKEND_URL = "https://jersey-pricing.preview.emergentagent.com/api"

# Admin Credentials
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class ModerationDashboardInvestigation:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.admin_user_data = None
        self.investigation_results = []
        
    def log_finding(self, investigation_area, success, message, details=None):
        """Log investigation finding"""
        result = {
            "area": investigation_area,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.investigation_results.append(result)
        
        status = "✅ FOUND" if success else "❌ ISSUE"
        print(f"{status} {investigation_area}: {message}")
        if details and isinstance(details, dict):
            for key, value in details.items():
                print(f"   {key}: {value}")
        elif details:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate with emergency admin credentials"""
        try:
            print(f"\n🔐 EMERGENCY ADMIN AUTHENTICATION")
            print("=" * 60)
            print(f"   Email: {ADMIN_CREDENTIALS['email']}")
            print(f"   Password: {ADMIN_CREDENTIALS['password']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_user_data = data.get('user', {})
                self.auth_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_finding("Authentication", True, 
                               f"Emergency admin authentication successful")
                print(f"      User ID: {self.admin_user_data.get('id')}")
                print(f"      Name: {self.admin_user_data.get('name')}")
                print(f"      Email: {self.admin_user_data.get('email')}")
                print(f"      Role: {self.admin_user_data.get('role')}")
                
                return True
                
            else:
                self.log_finding("Authentication", False, 
                               f"Emergency admin authentication failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_finding("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def investigate_moderation_stats_api(self):
        """Investigate the moderation stats API endpoint"""
        try:
            print(f"\n📊 INVESTIGATING MODERATION STATS API")
            print("=" * 80)
            print("Testing GET /api/contributions-v2/admin/moderation-stats...")
            
            # Test moderation stats endpoint
            stats_response = self.session.get(f"{BACKEND_URL}/contributions-v2/admin/moderation-stats", timeout=10)
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                print(f"         ✅ Moderation stats API accessible")
                print(f"            Response: {json.dumps(stats_data, indent=2)}")
                
                # Extract key stats
                pending_count = stats_data.get('pending_review', 0)
                total_count = stats_data.get('total', 0)
                approved_count = stats_data.get('approved', 0)
                rejected_count = stats_data.get('rejected', 0)
                
                self.log_finding("Moderation Stats API", True, 
                               f"Stats API working - shows {pending_count} pending review",
                               {
                                   "pending_review": pending_count,
                                   "total": total_count,
                                   "approved": approved_count,
                                   "rejected": rejected_count
                               })
                
                return True, stats_data
                
            else:
                print(f"         ❌ Moderation stats API failed - Status {stats_response.status_code}")
                print(f"            Error: {stats_response.text}")
                
                self.log_finding("Moderation Stats API", False, 
                               f"Stats API failed - Status {stats_response.status_code}", stats_response.text)
                return False, None
                
        except Exception as e:
            self.log_finding("Moderation Stats API", False, f"Exception: {str(e)}")
            return False, None
    
    def investigate_pending_contributions_apis(self):
        """Investigate different pending contributions API endpoints"""
        try:
            print(f"\n🔍 INVESTIGATING PENDING CONTRIBUTIONS APIs")
            print("=" * 80)
            
            # Test different status parameters
            status_tests = [
                ("pending_review", "GET /api/contributions-v2/?status=pending_review"),
                ("pending", "GET /api/contributions-v2/?status=pending"),
                (None, "GET /api/contributions-v2/ (all contributions)")
            ]
            
            api_results = {}
            
            for status_value, description in status_tests:
                print(f"      Testing {description}...")
                
                # Build URL
                if status_value:
                    url = f"{BACKEND_URL}/contributions-v2/?status={status_value}"
                else:
                    url = f"{BACKEND_URL}/contributions-v2/"
                
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else 0
                    
                    print(f"         ✅ {description} - {count} contributions found")
                    
                    # Analyze the contributions
                    if isinstance(data, list) and data:
                        entity_types = Counter([contrib.get('entity_type') for contrib in data])
                        statuses = Counter([contrib.get('status') for contrib in data])
                        
                        print(f"            Entity types: {dict(entity_types)}")
                        print(f"            Statuses: {dict(statuses)}")
                        
                        # Look for recent contributions
                        recent_contributions = []
                        today = datetime.now().date()
                        yesterday = today - timedelta(days=1)
                        
                        for contrib in data:
                            submitted_at = contrib.get('submitted_at')
                            if submitted_at:
                                try:
                                    # Parse the date
                                    if 'T' in submitted_at:
                                        contrib_date = datetime.fromisoformat(submitted_at.replace('Z', '+00:00')).date()
                                    else:
                                        contrib_date = datetime.fromisoformat(submitted_at).date()
                                    
                                    if contrib_date >= yesterday:
                                        recent_contributions.append({
                                            'id': contrib.get('id'),
                                            'entity_type': contrib.get('entity_type'),
                                            'status': contrib.get('status'),
                                            'submitted_at': submitted_at
                                        })
                                except:
                                    pass
                        
                        if recent_contributions:
                            print(f"            Recent contributions (last 2 days): {len(recent_contributions)}")
                            for contrib in recent_contributions[:5]:  # Show first 5
                                print(f"              - {contrib['entity_type']} ({contrib['status']}) - {contrib['submitted_at']}")
                    
                    api_results[status_value or 'all'] = {
                        'count': count,
                        'data': data,
                        'success': True
                    }
                    
                else:
                    print(f"         ❌ {description} failed - Status {response.status_code}")
                    print(f"            Error: {response.text}")
                    
                    api_results[status_value or 'all'] = {
                        'count': 0,
                        'data': None,
                        'success': False,
                        'error': response.text
                    }
            
            # Compare results
            print(f"\n      📊 API COMPARISON ANALYSIS:")
            pending_review_count = api_results.get('pending_review', {}).get('count', 0)
            pending_count = api_results.get('pending', {}).get('count', 0)
            all_count = api_results.get('all', {}).get('count', 0)
            
            print(f"         pending_review status: {pending_review_count} contributions")
            print(f"         pending status: {pending_count} contributions")
            print(f"         all contributions: {all_count} contributions")
            
            # Check for discrepancy
            if pending_review_count != pending_count:
                print(f"         🚨 DISCREPANCY FOUND: pending_review ({pending_review_count}) != pending ({pending_count})")
                
                self.log_finding("Pending Contributions APIs", False, 
                               f"Status discrepancy found - pending_review: {pending_review_count}, pending: {pending_count}",
                               {
                                   "pending_review_count": pending_review_count,
                                   "pending_count": pending_count,
                                   "all_count": all_count
                               })
            else:
                self.log_finding("Pending Contributions APIs", True, 
                               f"Status values consistent - both show {pending_review_count} contributions")
            
            return True, api_results
            
        except Exception as e:
            self.log_finding("Pending Contributions APIs", False, f"Exception: {str(e)}")
            return False, None
    
    def investigate_brand_contributions(self):
        """Investigate recent brand contributions specifically"""
        try:
            print(f"\n🏢 INVESTIGATING BRAND CONTRIBUTIONS")
            print("=" * 80)
            print("Looking for recent brand contributions...")
            
            # Get all contributions and filter for brands
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/", timeout=10)
            
            if response.status_code == 200:
                all_contributions = response.json()
                
                # Filter for brand contributions
                brand_contributions = [
                    contrib for contrib in all_contributions 
                    if contrib.get('entity_type') == 'brand'
                ]
                
                print(f"         Total contributions: {len(all_contributions)}")
                print(f"         Brand contributions: {len(brand_contributions)}")
                
                if brand_contributions:
                    print(f"         📋 BRAND CONTRIBUTIONS FOUND:")
                    
                    for i, contrib in enumerate(brand_contributions, 1):
                        print(f"            {i}. ID: {contrib.get('id')}")
                        print(f"               Status: {contrib.get('status')}")
                        print(f"               Submitted: {contrib.get('submitted_at')}")
                        print(f"               Submitted by: {contrib.get('submitted_by')}")
                        print(f"               Entity ID: {contrib.get('entity_id')}")
                        
                        # Check if this is recent (last 7 days)
                        submitted_at = contrib.get('submitted_at')
                        if submitted_at:
                            try:
                                if 'T' in submitted_at:
                                    contrib_date = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                                else:
                                    contrib_date = datetime.fromisoformat(submitted_at)
                                
                                days_ago = (datetime.now(contrib_date.tzinfo) - contrib_date).days
                                print(f"               Age: {days_ago} days ago")
                                
                                if days_ago <= 1:
                                    print(f"               🆕 RECENT CONTRIBUTION!")
                            except:
                                print(f"               Age: Could not parse date")
                        print()
                    
                    # Check status distribution
                    brand_statuses = Counter([contrib.get('status') for contrib in brand_contributions])
                    print(f"         📊 BRAND CONTRIBUTION STATUS BREAKDOWN:")
                    for status, count in brand_statuses.items():
                        print(f"            {status}: {count}")
                    
                    self.log_finding("Brand Contributions", True, 
                                   f"Found {len(brand_contributions)} brand contributions",
                                   {
                                       "total_brand_contributions": len(brand_contributions),
                                       "status_breakdown": dict(brand_statuses)
                                   })
                    
                    return True, brand_contributions
                    
                else:
                    print(f"         ⚠️ No brand contributions found")
                    
                    self.log_finding("Brand Contributions", False, 
                                   "No brand contributions found in system")
                    
                    return False, []
                    
            else:
                print(f"         ❌ Failed to get contributions - Status {response.status_code}")
                print(f"            Error: {response.text}")
                
                self.log_finding("Brand Contributions", False, 
                               f"Failed to get contributions - Status {response.status_code}")
                
                return False, None
                
        except Exception as e:
            self.log_finding("Brand Contributions", False, f"Exception: {str(e)}")
            return False, None
    
    def investigate_status_values(self):
        """Investigate all unique status values in contributions_v2 collection"""
        try:
            print(f"\n🔍 INVESTIGATING STATUS VALUES")
            print("=" * 80)
            print("Analyzing all unique status values in contributions...")
            
            # Get all contributions
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/", timeout=10)
            
            if response.status_code == 200:
                all_contributions = response.json()
                
                # Extract all status values
                all_statuses = [contrib.get('status') for contrib in all_contributions if contrib.get('status')]
                unique_statuses = list(set(all_statuses))
                status_counts = Counter(all_statuses)
                
                print(f"         Total contributions analyzed: {len(all_contributions)}")
                print(f"         Unique status values found: {len(unique_statuses)}")
                print()
                
                print(f"         📊 STATUS VALUE BREAKDOWN:")
                for status in sorted(unique_statuses):
                    count = status_counts[status]
                    percentage = (count / len(all_statuses)) * 100 if all_statuses else 0
                    print(f"            '{status}': {count} ({percentage:.1f}%)")
                
                # Check for inconsistencies
                print(f"\n         🔍 STATUS CONSISTENCY ANALYSIS:")
                
                # Look for variations of "pending"
                pending_variations = [status for status in unique_statuses if 'pending' in status.lower()]
                if len(pending_variations) > 1:
                    print(f"            🚨 MULTIPLE PENDING STATUS VARIATIONS FOUND:")
                    for variation in pending_variations:
                        count = status_counts[variation]
                        print(f"               '{variation}': {count} contributions")
                    
                    self.log_finding("Status Values", False, 
                                   f"Multiple pending status variations found: {pending_variations}",
                                   {
                                       "pending_variations": pending_variations,
                                       "variation_counts": {var: status_counts[var] for var in pending_variations}
                                   })
                else:
                    print(f"            ✅ Consistent pending status usage")
                
                # Look for variations of other statuses
                approved_variations = [status for status in unique_statuses if 'approved' in status.lower()]
                rejected_variations = [status for status in unique_statuses if 'rejected' in status.lower()]
                
                print(f"            Approved variations: {approved_variations}")
                print(f"            Rejected variations: {rejected_variations}")
                
                self.log_finding("Status Values", True, 
                               f"Found {len(unique_statuses)} unique status values",
                               {
                                   "unique_statuses": unique_statuses,
                                   "status_counts": dict(status_counts),
                                   "pending_variations": pending_variations
                               })
                
                return True, {
                    'unique_statuses': unique_statuses,
                    'status_counts': dict(status_counts),
                    'pending_variations': pending_variations
                }
                
            else:
                print(f"         ❌ Failed to get contributions - Status {response.status_code}")
                
                self.log_finding("Status Values", False, 
                               f"Failed to get contributions - Status {response.status_code}")
                
                return False, None
                
        except Exception as e:
            self.log_finding("Status Values", False, f"Exception: {str(e)}")
            return False, None
    
    def investigate_api_endpoint_discrepancies(self):
        """Compare results between different contribution endpoints"""
        try:
            print(f"\n🔄 INVESTIGATING API ENDPOINT DISCREPANCIES")
            print("=" * 80)
            print("Comparing different contribution API endpoints...")
            
            endpoints_to_test = [
                ("/contributions-v2/", "All Contributions V2"),
                ("/contributions-v2/?status=pending_review", "Pending Review V2"),
                ("/contributions-v2/?status=pending", "Pending V2"),
                ("/contributions-v2/?status=approved", "Approved V2"),
                ("/contributions-v2/?status=rejected", "Rejected V2")
            ]
            
            endpoint_results = {}
            
            for endpoint, description in endpoints_to_test:
                print(f"      Testing {description} ({endpoint})...")
                
                response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else 0
                    
                    print(f"         ✅ {description}: {count} contributions")
                    
                    # Analyze entity types
                    if isinstance(data, list) and data:
                        entity_types = Counter([contrib.get('entity_type') for contrib in data])
                        print(f"            Entity types: {dict(entity_types)}")
                    
                    endpoint_results[endpoint] = {
                        'count': count,
                        'data': data,
                        'success': True
                    }
                    
                else:
                    print(f"         ❌ {description} failed - Status {response.status_code}")
                    endpoint_results[endpoint] = {
                        'count': 0,
                        'success': False,
                        'error': response.text
                    }
            
            # Cross-check results
            print(f"\n      🔍 CROSS-ENDPOINT ANALYSIS:")
            
            all_count = endpoint_results.get('/contributions-v2/', {}).get('count', 0)
            pending_review_count = endpoint_results.get('/contributions-v2/?status=pending_review', {}).get('count', 0)
            pending_count = endpoint_results.get('/contributions-v2/?status=pending', {}).get('count', 0)
            approved_count = endpoint_results.get('/contributions-v2/?status=approved', {}).get('count', 0)
            rejected_count = endpoint_results.get('/contributions-v2/?status=rejected', {}).get('count', 0)
            
            calculated_total = pending_review_count + pending_count + approved_count + rejected_count
            
            print(f"         All contributions: {all_count}")
            print(f"         Pending review: {pending_review_count}")
            print(f"         Pending: {pending_count}")
            print(f"         Approved: {approved_count}")
            print(f"         Rejected: {rejected_count}")
            print(f"         Calculated total: {calculated_total}")
            
            # Check for discrepancies
            discrepancies = []
            
            if all_count != calculated_total:
                discrepancy = f"Total mismatch: all ({all_count}) != calculated ({calculated_total})"
                discrepancies.append(discrepancy)
                print(f"         🚨 {discrepancy}")
            
            if pending_review_count == 0 and pending_count > 0:
                discrepancy = f"Pending status mismatch: pending_review (0) vs pending ({pending_count})"
                discrepancies.append(discrepancy)
                print(f"         🚨 {discrepancy}")
            
            if discrepancies:
                self.log_finding("API Endpoint Discrepancies", False, 
                               f"Found {len(discrepancies)} discrepancies",
                               {
                                   "discrepancies": discrepancies,
                                   "endpoint_counts": {
                                       "all": all_count,
                                       "pending_review": pending_review_count,
                                       "pending": pending_count,
                                       "approved": approved_count,
                                       "rejected": rejected_count
                                   }
                               })
            else:
                self.log_finding("API Endpoint Discrepancies", True, 
                               "No discrepancies found between endpoints")
            
            return True, endpoint_results
            
        except Exception as e:
            self.log_finding("API Endpoint Discrepancies", False, f"Exception: {str(e)}")
            return False, None
    
    def run_comprehensive_investigation(self):
        """Run comprehensive moderation dashboard investigation"""
        print("\n🚀 MODERATION DASHBOARD BUG INVESTIGATION")
        print("Investigating the 30 vs 0 pending contributions discrepancy")
        print("=" * 80)
        
        investigation_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authentication...")
        auth_success = self.authenticate_admin()
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return False
        
        # Step 2: Investigate Moderation Stats API
        print("\n2️⃣ Investigating Moderation Stats API...")
        stats_success, stats_data = self.investigate_moderation_stats_api()
        investigation_results.append(stats_success)
        
        # Step 3: Investigate Pending Contributions APIs
        print("\n3️⃣ Investigating Pending Contributions APIs...")
        pending_success, pending_data = self.investigate_pending_contributions_apis()
        investigation_results.append(pending_success)
        
        # Step 4: Investigate Brand Contributions
        print("\n4️⃣ Investigating Brand Contributions...")
        brand_success, brand_data = self.investigate_brand_contributions()
        investigation_results.append(brand_success)
        
        # Step 5: Investigate Status Values
        print("\n5️⃣ Investigating Status Values...")
        status_success, status_data = self.investigate_status_values()
        investigation_results.append(status_success)
        
        # Step 6: Investigate API Endpoint Discrepancies
        print("\n6️⃣ Investigating API Endpoint Discrepancies...")
        endpoint_success, endpoint_data = self.investigate_api_endpoint_discrepancies()
        investigation_results.append(endpoint_success)
        
        return investigation_results
    
    def print_investigation_summary(self):
        """Print final investigation summary with root cause analysis"""
        print("\n📊 MODERATION DASHBOARD INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_investigations = len(self.investigation_results)
        successful_investigations = len([r for r in self.investigation_results if r['success']])
        failed_investigations = total_investigations - successful_investigations
        
        print(f"Total investigations: {total_investigations}")
        print(f"Successful: {successful_investigations} ✅")
        print(f"Issues found: {failed_investigations} ❌")
        
        # Key findings
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        # Look for specific issues
        issues_found = [r for r in self.investigation_results if not r['success']]
        
        if issues_found:
            print(f"  🚨 CRITICAL ISSUES IDENTIFIED ({len(issues_found)}):")
            for issue in issues_found:
                print(f"     • {issue['area']}: {issue['message']}")
                if issue.get('details'):
                    if isinstance(issue['details'], dict):
                        for key, value in issue['details'].items():
                            print(f"       - {key}: {value}")
        
        # Specific analysis for the 30 vs 0 discrepancy
        print(f"\n🎯 MODERATION DASHBOARD DISCREPANCY DIAGNOSIS:")
        
        # Check for status inconsistencies
        status_issue = next((r for r in self.investigation_results if r['area'] == 'Status Values' and not r['success']), None)
        if status_issue:
            print(f"  ❌ STATUS VALUE INCONSISTENCY FOUND:")
            print(f"     - Multiple pending status variations detected")
            print(f"     - This could cause the 30 vs 0 discrepancy")
            print(f"     - Frontend may be using different status values than backend")
        
        # Check for API discrepancies
        api_issue = next((r for r in self.investigation_results if r['area'] == 'API Endpoint Discrepancies' and not r['success']), None)
        if api_issue:
            print(f"  ❌ API ENDPOINT DISCREPANCY FOUND:")
            print(f"     - Different endpoints returning different counts")
            print(f"     - Overview tab may be using different API than Pending Review tab")
        
        # Check for missing brand contributions
        brand_issue = next((r for r in self.investigation_results if r['area'] == 'Brand Contributions' and not r['success']), None)
        if brand_issue:
            print(f"  ❌ MISSING BRAND CONTRIBUTIONS:")
            print(f"     - User's brand contribution not found in system")
            print(f"     - Contribution may have failed to save or has wrong status")
        
        # Provide recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if status_issue:
            print(f"  1. STANDARDIZE STATUS VALUES:")
            print(f"     - Ensure all pending contributions use 'pending_review' status")
            print(f"     - Update any contributions with 'pending' to 'pending_review'")
            print(f"     - Verify frontend uses consistent status values")
        
        if api_issue:
            print(f"  2. FIX API ENDPOINT CONSISTENCY:")
            print(f"     - Ensure moderation stats API uses same logic as contributions API")
            print(f"     - Verify filtering logic matches between endpoints")
        
        if brand_issue:
            print(f"  3. INVESTIGATE BRAND CONTRIBUTION CREATION:")
            print(f"     - Check brand contribution form submission logic")
            print(f"     - Verify contributions are saved with correct status")
            print(f"     - Test brand contribution creation process")
        
        print(f"\n" + "=" * 80)

def main():
    """Main function to run the moderation dashboard investigation"""
    investigator = ModerationDashboardInvestigation()
    
    # Run the comprehensive investigation
    investigation_results = investigator.run_comprehensive_investigation()
    
    # Print comprehensive summary
    investigator.print_investigation_summary()
    
    # Return overall success (True if no critical issues found)
    return all(investigation_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)