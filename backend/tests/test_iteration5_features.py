"""
Test iteration 5 features:
- Excel import: 167 master kits (8 teams x 21 seasons) 
- New fields: design, colors, sponsor, league, competition, source_url
- Image proxy endpoint for footballkitarchive CDN
- Updated filters for designs and leagues
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
API_URL = f"{BASE_URL}/api"


class TestStats:
    """Verify stats reflect imported data"""
    
    def test_stats_shows_167_master_kits(self):
        """Excel import resulted in 167 master kits"""
        response = requests.get(f"{API_URL}/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["master_kits"] == 167, f"Expected 167 kits, got {data['master_kits']}"
        
    def test_stats_shows_0_versions(self):
        """Old data cleared - no versions"""
        response = requests.get(f"{API_URL}/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["versions"] == 0, f"Expected 0 versions, got {data['versions']}"


class TestMasterKitsNewFields:
    """Verify kits have new fields from Excel import"""
    
    def test_kit_has_design_field(self):
        """Kits contain design field"""
        response = requests.get(f"{API_URL}/master-kits?limit=5")
        assert response.status_code == 200
        kits = response.json()
        assert len(kits) > 0
        for kit in kits:
            assert "design" in kit
            
    def test_kit_has_colors_field(self):
        """Kits contain colors field"""
        response = requests.get(f"{API_URL}/master-kits?limit=5")
        assert response.status_code == 200
        kits = response.json()
        for kit in kits:
            assert "colors" in kit
            
    def test_kit_has_sponsor_field(self):
        """Kits contain sponsor field"""
        response = requests.get(f"{API_URL}/master-kits?limit=5")
        assert response.status_code == 200
        kits = response.json()
        for kit in kits:
            assert "sponsor" in kit
            
    def test_kit_has_league_field(self):
        """Kits contain league field"""
        response = requests.get(f"{API_URL}/master-kits?limit=5")
        assert response.status_code == 200
        kits = response.json()
        for kit in kits:
            assert "league" in kit
            
    def test_kit_has_competition_field(self):
        """Kits contain competition field"""
        response = requests.get(f"{API_URL}/master-kits?limit=5")
        assert response.status_code == 200
        kits = response.json()
        for kit in kits:
            assert "competition" in kit
            
    def test_kit_has_source_url_field(self):
        """Kits contain source_url field"""
        response = requests.get(f"{API_URL}/master-kits?limit=5")
        assert response.status_code == 200
        kits = response.json()
        for kit in kits:
            assert "source_url" in kit

    def test_barcelona_kit_has_correct_design(self):
        """FC Barcelona kits have Stripes design"""
        response = requests.get(f"{API_URL}/master-kits?club=Barcelona&limit=1")
        assert response.status_code == 200
        kits = response.json()
        assert len(kits) > 0
        assert kits[0]["design"] == "Stripes", f"Expected 'Stripes' design, got '{kits[0]['design']}'"
        
    def test_la_liga_kit_has_league(self):
        """La Liga teams have league set"""
        response = requests.get(f"{API_URL}/master-kits?club=Barcelona&limit=1")
        assert response.status_code == 200
        kits = response.json()
        assert len(kits) > 0
        assert kits[0]["league"] == "La Liga", f"Expected 'La Liga', got '{kits[0]['league']}'"


class TestFilters:
    """Test filters endpoint for new fields"""
    
    def test_filters_contain_designs(self):
        """Filters endpoint returns designs"""
        response = requests.get(f"{API_URL}/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        assert "designs" in data
        assert len(data["designs"]) > 0
        
    def test_filters_contain_leagues(self):
        """Filters endpoint returns leagues"""
        response = requests.get(f"{API_URL}/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        assert "leagues" in data
        assert len(data["leagues"]) > 0
        
    def test_filters_designs_include_stripes(self):
        """Stripes design is in filters"""
        response = requests.get(f"{API_URL}/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        assert "Stripes" in data["designs"]
        
    def test_filters_leagues_include_la_liga(self):
        """La Liga is in leagues filter"""
        response = requests.get(f"{API_URL}/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        assert "La Liga" in data["leagues"]
        
    def test_filters_all_8_clubs_present(self):
        """All 8 teams from Excel are present"""
        response = requests.get(f"{API_URL}/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        expected_clubs = ["AC Milan", "Bayern München", "Borussia Dortmund", "FC Barcelona", 
                         "Inter Milan", "Olympique de Marseille", "Paris Saint Germain", "Real Madrid"]
        for club in expected_clubs:
            assert club in data["clubs"], f"Missing club: {club}"


class TestFiltering:
    """Test filtering by new fields"""
    
    def test_filter_by_club_barcelona(self):
        """Filter by club=Barcelona works"""
        response = requests.get(f"{API_URL}/master-kits?club=Barcelona")
        assert response.status_code == 200
        kits = response.json()
        assert len(kits) > 0
        for kit in kits:
            assert "Barcelona" in kit["club"]
            
    def test_filter_by_design_stripes(self):
        """Filter by design=Stripes works"""
        response = requests.get(f"{API_URL}/master-kits?design=Stripes")
        assert response.status_code == 200
        kits = response.json()
        assert len(kits) > 0
        for kit in kits:
            assert kit["design"] == "Stripes", f"Expected 'Stripes', got '{kit['design']}'"
            
    def test_filter_by_league_la_liga(self):
        """Filter by league=La Liga works"""
        response = requests.get(f"{API_URL}/master-kits?league=La%20Liga")
        assert response.status_code == 200
        kits = response.json()
        assert len(kits) > 0
        for kit in kits:
            assert kit["league"] == "La Liga", f"Expected 'La Liga', got '{kit['league']}'"


class TestImageProxy:
    """Test image proxy endpoint"""
    
    def test_image_proxy_valid_url(self):
        """Image proxy returns 200 for valid CDN URL"""
        url = "https://cdn.footballkitarchive.com/2025/03/28/1n1SonH8986lLqa.jpg"
        response = requests.get(f"{API_URL}/image-proxy?url={url}")
        assert response.status_code == 200
        assert "image" in response.headers.get("content-type", "")
        
    def test_image_proxy_rejects_non_cdn_url(self):
        """Image proxy rejects non-footballkitarchive URLs"""
        url = "https://example.com/image.jpg"
        response = requests.get(f"{API_URL}/image-proxy?url={url}")
        assert response.status_code == 400
        
    def test_image_proxy_has_cache_header(self):
        """Image proxy sets cache control header"""
        url = "https://cdn.footballkitarchive.com/2025/03/28/1n1SonH8986lLqa.jpg"
        response = requests.get(f"{API_URL}/image-proxy?url={url}")
        assert response.status_code == 200
        assert "Cache-Control" in response.headers


class TestKitDetail:
    """Test individual kit endpoint for new fields"""
    
    def test_kit_detail_has_new_fields(self):
        """Individual kit has all new fields"""
        # First get a kit ID
        response = requests.get(f"{API_URL}/master-kits?limit=1")
        assert response.status_code == 200
        kits = response.json()
        assert len(kits) > 0
        kit_id = kits[0]["kit_id"]
        
        # Get kit detail
        response = requests.get(f"{API_URL}/master-kits/{kit_id}")
        assert response.status_code == 200
        kit = response.json()
        
        # Verify new fields
        assert "design" in kit
        assert "colors" in kit
        assert "sponsor" in kit
        assert "league" in kit
        assert "competition" in kit
        assert "source_url" in kit


class TestSearchAcrossNewFields:
    """Test search functionality includes new fields"""
    
    def test_search_by_design_word(self):
        """Search finds kits by design term"""
        response = requests.get(f"{API_URL}/master-kits?search=Stripes")
        assert response.status_code == 200
        kits = response.json()
        assert len(kits) > 0
        
    def test_search_by_colors(self):
        """Search finds kits by color term"""
        response = requests.get(f"{API_URL}/master-kits?search=Blue")
        assert response.status_code == 200
        kits = response.json()
        assert len(kits) > 0


class TestDataIntegrity:
    """Verify data integrity from Excel import"""
    
    def test_21_seasons_exist(self):
        """21 seasons from 2005/2006 to 2025/2026"""
        response = requests.get(f"{API_URL}/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        assert len(data["seasons"]) == 21, f"Expected 21 seasons, got {len(data['seasons'])}"
        
    def test_8_clubs_exist(self):
        """8 clubs from import"""
        response = requests.get(f"{API_URL}/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        assert len(data["clubs"]) == 8, f"Expected 8 clubs, got {len(data['clubs'])}"
        
    def test_each_team_has_21_kits(self):
        """Each team has roughly 21 kits (some may be missing)"""
        # Barcelona should have 21
        response = requests.get(f"{API_URL}/master-kits?club=Barcelona&limit=50")
        assert response.status_code == 200
        kits = response.json()
        assert len(kits) == 21, f"Barcelona should have 21 kits, got {len(kits)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
