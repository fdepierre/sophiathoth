"""
Base test class for Web UI functional tests.
This module provides common functionality for all Web UI tests.
"""
import os
import unittest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class BaseWebUITest(unittest.TestCase):
    """Base class for Web UI functional tests."""
    
    # Default timeout for WebDriverWait
    WAIT_TIMEOUT = 10
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once before all tests."""
        # Get the base URL from environment variable or use default
        cls.base_url = os.environ.get('WEB_UI_BASE_URL', 'http://localhost:3000')
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # Use the new headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')  # Needed for WSL
        chrome_options.add_argument('--remote-debugging-port=9222')  # Fix DevToolsActivePort issue
        chrome_options.add_argument('--window-size=1920,1080')  # Set window size
        
        # Use the Chrome for testing binary directly
        chrome_binary_path = '/home/franck/chrome-linux64/chrome/linux-134.0.6998.35/chrome-linux64/chrome'
        if os.path.exists(chrome_binary_path):
            chrome_options.binary_location = chrome_binary_path
            print(f"Using Chrome for testing binary at: {chrome_binary_path}")
        else:
            print(f"Chrome for testing binary not found at: {chrome_binary_path}")
        
        # Set up the Chrome driver with the specific ChromeDriver for Chrome 134
        chromedriver_path = '/home/franck/chromedriver-linux64/chromedriver'
        
        try:
            if not os.path.exists(chromedriver_path):
                print(f"ChromeDriver not found at: {chromedriver_path}")
                cls.skipTest(cls, f"ChromeDriver not found at: {chromedriver_path}")
            
            # Use the specific ChromeDriver for Chrome 134
            cls.driver = webdriver.Chrome(
                service=Service(chromedriver_path),
                options=chrome_options
            )
            cls.driver.implicitly_wait(5)  # Set implicit wait timeout
            print("Chrome WebDriver initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {e}")
            # Try with a different approach - let's try to run in non-headless mode
            try:
                print("Trying alternative approach without headless mode...")
                chrome_options.headless = False  # Disable headless mode
                cls.driver = webdriver.Chrome(
                    service=Service(chromedriver_path),
                    options=chrome_options
                )
                cls.driver.implicitly_wait(5)  # Set implicit wait timeout
                print("Chrome WebDriver initialized successfully with alternative approach")
            except Exception as e2:
                print(f"Alternative approach also failed: {e2}")
                cls.skipTest(cls, f"Chrome driver initialization failed: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment after all tests."""
        if hasattr(cls, 'driver'):
            cls.driver.quit()
    
    def setUp(self):
        """Set up before each test."""
        # Navigate to the base URL
        try:
            self.driver.get(self.base_url)
            # Wait for the page to load
            WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
        except Exception as e:
            self.skipTest(f"Failed to load the application: {e}")
    
    def wait_for_element(self, by, value, timeout=None):
        """Wait for an element to be present on the page.
        
        Args:
            by: The method to locate the element (e.g., By.ID, By.CSS_SELECTOR)
            value: The value to search for
            timeout: Optional timeout in seconds (default: self.WAIT_TIMEOUT)
            
        Returns:
            The WebElement once it's found
        """
        if timeout is None:
            timeout = self.WAIT_TIMEOUT
        
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_for_element_clickable(self, by, value, timeout=None):
        """Wait for an element to be clickable.
        
        Args:
            by: The method to locate the element (e.g., By.ID, By.CSS_SELECTOR)
            value: The value to search for
            timeout: Optional timeout in seconds (default: self.WAIT_TIMEOUT)
            
        Returns:
            The WebElement once it's clickable
        """
        if timeout is None:
            timeout = self.WAIT_TIMEOUT
        
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    
    def login(self, username, password):
        """Log in to the application using the Material UI login form.
        
        Args:
            username: The username to log in with
            password: The password to log in with
            
        Returns:
            True if login was successful, False otherwise
        """
        try:
            # Navigate to login page if not already there
            if '/login' not in self.driver.current_url:
                self.driver.get(f"{self.base_url}/login")
                print(f"Navigated to login page: {self.driver.current_url}")
            
            # Wait for the page to load completely
            time.sleep(3)
            print("Page title:", self.driver.title)
            
            # Take a screenshot of the login page for debugging
            try:
                self.driver.save_screenshot('/tmp/login_page.png')
                print("Saved screenshot to /tmp/login_page.png")
            except Exception as e:
                print(f"Failed to save screenshot: {e}")
            
            # Try a more direct approach using JavaScript to fill the form
            print("Using JavaScript to fill login form...")
            
            # First, try to identify the form elements
            try:
                # Find all input elements
                input_elements = self.driver.find_elements(By.TAG_NAME, "input")
                
                # Find username and password fields
                username_field = None
                password_field = None
                
                for inp in input_elements:
                    if inp.is_displayed():
                        input_type = inp.get_attribute("type")
                        if input_type == "text" or input_type == "email":
                            username_field = inp
                        elif input_type == "password":
                            password_field = inp
                
                if username_field and password_field:
                    print("Found username and password fields")
                    
                    # Clear and fill username field
                    username_field.clear()
                    username_field.send_keys(username)
                    print(f"Filled username field with: {username}")
                    
                    # Clear and fill password field
                    password_field.clear()
                    password_field.send_keys(password)
                    print(f"Filled password field with: {password}")
                    
                    # Find and click the submit button
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    submit_button = None
                    
                    for button in buttons:
                        if button.is_displayed():
                            button_type = button.get_attribute("type")
                            button_text = button.text.lower()
                            
                            if button_type == "submit" or "sign in" in button_text or "login" in button_text:
                                submit_button = button
                                break
                    
                    if submit_button:
                        print(f"Found submit button with text: {submit_button.text}")
                        submit_button.click()
                        print("Clicked submit button")
                    else:
                        print("No submit button found, trying to submit form with Enter key")
                        password_field.send_keys(Keys.RETURN)
                        print("Sent Enter key to password field")
                else:
                    # If we couldn't find the fields, try JavaScript injection
                    print("Could not find form fields, trying JavaScript injection")
                    js_script = f'''
                    // Find all input elements
                    var inputs = document.getElementsByTagName('input');
                    var usernameField = null;
                    var passwordField = null;
                    
                    // Identify username and password fields
                    for (var i = 0; i < inputs.length; i++) {{
                        var input = inputs[i];
                        if (input.type === 'text' || input.type === 'email') {{
                            usernameField = input;
                        }} else if (input.type === 'password') {{
                            passwordField = input;
                        }}
                    }}
                    
                    // Fill the fields if found
                    if (usernameField && passwordField) {{
                        usernameField.value = '{username}';
                        passwordField.value = '{password}';
                        
                        // Find and click submit button
                        var buttons = document.getElementsByTagName('button');
                        var submitted = false;
                        
                        for (var i = 0; i < buttons.length; i++) {{
                            var button = buttons[i];
                            if (button.type === 'submit' || 
                                button.textContent.toLowerCase().includes('sign in') || 
                                button.textContent.toLowerCase().includes('login')) {{
                                button.click();
                                submitted = true;
                                break;
                            }}
                        }}
                        
                        // If no button found, try to submit the form
                        if (!submitted) {{
                            var form = usernameField.closest('form');
                            if (form) {{
                                form.submit();
                            }}
                        }}
                        
                        return true;
                    }}
                    
                    return false;
                    '''
                    
                    result = self.driver.execute_script(js_script)
                    print(f"JavaScript form fill result: {result}")
            except Exception as e:
                print(f"Error during form identification: {e}")
                
                # As a last resort, try direct JavaScript injection
                print("Trying direct JavaScript injection as last resort")
                js_direct = f'''
                // Try to find any login form on the page
                var forms = document.getElementsByTagName('form');
                if (forms.length > 0) {{
                    // Try to find username and password fields in the first form
                    var inputs = forms[0].getElementsByTagName('input');
                    var usernameField = null;
                    var passwordField = null;
                    
                    for (var i = 0; i < inputs.length; i++) {{
                        var input = inputs[i];
                        if (input.type === 'text' || input.type === 'email') {{
                            usernameField = input;
                        }} else if (input.type === 'password') {{
                            passwordField = input;
                        }}
                    }}
                    
                    if (usernameField && passwordField) {{
                        usernameField.value = '{username}';
                        passwordField.value = '{password}';
                        forms[0].submit();
                        return true;
                    }}
                }}
                
                return false;
                '''
                
                try:
                    result = self.driver.execute_script(js_direct)
                    print(f"Direct JavaScript form submission result: {result}")
                except Exception as e:
                    print(f"Error during direct JavaScript injection: {e}")
            
            # Wait for redirect or error message
            print("Waiting for login response...")
            time.sleep(5)
            
            # Check if we're redirected away from login page
            current_url = self.driver.current_url
            print(f"Current URL after login attempt: {current_url}")
            
            if '/login' not in current_url:
                print("Successfully redirected away from login page")
                return True
            
            # Try one more time with a direct approach
            print("Still on login page, trying one more direct approach...")
            try:
                # Try to directly access a protected route and see if we're already logged in
                self.driver.get(f"{self.base_url}/entries")
                time.sleep(3)
                
                current_url = self.driver.current_url
                print(f"URL after direct navigation to protected route: {current_url}")
                
                if '/login' not in current_url and '/entries' in current_url:
                    print("Successfully accessed protected route - we are logged in!")
                    return True
                else:
                    print("Still redirected to login page - not logged in")
            except Exception as e:
                print(f"Error during direct route access: {e}")
            
            # Take a screenshot after all login attempts
            try:
                self.driver.save_screenshot('/tmp/login_final_attempt.png')
                print("Saved final login attempt screenshot to /tmp/login_final_attempt.png")
            except Exception as e:
                print(f"Failed to save final screenshot: {e}")
            
            return False
        except Exception as e:
            print(f"Login process failed with exception: {e}")
            return False
    
    def logout(self):
        """Log out from the application.
        
        Returns:
            True if logout was successful, False otherwise
        """
        try:
            # Find and click the user menu - try different selectors
            try:
                user_menu = self.wait_for_element_clickable(By.CSS_SELECTOR, 'nav button[aria-label="account of current user"]')
                user_menu.click()
                
                # Find and click the logout option
                logout_option = self.wait_for_element_clickable(By.CSS_SELECTOR, 'li[data-testid="logout"]')
                logout_option.click()
            except Exception as e:
                print(f"Standard logout failed, trying alternative: {e}")
                # Try alternative logout approach - direct URL
                self.driver.get(f"{self.base_url}/logout")
            
            # Wait for redirect to login page or Keycloak
            WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(
                lambda driver: '/login' in driver.current_url or 'keycloak' in driver.current_url or 'auth' in driver.current_url
            )
            
            return True
        except Exception as e:
            print(f"Logout failed: {e}")
            return False
    
    def navigate_to(self, path):
        """Navigate to a specific path in the application.
        
        Args:
            path: The path to navigate to (without the base URL)
            
        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            self.driver.get(f"{self.base_url}/{path.lstrip('/')}")
            # Wait for the page to load
            WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            return True
        except Exception as e:
            print(f"Navigation failed: {e}")
            return False
