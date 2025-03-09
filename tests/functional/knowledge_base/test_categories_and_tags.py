"""
Functional tests for the Knowledge Base categories and tags functionality.
These tests verify the category and tag management capabilities of the knowledge base service.
"""
import os
import unittest
import requests
import json
from typing import Dict, Any, List, Optional

# Set the API base URL - use environment variable or default to localhost:8001
KB_API_BASE_URL = os.environ.get("KB_API_BASE_URL", "http://localhost:8001")


class TestKnowledgeBaseCategoriesAndTags(unittest.TestCase):
    """Test the Knowledge Base categories and tags functionality"""

    def setUp(self):
        """Set up test data and ensure the API is accessible"""
        self.categories_url = f"{KB_API_BASE_URL}/api/v1/categories"
        self.tags_url = f"{KB_API_BASE_URL}/api/v1/tags"
        
        # Test data
        self.test_category = {
            "name": "Test Category",
            "description": "Category for functional tests"
        }
        
        self.test_tag = {
            "name": "test-tag",
            "description": "Tag for functional tests"
        }
        
        # Verify API is accessible and database is healthy
        try:
            response = requests.get(f"{KB_API_BASE_URL}/health")
            if response.status_code != 200:
                self.skipTest(f"Knowledge Base API is not available at {KB_API_BASE_URL}")
            
            # Check if the database component is healthy
            health_data = response.json()
            if health_data.get("components", {}).get("database") != "healthy":
                self.skipTest(f"Knowledge Base database is not healthy at {KB_API_BASE_URL}")
            
            # Log if API is in degraded state but we're continuing with tests
            if health_data.get("status") == "degraded":
                print(f"WARNING: Knowledge Base API is in degraded state, but database is healthy. Continuing with tests.")
                
        except requests.RequestException:
            self.skipTest(f"Knowledge Base API is not available at {KB_API_BASE_URL}")
        except ValueError:
            self.skipTest(f"Invalid health response from Knowledge Base API at {KB_API_BASE_URL}")
        
        # Clean up any existing test categories and tags
        self._cleanup_test_categories()
        self._cleanup_test_tags()

    def tearDown(self):
        """Clean up after tests"""
        self._cleanup_test_categories()
        self._cleanup_test_tags()

    def test_create_category(self):
        """Test creating a category"""
        response = requests.post(self.categories_url, json=self.test_category)
        self.assertEqual(response.status_code, 200, f"Failed to create category: {response.text}")
        
        # Verify response
        category = response.json()
        self.assertEqual(category["name"], self.test_category["name"])
        self.assertEqual(category["description"], self.test_category["description"])
        self.assertIsNotNone(category["id"])

    def test_get_categories(self):
        """Test retrieving categories"""
        # Create a test category first
        create_response = requests.post(self.categories_url, json=self.test_category)
        self.assertEqual(create_response.status_code, 200)
        created_category = create_response.json()
        
        # Get all categories
        response = requests.get(self.categories_url)
        self.assertEqual(response.status_code, 200)
        categories = response.json()
        
        # Verify our test category is in the list
        category_ids = [category["id"] for category in categories]
        self.assertIn(created_category["id"], category_ids)

    def test_get_single_category(self):
        """Test retrieving a single category"""
        # Create a test category first
        create_response = requests.post(self.categories_url, json=self.test_category)
        self.assertEqual(create_response.status_code, 200)
        created_category = create_response.json()
        
        # Get the category by ID
        response = requests.get(f"{self.categories_url}/{created_category['id']}")
        self.assertEqual(response.status_code, 200)
        category = response.json()
        
        # Verify category data
        self.assertEqual(category["id"], created_category["id"])
        self.assertEqual(category["name"], self.test_category["name"])
        self.assertEqual(category["description"], self.test_category["description"])

    def test_update_category(self):
        """Test updating a category"""
        # Create a test category first
        create_response = requests.post(self.categories_url, json=self.test_category)
        self.assertEqual(create_response.status_code, 200)
        created_category = create_response.json()
        
        # Update data
        update_data = {
            "name": "Updated Test Category",
            "description": "Updated description"
        }
        
        # Update the category
        response = requests.put(f"{self.categories_url}/{created_category['id']}", json=update_data)
        self.assertEqual(response.status_code, 200)
        updated_category = response.json()
        
        # Verify updated data
        self.assertEqual(updated_category["id"], created_category["id"])
        self.assertEqual(updated_category["name"], update_data["name"])
        self.assertEqual(updated_category["description"], update_data["description"])

    def test_delete_category(self):
        """Test deleting a category"""
        # Create a test category first
        create_response = requests.post(self.categories_url, json=self.test_category)
        self.assertEqual(create_response.status_code, 200)
        created_category = create_response.json()
        
        # Delete the category
        response = requests.delete(f"{self.categories_url}/{created_category['id']}")
        self.assertEqual(response.status_code, 200)
        
        # Verify category is deleted
        get_response = requests.get(f"{self.categories_url}/{created_category['id']}")
        self.assertEqual(get_response.status_code, 404)

    def test_hierarchical_categories(self):
        """Test hierarchical categories (parent-child relationships)"""
        # Create a parent category
        parent_category = {
            "name": "Parent Category",
            "description": "Parent category for testing"
        }
        parent_response = requests.post(self.categories_url, json=parent_category)
        self.assertEqual(parent_response.status_code, 200)
        parent = parent_response.json()
        
        # Create a child category
        child_category = {
            "name": "Child Category",
            "description": "Child category for testing",
            "parent_id": parent["id"]
        }
        child_response = requests.post(self.categories_url, json=child_category)
        self.assertEqual(child_response.status_code, 200)
        child = child_response.json()
        
        # Verify parent-child relationship
        self.assertEqual(child["parent_id"], parent["id"])
        
        # Get the parent category with children
        response = requests.get(f"{self.categories_url}/{parent['id']}")
        self.assertEqual(response.status_code, 200)

    def test_create_tag(self):
        """Test creating a tag"""
        response = requests.post(self.tags_url, json=self.test_tag)
        self.assertEqual(response.status_code, 200, f"Failed to create tag: {response.text}")
        
        # Verify response
        tag = response.json()
        self.assertEqual(tag["name"], self.test_tag["name"])
        self.assertEqual(tag["description"], self.test_tag["description"])
        self.assertIsNotNone(tag["id"])

    def test_get_tags(self):
        """Test retrieving tags"""
        # Create a test tag first
        create_response = requests.post(self.tags_url, json=self.test_tag)
        self.assertEqual(create_response.status_code, 200)
        created_tag = create_response.json()
        
        # Get all tags
        response = requests.get(self.tags_url)
        self.assertEqual(response.status_code, 200)
        tags = response.json()
        
        # Verify our test tag is in the list
        tag_ids = [tag["id"] for tag in tags]
        self.assertIn(created_tag["id"], tag_ids)

    def test_get_single_tag(self):
        """Test retrieving a single tag"""
        # Create a test tag first
        create_response = requests.post(self.tags_url, json=self.test_tag)
        self.assertEqual(create_response.status_code, 200)
        created_tag = create_response.json()
        
        # Get the tag by ID
        response = requests.get(f"{self.tags_url}/{created_tag['id']}")
        self.assertEqual(response.status_code, 200)
        tag = response.json()
        
        # Verify tag data
        self.assertEqual(tag["id"], created_tag["id"])
        self.assertEqual(tag["name"], self.test_tag["name"])
        self.assertEqual(tag["description"], self.test_tag["description"])

    def test_update_tag(self):
        """Test updating a tag"""
        # Create a test tag first
        create_response = requests.post(self.tags_url, json=self.test_tag)
        self.assertEqual(create_response.status_code, 200)
        created_tag = create_response.json()
        
        # Update data
        update_data = {
            "name": "updated-test-tag",
            "description": "Updated description"
        }
        
        # Update the tag
        response = requests.put(f"{self.tags_url}/{created_tag['id']}", json=update_data)
        self.assertEqual(response.status_code, 200)
        updated_tag = response.json()
        
        # Verify updated data
        self.assertEqual(updated_tag["id"], created_tag["id"])
        self.assertEqual(updated_tag["name"], update_data["name"])
        self.assertEqual(updated_tag["description"], update_data["description"])

    def test_delete_tag(self):
        """Test deleting a tag"""
        # Create a test tag first
        create_response = requests.post(self.tags_url, json=self.test_tag)
        self.assertEqual(create_response.status_code, 200)
        created_tag = create_response.json()
        
        # Delete the tag
        response = requests.delete(f"{self.tags_url}/{created_tag['id']}")
        self.assertEqual(response.status_code, 200)
        
        # Verify tag is deleted
        get_response = requests.get(f"{self.tags_url}/{created_tag['id']}")
        self.assertEqual(get_response.status_code, 404)

    # Helper methods
    def _cleanup_test_categories(self):
        """Clean up test categories created during testing"""
        try:
            # Get all categories
            response = requests.get(self.categories_url)
            if response.status_code == 200:
                categories = response.json()
                
                # Delete test categories
                for category in categories:
                    if category["name"].startswith("Test ") or category["name"] in ["Parent Category", "Child Category", "Updated Test Category"]:
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
                    if tag["name"] in ["test-tag", "updated-test-tag"]:
                        requests.delete(f"{self.tags_url}/{tag['id']}")
        except requests.RequestException:
            pass


if __name__ == "__main__":
    unittest.main()
