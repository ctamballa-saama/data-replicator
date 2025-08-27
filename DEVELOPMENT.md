# DataReplicator Development Guide

This document contains important information for developers working on the DataReplicator project.

## Development Environment

### Prerequisites
- Python 3.8+
- Node.js 14+ and npm
- Git

### Setup
1. Clone the repository
2. Create a virtual environment and install Python dependencies
3. Install frontend dependencies
4. Run the application using `./start_app.sh`

Detailed instructions are available in the [README.md](README.md) file.

## Authentication System

### Current Implementation
The application currently uses a mock authentication system for development purposes. This is implemented in the frontend only, without requiring backend authentication endpoints.

### Mock Credentials

#### Admin Users
| Email/Username | Password | Role | Permissions |
|--------------|----------|------|------------|
| admin@datareplicator.com | admin123 | admin | admin, read, write, delete |
| admin | password | admin | admin, read, write, delete |

#### Regular Users
| Email/Username | Password | Role | Permissions |
|--------------|----------|------|------------|
| user@datareplicator.com | user123 | user | read |
| dev | dev | developer | read |

### How It Works
The mock authentication is implemented in `/frontend/src/services/auth.js` and works as follows:

1. When a user attempts to log in, the credentials are checked against the hardcoded list
2. If valid, mock tokens are generated and stored in localStorage
3. The user profile is created with appropriate role and permissions
4. Protected routes check for these tokens and user profile

### Future Implementation
In production, authentication will be handled by the FastAPI backend using:
- OAuth2 with JWT tokens
- Role-based access control
- Integration with the user database

## Admin UI

The Admin UI is available at `/admin` and includes the following components:

- **AdminDashboard**: Overview statistics and monitoring
- **UserManagement**: User administration
- **DomainManagement**: Clinical domain oversight
- **JobManagement**: Generation job monitoring
- **ExportManagement**: Data exports
- **SystemSettings**: Application configuration

Access to the Admin UI requires admin role permissions.

## API Structure

The main API endpoints are documented in the API documentation at `http://localhost:8000/docs`. Key endpoints include:

- **/generation/generate**: Creates and starts data generation jobs (POST)
- **/generation/status/{job_id}**: Returns job status (GET)
- **/generation/download/{domain_name}**: Generates/returns CSV files (GET)
- **/analysis/statistics/{domain_name}**: Domain statistics (GET)
- **/analysis/variable/{domain_name}/{variable_name}**: Variable statistics (GET)
- **/analysis/relationships**: Domain relationship data (GET)

## Known Issues and Workarounds

### Issues Fixed
- Fixed JavaScript errors with `toFixed()` calls on null/undefined values
- Fixed numpy/pandas compatibility by directly importing numpy
- Enhanced error handling in API endpoints
- Fixed job management and background task handling

### Current Limitations
- Authentication is mocked in the frontend
- Some admin features are using placeholder data
- Error handling could be improved in certain areas

## Testing

Run backend tests:
```bash
cd datareplicator
python -m pytest
```

Run frontend tests:
```bash
cd frontend
npm test
```

## Contribution Guidelines

1. Create a feature branch from `main`
2. Make your changes
3. Write tests for your code
4. Ensure all tests pass
5. Create a pull request

Please follow the existing code style and structure.
