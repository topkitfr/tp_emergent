#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"

# PSG Jersey Details from review request
PSG_JERSEY_ID = "c578d59f-43ab-4b27-bda5-fc337f7c1250"
PSG_JERSEY_REF = "TK-000051"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def test_fix_verification():
    """Test if the pagination fix works"""
    print_section("VÉRIFICATION DU FIX DE PAGINATION")
    
    endpoints_to_test = [
        "/jerseys",
        "/jerseys/approved"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}")
            
            if response.status_code == 200:
                jerseys = response.json()
                found_psg = any(jersey.get('id') == PSG_JERSEY_ID for jersey in jerseys)
                
                print(f"✅ {endpoint}: {len(jerseys)} jerseys returned")
                print(f"   🎯 PSG Jersey found: {'✅ YES' if found_psg else '❌ NO'}")
                
                if found_psg:
                    # Find position
                    for i, jersey in enumerate(jerseys):
                        if jersey.get('id') == PSG_JERSEY_ID:
                            print(f"   📍 PSG Jersey position: {i+1}/{len(jerseys)}")
                            print(f"   📝 Reference: {jersey.get('reference_number')}")
                            print(f"   🏆 Team: {jersey.get('team')}")
                            print(f"   📸 Has photos: Front={bool(jersey.get('front_photo_url'))}, Back={bool(jersey.get('back_photo_url'))}")
                            break
                
                # Show reference range
                refs = [jersey.get('reference_number') for jersey in jerseys if jersey.get('reference_number')]
                if refs:
                    refs.sort()
                    print(f"   📝 Reference range: {refs[0]} to {refs[-1]}")
                    
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: Error {str(e)}")

def test_photo_accessibility():
    """Test if PSG photos are accessible"""
    print_section("VÉRIFICATION ACCESSIBILITÉ PHOTOS PSG")
    
    try:
        # Get PSG jersey data
        response = requests.get(f"{BACKEND_URL}/jerseys/{PSG_JERSEY_ID}")
        
        if response.status_code == 200:
            jersey = response.json()
            base_url = "https://jersey-catalog-2.preview.emergentagent.com"
            
            # Test front photo
            front_photo = jersey.get('front_photo_url')
            if front_photo:
                front_url = f"{base_url}/{front_photo.lstrip('/')}"
                try:
                    photo_response = requests.get(front_url, timeout=10)
                    print(f"✅ Front photo accessible: HTTP {photo_response.status_code}, Size: {len(photo_response.content)} bytes")
                except Exception as e:
                    print(f"❌ Front photo error: {str(e)}")
            
            # Test back photo
            back_photo = jersey.get('back_photo_url')
            if back_photo:
                back_url = f"{base_url}/{back_photo.lstrip('/')}"
                try:
                    photo_response = requests.get(back_url, timeout=10)
                    print(f"✅ Back photo accessible: HTTP {photo_response.status_code}, Size: {len(photo_response.content)} bytes")
                except Exception as e:
                    print(f"❌ Back photo error: {str(e)}")
                    
        else:
            print(f"❌ Could not get PSG jersey data: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Photo accessibility test error: {str(e)}")

def main():
    print("🔧 VÉRIFICATION DU FIX PSG JERSEY - PAGINATION CORRIGÉE")
    print(f"🎯 Target Jersey ID: {PSG_JERSEY_ID}")
    print(f"🎯 Target Jersey Ref: {PSG_JERSEY_REF}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test the fix
    test_fix_verification()
    
    # Test photo accessibility
    test_photo_accessibility()
    
    print_section("RÉSULTAT FINAL")
    print("🎯 OBJECTIF: Vérifier que le maillot PSG TK-000051 est maintenant visible")
    print("   dans l'explorateur après correction de la limite de pagination")
    print("\n💡 SI LE FIX FONCTIONNE:")
    print("   ✅ Le maillot PSG devrait apparaître dans /api/jerseys")
    print("   ✅ Le maillot PSG devrait apparaître dans /api/jerseys/approved")
    print("   ✅ Les photos devraient être accessibles")
    print("   ✅ L'utilisateur devrait maintenant voir le maillot dans l'explorateur")

if __name__ == "__main__":
    main()