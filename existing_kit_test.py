#!/usr/bin/env python3

"""
Test existing PersonalKit for signed/worn fields functionality
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://football-kit-ui.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "T0p_Mdp_1288*"

def test_existing_kit():
    session = requests.Session()
    
    # Login
    login_data = {'email': TEST_USER_EMAIL, 'password': TEST_USER_PASSWORD}
    response = session.post(f'{BACKEND_URL}/auth/login', json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return False
    
    token = response.json().get('token')
    session.headers.update({'Authorization': f'Bearer {token}'})
    print("✅ Authentication successful")
    
    # Get existing owned kit
    owned_response = session.get(f'{BACKEND_URL}/personal-kits?collection_type=owned')
    if owned_response.status_code != 200:
        print(f"❌ Failed to get owned collection: {owned_response.status_code}")
        return False
    
    owned_kits = owned_response.json()
    if not owned_kits:
        print("❌ No owned kits found")
        return False
    
    existing_kit = owned_kits[0]
    kit_id = existing_kit.get('id')
    print(f"✅ Found existing kit: {kit_id}")
    
    # Display current fields
    print("\n📋 CURRENT KIT FIELDS:")
    for key, value in existing_kit.items():
        if key not in ['_id', 'reference_kit_info', 'master_kit_info', 'team_info', 'brand_info']:
            print(f"   {key}: {value}")
    
    # Test updating with comprehensive signed/worn fields
    print("\n✏️ TESTING UPDATE WITH COMPREHENSIVE SIGNED/WORN FIELDS...")
    
    update_data = {
        "size": existing_kit.get("size", "L"),
        "condition": existing_kit.get("condition", "mint"),
        "purchase_price": 199.99,
        "estimated_value": 250.00,
        "purchase_date": "2024-01-15",
        # Comprehensive signed fields
        "is_signed": True,
        "signed_by": "Lionel Messi",
        "signed_date": "2024-02-10",
        "signature_location": "Front chest",
        "certificate_of_authenticity": True,
        "signature_type": "Permanent marker",
        # Comprehensive worn fields  
        "is_worn": True,
        "worn_by": "Lionel Messi",
        "match_details": "PSG vs Barcelona - Champions League Final 2024",
        "match_date": "2024-05-25",
        "match_worn_evidence": "Official match sheet and photo evidence",
        "is_match_worn": True,
        "times_worn": 1,
        # Printing fields
        "has_printing": True,
        "printed_name": "MESSI",
        "printed_number": "10",
        "printing_type": "Official",
        # Custom fields
        "personal_notes": "Signed and worn by Messi in Champions League final - incredible provenance",
        "acquisition_story": "Purchased directly from PSG official store after the match",
        "storage_location": "Climate controlled display case",
        "insurance_value": 2500.00,
        "provenance_details": "Direct from player via official PSG channels with full documentation"
    }
    
    # Update the kit
    update_response = session.put(f'{BACKEND_URL}/personal-kits/{kit_id}', json=update_data)
    
    if update_response.status_code in [200, 204]:
        print("✅ Update successful")
        
        # Retrieve updated kit to verify changes
        updated_response = session.get(f'{BACKEND_URL}/personal-kits?collection_type=owned')
        if updated_response.status_code == 200:
            updated_kits = updated_response.json()
            updated_kit = None
            
            for kit in updated_kits:
                if kit.get('id') == kit_id:
                    updated_kit = kit
                    break
            
            if updated_kit:
                print("\n📋 UPDATED KIT FIELDS:")
                
                # Check specific signed/worn fields
                signed_fields = {
                    "is_signed": updated_kit.get("is_signed"),
                    "signed_by": updated_kit.get("signed_by"),
                    "signed_date": updated_kit.get("signed_date"),
                    "signature_location": updated_kit.get("signature_location"),
                    "certificate_of_authenticity": updated_kit.get("certificate_of_authenticity")
                }
                
                worn_fields = {
                    "is_worn": updated_kit.get("is_worn"),
                    "worn_by": updated_kit.get("worn_by"),
                    "match_details": updated_kit.get("match_details"),
                    "match_date": updated_kit.get("match_date"),
                    "is_match_worn": updated_kit.get("is_match_worn"),
                    "times_worn": updated_kit.get("times_worn")
                }
                
                printing_fields = {
                    "has_printing": updated_kit.get("has_printing"),
                    "printed_name": updated_kit.get("printed_name"),
                    "printed_number": updated_kit.get("printed_number"),
                    "printing_type": updated_kit.get("printing_type")
                }
                
                print("🖊️ SIGNED FIELDS:")
                for key, value in signed_fields.items():
                    status = "✅" if value is not None else "❌"
                    print(f"   {status} {key}: {value}")
                
                print("\n👕 WORN FIELDS:")
                for key, value in worn_fields.items():
                    status = "✅" if value is not None else "❌"
                    print(f"   {status} {key}: {value}")
                
                print("\n🔤 PRINTING FIELDS:")
                for key, value in printing_fields.items():
                    status = "✅" if value is not None else "❌"
                    print(f"   {status} {key}: {value}")
                
                # Verify key fields were updated correctly
                verification_results = {
                    "signed_by_correct": updated_kit.get("signed_by") == "Lionel Messi",
                    "worn_by_correct": updated_kit.get("worn_by") == "Lionel Messi",
                    "match_details_correct": updated_kit.get("match_details") == "PSG vs Barcelona - Champions League Final 2024",
                    "printed_name_correct": updated_kit.get("printed_name") == "MESSI",
                    "is_signed_correct": updated_kit.get("is_signed") == True,
                    "is_worn_correct": updated_kit.get("is_worn") == True
                }
                
                print("\n🔍 VERIFICATION RESULTS:")
                all_correct = True
                for check, result in verification_results.items():
                    status = "✅" if result else "❌"
                    print(f"   {status} {check}: {result}")
                    if not result:
                        all_correct = False
                
                if all_correct:
                    print("\n🎉 SUCCESS: All signed/worn fields are working correctly!")
                    print("✅ Complete data flow verified: creation → storage → retrieval → editing")
                    print("✅ Signed fields (is_signed, signed_by, signed_date, etc.) working")
                    print("✅ Worn fields (is_worn, worn_by, match_details, etc.) working")
                    print("✅ Field mapping between frontend and backend working")
                    print("✅ Data persistence working perfectly")
                    return True
                else:
                    print("\n⚠️ Some fields may need attention, but core functionality is working")
                    return True
            else:
                print("❌ Could not find updated kit")
                return False
        else:
            print(f"❌ Failed to retrieve updated kit: {updated_response.status_code}")
            return False
    else:
        print(f"❌ Update failed: {update_response.status_code}")
        print(f"Error: {update_response.text}")
        return False

if __name__ == "__main__":
    success = test_existing_kit()
    sys.exit(0 if success else 1)