"""
Functional tests for the Knowledge Base API.
These tests verify the core functionality of the knowledge base service.
"""
import os
import unittest
import requests
import json
import tempfile
from typing import Dict, Any, List, Optional

# Set the API base URL - use environment variable or default to localhost:8001
KB_API_BASE_URL = os.environ.get("KB_API_BASE_URL", "http://localhost:8001")


class TestKnowledgeBaseAPI(unittest.TestCase):
    """Test the Knowledge Base API endpoints"""

    def setUp(self):
        """Set up test data and ensure the API is accessible"""
        self.api_url = f"{KB_API_BASE_URL}/api/v1/knowledge"
        self.categories_url = f"{KB_API_BASE_URL}/api/v1/categories"
        self.tags_url = f"{KB_API_BASE_URL}/api/v1/tags"
        
        # Test data
        self.test_entry = {
            "title": "Test Knowledge Entry",
            "content": "This is a test knowledge entry created for functional testing.",
            "summary": "Test entry summary",
            "source_type": "test",
            "tags": ["test", "functional-test"]
        }
        
        # Verify API is accessible
        try:
            response = requests.get(f"{KB_API_BASE_URL}/health")
            if response.status_code != 200:
                self.skipTest(f"Knowledge Base API is not available at {KB_API_BASE_URL}")
        except requests.RequestException:
            self.skipTest(f"Knowledge Base API is not available at {KB_API_BASE_URL}")
        
        # Create test category for use in tests
        self.test_category = self._create_test_category()
        
        # Clean up any existing test entries
        self._cleanup_test_entries()

    def tearDown(self):
        """Clean up after tests"""
        self._cleanup_test_entries()
        self._cleanup_test_categories()
        self._cleanup_test_tags()

    def test_create_knowledge_entry(self):
        """Test creating a knowledge entry"""
        # Add category to the test entry
        entry_data = self.test_entry.copy()
        if self.test_category:
            entry_data["category_id"] = self.test_category["id"]
        
        # Create entry
        response = requests.post(self.api_url, json=entry_data)
        self.assertEqual(response.status_code, 200, f"Failed to create knowledge entry: {response.text}")
        
        # Verify response
        entry = response.json()
        self.assertEqual(entry["title"], entry_data["title"])
        self.assertEqual(entry["content"], entry_data["content"])
        self.assertEqual(entry["source_type"], entry_data["source_type"])
        
        # Verify tags were created
        self.assertEqual(len(entry["tags"]), len(entry_data["tags"]))
        tag_names = [tag["name"] for tag in entry["tags"]]
        for tag_name in entry_data["tags"]:
            self.assertIn(tag_name, tag_names)

    def test_get_knowledge_entries(self):
        """Test retrieving knowledge entries"""
        # Create a test entry first
        entry_data = self.test_entry.copy()
        if self.test_category:
            entry_data["category_id"] = self.test_category["id"]
        
        create_response = requests.post(self.api_url, json=entry_data)
        self.assertEqual(create_response.status_code, 200)
        created_entry = create_response.json()
        
        # Get all entries
        response = requests.get(self.api_url)
        self.assertEqual(response.status_code, 200)
        entries = response.json()
        
        # Verify our test entry is in the list
        entry_ids = [entry["id"] for entry in entries]
        self.assertIn(created_entry["id"], entry_ids)
        
        # Test filtering by category
        if self.test_category:
            response = requests.get(f"{self.api_url}?category_id={self.test_category['id']}")
            self.assertEqual(response.status_code, 200)
            filtered_entries = response.json()
            self.assertTrue(all(entry["category_id"] == self.test_category["id"] for entry in filtered_entries))

    def test_get_single_knowledge_entry(self):
        """Test retrieving a single knowledge entry"""
        # Create a test entry first
        create_response = requests.post(self.api_url, json=self.test_entry)
        self.assertEqual(create_response.status_code, 200)
        created_entry = create_response.json()
        
        # Get the entry by ID
        response = requests.get(f"{self.api_url}/{created_entry['id']}")
        self.assertEqual(response.status_code, 200)
        entry = response.json()
        
        # Verify entry data
        self.assertEqual(entry["id"], created_entry["id"])
        self.assertEqual(entry["title"], self.test_entry["title"])
        self.assertEqual(entry["content"], self.test_entry["content"])

    def test_update_knowledge_entry(self):
        """Test updating a knowledge entry"""
        # Create a test entry first
        create_response = requests.post(self.api_url, json=self.test_entry)
        self.assertEqual(create_response.status_code, 200)
        created_entry = create_response.json()
        
        # Update data
        update_data = {
            "title": "Updated Test Entry",
            "content": "This content has been updated",
            "summary": "Updated summary"
        }
        
        # Update the entry
        response = requests.put(f"{self.api_url}/{created_entry['id']}", json=update_data)
        self.assertEqual(response.status_code, 200)
        updated_entry = response.json()
        
        # Verify updated data
        self.assertEqual(updated_entry["id"], created_entry["id"])
        self.assertEqual(updated_entry["title"], update_data["title"])
        self.assertEqual(updated_entry["content"], update_data["content"])
        self.assertEqual(updated_entry["summary"], update_data["summary"])

    def test_delete_knowledge_entry(self):
        """Test deleting a knowledge entry"""
        # Create a test entry first
        create_response = requests.post(self.api_url, json=self.test_entry)
        self.assertEqual(create_response.status_code, 200)
        created_entry = create_response.json()
        
        # Delete the entry
        response = requests.delete(f"{self.api_url}/{created_entry['id']}")
        self.assertEqual(response.status_code, 200)
        
        # Verify entry is deleted
        get_response = requests.get(f"{self.api_url}/{created_entry['id']}")
        self.assertEqual(get_response.status_code, 404)

    def test_search_knowledge(self):
        """Test searching knowledge entries"""
        # Create a test entry with specific content for searching
        search_entry = self.test_entry.copy()
        search_entry["title"] = "Unique Search Title"
        search_entry["content"] = "This entry contains unique search terms like xylophone and zephyr"
        
        create_response = requests.post(self.api_url, json=search_entry)
        self.assertEqual(create_response.status_code, 200)
        
        # Search using GET endpoint
        response = requests.get(f"{self.api_url}/search?query=xylophone")
        self.assertEqual(response.status_code, 200)
        search_results = response.json()
        
        # Verify search results
        self.assertGreaterEqual(len(search_results["results"]), 1)
        
        # Search using POST endpoint
        search_request = {
            "query": "zephyr",
            "limit": 10,
            "offset": 0
        }
        response = requests.post(f"{self.api_url}/search", json=search_request)
        self.assertEqual(response.status_code, 200)
        post_search_results = response.json()
        
        # Verify search results
        self.assertGreaterEqual(len(post_search_results["results"]), 1)

    def test_attachment_upload_and_download(self):
        """Test uploading and downloading attachments"""
        # Create a test entry first
        create_response = requests.post(self.api_url, json=self.test_entry)
        self.assertEqual(create_response.status_code, 200)
        created_entry = create_response.json()
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            temp_file.write(b"This is test attachment content")
            temp_file.flush()
            temp_file.seek(0)
            
            # Upload the attachment
            files = {"file": ("test_attachment.txt", temp_file, "text/plain")}
            response = requests.post(
                f"{self.api_url}/{created_entry['id']}/attachments",
                files=files
            )
            self.assertEqual(response.status_code, 200)
            attachment = response.json()
            
            # Verify attachment data
            self.assertEqual(attachment["knowledge_id"], created_entry["id"])
            self.assertEqual(attachment["original_filename"], "test_attachment.txt")
            self.assertEqual(attachment["content_type"], "text/plain")
            
            # Get all attachments
            response = requests.get(f"{self.api_url}/{created_entry['id']}/attachments")
            self.assertEqual(response.status_code, 200)
            attachments = response.json()
            self.assertEqual(len(attachments), 1)
            
            # Download the attachment
            response = requests.get(
                f"{self.api_url}/{created_entry['id']}/attachments/{attachment['id']}/download"
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"This is test attachment content")

    def test_revisions(self):
        """Test knowledge entry revisions"""
        # Create a test entry first
        create_response = requests.post(self.api_url, json=self.test_entry)
        self.assertEqual(create_response.status_code, 200)
        created_entry = create_response.json()
        
        # Update the entry to create a new revision
        update_data = {
            "title": "Updated for Revision",
            "content": "This content has been updated to create a revision"
        }
        response = requests.put(f"{self.api_url}/{created_entry['id']}", json=update_data)
        self.assertEqual(response.status_code, 200)
        
        # Get revisions
        response = requests.get(f"{self.api_url}/{created_entry['id']}/revisions")
        self.assertEqual(response.status_code, 200)
        revisions = response.json()
        
        # Verify revisions
        self.assertGreaterEqual(len(revisions), 1)
        # First revision should match original content
        self.assertEqual(revisions[0]["title"], self.test_entry["title"])
        self.assertEqual(revisions[0]["content"], self.test_entry["content"])

    # Helper methods
    def _create_test_category(self) -> Optional[Dict[str, Any]]:
        """Create a test category for use in tests"""
        category_data = {
            "name": "Test Category",
            "description": "Category for functional tests"
        }
        
        try:
            response = requests.post(self.categories_url, json=category_data)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        
        return None

    def _cleanup_test_entries(self):
        """Clean up test entries created during testing"""
        try:
            # Get all entries
            response = requests.get(self.api_url)
            if response.status_code == 200:
                entries = response.json()
                
                # Delete test entries
                for entry in entries:
                    if entry["title"].startswith("Test ") or "test" in entry["source_type"]:
                        requests.delete(f"{self.api_url}/{entry['id']}")
        except requests.RequestException:
            pass

    def _cleanup_test_categories(self):
        """Clean up test categories created during testing"""
        try:
            # Get all categories
            response = requests.get(self.categories_url)
            if response.status_code == 200:
                categories = response.json()
                
                # Delete test categories
                for category in categories:
                    if category["name"].startswith("Test "):
                        requests.delete(f"{self.categories_url}/{category['id']}")
        except requests.RequestException:
            pass

    def _cleanup_test_tags(self):
        """Clean up test tags created during testing"""
        try:
            # Get all tags
            response = requests.get(self.tags_url)
            if response.status_code == 200:
                tags = response.json()
                
                # Delete test tags
                for tag in tags:
                    if tag["name"] in ["test", "functional-test"]:
                        requests.delete(f"{self.tags_url}/{tag['id']}")
        except requests.RequestException:
            pass


if __name__ == "__main__":
    unittest.main()
