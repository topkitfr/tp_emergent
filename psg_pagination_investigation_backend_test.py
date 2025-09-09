#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-tracker.preview.emergentagent.com/api"

# PSG Jersey Details from review request
PSG_JERSEY_ID = "c578d59f-43ab-4b27-bda5-fc337f7c1250"
PSG_JERSEY_REF = "TK-000051"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def investigate_pagination_and_limits():
    """Investigate if there are pagination or limit issues"""
    print_section("INVESTIGATION PAGINATION ET LIMITES")
    
    # Test different limit parameters
    limits_to_test = [10, 20, 50, 100, 1000]
    
    for limit in limits_to_test:
        try:
            response = requests.get(f"{BACKEND_URL}/jerseys/approved?limit={limit}")
            if response.status_code == 200:
                jerseys = response.json()
                found_target = any(jersey.get('id') == PSG_JERSEY_ID for jersey in jerseys)
                print(f"✅ Limit {limit}: {len(jerseys)} jerseys, Target found: {'✅' if found_target else '❌'}")
                
                if found_target:
                    # Find the position of our jersey
                    for i, jersey in enumerate(jerseys):
                        if jersey.get('id') == PSG_JERSEY_ID:
                            print(f"   🎯 PSG Jersey found at position {i+1}")
                            break
            else:
                print(f"❌ Limit {limit}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Limit {limit}: Error {str(e)}")

def investigate_sorting_and_ordering():
    """Investigate different sorting options"""
    print_section("INVESTIGATION TRI ET ORDRE")
    
    # Test different sorting parameters
    sort_options = [
        "",  # default
        "?sort=created_at",
        "?sort=-created_at",  # descending
        "?sort=reference_number",
        "?sort=-reference_number",
        "?sort=team",
        "?sort=-team"
    ]
    
    for sort_param in sort_options:
        try:
            url = f"{BACKEND_URL}/jerseys/approved{sort_param}"
            response = requests.get(url)
            if response.status_code == 200:
                jerseys = response.json()
                found_target = any(jersey.get('id') == PSG_JERSEY_ID for jersey in jerseys)
                
                sort_desc = sort_param if sort_param else "default"
                print(f"✅ Sort {sort_desc}: {len(jerseys)} jerseys, Target found: {'✅' if found_target else '❌'}")
                
                if found_target:
                    # Find the position of our jersey
                    for i, jersey in enumerate(jerseys):
                        if jersey.get('id') == PSG_JERSEY_ID:
                            print(f"   🎯 PSG Jersey found at position {i+1}")
                            print(f"   📅 Created: {jersey.get('created_at')}")
                            print(f"   📝 Reference: {jersey.get('reference_number')}")
                            break
                
                # Show first few jerseys for context
                if len(jerseys) > 0:
                    print(f"   📋 First 3 jerseys:")
                    for i, jersey in enumerate(jerseys[:3]):
                        ref = jersey.get('reference_number', 'No Ref')
                        team = jersey.get('team', 'No Team')
                        created = jersey.get('created_at', 'No Date')[:10] if jersey.get('created_at') else 'No Date'
                        print(f"      {i+1}. {team} ({ref}) - {created}")
            else:
                print(f"❌ Sort {sort_param}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Sort {sort_param}: Error {str(e)}")

def check_total_jerseys_count():
    """Check the total number of jerseys in the system"""
    print_section("VÉRIFICATION NOMBRE TOTAL DE MAILLOTS")
    
    endpoints_to_check = [
        "/jerseys",
        "/jerseys/approved",
        "/jerseys?status=approved",
        "/jerseys?limit=1000"
    ]
    
    for endpoint in endpoints_to_check:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}")
            if response.status_code == 200:
                jerseys = response.json()
                found_target = any(jersey.get('id') == PSG_JERSEY_ID for jersey in jerseys)
                
                print(f"✅ {endpoint}: {len(jerseys)} jerseys, Target found: {'✅' if found_target else '❌'}")
                
                # Count by status
                status_counts = {}
                for jersey in jerseys:
                    status = jersey.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                print(f"   📊 Status breakdown: {status_counts}")
                
                # Show reference number range
                refs = [jersey.get('reference_number') for jersey in jerseys if jersey.get('reference_number')]
                if refs:
                    refs.sort()
                    print(f"   📝 Reference range: {refs[0]} to {refs[-1]}")
                    
                    # Check if TK-000051 is in the expected range
                    if 'TK-000051' >= refs[0] and 'TK-000051' <= refs[-1]:
                        print(f"   ✅ TK-000051 is within the reference range")
                    else:
                        print(f"   ❌ TK-000051 is outside the reference range")
                        
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error {str(e)}")

def check_database_consistency():
    """Check for database consistency issues"""
    print_section("VÉRIFICATION COHÉRENCE BASE DE DONNÉES")
    
    # Get the jersey directly
    try:
        direct_response = requests.get(f"{BACKEND_URL}/jerseys/{PSG_JERSEY_ID}")
        if direct_response.status_code == 200:
            direct_jersey = direct_response.json()
            
            print("✅ Direct jersey data:")
            print(f"   ID: {direct_jersey.get('id')}")
            print(f"   Reference: {direct_jersey.get('reference_number')}")
            print(f"   Team: {direct_jersey.get('team')}")
            print(f"   Status: {direct_jersey.get('status')}")
            print(f"   Created: {direct_jersey.get('created_at')}")
            print(f"   Approved: {direct_jersey.get('approved_at')}")
            print(f"   Approved by: {direct_jersey.get('approved_by')}")
            
            # Check if there are any unusual fields
            print(f"\n   📋 All fields in direct jersey:")
            for key, value in direct_jersey.items():
                if key not in ['id', 'reference_number', 'team', 'status', 'created_at', 'approved_at', 'approved_by']:
                    print(f"      {key}: {value}")
                    
        else:
            print(f"❌ Direct jersey lookup failed: HTTP {direct_response.status_code}")
    except Exception as e:
        print(f"❌ Direct jersey lookup error: {str(e)}")

def test_specific_filters():
    """Test specific filters that might be hiding the jersey"""
    print_section("TEST FILTRES SPÉCIFIQUES")
    
    # Test various filter combinations
    filters_to_test = [
        "?status=approved",
        "?team=Paris Saint-Germain",
        "?league=Ligue 1",
        "?season=2024/25",
        "?reference_number=TK-000051",
        "?status=approved&team=Paris Saint-Germain",
        "?status=approved&league=Ligue 1",
        "?status=approved&season=2024/25"
    ]
    
    for filter_param in filters_to_test:
        try:
            url = f"{BACKEND_URL}/jerseys{filter_param}"
            response = requests.get(url)
            if response.status_code == 200:
                jerseys = response.json()
                found_target = any(jersey.get('id') == PSG_JERSEY_ID for jersey in jerseys)
                
                print(f"✅ Filter {filter_param}: {len(jerseys)} jerseys, Target found: {'✅' if found_target else '❌'}")
                
                if found_target and len(jerseys) <= 10:
                    # Show all jerseys if small result set
                    print(f"   📋 All results:")
                    for i, jersey in enumerate(jerseys):
                        ref = jersey.get('reference_number', 'No Ref')
                        team = jersey.get('team', 'No Team')
                        status = jersey.get('status', 'No Status')
                        marker = "🎯" if jersey.get('id') == PSG_JERSEY_ID else "  "
                        print(f"   {marker} {i+1}. {team} ({ref}) - {status}")
                        
            else:
                print(f"❌ Filter {filter_param}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Filter {filter_param}: Error {str(e)}")

def main():
    print("🔍 INVESTIGATION APPROFONDIE DU PROBLÈME PSG JERSEY")
    print(f"🎯 Target Jersey ID: {PSG_JERSEY_ID}")
    print(f"🎯 Target Jersey Ref: {PSG_JERSEY_REF}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Investigate pagination
    investigate_pagination_and_limits()
    
    # Investigate sorting
    investigate_sorting_and_ordering()
    
    # Check total counts
    check_total_jerseys_count()
    
    # Check database consistency
    check_database_consistency()
    
    # Test specific filters
    test_specific_filters()
    
    print_section("CONCLUSION DE L'INVESTIGATION")
    print("🔍 Cette investigation approfondie devrait révéler:")
    print("   1. Si le problème est lié à la pagination/limite")
    print("   2. Si le problème est lié au tri/ordre")
    print("   3. Si le problème est lié à des filtres cachés")
    print("   4. Si il y a une incohérence dans la base de données")

if __name__ == "__main__":
    main()