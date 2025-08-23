#!/usr/bin/env python3
"""
Cleanup test data from TopKit database
Remove test teams, master jerseys, jersey releases and associated contributions
"""

import os
import pymongo
from datetime import datetime

def main():
    # Get MongoDB connection
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/topkit')
    client = pymongo.MongoClient(mongo_url)
    db = client.get_default_database()
    
    print("🧹 CLEANING UP TEST DATA FROM TOPKIT DATABASE")
    print("=" * 60)
    
    deleted_counts = {
        'teams': 0,
        'brands': 0,
        'master_jerseys': 0,
        'jersey_releases': 0,
        'contributions': 0
    }
    
    # 1. Delete test teams
    test_team_ids = [
        '67fdd572-78bd-4207-b3a1-0503970b482b',  # FC Barcelona Test
        '212221c8-0182-4e81-a915-33a41909a635',  # Paris Saint-Germain Actualisation
        '669c3187-e6d5-4c28-87e8-20786c172735',  # AS Monaco Updated
        'ca51d848-e2a3-469c-82b5-8952ce6ec87f',  # Test Team PNG valide
        '438d3668-39c2-4377-ae52-268d39076383',  # Test Storage Team
        '76a5c303-c356-4ddc-b377-ace6f7ed8d36'   # Test Team for Reference
    ]
    
    print(f"🏃 Deleting {len(test_team_ids)} test teams...")
    for team_id in test_team_ids:
        team = db.teams.find_one({'id': team_id})
        if team:
            print(f"- Deleting team: {team['name']} ({team_id})")
            db.teams.delete_one({'id': team_id})
            deleted_counts['teams'] += 1
        else:
            print(f"- Team not found: {team_id}")
    
    # 2. Remove image modifications from real brands (keep Adidas but remove test modifications)
    print(f"\n🏢 Cleaning up brand modifications...")
    adidas_updates = db.brands.update_one(
        {'id': 'c2538384-3e83-41e3-8d1c-8c96f89b1c5a'},
        {'$unset': {
            'images_applied_from_contribution': '',
            'last_modified_at': '',
            'last_modified_by': ''
        }}
    )
    if adidas_updates.modified_count > 0:
        print("- Removed test modifications from Adidas brand")
    
    # 3. Delete all master jerseys (they appear to be test data)
    master_jerseys_result = db.master_jerseys.delete_many({})
    deleted_counts['master_jerseys'] = master_jerseys_result.deleted_count
    print(f"🏈 Deleted {deleted_counts['master_jerseys']} master jerseys")
    
    # 4. Delete all jersey releases (they appear to be test data)
    jersey_releases_result = db.jersey_releases.delete_many({})
    deleted_counts['jersey_releases'] = jersey_releases_result.deleted_count
    print(f"👕 Deleted {deleted_counts['jersey_releases']} jersey releases")
    
    # 5. Delete contributions related to test entities
    test_contribution_result = db.contributions.delete_many({
        '$or': [
            {'entity_id': {'$in': test_team_ids}},
            {'entity_id': 'c2538384-3e83-41e3-8d1c-8c96f89b1c5a'},  # Adidas contributions
            {'title': {'$regex': 'test', '$options': 'i'}},
            {'description': {'$regex': 'test', '$options': 'i'}}
        ]
    })
    deleted_counts['contributions'] = test_contribution_result.deleted_count
    print(f"📝 Deleted {deleted_counts['contributions']} test contributions")
    
    # 6. Clean up any collections or user data related to test entities
    print(f"\n🗂️ Cleaning up user collections...")
    collections_cleaned = db.user_jersey_collections.delete_many({
        'jersey_release_id': {'$in': []}  # No specific releases to delete for now
    })
    print(f"- Cleaned {collections_cleaned.deleted_count} collection entries")
    
    # 7. Summary
    print(f"\n🎉 CLEANUP COMPLETE!")
    print(f"=" * 40)
    total_deleted = sum(deleted_counts.values())
    for entity_type, count in deleted_counts.items():
        if count > 0:
            print(f"✅ {entity_type.replace('_', ' ').title()}: {count} deleted")
    
    print(f"\n📊 Total items deleted: {total_deleted}")
    
    # 8. Final verification
    print(f"\n📋 FINAL DATABASE COUNTS:")
    print(f"- Teams: {db.teams.count_documents({})}")
    print(f"- Brands: {db.brands.count_documents({})}")
    print(f"- Players: {db.players.count_documents({})}")
    print(f"- Competitions: {db.competitions.count_documents({})}")
    print(f"- Master Jerseys: {db.master_jerseys.count_documents({})}")
    print(f"- Jersey Releases: {db.jersey_releases.count_documents({})}")
    print(f"- Contributions: {db.contributions.count_documents({})}")
    
    # 9. Check for any remaining entities with test-related modifications
    print(f"\n🔍 CHECKING FOR REMAINING TEST DATA:")
    remaining_test_teams = db.teams.count_documents({
        'name': {'$regex': 'test|actualisation|updated', '$options': 'i'}
    })
    remaining_modified_entities = db.teams.count_documents({
        'images_applied_from_contribution': {'$exists': True}
    }) + db.brands.count_documents({
        'images_applied_from_contribution': {'$exists': True}
    })
    
    if remaining_test_teams > 0:
        print(f"⚠️ {remaining_test_teams} teams with test-like names still exist")
    if remaining_modified_entities > 0:
        print(f"⚠️ {remaining_modified_entities} entities still have test modifications")
    
    if remaining_test_teams == 0 and remaining_modified_entities == 0:
        print("✅ No remaining test data found - database is clean!")
    
    client.close()

if __name__ == "__main__":
    main()