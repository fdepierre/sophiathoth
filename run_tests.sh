#!/bin/bash
# Script to run functional tests for the document processor, knowledge base, and web UI

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

# Function to run web UI tests
run_web_ui_tests() {
    echo "Running web UI functional tests..."
    # Note: Test credentials for Keycloak authentication are defined in set_up/setup-keycloak.sh
    # Default test user: knowledge_user / Test@123
    
    # Check if the web UI is running
    if ! curl -s http://localhost:3000 > /dev/null; then
        echo "Web UI is not running at http://localhost:3000. Please start the web UI before running tests."
        echo "Skipping web UI tests."
        return 1
    fi
    
    # Create a virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Install required dependencies in the virtual environment
    echo "Installing required dependencies for web UI tests..."
    ./venv/bin/pip install selenium==4.29.0 webdriver-manager==4.0.2
    
    # Run the tests using the Python from the virtual environment
    echo "Running web UI tests..."
    ./venv/bin/python -m unittest discover -s tests/functional/web_ui
    
    echo "Web UI tests completed!"
}

# Parse command line arguments
if [ "$1" == "document" ]; then
    run_document_processor_tests
elif [ "$1" == "knowledge" ]; then
    run_knowledge_base_tests
elif [ "$1" == "web" ]; then
    run_web_ui_tests
else
    # Run all tests by default
    run_document_processor_tests
    run_knowledge_base_tests
    run_web_ui_tests
fi

echo "All tests completed!"
