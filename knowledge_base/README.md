# Knowledge Base Service

This service is responsible for managing knowledge entries related to tenders in the Tender Management System. It provides APIs for creating, retrieving, updating, and deleting knowledge entries, as well as categorizing and tagging them.

## Features

- CRUD operations for knowledge entries
- Categorization of knowledge entries
- Tagging system for knowledge entries
- Attachment management
- Revision history
- Semantic search using the Semantic Engine service

## API Endpoints

### Knowledge Entries

- `POST /api/v1/entries`: Create a new knowledge entry
- `GET /api/v1/entries`: List knowledge entries with optional filtering
- `GET /api/v1/entries/{entry_id}`: Get a specific knowledge entry
- `PUT /api/v1/entries/{entry_id}`: Update a knowledge entry
- `DELETE /api/v1/entries/{entry_id}`: Delete a knowledge entry
- `POST /api/v1/entries/{entry_id}/attachments`: Upload an attachment for a knowledge entry
- `GET /api/v1/entries/{entry_id}/attachments`: Get all attachments for a knowledge entry
- `GET /api/v1/entries/{entry_id}/attachments/{attachment_id}`: Download a specific attachment
- `GET /api/v1/entries/{entry_id}/revisions`: Get all revisions for a knowledge entry
- `POST /api/v1/entries/search`: Search knowledge entries using semantic search
- `GET /api/v1/search?query={query}`: Search knowledge entries using text search

### Categories

- `POST /api/v1/categories`: Create a new knowledge category
- `GET /api/v1/categories`: List knowledge categories
- `GET /api/v1/categories/{category_id}`: Get a specific knowledge category
- `PUT /api/v1/categories/{category_id}`: Update a knowledge category
- `DELETE /api/v1/categories/{category_id}`: Delete a knowledge category

### Tags

- `POST /api/v1/tags`: Create a new tag
- `GET /api/v1/tags`: List tags
- `GET /api/v1/tags/{tag_id}`: Get a specific tag
- `PUT /api/v1/tags/{tag_id}`: Update a tag
- `DELETE /api/v1/tags/{tag_id}`: Delete a tag

## Dependencies

- FastAPI: Web framework
- SQLAlchemy: ORM for database interactions
- PostgreSQL: Database
- MinIO: Object storage for attachments
- Redis: Caching for semantic operations
- Semantic Engine Service: For semantic search and categorization (optional)

## Running the Service

### Using Docker Compose

1. Start the required services:

```bash
docker-compose up -d postgres redis minio
```

2. Build and start the Knowledge Base service:

```bash
docker-compose build knowledge-base
docker-compose up -d knowledge-base
```

3. Initialize the database:

```bash
docker exec -it tender-management-system_knowledge-base_1 python -m app.init_db
```

4. Check the health status:

```bash
curl http://localhost:8003/health
```

### API Usage Examples

#### Create a Category

```bash
curl -X POST http://localhost:8003/api/v1/categories/ -H "Content-Type: application/json" -d '{"name": "General", "description": "General knowledge entries"}'
```

#### Create a Knowledge Entry

```bash
curl -X POST http://localhost:8003/api/v1/entries/ -H "Content-Type: application/json" -d '{"title": "Sample Knowledge Entry", "content": "This is a sample knowledge entry for testing purposes.", "summary": "Sample entry", "source_type": "manual", "category_id": "YOUR_CATEGORY_ID", "tags": ["sample", "test"]}'
```

#### Search Knowledge Entries

```bash
curl -X GET "http://localhost:8003/api/v1/search/?query=sample&limit=10"
```

## Configuration

The service is configured using environment variables, which can be set in a `.env` file:

- `DATABASE_URL`: PostgreSQL connection string
- `MINIO_ENDPOINT`: MinIO server endpoint
- `MINIO_ACCESS_KEY`: MinIO access key
- `MINIO_SECRET_KEY`: MinIO secret key
- `MINIO_SECURE`: Whether to use HTTPS for MinIO (default: False)
- `MINIO_BUCKET_NAME`: MinIO bucket name for storing attachments
- `REDIS_HOST`: Redis server host
- `REDIS_PORT`: Redis server port
- `REDIS_DB`: Redis database number
- `REDIS_PASSWORD`: Redis password (optional)
- `SEMANTIC_ENGINE_URL`: URL of the Semantic Engine service
- `LOG_LEVEL`: Logging level (default: INFO)

## Running the Service

### Using Docker

```bash
docker build -t knowledge-base-service .
docker run -p 8000:8000 knowledge-base-service
```

### Using Docker Compose

```bash
docker-compose up -d knowledge-base
```

### Local Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Testing

```bash
pytest
```
