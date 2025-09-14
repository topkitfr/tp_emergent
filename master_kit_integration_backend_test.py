#!/usr/bin/env python3
"""
TopKit Backend Testing - Master Kit Integration Workflow Investigation
Testing the master kit -> master jersey integration workflow to identify why master kits 
are not appearing in the catalogue after approval.

Focus Areas:
1. Check if master kits are being created in contributions first
2. Check the master jerseys collection directly  
3. Test the contribution approval workflow
4. Check if the issue is in the integration process
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class MasterKitIntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_admin(self):
        """Authenticate admin user and get JWT token"""
        try:
            auth_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Successfully authenticated admin user. Token length: {len(self.admin_token)}"
                    )
                    return True
                else:
                    self.log_result("Admin Authentication", False, "", "No token in response")
                    return False
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    "", 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e))
            return False

    def test_master_kit_contributions(self):
        """Test 1: Check if master kits are being created in contributions first"""
        try:
            # Test GET /api/contributions-v2?entity_type=master_kit
            response = self.session.get(f"{API_BASE}/contributions-v2/", params={"entity_type": "master_kit"})
            
            if response.status_code == 200:
                data = response.json()
                contributions = data if isinstance(data, list) else data.get('contributions', [])
                
                # Filter for master_kit contributions
                master_kit_contributions = [c for c in contributions if c.get('entity_type') == 'master_kit']
                
                # Look for approved master kit contributions
                approved_master_kits = [c for c in master_kit_contributions if c.get('status') == 'APPROVED']
                
                self.log_result(
                    "Master Kit Contributions Check",
                    True,
                    f"Found {len(master_kit_contributions)} master kit contributions total, {len(approved_master_kits)} approved"
                )
                
                # Log details of approved master kits
                if approved_master_kits:
                    print("   📋 Approved Master Kit Contributions:")
                    for kit in approved_master_kits:
                        print(f"      - ID: {kit.get('id')}, Status: {kit.get('status')}, Integrated: {kit.get('integrated', 'N/A')}")
                        print(f"        Title: {kit.get('title', 'N/A')}")
                        if kit.get('changes'):
                            changes = kit.get('changes', {})
                            print(f"        Team: {changes.get('team_name', 'N/A')}, Brand: {changes.get('brand_name', 'N/A')}")
                            print(f"        Season: {changes.get('season', 'N/A')}, Type: {changes.get('kit_type', 'N/A')}")
                
                return {
                    'total_master_kit_contributions': len(master_kit_contributions),
                    'approved_master_kit_contributions': len(approved_master_kits),
                    'approved_contributions': approved_master_kits
                }
            else:
                self.log_result(
                    "Master Kit Contributions Check",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Master Kit Contributions Check", False, "", str(e))
            return None

    def test_master_jerseys_collection(self):
        """Test 2: Check the master jerseys collection directly"""
        try:
            # Test GET /api/master-jerseys
            response = self.session.get(f"{API_BASE}/master-jerseys")
            
            if response.status_code == 200:
                data = response.json()
                master_jerseys = data if isinstance(data, list) else data.get('master_jerseys', [])
                
                self.log_result(
                    "Master Jerseys Collection Check",
                    True,
                    f"Found {len(master_jerseys)} master jerseys in collection"
                )
                
                # Log details of master jerseys
                if master_jerseys:
                    print("   📋 Master Jerseys in Collection:")
                    for jersey in master_jerseys:
                        print(f"      - ID: {jersey.get('id')}, TopKit Ref: {jersey.get('topkit_reference', 'N/A')}")
                        print(f"        Team: {jersey.get('team_name', 'N/A')}, Brand: {jersey.get('brand_name', 'N/A')}")
                        print(f"        Season: {jersey.get('season', 'N/A')}, Type: {jersey.get('jersey_type', 'N/A')}")
                        print(f"        Created: {jersey.get('created_at', 'N/A')}")
                
                return {
                    'total_master_jerseys': len(master_jerseys),
                    'master_jerseys': master_jerseys
                }
            else:
                self.log_result(
                    "Master Jerseys Collection Check",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Master Jerseys Collection Check", False, "", str(e))
            return None

    def test_master_kits_collection(self):
        """Test 2b: Check the master kits collection directly"""
        try:
            # Test GET /api/master-kits
            response = self.session.get(f"{API_BASE}/master-kits")
            
            if response.status_code == 200:
                data = response.json()
                master_kits = data if isinstance(data, list) else data.get('master_kits', [])
                
                self.log_result(
                    "Master Kits Collection Check",
                    True,
                    f"Found {len(master_kits)} master kits in collection"
                )
                
                # Log details of master kits
                if master_kits:
                    print("   📋 Master Kits in Collection:")
                    for kit in master_kits:
                        print(f"      - ID: {kit.get('id')}, TopKit Ref: {kit.get('topkit_reference', 'N/A')}")
                        print(f"        Team: {kit.get('team_name', 'N/A')}, Brand: {kit.get('brand_name', 'N/A')}")
                        print(f"        Season: {kit.get('season', 'N/A')}, Type: {kit.get('kit_type', 'N/A')}")
                        print(f"        Created: {kit.get('created_at', 'N/A')}")
                
                return {
                    'total_master_kits': len(master_kits),
                    'master_kits': master_kits
                }
            else:
                self.log_result(
                    "Master Kits Collection Check",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Master Kits Collection Check", False, "", str(e))
            return None

    def test_contribution_approval_workflow(self, approved_contributions):
        """Test 3: Test the contribution approval workflow"""
        try:
            if not approved_contributions:
                self.log_result(
                    "Contribution Approval Workflow",
                    False,
                    "",
                    "No approved master kit contributions found to test workflow"
                )
                return None
            
            # Check if approved contributions have been integrated
            integrated_contributions = []
            not_integrated_contributions = []
            
            for contrib in approved_contributions:
                if contrib.get('integrated') == True:
                    integrated_contributions.append(contrib)
                else:
                    not_integrated_contributions.append(contrib)
            
            self.log_result(
                "Contribution Approval Workflow",
                True,
                f"Workflow analysis: {len(integrated_contributions)} integrated, {len(not_integrated_contributions)} not integrated"
            )
            
            # Log details
            if integrated_contributions:
                print("   ✅ Integrated Contributions:")
                for contrib in integrated_contributions:
                    print(f"      - ID: {contrib.get('id')}, Status: {contrib.get('status')}")
            
            if not_integrated_contributions:
                print("   ⚠️ Not Integrated Contributions:")
                for contrib in not_integrated_contributions:
                    print(f"      - ID: {contrib.get('id')}, Status: {contrib.get('status')}")
            
            return {
                'integrated_count': len(integrated_contributions),
                'not_integrated_count': len(not_integrated_contributions),
                'integrated_contributions': integrated_contributions,
                'not_integrated_contributions': not_integrated_contributions
            }
            
        except Exception as e:
            self.log_result("Contribution Approval Workflow", False, "", str(e))
            return None

    def test_integration_process_analysis(self, approved_contributions, master_jerseys, master_kits):
        """Test 4: Check if the issue is in the integration process"""
        try:
            if not approved_contributions:
                self.log_result(
                    "Integration Process Analysis",
                    False,
                    "",
                    "No approved master kit contributions found for integration analysis"
                )
                return None
            
            # Cross-reference approved contributions with master jerseys and master kits
            integration_matches = []
            missing_integrations = []
            
            for contrib in approved_contributions:
                contrib_changes = contrib.get('changes', {})
                contrib_team = contrib_changes.get('team_name', '')
                contrib_brand = contrib_changes.get('brand_name', '')
                contrib_season = contrib_changes.get('season', '')
                contrib_type = contrib_changes.get('kit_type', '')
                
                # Look for matching master jersey or master kit
                found_match = False
                
                # Check master jerseys
                for jersey in master_jerseys:
                    if (jersey.get('team_name', '').lower() == contrib_team.lower() and
                        jersey.get('brand_name', '').lower() == contrib_brand.lower() and
                        jersey.get('season', '') == contrib_season and
                        jersey.get('jersey_type', '').lower() == contrib_type.lower()):
                        integration_matches.append({
                            'contribution': contrib,
                            'master_jersey': jersey,
                            'type': 'master_jersey'
                        })
                        found_match = True
                        break
                
                # Check master kits if no jersey match found
                if not found_match:
                    for kit in master_kits:
                        if (kit.get('team_name', '').lower() == contrib_team.lower() and
                            kit.get('brand_name', '').lower() == contrib_brand.lower() and
                            kit.get('season', '') == contrib_season and
                            kit.get('kit_type', '').lower() == contrib_type.lower()):
                            integration_matches.append({
                                'contribution': contrib,
                                'master_kit': kit,
                                'type': 'master_kit'
                            })
                            found_match = True
                            break
                
                if not found_match:
                    missing_integrations.append(contrib)
            
            self.log_result(
                "Integration Process Analysis",
                True,
                f"Integration analysis: {len(integration_matches)} matches found, {len(missing_integrations)} missing integrations"
            )
            
            # Log detailed analysis
            if integration_matches:
                print("   ✅ Successfully Integrated:")
                for match in integration_matches:
                    contrib = match['contribution']
                    if match['type'] == 'master_jersey':
                        target = match['master_jersey']
                        print(f"      - Contribution {contrib.get('id')} → Master Jersey {target.get('id')}")
                    else:
                        target = match['master_kit']
                        print(f"      - Contribution {contrib.get('id')} → Master Kit {target.get('id')}")
                    print(f"        {contrib.get('changes', {}).get('team_name')} {contrib.get('changes', {}).get('season')} {contrib.get('changes', {}).get('kit_type')}")
            
            if missing_integrations:
                print("   ❌ Missing Integrations (Approved but not in Master Collections):")
                for contrib in missing_integrations:
                    changes = contrib.get('changes', {})
                    print(f"      - Contribution {contrib.get('id')}: {changes.get('team_name')} {changes.get('season')} {changes.get('kit_type')}")
                    print(f"        Status: {contrib.get('status')}, Integrated: {contrib.get('integrated', 'N/A')}")
            
            return {
                'successful_integrations': len(integration_matches),
                'missing_integrations': len(missing_integrations),
                'integration_matches': integration_matches,
                'missing_integration_details': missing_integrations
            }
            
        except Exception as e:
            self.log_result("Integration Process Analysis", False, "", str(e))
            return None

    def test_create_master_kit_contribution(self):
        """Test creating a new master kit contribution to verify the workflow"""
        try:
            # Create a test master kit contribution
            test_contribution = {
                "entity_type": "master_kit",
                "entity_id": None,
                "title": "Test Master Kit Integration Workflow",
                "description": "Testing master kit integration workflow",
                "changes": {
                    "team_name": "Test Integration FC",
                    "brand_name": "Test Brand",
                    "season": "2024-25",
                    "kit_type": "home",
                    "model": "authentic",
                    "primary_color": "#FF0000"
                },
                "source_urls": ["https://example.com/test-master-kit"]
            }
            
            response = self.session.post(f"{API_BASE}/contributions-v2/", json=test_contribution)
            
            if response.status_code in [200, 201]:
                data = response.json()
                contribution_id = data.get('id')
                
                self.log_result(
                    "Create Master Kit Contribution Test",
                    True,
                    f"Successfully created test master kit contribution with ID: {contribution_id}"
                )
                
                # Check if it appears in contributions
                contrib_response = self.session.get(f"{API_BASE}/contributions-v2", params={"entity_type": "master_kit"})
                if contrib_response.status_code == 200:
                    contributions = contrib_response.json()
                    test_contrib_found = any(c.get('id') == contribution_id for c in contributions)
                    
                    if test_contrib_found:
                        print(f"   ✅ Test contribution found in contributions list")
                        
                        # Check if it gets auto-approved and integrated
                        # Wait a moment and check master jerseys
                        import time
                        time.sleep(2)
                        
                        jerseys_response = self.session.get(f"{API_BASE}/master-jerseys")
                        if jerseys_response.status_code == 200:
                            jerseys = jerseys_response.json()
                            test_jersey_found = any(
                                j.get('team_name', '').lower() == 'test integration fc' 
                                for j in jerseys
                            )
                            
                            if test_jersey_found:
                                print(f"   ✅ Test master kit successfully integrated to master jerseys collection")
                            else:
                                print(f"   ⚠️ Test master kit NOT found in master jerseys collection")
                    
                return contribution_id
            else:
                self.log_result(
                    "Create Master Kit Contribution Test",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Create Master Kit Contribution Test", False, "", str(e))
            return None

    def test_auto_approval_settings(self):
        """Test auto-approval system settings"""
        try:
            response = self.session.get(f"{API_BASE}/admin/settings")
            
            if response.status_code == 200:
                settings = response.json()
                auto_approval = settings.get("auto_approval_enabled", False)
                
                self.log_result(
                    "Auto-Approval Settings Check",
                    True,
                    f"Auto-approval enabled: {auto_approval}"
                )
                
                return auto_approval
            else:
                self.log_result(
                    "Auto-Approval Settings Check",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Auto-Approval Settings Check", False, "", str(e))
            return None

    def test_integrate_approved_contribution_function(self):
        """Test the integrate_approved_contribution_to_catalogue function execution"""
        try:
            # Get all contributions to see if there's an integration endpoint
            response = self.session.get(f"{API_BASE}/contributions-v2/")
            
            if response.status_code == 200:
                contributions = response.json()
                approved_contributions = [c for c in contributions if c.get('status') == 'APPROVED' and c.get('entity_type') == 'master_kit']
                
                if approved_contributions:
                    # Try to find an integration endpoint or trigger integration
                    test_contrib = approved_contributions[0]
                    contrib_id = test_contrib.get('id')
                    
                    # Test possible integration endpoints
                    integration_endpoints = [
                        f"/contributions-v2/{contrib_id}/integrate",
                        f"/admin/integrate-contribution/{contrib_id}",
                        f"/contributions-v2/{contrib_id}/approve"
                    ]
                    
                    for endpoint in integration_endpoints:
                        try:
                            response = self.session.post(f"{API_BASE}{endpoint}")
                            if response.status_code in [200, 201]:
                                self.log_result(
                                    "Integration Function Test",
                                    True,
                                    f"Found working integration endpoint: {endpoint}"
                                )
                                return True
                        except:
                            continue
                    
                    self.log_result(
                        "Integration Function Test",
                        False,
                        "",
                        "No working integration endpoint found"
                    )
                    return False
                else:
                    self.log_result(
                        "Integration Function Test",
                        False,
                        "",
                        "No approved master kit contributions found to test integration"
                    )
                    return False
            else:
                self.log_result(
                    "Integration Function Test",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Integration Function Test", False, "", str(e))
            return False

    def run_master_kit_investigation(self):
        """Run comprehensive master kit integration investigation"""
        print("🚀 Starting Master Kit Integration Workflow Investigation")
        print("Investigating why master kits are not appearing in catalogue after approval")
        print("=" * 80)
        
        # Step 1: Authenticate admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Check auto-approval settings
        print("\n🔧 STEP 1: Checking Auto-Approval Settings")
        print("-" * 50)
        auto_approval_enabled = self.test_auto_approval_settings()
        
        # Step 3: Check master kit contributions
        print("\n📋 STEP 2: Checking Master Kit Contributions")
        print("-" * 50)
        contributions_data = self.test_master_kit_contributions()
        
        # Step 4: Check master jerseys collection
        print("\n👕 STEP 3: Checking Master Jerseys Collection")
        print("-" * 50)
        jerseys_data = self.test_master_jerseys_collection()
        
        # Step 4b: Check master kits collection
        print("\n🎽 STEP 3b: Checking Master Kits Collection")
        print("-" * 50)
        kits_data = self.test_master_kits_collection()
        
        # Step 5: Analyze contribution approval workflow
        print("\n🔄 STEP 4: Analyzing Contribution Approval Workflow")
        print("-" * 50)
        if contributions_data and contributions_data.get('approved_contributions'):
            workflow_data = self.test_contribution_approval_workflow(contributions_data['approved_contributions'])
        else:
            workflow_data = None
            print("   ⚠️ No approved master kit contributions found to analyze workflow")
        
        # Step 6: Analyze integration process
        print("\n🔗 STEP 5: Analyzing Integration Process")
        print("-" * 50)
        if contributions_data and (jerseys_data or kits_data):
            integration_data = self.test_integration_process_analysis(
                contributions_data.get('approved_contributions', []),
                jerseys_data.get('master_jerseys', []) if jerseys_data else [],
                kits_data.get('master_kits', []) if kits_data else []
            )
        else:
            integration_data = None
            print("   ⚠️ Missing data for integration analysis")
        
        # Step 7: Test integration function
        print("\n⚙️ STEP 6: Testing Integration Function")
        print("-" * 50)
        integration_function_working = self.test_integrate_approved_contribution_function()
        
        # Step 8: Create test contribution to verify workflow
        print("\n🧪 STEP 7: Creating Test Master Kit Contribution")
        print("-" * 50)
        test_contribution_id = self.test_create_master_kit_contribution()
        
        # Generate comprehensive analysis
        self.generate_master_kit_analysis(
            auto_approval_enabled,
            contributions_data,
            jerseys_data,
            kits_data,
            workflow_data,
            integration_data,
            integration_function_working,
            test_contribution_id
        )
        
        return True

    def generate_master_kit_analysis(self, auto_approval, contributions_data, jerseys_data, kits_data,
                                   workflow_data, integration_data, integration_function, test_contrib_id):
        """Generate comprehensive analysis of master kit integration workflow"""
        print("\n" + "=" * 80)
        print("📊 MASTER KIT INTEGRATION WORKFLOW ANALYSIS")
        print("=" * 80)
        
        # Summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        print("-" * 40)
        
        # Auto-approval status
        if auto_approval is not None:
            print(f"✅ Auto-Approval System: {'ENABLED' if auto_approval else 'DISABLED'}")
        else:
            print(f"❌ Auto-Approval System: UNKNOWN (failed to check)")
        
        # Contributions analysis
        if contributions_data:
            total_master_kit_contribs = contributions_data.get('total_master_kit_contributions', 0)
            approved_master_kit_contribs = contributions_data.get('approved_master_kit_contributions', 0)
            print(f"📋 Master Kit Contributions: {total_master_kit_contribs} total, {approved_master_kit_contribs} approved")
        else:
            print(f"❌ Master Kit Contributions: FAILED TO RETRIEVE")
        
        # Master jerseys analysis
        if jerseys_data:
            total_master_jerseys = jerseys_data.get('total_master_jerseys', 0)
            print(f"👕 Master Jerseys Collection: {total_master_jerseys} items")
        else:
            print(f"❌ Master Jerseys Collection: FAILED TO RETRIEVE")
        
        # Master kits analysis
        if kits_data:
            total_master_kits = kits_data.get('total_master_kits', 0)
            print(f"🎽 Master Kits Collection: {total_master_kits} items")
        else:
            print(f"❌ Master Kits Collection: FAILED TO RETRIEVE")
        
        # Integration analysis
        if integration_data:
            successful_integrations = integration_data.get('successful_integrations', 0)
            missing_integrations = integration_data.get('missing_integrations', 0)
            print(f"🔗 Integration Status: {successful_integrations} successful, {missing_integrations} missing")
        else:
            print(f"⚠️ Integration Analysis: INSUFFICIENT DATA")
        
        # Root cause analysis
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        print("-" * 40)
        
        issues_found = []
        
        # Check for integration issues
        if integration_data and integration_data.get('missing_integrations', 0) > 0:
            issues_found.append("INTEGRATION FAILURE: Approved master kit contributions not being integrated to master jerseys collection")
        
        # Check for approval workflow issues
        if contributions_data and contributions_data.get('approved_master_kit_contributions', 0) == 0:
            issues_found.append("APPROVAL WORKFLOW: No approved master kit contributions found")
        
        # Check for collection issues
        if jerseys_data and jerseys_data.get('total_master_jerseys', 0) == 0 and kits_data and kits_data.get('total_master_kits', 0) == 0:
            issues_found.append("COLLECTIONS EMPTY: Both master jerseys and master kits collections are empty")
        
        # Check for auto-approval issues
        if auto_approval is False:
            issues_found.append("AUTO-APPROVAL DISABLED: Master kits require manual approval")
        
        if issues_found:
            print("❌ CRITICAL ISSUES IDENTIFIED:")
            for i, issue in enumerate(issues_found, 1):
                print(f"   {i}. {issue}")
        else:
            print("✅ No critical issues detected in master kit workflow")
        
        # Specific recommendations
        print(f"\n📝 RECOMMENDATIONS:")
        print("-" * 40)
        
        if not issues_found:
            print("✅ Master kit integration workflow appears to be working correctly")
            print("   - Check frontend display logic if master kits still not visible")
            print("   - Verify catalogue page is querying master jerseys collection properly")
        else:
            print("🔧 REQUIRED FIXES:")
            
            if any("INTEGRATION FAILURE" in issue for issue in issues_found):
                print("   1. Fix integrate_approved_contribution_to_catalogue function")
                print("      - Ensure approved master kit contributions are properly integrated")
                print("      - Check if integration logic copies all required fields")
                print("      - Verify master jersey creation from contribution data")
            
            if any("APPROVAL WORKFLOW" in issue for issue in issues_found):
                print("   2. Fix contribution approval workflow")
                print("      - Ensure master kit contributions can be approved")
                print("      - Check if auto-approval is working for master kits")
            
            if any("COLLECTION EMPTY" in issue for issue in issues_found):
                print("   3. Populate master jerseys collection")
                print("      - Create initial master jersey entries")
                print("      - Verify collection structure and fields")
            
            if any("AUTO-APPROVAL DISABLED" in issue for issue in issues_found):
                print("   4. Enable auto-approval for testing")
                print("      - Set auto_approval_enabled to true in admin settings")
                print("      - Or implement manual approval process")
        
        # Test results summary
        print(f"\n📋 DETAILED TEST RESULTS:")
        print("-" * 40)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['error']:
                print(f"    Error: {result['error']}")
        
        # Final assessment
        print(f"\n🎯 FINAL ASSESSMENT:")
        print("-" * 40)
        
        if success_rate >= 80 and not issues_found:
            print("✅ WORKFLOW HEALTHY: Master kit integration workflow is working correctly")
            print("   The issue may be in frontend display logic rather than backend integration")
        elif success_rate >= 60:
            print("⚠️ PARTIAL ISSUES: Master kit workflow has some problems but core functionality works")
            print("   Some components working but integration needs fixes")
        else:
            print("❌ CRITICAL PROBLEMS: Master kit integration workflow has major issues")
            print("   Significant fixes required for proper master kit -> master jersey integration")
        
        print(f"\n🔄 NEXT STEPS:")
        if success_rate >= 80 and not issues_found:
            print("   1. ✅ Backend integration workflow is healthy")
            print("   2. 🔍 Investigate frontend catalogue display logic")
            print("   3. 📱 Check if master jerseys are being queried properly in UI")
        else:
            print("   1. 🔧 Fix identified backend integration issues")
            print("   2. 🧪 Re-test master kit contribution -> master jersey workflow")
            print("   3. 🔍 Verify integrate_approved_contribution_to_catalogue function")
            print("   4. 📱 Test complete workflow from contribution to catalogue display")

if __name__ == "__main__":
    tester = MasterKitIntegrationTester()
    tester.run_master_kit_investigation()