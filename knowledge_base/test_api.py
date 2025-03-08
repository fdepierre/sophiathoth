#!/usr/bin/env python3
"""
Test script for the Knowledge Base Service API
"""
import requests
import json
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Base URL
BASE_URL = "http://localhost:8003/api/v1"

def check_health():
    """Check the health of the Knowledge Base service"""
    try:
        response = requests.get("http://localhost:8003/health")
        response.raise_for_status()
        health_data = response.json()
        logger.info(f"Health status: {health_data}")
        return health_data["status"] == "ok"
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

def create_category(name, description=None):
    """Create a new knowledge category or get an existing one"""
    try:
        # Try to create a new category
        data = {
            "name": name,
            "description": description
        }
        response = requests.post(f"{BASE_URL}/categories/", json=data)
        
        # If creation fails because the category already exists, try to get it
        if response.status_code == 400 and "already exists" in response.text:
            # Get all categories
            get_response = requests.get(f"{BASE_URL}/categories/")
            get_response.raise_for_status()
            categories = get_response.json()
            
            # Find the category with the matching name
            for category in categories:
                if category["name"] == name:
                    logger.info(f"Using existing category: {category['name']} (ID: {category['id']})")
                    return category
        else:
            # If creation succeeded, return the new category
            response.raise_for_status()
            category = response.json()
            logger.info(f"Created category: {category['name']} (ID: {category['id']})")
            return category
            
        # If we get here, we couldn't create or find the category
        logger.error(f"Could not create or find category: {name}")
        return None
    except Exception as e:
        logger.error(f"Failed to create/get category: {e}")
        return None

def create_knowledge_entry(title, content, summary=None, source_type="manual", category_id=None, tags=None):
    """Create a new knowledge entry"""
    try:
        data = {
            "title": title,
            "content": content,
            "summary": summary,
            "source_type": source_type,
            "category_id": category_id,
            "tags": tags or []
        }
        response = requests.post(f"{BASE_URL}/entries/", json=data)
        response.raise_for_status()
        entry = response.json()
        logger.info(f"Created knowledge entry: {entry['title']} (ID: {entry['id']})")
        return entry
    except Exception as e:
        logger.error(f"Failed to create knowledge entry: {e}")
        return None

def search_knowledge(query, limit=10):
    """Search for knowledge entries"""
    try:
        response = requests.get(f"{BASE_URL}/search/?query={query}&limit={limit}")
        response.raise_for_status()
        results = response.json()
        logger.info(f"Search for '{query}' found {results['total']} results")
        for i, entry in enumerate(results['results'], 1):
            logger.info(f"  {i}. {entry['title']}")
        return results
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return None

def upload_attachment(entry_id, filename="test_file.txt", content="This is a test file"):
    """Upload an attachment for a knowledge entry"""
    try:
        # Create a test file
        files = {
            'file': (filename, content.encode('utf-8'), 'text/plain')
        }
        response = requests.post(f"{BASE_URL}/entries/{entry_id}/attachments", files=files)
        response.raise_for_status()
        attachment = response.json()
        logger.info(f"Uploaded attachment: {attachment['original_filename']} (ID: {attachment['id']})")
        return attachment
    except Exception as e:
        logger.error(f"Failed to upload attachment: {e}")
        return None

def download_attachment(entry_id, attachment_id):
    """Download an attachment for a knowledge entry"""
    try:
        response = requests.get(f"{BASE_URL}/entries/{entry_id}/attachments/{attachment_id}")
        response.raise_for_status()
        logger.info(f"Downloaded attachment: {len(response.content)} bytes")
        return response.content
    except Exception as e:
        logger.error(f"Failed to download attachment: {e}")
        return None

def run_tests():
    """Run a series of tests on the Knowledge Base API"""
    if not check_health():
        logger.error("Health check failed. Exiting.")
        return False
    
    # Create a test category
    category = create_category("Test Category", "A category for testing purposes")
    if not category:
        return False
    
    # Create a test knowledge entry
    entry = create_knowledge_entry(
        title="Test Knowledge Entry",
        content="This is a test knowledge entry with detailed content about testing procedures.",
        summary="Test entry about testing",
        category_id=category["id"],
        tags=["test", "api", "documentation"]
    )
    if not entry:
        return False
    
    # Upload an attachment
    attachment = upload_attachment(entry["id"])
    if not attachment:
        return False
    
    # Download the attachment
    attachment_content = download_attachment(entry["id"], attachment["id"])
    if not attachment_content:
        return False
    
    # Search for the entry
    search_results = search_knowledge("test")
    if not search_results:
        return False
    
    logger.info("All tests completed successfully!")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
