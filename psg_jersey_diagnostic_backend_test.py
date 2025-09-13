#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-debug-1.preview.emergentagent.com/api"

# PSG Jersey Details from review request
PSG_JERSEY_ID = "c578d59f-43ab-4b27-bda5-fc337f7c1250"
PSG_JERSEY_REF = "TK-000051"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

def test_psg_jersey_status():
    """Test 1: Verify real status of PSG jersey"""
    print_section("TEST 1: VÉRIFIER STATUT RÉEL DU MAILLOT PSG")
    
    try:
        # Direct jersey lookup by ID
        response = requests.get(f"{BACKEND_URL}/jerseys/{PSG_JERSEY_ID}")
        
        if response.status_code == 200:
            jersey = response.json()
            print_result("PSG Jersey Found by ID", True, f"ID: {jersey.get('id')}")
            print_result("Jersey Reference", True, f"Ref: {jersey.get('reference_number')}")
            print_result("Jersey Team", True, f"Team: {jersey.get('team')}")
            print_result("Jersey Status", True, f"Status: {jersey.get('status')}")
            print_result("Jersey League", True, f"League: {jersey.get('league')}")
            print_result("Jersey Season", True, f"Season: {jersey.get('season')}")
            
            # Check photos
            front_photo = jersey.get('front_photo_url')
            back_photo = jersey.get('back_photo_url')
            images_array = jersey.get('images')
            
            print_result("Front Photo URL", bool(front_photo), f"URL: {front_photo}")
            print_result("Back Photo URL", bool(back_photo), f"URL: {back_photo}")
            print_result("Images Array", bool(images_array), f"Images: {images_array}")
            
            return jersey
        else:
            print_result("PSG Jersey Found by ID", False, f"HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print_result("PSG Jersey Lookup", False, f"Error: {str(e)}")
        return None

def test_approved_jerseys_endpoint():
    """Test 2: Check if PSG jersey appears in /api/jerseys/approved"""
    print_section("TEST 2: VÉRIFIER PRÉSENCE DANS /api/jerseys/approved")
    
    try:
        response = requests.get(f"{BACKEND_URL}/jerseys/approved")
        
        if response.status_code == 200:
            jerseys = response.json()
            print_result("Approved Jerseys Endpoint", True, f"Found {len(jerseys)} approved jerseys")
            
            # Look for PSG jersey
            psg_found = False
            psg_jersey = None
            
            for jersey in jerseys:
                if jersey.get('id') == PSG_JERSEY_ID or jersey.get('reference_number') == PSG_JERSEY_REF:
                    psg_found = True
                    psg_jersey = jersey
                    break
                    
                # Also check for PSG team name variations
                team = jersey.get('team', '').lower()
                if 'psg' in team or 'paris saint-germain' in team or 'paris' in team:
                    print(f"   Found PSG-related jersey: {jersey.get('team')} (ID: {jersey.get('id')}, Ref: {jersey.get('reference_number')})")
            
            print_result("PSG Jersey in Approved List", psg_found, 
                        f"PSG Jersey {'FOUND' if psg_found else 'NOT FOUND'} in approved list")
            
            if psg_found:
                print(f"   PSG Jersey Details:")
                print(f"   - ID: {psg_jersey.get('id')}")
                print(f"   - Reference: {psg_jersey.get('reference_number')}")
                print(f"   - Team: {psg_jersey.get('team')}")
                print(f"   - Status: {psg_jersey.get('status')}")
                print(f"   - Front Photo: {psg_jersey.get('front_photo_url')}")
                print(f"   - Back Photo: {psg_jersey.get('back_photo_url')}")
                print(f"   - Images Array: {psg_jersey.get('images')}")
            
            return jerseys, psg_jersey
        else:
            print_result("Approved Jerseys Endpoint", False, f"HTTP {response.status_code}: {response.text}")
            return [], None
            
    except Exception as e:
        print_result("Approved Jerseys Endpoint", False, f"Error: {str(e)}")
        return [], None

def test_photo_accessibility(jersey):
    """Test 3: Test accessibility of PSG jersey photos"""
    print_section("TEST 3: TESTER ACCESSIBILITÉ DES PHOTOS")
    
    if not jersey:
        print_result("Photo Accessibility Test", False, "No jersey data provided")
        return
    
    base_url = "https://topkit-debug-1.preview.emergentagent.com"
    
    # Test front photo
    front_photo = jersey.get('front_photo_url')
    if front_photo:
        try:
            # Construct full URL
            if front_photo.startswith('http'):
                front_url = front_photo
            else:
                front_url = f"{base_url}/{front_photo.lstrip('/')}"
            
            print(f"   Testing front photo URL: {front_url}")
            response = requests.get(front_url, timeout=10)
            print_result("Front Photo Accessible", response.status_code == 200, 
                        f"HTTP {response.status_code}, Size: {len(response.content)} bytes")
        except Exception as e:
            print_result("Front Photo Accessible", False, f"Error: {str(e)}")
    else:
        print_result("Front Photo URL", False, "No front photo URL found")
    
    # Test back photo
    back_photo = jersey.get('back_photo_url')
    if back_photo:
        try:
            # Construct full URL
            if back_photo.startswith('http'):
                back_url = back_photo
            else:
                back_url = f"{base_url}/{back_photo.lstrip('/')}"
            
            print(f"   Testing back photo URL: {back_url}")
            response = requests.get(back_url, timeout=10)
            print_result("Back Photo Accessible", response.status_code == 200, 
                        f"HTTP {response.status_code}, Size: {len(response.content)} bytes")
        except Exception as e:
            print_result("Back Photo Accessible", False, f"Error: {str(e)}")
    else:
        print_result("Back Photo URL", False, "No back photo URL found")
    
    # Test images array
    images = jersey.get('images')
    if images and isinstance(images, list):
        for i, image_url in enumerate(images):
            try:
                if image_url.startswith('http'):
                    full_url = image_url
                else:
                    full_url = f"{base_url}/{image_url.lstrip('/')}"
                
                print(f"   Testing image {i+1} URL: {full_url}")
                response = requests.get(full_url, timeout=10)
                print_result(f"Image {i+1} Accessible", response.status_code == 200, 
                            f"HTTP {response.status_code}, Size: {len(response.content)} bytes")
            except Exception as e:
                print_result(f"Image {i+1} Accessible", False, f"Error: {str(e)}")
    else:
        print_result("Images Array", False, "No images array found")

def test_other_jerseys_comparison():
    """Test 4: Compare with other jerseys to see what's visible"""
    print_section("TEST 4: COMPARER AVEC AUTRES MAILLOTS")
    
    try:
        response = requests.get(f"{BACKEND_URL}/jerseys/approved")
        
        if response.status_code == 200:
            jerseys = response.json()
            
            print(f"   Total approved jerseys: {len(jerseys)}")
            
            # Analyze jerseys with photos
            jerseys_with_photos = []
            jerseys_without_photos = []
            
            for jersey in jerseys:
                has_photos = bool(jersey.get('front_photo_url') or jersey.get('back_photo_url') or jersey.get('images'))
                
                if has_photos:
                    jerseys_with_photos.append(jersey)
                else:
                    jerseys_without_photos.append(jersey)
            
            print_result("Jerseys with Photos", True, f"{len(jerseys_with_photos)} jerseys have photos")
            print_result("Jerseys without Photos", True, f"{len(jerseys_without_photos)} jerseys have no photos")
            
            # Show details of jerseys with photos
            print("\n   📸 JERSEYS WITH PHOTOS:")
            for jersey in jerseys_with_photos[:10]:  # Show first 10
                team = jersey.get('team', 'Unknown')
                ref = jersey.get('reference_number', 'No Ref')
                front = "✅" if jersey.get('front_photo_url') else "❌"
                back = "✅" if jersey.get('back_photo_url') else "❌"
                images = "✅" if jersey.get('images') else "❌"
                
                print(f"   - {team} ({ref}): Front:{front} Back:{back} Images:{images}")
                
                # Check if this is our PSG jersey
                if jersey.get('id') == PSG_JERSEY_ID:
                    print(f"     🎯 THIS IS THE PSG JERSEY WE'RE LOOKING FOR!")
            
            return jerseys_with_photos, jerseys_without_photos
        else:
            print_result("Jersey Comparison", False, f"HTTP {response.status_code}")
            return [], []
            
    except Exception as e:
        print_result("Jersey Comparison", False, f"Error: {str(e)}")
        return [], []

def test_all_jersey_endpoints():
    """Test 5: Check all jersey-related endpoints"""
    print_section("TEST 5: VÉRIFIER TOUS LES ENDPOINTS JERSEY")
    
    endpoints = [
        "/jerseys",
        "/jerseys/approved", 
        "/explorer/leagues",
        "/marketplace/catalog"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else "N/A"
                print_result(f"Endpoint {endpoint}", True, f"HTTP 200, Items: {count}")
                
                # If this is a jersey endpoint, check for PSG
                if 'jersey' in endpoint and isinstance(data, list):
                    psg_found = any(
                        jersey.get('id') == PSG_JERSEY_ID or 
                        jersey.get('reference_number') == PSG_JERSEY_REF or
                        'psg' in jersey.get('team', '').lower() or
                        'paris' in jersey.get('team', '').lower()
                        for jersey in data
                    )
                    print(f"     PSG Jersey found in {endpoint}: {'✅ YES' if psg_found else '❌ NO'}")
            else:
                print_result(f"Endpoint {endpoint}", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            print_result(f"Endpoint {endpoint}", False, f"Error: {str(e)}")

def main():
    print("🔍 DIAGNOSTIC COMPLET DU MAILLOT PSG - TOPKIT")
    print(f"🎯 Target Jersey ID: {PSG_JERSEY_ID}")
    print(f"🎯 Target Jersey Ref: {PSG_JERSEY_REF}")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Check PSG jersey status
    psg_jersey = test_psg_jersey_status()
    
    # Test 2: Check approved jerseys endpoint
    approved_jerseys, psg_in_approved = test_approved_jerseys_endpoint()
    
    # Test 3: Test photo accessibility
    if psg_jersey:
        test_photo_accessibility(psg_jersey)
    
    # Test 4: Compare with other jerseys
    jerseys_with_photos, jerseys_without_photos = test_other_jerseys_comparison()
    
    # Test 5: Check all endpoints
    test_all_jersey_endpoints()
    
    # Final diagnosis
    print_section("DIAGNOSTIC FINAL")
    
    if psg_jersey:
        status = psg_jersey.get('status')
        if status == 'approved':
            if psg_in_approved:
                print("🎯 PROBLÈME IDENTIFIÉ: Le maillot PSG existe, est approuvé, et apparaît dans l'API")
                print("   ➡️ Le problème est probablement côté FRONTEND ou AFFICHAGE")
                print("   ➡️ Vérifier le code React de l'explorateur")
                print("   ➡️ Vérifier les filtres appliqués dans l'interface")
            else:
                print("🚨 PROBLÈME CRITIQUE: Le maillot PSG est approuvé mais N'APPARAÎT PAS dans /api/jerseys/approved")
                print("   ➡️ Problème de filtrage dans l'endpoint approved")
        else:
            print(f"🚨 PROBLÈME IDENTIFIÉ: Le maillot PSG n'est PAS approuvé (Status: {status})")
            print("   ➡️ Le maillot doit être approuvé par un admin pour être visible")
    else:
        print("🚨 PROBLÈME CRITIQUE: Le maillot PSG N'EXISTE PAS dans la base de données")
        print("   ➡️ Vérifier l'ID et la référence fournis")
        print("   ➡️ Le maillot a peut-être été supprimé")
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"   - Maillot PSG trouvé: {'✅ OUI' if psg_jersey else '❌ NON'}")
    print(f"   - Status du maillot: {psg_jersey.get('status') if psg_jersey else 'N/A'}")
    print(f"   - Dans liste approved: {'✅ OUI' if psg_in_approved else '❌ NON'}")
    print(f"   - Total maillots approved: {len(approved_jerseys)}")
    print(f"   - Maillots avec photos: {len(jerseys_with_photos) if 'jerseys_with_photos' in locals() else 'N/A'}")

if __name__ == "__main__":
    main()