"""
Functional tests for Web UI knowledge entries management.
These tests verify the knowledge entries management functionality of the web UI.
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


class TestKnowledgeEntries(BaseWebUITest):
    """Test the knowledge entries management functionality of the web UI."""
    
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
        
        # Navigate to entries page
        self.navigate_to('/entries')
    
    def tearDown(self):
        """Clean up after each test."""
        # Try to delete any test entries we created
        self.cleanup_test_entries()
        super().tearDown()
    
    def generate_random_string(self, length=8):
        """Generate a random string for test data."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def cleanup_test_entries(self):
        """Clean up test entries created during testing."""
        try:
            # Navigate to entries page
            self.navigate_to('/entries')
            
            # Look for entries with "Test Entry" in the title
            time.sleep(2)  # Wait for entries to load
            
            # Find all entry rows
            entry_rows = self.driver.find_elements(By.CSS_SELECTOR, 'tr')
            
            for row in entry_rows:
                try:
                    title_cell = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)')
                    if 'Test Entry' in title_cell.text:
                        # Click the delete button
                        delete_button = row.find_element(By.CSS_SELECTOR, 'button[aria-label="delete"]')
                        delete_button.click()
                        
                        # Confirm deletion in the dialog
                        confirm_button = self.wait_for_element(By.CSS_SELECTOR, 'button[data-testid="confirm-delete"]')
                        confirm_button.click()
                        
                        # Wait for the deletion to complete
                        time.sleep(1)
                except Exception as e:
                    print(f"Error cleaning up entry: {e}")
        except Exception as e:
            print(f"Error in cleanup: {e}")
    
    def test_entries_page_loads(self):
        """Test that the entries page loads correctly."""
        # Check that the entries page is loaded
        entries_title = self.wait_for_element(By.CSS_SELECTOR, 'h1')
        self.assertIn('Knowledge Entries', entries_title.text)
        
        # Check that the entries table is present
        entries_table = self.wait_for_element(By.CSS_SELECTOR, 'table')
        self.assertIsNotNone(entries_table)
    
    def test_create_entry(self):
        """Test creating a new knowledge entry."""
        # Generate a unique test title
        test_title = f"Test Entry {self.generate_random_string()}"
        
        # Click the "Add Entry" button
        add_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[data-testid="add-entry"]')
        add_button.click()
        
        # Wait for the entry form dialog to appear
        form_dialog = self.wait_for_element(By.CSS_SELECTOR, 'div[role="dialog"]')
        
        # Fill in the form
        title_field = self.wait_for_element(By.ID, 'title')
        title_field.clear()
        title_field.send_keys(test_title)
        
        content_field = self.wait_for_element(By.ID, 'content')
        content_field.clear()
        content_field.send_keys("This is a test entry created by the functional test.")
        
        # Add tags
        tags_field = self.wait_for_element(By.ID, 'tags')
        tags_field.send_keys("test")
        tags_field.send_keys(Keys.ENTER)
        tags_field.send_keys("functional-test")
        tags_field.send_keys(Keys.ENTER)
        
        # Submit the form
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for the entry to be created and the dialog to close
        WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"]'))
        )
        
        # Verify that the entry appears in the table
        time.sleep(2)  # Wait for the table to refresh
        
        # Search for the entry in the table
        search_field = self.wait_for_element(By.CSS_SELECTOR, 'input[placeholder="Search..."]')
        search_field.clear()
        search_field.send_keys(test_title)
        search_field.send_keys(Keys.ENTER)
        
        # Wait for search results
        time.sleep(2)
        
        # Check if our entry is in the results
        table_rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        entry_found = False
        for row in table_rows:
            title_cell = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)')
            if test_title in title_cell.text:
                entry_found = True
                break
        
        self.assertTrue(entry_found, f"Created entry '{test_title}' not found in the table")
    
    def test_view_entry_details(self):
        """Test viewing the details of a knowledge entry."""
        # First create a test entry
        test_title = f"Test Entry {self.generate_random_string()}"
        
        # Click the "Add Entry" button
        add_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[data-testid="add-entry"]')
        add_button.click()
        
        # Wait for the entry form dialog to appear
        form_dialog = self.wait_for_element(By.CSS_SELECTOR, 'div[role="dialog"]')
        
        # Fill in the form
        title_field = self.wait_for_element(By.ID, 'title')
        title_field.clear()
        title_field.send_keys(test_title)
        
        content_field = self.wait_for_element(By.ID, 'content')
        content_field.clear()
        content_field.send_keys("This is a test entry created by the functional test.")
        
        # Submit the form
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for the entry to be created and the dialog to close
        WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"]'))
        )
        
        # Wait for the table to refresh
        time.sleep(2)
        
        # Search for the entry in the table
        search_field = self.wait_for_element(By.CSS_SELECTOR, 'input[placeholder="Search..."]')
        search_field.clear()
        search_field.send_keys(test_title)
        search_field.send_keys(Keys.ENTER)
        
        # Wait for search results
        time.sleep(2)
        
        # Click on the entry to view details
        table_rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        for row in table_rows:
            title_cell = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)')
            if test_title in title_cell.text:
                title_cell.click()
                break
        
        # Wait for the details page to load
        self.wait_for_element(By.CSS_SELECTOR, 'h1')
        
        # Verify that the entry details are displayed
        page_title = self.driver.find_element(By.CSS_SELECTOR, 'h1').text
        self.assertEqual(test_title, page_title)
        
        # Verify that the content is displayed
        content_element = self.wait_for_element(By.CSS_SELECTOR, '.entry-content')
        self.assertIn("This is a test entry", content_element.text)
    
    def test_update_entry(self):
        """Test updating an existing knowledge entry."""
        # First create a test entry
        test_title = f"Test Entry {self.generate_random_string()}"
        
        # Click the "Add Entry" button
        add_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[data-testid="add-entry"]')
        add_button.click()
        
        # Wait for the entry form dialog to appear
        form_dialog = self.wait_for_element(By.CSS_SELECTOR, 'div[role="dialog"]')
        
        # Fill in the form
        title_field = self.wait_for_element(By.ID, 'title')
        title_field.clear()
        title_field.send_keys(test_title)
        
        content_field = self.wait_for_element(By.ID, 'content')
        content_field.clear()
        content_field.send_keys("Original content")
        
        # Submit the form
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for the entry to be created and the dialog to close
        WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"]'))
        )
        
        # Wait for the table to refresh
        time.sleep(2)
        
        # Search for the entry in the table
        search_field = self.wait_for_element(By.CSS_SELECTOR, 'input[placeholder="Search..."]')
        search_field.clear()
        search_field.send_keys(test_title)
        search_field.send_keys(Keys.ENTER)
        
        # Wait for search results
        time.sleep(2)
        
        # Click the edit button for our entry
        table_rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        for row in table_rows:
            title_cell = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)')
            if test_title in title_cell.text:
                edit_button = row.find_element(By.CSS_SELECTOR, 'button[aria-label="edit"]')
                edit_button.click()
                break
        
        # Wait for the edit form to appear
        form_dialog = self.wait_for_element(By.CSS_SELECTOR, 'div[role="dialog"]')
        
        # Update the content
        content_field = self.wait_for_element(By.ID, 'content')
        content_field.clear()
        content_field.send_keys("Updated content")
        
        # Submit the form
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for the entry to be updated and the dialog to close
        WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"]'))
        )
        
        # Wait for the table to refresh
        time.sleep(2)
        
        # Click on the entry to view details
        table_rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        for row in table_rows:
            title_cell = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)')
            if test_title in title_cell.text:
                title_cell.click()
                break
        
        # Wait for the details page to load
        self.wait_for_element(By.CSS_SELECTOR, 'h1')
        
        # Verify that the content has been updated
        content_element = self.wait_for_element(By.CSS_SELECTOR, '.entry-content')
        self.assertIn("Updated content", content_element.text)
    
    def test_delete_entry(self):
        """Test deleting a knowledge entry."""
        # First create a test entry
        test_title = f"Test Entry {self.generate_random_string()}"
        
        # Click the "Add Entry" button
        add_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[data-testid="add-entry"]')
        add_button.click()
        
        # Wait for the entry form dialog to appear
        form_dialog = self.wait_for_element(By.CSS_SELECTOR, 'div[role="dialog"]')
        
        # Fill in the form
        title_field = self.wait_for_element(By.ID, 'title')
        title_field.clear()
        title_field.send_keys(test_title)
        
        content_field = self.wait_for_element(By.ID, 'content')
        content_field.clear()
        content_field.send_keys("This is a test entry that will be deleted.")
        
        # Submit the form
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for the entry to be created and the dialog to close
        WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"]'))
        )
        
        # Wait for the table to refresh
        time.sleep(2)
        
        # Search for the entry in the table
        search_field = self.wait_for_element(By.CSS_SELECTOR, 'input[placeholder="Search..."]')
        search_field.clear()
        search_field.send_keys(test_title)
        search_field.send_keys(Keys.ENTER)
        
        # Wait for search results
        time.sleep(2)
        
        # Click the delete button for our entry
        table_rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        entry_found = False
        for row in table_rows:
            title_cell = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)')
            if test_title in title_cell.text:
                entry_found = True
                delete_button = row.find_element(By.CSS_SELECTOR, 'button[aria-label="delete"]')
                delete_button.click()
                break
        
        self.assertTrue(entry_found, "Entry not found for deletion")
        
        # Confirm deletion in the dialog
        confirm_button = self.wait_for_element(By.CSS_SELECTOR, 'button[data-testid="confirm-delete"]')
        confirm_button.click()
        
        # Wait for the deletion to complete
        time.sleep(2)
        
        # Search again to verify the entry is gone
        search_field = self.wait_for_element(By.CSS_SELECTOR, 'input[placeholder="Search..."]')
        search_field.clear()
        search_field.send_keys(test_title)
        search_field.send_keys(Keys.ENTER)
        
        # Wait for search results
        time.sleep(2)
        
        # Check that the entry is no longer in the table
        table_rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        entry_found = False
        for row in table_rows:
            try:
                title_cell = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)')
                if test_title in title_cell.text:
                    entry_found = True
                    break
            except:
                pass
        
        self.assertFalse(entry_found, "Entry still exists after deletion")


if __name__ == '__main__':
    unittest.main()
