"""
Functional tests for Web UI search functionality.
These tests verify the search functionality of the web UI.
"""
import os
import unittest
import time
import random
import string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from tests.functional.web_ui.base_test import BaseWebUITest


class TestSearch(BaseWebUITest):
    """Test the search functionality of the web UI."""
    
    def setUp(self):
        """Set up before each test."""
        super().setUp()
        # Get test credentials from environment variables
        self.test_username = os.environ.get('TEST_USERNAME', 'testuser')
        self.test_password = os.environ.get('TEST_PASSWORD', 'testpassword')
        
        # Login before each test
        self.navigate_to('/login')
        login_success = self.login(self.test_username, self.test_password)
        if not login_success:
            self.skipTest("Login failed, skipping test")
        
        # Create test entries for search tests
        self.test_entries = self.create_test_entries()
    
    def tearDown(self):
        """Clean up after each test."""
        # Delete test entries
        self.delete_test_entries()
        super().tearDown()
    
    def generate_random_string(self, length=8):
        """Generate a random string for test data."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def create_test_entries(self):
        """Create test entries for search tests."""
        test_entries = []
        
        # Create entries with specific content for search tests
        entries_data = [
            {
                "title": f"Climate Change Test Entry {self.generate_random_string()}",
                "content": "Climate change is causing rising sea levels and extreme weather events."
            },
            {
                "title": f"Renewable Energy Test Entry {self.generate_random_string()}",
                "content": "Solar and wind power are renewable energy sources that help reduce emissions."
            },
            {
                "title": f"AI Technology Test Entry {self.generate_random_string()}",
                "content": "Artificial intelligence is transforming various industries through automation."
            }
        ]
        
        # Navigate to entries page
        self.navigate_to('/entries')
        
        # Create each test entry
        for entry_data in entries_data:
            try:
                # Click the "Add Entry" button
                add_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[data-testid="add-entry"]')
                add_button.click()
                
                # Wait for the entry form dialog to appear
                form_dialog = self.wait_for_element(By.CSS_SELECTOR, 'div[role="dialog"]')
                
                # Fill in the form
                title_field = self.wait_for_element(By.ID, 'title')
                title_field.clear()
                title_field.send_keys(entry_data["title"])
                
                content_field = self.wait_for_element(By.ID, 'content')
                content_field.clear()
                content_field.send_keys(entry_data["content"])
                
                # Add a test tag
                tags_field = self.wait_for_element(By.ID, 'tags')
                tags_field.send_keys("search-test")
                tags_field.send_keys(Keys.ENTER)
                
                # Submit the form
                submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[type="submit"]')
                submit_button.click()
                
                # Wait for the entry to be created and the dialog to close
                WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"]'))
                )
                
                # Wait for the table to refresh
                time.sleep(2)
                
                test_entries.append(entry_data["title"])
            except Exception as e:
                print(f"Error creating test entry: {e}")
        
        return test_entries
    
    def delete_test_entries(self):
        """Delete test entries created for search tests."""
        try:
            # Navigate to entries page
            self.navigate_to('/entries')
            
            # Wait for the table to load
            time.sleep(2)
            
            # Search for entries with the test tag
            search_field = self.wait_for_element(By.CSS_SELECTOR, 'input[placeholder="Search..."]')
            search_field.clear()
            search_field.send_keys("Test Entry")
            search_field.send_keys(Keys.ENTER)
            
            # Wait for search results
            time.sleep(2)
            
            # Delete each test entry
            table_rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
            for row in table_rows:
                try:
                    title_cell = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)')
                    if "Test Entry" in title_cell.text:
                        delete_button = row.find_element(By.CSS_SELECTOR, 'button[aria-label="delete"]')
                        delete_button.click()
                        
                        # Confirm deletion in the dialog
                        confirm_button = self.wait_for_element(By.CSS_SELECTOR, 'button[data-testid="confirm-delete"]')
                        confirm_button.click()
                        
                        # Wait for the deletion to complete
                        time.sleep(1)
                except Exception as e:
                    print(f"Error deleting test entry: {e}")
        except Exception as e:
            print(f"Error in delete_test_entries: {e}")
    
    def test_search_page_loads(self):
        """Test that the search page loads correctly."""
        # Navigate to search page
        self.navigate_to('/search')
        
        # Check that the search page is loaded
        search_title = self.wait_for_element(By.CSS_SELECTOR, 'h1')
        self.assertIn('Search', search_title.text)
        
        # Check that the search input is present
        search_input = self.wait_for_element(By.CSS_SELECTOR, 'input[type="text"]')
        self.assertIsNotNone(search_input)
    
    def test_basic_search(self):
        """Test basic search functionality."""
        # Navigate to search page
        self.navigate_to('/search')
        
        # Enter a search query
        search_input = self.wait_for_element(By.CSS_SELECTOR, 'input[type="text"]')
        search_input.clear()
        search_input.send_keys("climate change")
        
        # Submit the search
        search_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[type="submit"]')
        search_button.click()
        
        # Wait for search results
        time.sleep(3)
        
        # Check that results are displayed
        results_container = self.wait_for_element(By.CSS_SELECTOR, '.search-results')
        self.assertIsNotNone(results_container)
        
        # Check that our climate change entry is in the results
        result_items = self.driver.find_elements(By.CSS_SELECTOR, '.search-result-item')
        climate_result_found = False
        for item in result_items:
            try:
                title_element = item.find_element(By.CSS_SELECTOR, 'h2')
                if "Climate Change Test Entry" in title_element.text:
                    climate_result_found = True
                    break
            except:
                pass
        
        self.assertTrue(climate_result_found, "Climate change test entry not found in search results")
    
    def test_semantic_search(self):
        """Test semantic search functionality."""
        # Navigate to search page
        self.navigate_to('/search')
        
        # Enter a semantic search query (not exact match but related)
        search_input = self.wait_for_element(By.CSS_SELECTOR, 'input[type="text"]')
        search_input.clear()
        search_input.send_keys("sustainable power sources")  # Should match renewable energy entry
        
        # Submit the search
        search_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[type="submit"]')
        search_button.click()
        
        # Wait for search results
        time.sleep(3)
        
        # Check that results are displayed
        results_container = self.wait_for_element(By.CSS_SELECTOR, '.search-results')
        self.assertIsNotNone(results_container)
        
        # Check that our renewable energy entry is in the results
        result_items = self.driver.find_elements(By.CSS_SELECTOR, '.search-result-item')
        renewable_result_found = False
        for item in result_items:
            try:
                title_element = item.find_element(By.CSS_SELECTOR, 'h2')
                if "Renewable Energy Test Entry" in title_element.text:
                    renewable_result_found = True
                    break
            except:
                pass
        
        self.assertTrue(renewable_result_found, "Renewable energy test entry not found in semantic search results")
    
    def test_search_with_filters(self):
        """Test search with category and tag filters."""
        # Navigate to search page
        self.navigate_to('/search')
        
        # Enter a search query
        search_input = self.wait_for_element(By.CSS_SELECTOR, 'input[type="text"]')
        search_input.clear()
        search_input.send_keys("test")
        
        # Apply tag filter for "search-test"
        tag_filter = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[data-testid="filter-button"]')
        tag_filter.click()
        
        # Select the search-test tag in the filter dialog
        tag_checkbox = self.wait_for_element_clickable(By.CSS_SELECTOR, 'input[value="search-test"]')
        tag_checkbox.click()
        
        # Apply the filter
        apply_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[data-testid="apply-filters"]')
        apply_button.click()
        
        # Submit the search
        search_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[type="submit"]')
        search_button.click()
        
        # Wait for search results
        time.sleep(3)
        
        # Check that results are displayed
        results_container = self.wait_for_element(By.CSS_SELECTOR, '.search-results')
        self.assertIsNotNone(results_container)
        
        # Check that all our test entries are in the results
        result_items = self.driver.find_elements(By.CSS_SELECTOR, '.search-result-item')
        self.assertGreaterEqual(len(result_items), len(self.test_entries), 
                               f"Expected at least {len(self.test_entries)} results, got {len(result_items)}")
    
    def test_search_result_navigation(self):
        """Test navigation to a knowledge entry from search results."""
        # Navigate to search page
        self.navigate_to('/search')
        
        # Enter a search query
        search_input = self.wait_for_element(By.CSS_SELECTOR, 'input[type="text"]')
        search_input.clear()
        search_input.send_keys("artificial intelligence")
        
        # Submit the search
        search_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[type="submit"]')
        search_button.click()
        
        # Wait for search results
        time.sleep(3)
        
        # Find and click on the AI entry in the results
        result_items = self.driver.find_elements(By.CSS_SELECTOR, '.search-result-item')
        ai_result_found = False
        for item in result_items:
            try:
                title_element = item.find_element(By.CSS_SELECTOR, 'h2')
                if "AI Technology Test Entry" in title_element.text:
                    ai_result_found = True
                    title_element.click()
                    break
            except:
                pass
        
        self.assertTrue(ai_result_found, "AI technology test entry not found in search results")
        
        # Wait for the entry details page to load
        time.sleep(2)
        
        # Verify that we're on the entry details page
        page_title = self.wait_for_element(By.CSS_SELECTOR, 'h1').text
        self.assertIn("AI Technology Test Entry", page_title)
        
        # Verify that the content is displayed
        content_element = self.wait_for_element(By.CSS_SELECTOR, '.entry-content')
        self.assertIn("Artificial intelligence", content_element.text)


if __name__ == '__main__':
    unittest.main()
