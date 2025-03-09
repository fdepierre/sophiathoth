#!/bin/bash
# Script to run functional tests for the document processor and knowledge base

# Function to run document processor tests
run_document_processor_tests() {
    echo "Running document processor functional tests..."
    echo "Copying test files to the document processor container..."

    # Copy test files to the container
    docker cp tests/earth_question_answer.xlsx sophiathoth_document-processor_1:/app/tests/
    docker cp tests/test_question_answers.xlsx sophiathoth_document-processor_1:/app/tests/
    docker cp tests/functional sophiathoth_document-processor_1:/app/tests/

    # Run the tests inside the container
    echo "Running document processor tests inside the container..."
    docker exec sophiathoth_document-processor_1 bash -c "cd /app && pip install pandas requests openpyxl && python -m unittest discover -s tests/functional"
    
    echo "Document processor tests completed!"
}

# Function to run knowledge base tests
run_knowledge_base_tests() {
    echo "Running knowledge base functional tests..."
    echo "Copying test files to the knowledge base container..."

    # Copy test files to the container
    docker cp tests/functional/knowledge_base sophiathoth_knowledge-base_1:/app/tests/functional/

    # Run the tests inside the container
    echo "Running knowledge base tests inside the container..."
    docker exec sophiathoth_knowledge-base_1 bash -c "cd /app && pip install requests && python -m unittest discover -s tests/functional/knowledge_base"
    
    echo "Knowledge base tests completed!"
}

# Parse command line arguments
if [ "$1" == "document" ]; then
    run_document_processor_tests
elif [ "$1" == "knowledge" ]; then
    run_knowledge_base_tests
else
    # Run all tests by default
    run_document_processor_tests
    run_knowledge_base_tests
fi

echo "All tests completed!"
