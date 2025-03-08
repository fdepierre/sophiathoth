# Tender Management System - Web UI

This directory contains the Web UI for the Tender Management System, providing a user-friendly interface for interacting with the Knowledge Base Service.

## Features

- **Dashboard**: Overview of knowledge entries, categories, and tags
- **Knowledge Entries**: Create, view, edit, and delete knowledge entries
- **Categories**: Manage categories for organizing knowledge entries
- **Search**: Perform semantic searches across the knowledge base
- **Attachments**: Upload and download files associated with knowledge entries

## Technology Stack

- **React**: JavaScript library for building user interfaces
- **Material-UI**: React component library implementing Google's Material Design
- **React Router**: Library for routing in React applications
- **Axios**: Promise-based HTTP client for making API requests

## Directory Structure

```
web_ui/
├── public/                # Static files
├── src/                   # Source code
│   ├── components/        # Reusable UI components
│   ├── pages/             # Page components
│   ├── services/          # API services
│   ├── App.js             # Main application component
│   └── index.js           # Entry point
├── Dockerfile             # Docker configuration
├── nginx.conf             # Nginx configuration for serving the app
└── package.json           # Dependencies and scripts
```

## Development

### Prerequisites

- Node.js 18+ and npm
- Access to the Knowledge Base Service API

### Local Development

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm start
   ```

3. The application will be available at http://localhost:3000

### Building for Production

1. Build the application:
   ```
   npm run build
   ```

2. The built files will be in the `build` directory

## Docker Deployment

The Web UI can be deployed using Docker:

```
docker build -t tender-management-web-ui .
docker run -p 3000:80 tender-management-web-ui
```

Or using Docker Compose:

```
docker-compose up web-ui
```

## API Integration

The Web UI communicates with the Knowledge Base Service API. The API URL can be configured using the `REACT_APP_API_URL` environment variable.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
