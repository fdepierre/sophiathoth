#!/bin/bash
# Script to run functional tests for the document processor

echo "Running document processor functional tests..."
echo "Copying test files to the document processor container..."

# Copy test files to the container
docker cp tests/earth_question_answer.xlsx sophiathoth_document-processor_1:/app/tests/
docker cp tests/test_question_answers.xlsx sophiathoth_document-processor_1:/app/tests/
docker cp tests/functional sophiathoth_document-processor_1:/app/tests/

# Run the tests inside the container
echo "Running tests inside the container..."
docker exec sophiathoth_document-processor_1 bash -c "cd /app && pip install pandas requests openpyxl && python -m unittest discover -s tests/functional"

echo "Tests completed!"
