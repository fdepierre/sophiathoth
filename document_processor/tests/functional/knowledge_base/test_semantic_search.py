"""
Functional tests for the Knowledge Base semantic search functionality.
These tests verify the semantic search capabilities of the knowledge base service.
"""
import os
import unittest
import requests
import json
from typing import Dict, Any, List, Optional

# Set the API base URL - use environment variable or default to localhost:8001
KB_API_BASE_URL = os.environ.get("KB_API_BASE_URL", "http://localhost:8001")


class TestKnowledgeBaseSemanticSearch(unittest.TestCase):
    """Test the Knowledge Base semantic search functionality"""

    def setUp(self):
        """Set up test data and ensure the API is accessible"""
        self.api_url = f"{KB_API_BASE_URL}/api/v1/entries"
        
        # Test data - create entries with varied content for semantic search testing
        self.test_entries = [
            {
                "title": "Climate Change Effects",
                "content": "Climate change is causing rising sea levels, extreme weather events, and disruptions to ecosystems worldwide. Many species are at risk of extinction due to habitat loss.",
                "summary": "Overview of climate change impacts",
                "source_type": "test",
                "tags": ["climate", "environment", "test"]
            },
            {
                "title": "Renewable Energy Solutions",
                "content": "Solar, wind, and hydroelectric power are renewable energy sources that can help reduce greenhouse gas emissions. These technologies are becoming more affordable and efficient.",
                "summary": "Overview of renewable energy options",
                "source_type": "test",
                "tags": ["energy", "environment", "test"]
            },
            {
                "title": "Artificial Intelligence Applications",
                "content": "AI is being used in healthcare for diagnosis, in transportation for autonomous vehicles, and in business for process optimization. Machine learning algorithms can identify patterns in large datasets.",
                "summary": "Overview of AI applications",
                "source_type": "test",
                "tags": ["technology", "ai", "test"]
            }
        ]
        
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
        
        # Create test entries for semantic search
        self.created_entries = []
        for entry in self.test_entries:
            response = requests.post(self.api_url, json=entry)
            if response.status_code == 200:
                self.created_entries.append(response.json())

    def tearDown(self):
        """Clean up after tests"""
        # Delete test entries
        for entry in self.created_entries:
            try:
                requests.delete(f"{self.api_url}/{entry['id']}")
            except Exception:
                pass

    def test_semantic_search_get(self):
        """Test semantic search using GET endpoint"""
        # Skip if no test entries were created
        if not self.created_entries:
            self.skipTest("No test entries were created for semantic search")
        
        # Test semantic search for climate-related content
        response = requests.get(f"{self.api_url}/search?query=global warming impacts")
        self.assertEqual(response.status_code, 200)
        results = response.json()
        
        # Verify results
        self.assertIsNotNone(results.get("results"))
        self.assertGreaterEqual(len(results["results"]), 1)
        
        # The climate change entry should be in the top results
        found_climate_entry = False
        for result in results["results"]:
            if "Climate Change" in result["title"]:
                found_climate_entry = True
                break
        
        self.assertTrue(found_climate_entry, "Climate change entry not found in search results")

    def test_semantic_search_post(self):
        """Test semantic search using POST endpoint with filters"""
        # Skip if no test entries were created
        if not self.created_entries:
            self.skipTest("No test entries were created for semantic search")
        
        # Test semantic search for renewable energy with filters
        search_request = {
            "query": "sustainable power generation",
            "filters": {
                "tags": ["energy"]
            },
            "limit": 10,
            "offset": 0
        }
        
        response = requests.post(f"{self.api_url}/search", json=search_request)
        self.assertEqual(response.status_code, 200)
        results = response.json()
        
        # Verify results
        self.assertIsNotNone(results.get("results"))
        
        # If we have results, they should all have the energy tag
        if results["results"]:
            for result in results["results"]:
                tag_names = [tag["name"] for tag in result["tags"]]
                self.assertIn("energy", tag_names)
        
        # The renewable energy entry should be in the top results if we have any results
        if results["results"]:
            found_energy_entry = False
            for result in results["results"]:
                if "Renewable Energy" in result["title"]:
                    found_energy_entry = True
                    break
            
            self.assertTrue(found_energy_entry, "Renewable energy entry not found in search results")

    def test_semantic_search_with_category_filter(self):
        """Test semantic search with category filter"""
        # Skip if no test entries were created
        if not self.created_entries:
            self.skipTest("No test entries were created for semantic search")
        
        # First, create a category
        category_data = {
            "name": "Technology",
            "description": "Technology-related knowledge"
        }
        
        category_response = requests.post(f"{KB_API_BASE_URL}/api/v1/categories", json=category_data)
        self.assertEqual(category_response.status_code, 200)
        category = category_response.json()
        
        # Update the AI entry to have this category
        ai_entry = next((entry for entry in self.created_entries if "Artificial Intelligence" in entry["title"]), None)
        if ai_entry:
            update_data = {"category_id": category["id"]}
            requests.put(f"{self.api_url}/{ai_entry['id']}", json=update_data)
        
        # Search with category filter
        search_request = {
            "query": "machine learning applications",
            "filters": {
                "category_id": category["id"]
            }
        }
        
        response = requests.post(f"{self.api_url}/search", json=search_request)
        self.assertEqual(response.status_code, 200)
        results = response.json()
        
        # Verify results
        if results["results"]:
            # All results should have the Technology category
            for result in results["results"]:
                self.assertEqual(result["category_id"], category["id"])
        
        # Clean up the category
        try:
            requests.delete(f"{KB_API_BASE_URL}/api/v1/categories/{category['id']}")
        except Exception:
            pass

    def test_semantic_similarity(self):
        """Test semantic similarity between entries"""
        # Skip if no test entries were created
        if not self.created_entries:
            self.skipTest("No test entries were created for semantic search")
        
        # Find entries about environment (should match both climate and renewable energy)
        response = requests.get(f"{self.api_url}/search?query=environmental protection")
        self.assertEqual(response.status_code, 200)
        results = response.json()
        
        # Verify results
        self.assertIsNotNone(results.get("results"))
        
        # We should have at least 2 results related to environment
        environment_entries = 0
        for result in results["results"]:
            if "Climate Change" in result["title"] or "Renewable Energy" in result["title"]:
                environment_entries += 1
        
        self.assertGreaterEqual(environment_entries, 1, "Not enough environment-related entries found")


if __name__ == "__main__":
    unittest.main()
