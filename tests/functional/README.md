# Document Processor Functional Tests

This directory contains functional tests for the Document Processor service of the Tender Management System.

## Test Files

The tests use the Excel files located in the parent directory:
- `earth_question_answer.xlsx`
- `test_question_answers.xlsx`

## Test Modules

1. **test_document_processor.py**
   - Tests the Excel parser directly without API
   - Tests question extraction accuracy
   - Tests the API document upload endpoint
   - Tests document retrieval endpoints

2. **test_document_processor_e2e.py**
   - End-to-end tests for the complete document processing workflow
   - Tests API error handling
   - Tests concurrent document uploads
   - Tests document deletion and cascading effects

## Running the Tests

### Prerequisites

1. Make sure the Document Processor service is running:
   ```bash
   cd /home/franck/winhome/Documents/Development/MyProgram/sophiathoth
   docker-compose up -d document-processor
   ```

2. Install the required Python packages:
   ```bash
   pip install requests pandas openpyxl
   ```

### Running Individual Test Modules

```bash
# Run the basic functional tests
python -m tests.functional.test_document_processor

# Run the end-to-end tests
python -m tests.functional.test_document_processor_e2e
```

### Running All Tests

```bash
# From the project root
python -m unittest discover -s tests/functional
```

## Test Output

The tests will output their results to the console. If any test fails, an error message will be displayed with details about the failure.

## Notes

- The tests are designed to clean up after themselves by deleting any documents they create.
- If the Document Processor service is not running, the API tests will be skipped.
- The tests are designed to be independent of each other, so they can be run in any order.
