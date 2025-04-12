# Knowledge Base Functional Tests

This directory contains functional tests for the Knowledge Base service. These tests verify that the Knowledge Base API endpoints work correctly and that the core functionality of the service is maintained.

## Test Files

- **test_knowledge_api.py**: Tests the core CRUD operations for knowledge entries, including creating, retrieving, updating, and deleting entries. Also tests attachment handling and revision history.
- **test_semantic_search.py**: Tests the semantic search functionality, ensuring that searches return relevant results based on semantic similarity rather than just keyword matching.
- **test_categories_and_tags.py**: Tests the category and tag management functionality, including hierarchical categories.

## Requirements

The tests require the following Python packages:
- requests
- unittest (part of the Python standard library)

## Running the Tests

### Environment Setup

By default, the tests assume the Knowledge Base service is running at `http://localhost:8001`. You can override this by setting the `KB_API_BASE_URL` environment variable:

```bash
export KB_API_BASE_URL=http://your-kb-service-host:port
```

### Running Tests Locally

To run all the knowledge base tests:

```bash
cd /path/to/sophiathoth
python -m unittest discover -s tests/functional/knowledge_base
```

To run a specific test file:

```bash
python -m unittest tests/functional/knowledge_base/test_knowledge_api.py
```

### Running Tests in Docker

If you're using Docker, you can run the tests inside the Docker container:

```bash
docker exec -it sophiathoth_knowledge_base python -m unittest discover -s /app/tests/functional/knowledge_base
```

## Test Data

The tests create temporary test data (knowledge entries, categories, tags) during execution and clean up after themselves. If tests fail unexpectedly, some test data might remain in the database. The test data is designed to be identifiable (with names starting with "Test " or specific test tags) to make manual cleanup easier if needed.

## Test Dependencies

The Knowledge Base tests depend on:
1. A running Knowledge Base service
2. A properly configured database
3. A running semantic engine service (for semantic search tests)
4. MinIO or compatible object storage (for attachment tests)

If any of these dependencies are not available, relevant tests will be skipped.

## Extending the Tests

When adding new functionality to the Knowledge Base service, please add corresponding tests to maintain test coverage. Follow the existing patterns for setup, teardown, and test organization.
