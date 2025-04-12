"""
Functional tests for Web UI authentication.
These tests verify the authentication functionality of the web UI.
"""
import os
import unittest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.functional.web_ui.base_test import BaseWebUITest


class TestAuthentication(BaseWebUITest):
    """Test the authentication functionality of the web UI."""
    
    def setUp(self):
        """Set up before each test."""
        super().setUp()
        # Use the working Keycloak credentials
        self.test_username = os.environ.get('TEST_USERNAME', 'knowledge_user')
        self.test_password = os.environ.get('TEST_PASSWORD', 'Test@123')
    
    def test_login_page_loads(self):
        """Test that the login page loads correctly."""
        # Navigate to login page
        self.navigate_to('/login')
        
        # Wait for the page to load completely
        time.sleep(2)
        
        # Check that the login form is present using Material UI selectors
        try:
            # Look for input fields by their label text
            username_field = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Username')]/following::input")
            password_field = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Password')]/following::input")
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            
            self.assertIsNotNone(username_field)
            self.assertIsNotNone(password_field)
            self.assertIsNotNone(login_button)
        except:
            # If Material UI selectors fail, look for any input fields and buttons
            print("Material UI form elements not found, checking for alternative elements")
            
            # Get all input fields and filter to only visible ones
            input_fields = self.driver.find_elements(By.TAG_NAME, 'input')
            visible_inputs = [inp for inp in input_fields if inp.is_displayed()]
            
            # Get all buttons and filter to only visible ones
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            visible_buttons = [btn for btn in buttons if btn.is_displayed()]
            
            # Check that we have at least two input fields (username and password)
            # and at least one button (login button)
            self.assertGreaterEqual(len(visible_inputs), 2, "Expected at least 2 visible input fields on login page")
            self.assertGreaterEqual(len(visible_buttons), 1, "Expected at least 1 visible button on login page")
    
    def test_login_success(self):
        """Test successful login with valid credentials."""
        # Navigate to login page
        self.navigate_to('/login')
        
        # Perform login
        login_success = self.login(self.test_username, self.test_password)
        
        # Assert that login was successful
        self.assertTrue(login_success)
        
        # Check that we're redirected to the dashboard or another protected page
        self.assertNotIn('/login', self.driver.current_url)
        
        # Check that the navbar shows the user's information
        user_menu = self.wait_for_element(By.CSS_SELECTOR, 'nav button[aria-label="account of current user"]')
        self.assertIsNotNone(user_menu)
    
    def test_login_failure(self):
        """Test login failure with invalid credentials."""
        # Navigate to login page
        self.navigate_to('/login')
        
        # Wait for the page to load completely
        time.sleep(2)
        
        # Try to find the login form elements using Material UI selectors
        try:
            # Look for input fields by their label text
            username_field = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Username')]/following::input")
            password_field = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Password')]/following::input")
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            
            # Fill in the login form with invalid credentials
            username_field.clear()
            username_field.send_keys(self.test_username)
            password_field.clear()
            password_field.send_keys('wrong_password')
            
            # Submit the form
            login_button.click()
        except Exception as e:
            print(f"Material UI form elements not found: {e}")
            # Get all input fields and filter to only visible ones
            input_fields = self.driver.find_elements(By.TAG_NAME, 'input')
            visible_inputs = [inp for inp in input_fields if inp.is_displayed()]
            
            # Get all buttons and filter to only visible ones
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            visible_buttons = [btn for btn in buttons if btn.is_displayed()]
            
            if len(visible_inputs) >= 2 and len(visible_buttons) >= 1:
                # Use the first two visible inputs for username and password
                visible_inputs[0].clear()
                visible_inputs[0].send_keys(self.test_username)
                visible_inputs[1].clear()
                visible_inputs[1].send_keys('wrong_password')
                
                # Click the first visible button (likely the login button)
                visible_buttons[0].click()
            else:
                self.fail("Could not find enough visible form elements")
        
        # Wait for the error to appear
        time.sleep(3)
        
        # Try different selectors for error messages
        try:
            # First try MUI Snackbar error alert
            error_message = self.driver.find_element(By.CSS_SELECTOR, '.MuiAlert-filled.MuiAlert-filledError')
            self.assertIsNotNone(error_message)
            print(f"Found error message: {error_message.text}")
        except Exception as e:
            print(f"Could not find MUI error alert: {e}")
            try:
                # Try any element with error-related text
                error_xpath = "//*[contains(text(), 'Invalid') or contains(text(), 'invalid') "
                error_xpath += "or contains(text(), 'failed') or contains(text(), 'Failed') "
                error_xpath += "or contains(text(), 'error') or contains(text(), 'Error')]"
                
                error_elements = self.driver.find_elements(By.XPATH, error_xpath)
                if len(error_elements) > 0:
                    print(f"Found error element with text: {error_elements[0].text}")
                else:
                    print("No error elements found with error-related text")
            except Exception as e:
                print(f"Error while searching for error elements: {e}")
        
        # Assert that we're still on the login page
        self.assertIn('/login', self.driver.current_url)
    
    def test_logout(self):
        """Test logout functionality."""
        # First login
        self.navigate_to('/login')
        login_success = self.login(self.test_username, self.test_password)
        self.assertTrue(login_success)
        
        # Now logout
        logout_success = self.logout()
        
        # Assert that logout was successful
        self.assertTrue(logout_success)
        
        # Check that we're redirected to the login page
        self.assertIn('/login', self.driver.current_url)
    
    def test_protected_route_redirect(self):
        """Test that protected routes redirect to login when not authenticated."""
        # Try to access a protected route without logging in
        self.navigate_to('/entries')
        
        # Check that we're redirected to the login page
        self.assertIn('/login', self.driver.current_url)
        
        # Now login and try again
        login_success = self.login(self.test_username, self.test_password)
        self.assertTrue(login_success)
        
        # Navigate to the protected route
        self.navigate_to('/entries')
        
        # Check that we can access it now
        self.assertIn('/entries', self.driver.current_url)
        
        # Check that the entries page is loaded
        entries_title = self.wait_for_element(By.CSS_SELECTOR, 'h1')
        self.assertIn('Knowledge Entries', entries_title.text)


if __name__ == '__main__':
    unittest.main()
