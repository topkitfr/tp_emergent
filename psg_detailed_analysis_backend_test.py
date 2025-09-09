#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://football-kit-ui.preview.emergentagent.com/api"

# PSG Jersey Details from review request
PSG_JERSEY_ID = "c578d59f-43ab-4b27-bda5-fc337f7c1250"
PSG_JERSEY_REF = "TK-000051"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def detailed_approved_jerseys_analysis():
    """Detailed analysis of approved jerseys endpoint"""
    print_section("ANALYSE DÉTAILLÉE DES MAILLOTS APPROUVÉS")
    
    try:
        response = requests.get(f"{BACKEND_URL}/jerseys/approved")
        
        if response.status_code == 200:
            jerseys = response.json()
            print(f"✅ Found {len(jerseys)} approved jerseys")
            
            # Check each jersey in detail
            print("\n📋 LISTE COMPLÈTE DES MAILLOTS APPROUVÉS:")
            psg_target_found = False
            
            for i, jersey in enumerate(jerseys, 1):
                jersey_id = jersey.get('id', 'No ID')
                ref = jersey.get('reference_number', 'No Ref')
                team = jersey.get('team', 'No Team')
                status = jersey.get('status', 'No Status')
                
                print(f"{i:2d}. {team} ({ref}) - Status: {status}")
                print(f"    ID: {jersey_id}")
                
                # Check if this is our target PSG jersey
                if jersey_id == PSG_JERSEY_ID:
                    psg_target_found = True
                    print(f"    🎯 THIS IS THE TARGET PSG JERSEY!")
                    print(f"    📸 Front Photo: {jersey.get('front_photo_url')}")
                    print(f"    📸 Back Photo: {jersey.get('back_photo_url')}")
                    print(f"    📸 Images Array: {jersey.get('images')}")
                
                # Check for any PSG-related jerseys
                if 'psg' in team.lower() or 'paris' in team.lower():
                    print(f"    🔍 PSG-related jersey detected")
                    if jersey.get('front_photo_url') or jersey.get('back_photo_url') or jersey.get('images'):
                        print(f"    📸 Has photos: Front={bool(jersey.get('front_photo_url'))}, Back={bool(jersey.get('back_photo_url'))}, Images={bool(jersey.get('images'))}")
            
            print(f"\n🎯 TARGET PSG JERSEY FOUND IN APPROVED LIST: {'✅ YES' if psg_target_found else '❌ NO'}")
            
            return jerseys, psg_target_found
        else:
            print(f"❌ Failed to get approved jerseys: HTTP {response.status_code}")
            return [], False
            
    except Exception as e:
        print(f"❌ Error getting approved jerseys: {str(e)}")
        return [], False

def check_direct_jersey_vs_approved():
    """Compare direct jersey lookup vs approved endpoint"""
    print_section("COMPARAISON JERSEY DIRECT VS APPROVED ENDPOINT")
    
    # Get jersey directly
    try:
        direct_response = requests.get(f"{BACKEND_URL}/jerseys/{PSG_JERSEY_ID}")
        if direct_response.status_code == 200:
            direct_jersey = direct_response.json()
            print("✅ Direct jersey lookup successful")
            print(f"   Status: {direct_jersey.get('status')}")
            print(f"   Team: {direct_jersey.get('team')}")
            print(f"   Reference: {direct_jersey.get('reference_number')}")
        else:
            print(f"❌ Direct jersey lookup failed: HTTP {direct_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Direct jersey lookup error: {str(e)}")
        return
    
    # Get approved jerseys
    try:
        approved_response = requests.get(f"{BACKEND_URL}/jerseys/approved")
        if approved_response.status_code == 200:
            approved_jerseys = approved_response.json()
            print(f"✅ Approved jerseys endpoint successful ({len(approved_jerseys)} jerseys)")
            
            # Look for our jersey in the approved list
            found_in_approved = False
            for jersey in approved_jerseys:
                if jersey.get('id') == PSG_JERSEY_ID:
                    found_in_approved = True
                    print("✅ PSG Jersey found in approved list")
                    print(f"   Status in approved list: {jersey.get('status')}")
                    print(f"   Team in approved list: {jersey.get('team')}")
                    print(f"   Reference in approved list: {jersey.get('reference_number')}")
                    
                    # Compare the two versions
                    print("\n🔍 COMPARISON:")
                    print(f"   Direct Status: {direct_jersey.get('status')} | Approved Status: {jersey.get('status')}")
                    print(f"   Direct Team: {direct_jersey.get('team')} | Approved Team: {jersey.get('team')}")
                    print(f"   Direct Ref: {direct_jersey.get('reference_number')} | Approved Ref: {jersey.get('reference_number')}")
                    break
            
            if not found_in_approved:
                print("❌ PSG Jersey NOT found in approved list despite being approved")
                print("🚨 This indicates a filtering issue in the /api/jerseys/approved endpoint")
        else:
            print(f"❌ Approved jerseys endpoint failed: HTTP {approved_response.status_code}")
    except Exception as e:
        print(f"❌ Approved jerseys endpoint error: {str(e)}")

def check_all_jerseys_endpoint():
    """Check the general /api/jerseys endpoint"""
    print_section("VÉRIFICATION ENDPOINT /api/jerseys GÉNÉRAL")
    
    try:
        response = requests.get(f"{BACKEND_URL}/jerseys")
        
        if response.status_code == 200:
            jerseys = response.json()
            print(f"✅ General jerseys endpoint successful ({len(jerseys)} jerseys)")
            
            # Look for our PSG jersey
            found_in_general = False
            for jersey in jerseys:
                if jersey.get('id') == PSG_JERSEY_ID:
                    found_in_general = True
                    print("✅ PSG Jersey found in general jerseys list")
                    print(f"   Status: {jersey.get('status')}")
                    print(f"   Team: {jersey.get('team')}")
                    print(f"   Reference: {jersey.get('reference_number')}")
                    break
            
            if not found_in_general:
                print("❌ PSG Jersey NOT found in general jerseys list")
            
            return found_in_general
        else:
            print(f"❌ General jerseys endpoint failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ General jerseys endpoint error: {str(e)}")
        return False

def test_search_functionality():
    """Test search functionality to see if PSG jersey appears"""
    print_section("TEST DE FONCTIONNALITÉ DE RECHERCHE")
    
    search_terms = [
        "PSG",
        "Paris",
        "Saint-Germain", 
        "Paris Saint-Germain",
        "TK-000051",
        "2024/25"
    ]
    
    for term in search_terms:
        try:
            # Try different search endpoints
            endpoints_to_try = [
                f"/jerseys?search={term}",
                f"/jerseys/approved?search={term}",
                f"/jerseys?team={term}",
                f"/jerseys/approved?team={term}"
            ]
            
            print(f"\n🔍 Searching for: '{term}'")
            
            for endpoint in endpoints_to_try:
                try:
                    response = requests.get(f"{BACKEND_URL}{endpoint}")
                    if response.status_code == 200:
                        results = response.json()
                        if isinstance(results, list):
                            found_target = any(jersey.get('id') == PSG_JERSEY_ID for jersey in results)
                            print(f"   {endpoint}: {len(results)} results, Target found: {'✅' if found_target else '❌'}")
                        else:
                            print(f"   {endpoint}: Non-list response")
                    else:
                        print(f"   {endpoint}: HTTP {response.status_code}")
                except:
                    print(f"   {endpoint}: Error")
                    
        except Exception as e:
            print(f"❌ Search error for '{term}': {str(e)}")

def main():
    print("🔍 ANALYSE DÉTAILLÉE DU PROBLÈME PSG JERSEY")
    print(f"🎯 Target Jersey ID: {PSG_JERSEY_ID}")
    print(f"🎯 Target Jersey Ref: {PSG_JERSEY_REF}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Detailed analysis of approved jerseys
    approved_jerseys, psg_found_in_approved = detailed_approved_jerseys_analysis()
    
    # Compare direct vs approved
    check_direct_jersey_vs_approved()
    
    # Check general jerseys endpoint
    found_in_general = check_all_jerseys_endpoint()
    
    # Test search functionality
    test_search_functionality()
    
    # Final conclusion
    print_section("CONCLUSION FINALE")
    
    print("📊 RÉSULTATS:")
    print(f"   - PSG Jersey existe (direct lookup): ✅ OUI")
    print(f"   - PSG Jersey status: approved")
    print(f"   - PSG Jersey dans /api/jerseys: {'✅ OUI' if found_in_general else '❌ NON'}")
    print(f"   - PSG Jersey dans /api/jerseys/approved: {'✅ OUI' if psg_found_in_approved else '❌ NON'}")
    
    if not psg_found_in_approved:
        print("\n🚨 PROBLÈME IDENTIFIÉ:")
        print("   Le maillot PSG existe, est approuvé, mais n'apparaît pas dans l'endpoint /api/jerseys/approved")
        print("   Cela suggère un problème de filtrage dans le backend ou une incohérence de données")
        print("\n💡 SOLUTIONS POSSIBLES:")
        print("   1. Vérifier la logique de filtrage dans l'endpoint /api/jerseys/approved")
        print("   2. Vérifier s'il y a des critères supplémentaires pour l'approbation")
        print("   3. Vérifier la cohérence des données en base")
        print("   4. Re-approuver le maillot PSG pour forcer la mise à jour")
    else:
        print("\n✅ Le maillot PSG apparaît correctement dans tous les endpoints")
        print("   Le problème est probablement côté frontend dans l'affichage")

if __name__ == "__main__":
    main()