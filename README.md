# SophiaThoth

SophiaThoth is a collaborative knowledge management system designed to populate a comprehensive knowledge base with accurate information and provide users with the ability to ask questions and receive informed answers.

## System Overview

SophiaThoth is designed as a microservices architecture with the following components:

1. **Document Processor Service**: Handles Excel file parsing, extraction, and export
2. **Semantic Engine Service**: Performs natural language processing, embeddings generation, and semantic similarity matching
3. **Knowledge Base Service**: Manages storage and retrieval of tender questions and answers
4. **User Management Service**: Handles authentication, authorization, and user profiles
5. **Workflow Service**: Manages tender processing workflow, notifications, and approvals
6. **API Gateway**: Provides a unified entry point for all client requests
7. **Web UI**: Delivers a responsive user interface tailored to different personas

## Technology Stack

- **Programming Languages**: Python 3.12+
- **Backend Frameworks**: FastAPI, gRPC
- **Data Storage**: PostgreSQL 16+ with pgvector, Redis, MinIO
- **AI/ML Components**: Sentence-transformers, Ollama, Hugging Face, spaCy
- **Workflow Orchestration**: Temporal.io
- **Identity Management**: Keycloak
- **Frontend**: React 19+, TypeScript, TailwindCSS

## Detailed Architecture

### Document Processor Service

- **Implementation**: Python with FastAPI
- **Key Dependencies**: pandas, openpyxl, SQLAlchemy
- **Database Models**:
  - `TenderDocument`: Stores metadata about uploaded documents
  - `TenderSheet`: Represents individual sheets within Excel documents
  - `TenderQuestion`: Extracted questions from tender documents
  - `TenderResponse`: Responses to tender questions
- **Main Features**:
  - Excel file parsing and data extraction
  - Question identification using heuristic patterns
  - Document storage in MinIO object storage
  - Metadata extraction and indexing

### Semantic Engine Service

- **Implementation**: Python with FastAPI
- **Key Dependencies**: sentence-transformers, spaCy, numpy
- **Main Features**:
  - Text embedding generation
  - Semantic similarity calculation
  - Entity recognition and extraction
  - Integration with vector database (PostgreSQL with pgvector)

### Knowledge Base Service

- **Implementation**: Python with FastAPI
- **Key Dependencies**: SQLAlchemy, pydantic, alembic
- **Database Models**:
  - `KnowledgeEntry`: Core knowledge items
  - `Category`: Hierarchical organization of knowledge
  - `Tag`: Flexible labeling system
  - `Attachment`: Files associated with knowledge entries
- **Main Features**:
  - CRUD operations for knowledge entries
  - Category and tag management
  - Full-text and semantic search
  - Version history tracking

### Web UI

- **Implementation**: React, TypeScript, TailwindCSS
- **Key Dependencies**: React Router, React Query, Material UI
- **Authentication**: Keycloak integration with JWT token management
- **Main Features**:
  - Dashboard with statistics and recent entries
  - Knowledge entry management (CRUD operations)
  - Category and tag management
  - Search functionality
  - File upload/download capabilities
  - Responsive design for desktop and mobile

### API Gateway

- **Implementation**: Traefik
- **Configuration**: Docker labels for service discovery
- **Features**:
  - Routing and load balancing
  - SSL termination
  - Service discovery
  - Rate limiting

## Database Schema

### PostgreSQL

The system uses PostgreSQL for structured data storage with the following key tables:

- **tender_documents**: Stores metadata about uploaded tender documents
- **tender_sheets**: Contains information about individual sheets within Excel documents
- **tender_questions**: Stores questions extracted from tender documents
- **tender_responses**: Contains responses to tender questions
- **knowledge_entries**: Stores knowledge base entries
- **categories**: Hierarchical organization of knowledge
- **tags**: Flexible labeling system for knowledge entries
- **attachments**: Files associated with knowledge entries

### MinIO

MinIO is used for object storage with the following buckets:

- **documents**: Stores uploaded tender documents
- **attachments**: Stores files attached to knowledge entries

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Ollama (for local LLM access)

### Local Development

1. Clone this repository
2. Run `docker-compose up` to start all services
3. Access the Web UI at http://localhost:3000

### Rebuilding Services

To rebuild a specific service after making changes:

```bash
# Rebuild a specific service
docker-compose build <service-name>

# Restart a specific service
docker-compose up -d <service-name>

# Rebuild and restart all services
docker-compose down --volumes --remove-orphans
docker-compose build
docker-compose up -d
```

## Web UI

The Web UI provides a user-friendly interface for interacting with the Knowledge Base Service. Key features include:

- **Dashboard**: Overview of knowledge entries, categories, and tags
- **Knowledge Entries**: Create, view, edit, and delete knowledge entries
- **Categories**: Manage categories for organizing knowledge entries
- **Search**: Perform semantic searches across the knowledge base
- **Attachments**: Upload and download files associated with knowledge entries

The UI is built with React and Material-UI, providing a responsive design that works across desktop and mobile devices.

## Authentication and Authorization

The system uses Keycloak for identity and access management with the following features:

- **User Authentication**: Login with username/password
- **Role-Based Access Control**: Different permissions for different user roles
- **Token Management**: JWT tokens with automatic refresh
- **Single Sign-On**: Integration with external identity providers

## Development Guidelines

### Code Structure

Each microservice follows a similar structure:

```
service-name/
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   ├── errors.py
│   │   └── routes/
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   └── *.py
│   ├── schemas/
│   │   └── *.py
│   └── services/
│       └── *.py
├── alembic/
├── tests/
├── Dockerfile
└── requirements.txt
```

### Naming Conventions

- **Python**: Follow PEP 8 guidelines
- **JavaScript/TypeScript**: Camel case for variables and functions, Pascal case for components
- **Database**: Snake case for table and column names

## Deployment

The system can be deployed locally using Docker Compose or to Kubernetes for production environments.

### Docker Compose

For local development and testing, use the provided `docker-compose.yml` file:

```bash
docker-compose up -d
```

### Kubernetes

For production deployment, Kubernetes manifests are provided in the `k8s/` directory.

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: Check PostgreSQL container logs and ensure the service is running
2. **MinIO Access Issues**: Verify credentials in environment variables
3. **Service Dependencies**: Some services require others to be running first

### Debugging

- Check service logs: `docker-compose logs <service-name>`
- Inspect containers: `docker-compose ps`
- Access service directly: `curl http://localhost:<port>/<endpoint>`

## Future Development

Planned enhancements for the system include:

1. **Advanced NLP Features**: Improved question extraction and classification
2. **Workflow Automation**: Enhanced tender response workflow
3. **Analytics Dashboard**: Insights into tender performance
4. **Mobile Application**: Native mobile experience
5. **Multi-language Support**: Internationalization of the UI and document processing

## License

This project is licensed under the MIT License - see the LICENSE file for details.
