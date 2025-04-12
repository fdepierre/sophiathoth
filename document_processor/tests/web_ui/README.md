# Web UI Functional Tests

This directory contains functional tests for the Sophiathoth Web UI. These tests use Selenium WebDriver to automate browser interactions and verify that the web UI functions correctly.

## Test Files

- **test_authentication.py**: Tests the authentication functionality, including login, logout, and protected routes.
- **test_knowledge_entries.py**: Tests the knowledge entries management functionality, including creating, viewing, updating, and deleting entries.
- **test_search.py**: Tests the search functionality, including basic search, semantic search, and search with filters.

## Requirements

The tests require the following Python packages:
- selenium
- webdriver-manager
- unittest (part of the Python standard library)

Install the dependencies with:

```bash
pip install selenium webdriver-manager
```

You'll also need Chrome browser installed on your system for the tests to run.

## Running the Tests

### Environment Setup

By default, the tests assume the Web UI is running at `http://localhost:3000`. You can override this by setting the `WEB_UI_BASE_URL` environment variable:

```bash
export WEB_UI_BASE_URL=http://your-web-ui-host:port
```

You'll also need to set up test credentials for authentication tests:

```bash
export TEST_USERNAME=your_test_username
export TEST_PASSWORD=your_test_password
```

Make sure these credentials exist in your Keycloak instance with appropriate roles.

### Running Tests Locally

To run all the web UI tests:

```bash
cd /path/to/sophiathoth
python -m unittest discover -s tests/functional/web_ui
```

To run a specific test file:

```bash
python -m unittest tests/functional/web_ui/test_authentication.py
```

To run a specific test case:

```bash
python -m unittest tests/functional/web_ui.test_authentication.TestAuthentication.test_login_success
```

## Test Dependencies

The Web UI tests depend on:
1. A running Web UI service (React app)
2. A running Knowledge Base API
3. A running Keycloak service for authentication
4. Chrome browser installed on the test machine

If any of these dependencies are not available, the tests will be skipped.

## Headless Mode

By default, the tests run in headless mode (without a visible browser window). This is suitable for CI/CD environments. If you want to see the browser during test execution for debugging purposes, you can modify the `chrome_options` in `base_test.py` to remove the `--headless` argument.

## Test Data

The tests create temporary test data (knowledge entries, categories, tags) during execution and clean up after themselves. If tests fail unexpectedly, some test data might remain in the database. The test data is designed to be identifiable (with names starting with "Test Entry" or specific test tags) to make manual cleanup easier if needed.

## Extending the Tests

When adding new functionality to the Web UI, please add corresponding tests to maintain test coverage. Follow the existing patterns for setup, teardown, and test organization.

## Troubleshooting

If you encounter issues with the tests:

1. **Element not found errors**: The tests use explicit waits to handle timing issues, but you may need to adjust the `WAIT_TIMEOUT` constant in `base_test.py` if your system is slower.

2. **Authentication failures**: Ensure your Keycloak instance is properly configured and the test user has the necessary roles.

3. **WebDriver errors**: Make sure you have the correct version of Chrome installed. The `webdriver-manager` package should handle downloading the appropriate ChromeDriver version.

4. **Test data cleanup issues**: If tests fail unexpectedly, you may need to manually clean up test data. Look for entries with titles containing "Test Entry" in the knowledge base.
