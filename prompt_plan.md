# DataReplicator Implementation Blueprint

## High-Level Implementation Plan

I've analyzed the DataReplicator specification and created a comprehensive implementation plan broken down into small, iterative steps. This plan follows a test-driven development approach and ensures each component builds logically on previous work.

## Project Structure and Setup

### Step 1: Project Setup and Basic Structure

```
# Project Setup Prompt

Create a new Python project called "DataReplicator" with the following structure:

- datareplicator/
  - __init__.py
  - core/
    - __init__.py
  - data/
    - __init__.py
  - analysis/
    - __init__.py
  - generation/
    - __init__.py
  - validation/
    - __init__.py
  - export/
    - __init__.py
  - api/
    - __init__.py
  - ui/
    - __init__.py

Set up a basic requirements.txt file with the following dependencies:
- fastapi
- uvicorn
- pandas
- numpy
- scikit-learn
- pytest
- sqlalchemy
- python-dotenv
- pydantic

Also create a basic README.md explaining the project's purpose: DataReplicator is a tool designed to analyze existing clinical datasets and generate additional synthetic data while maintaining statistical properties, relationships, and domain-specific integrity.

Create a basic setup.py file to make the package installable.
Create a .gitignore file for Python projects.

Write a simple test to verify the project structure is correctly set up.
```

### Step 2: Configuration Management

```
# Configuration Management Prompt

Create a configuration management system for DataReplicator with the following features:

1. Create a config/ directory with:
   - __init__.py
   - settings.py - For application settings
   - constants.py - For application constants

2. In settings.py, implement:
   - A Settings class using Pydantic BaseSettings
   - Environment variables support via python-dotenv
   - Configuration for:
     - Database connection
     - Application host/port
     - Logging settings
     - Default file paths

3. In constants.py, define:
   - File format constants
   - Validation rule types
   - User role types (ADMIN, USER, VIEWER)
   - Other application constants

4. Create a sample .env.example file (don't create .env directly)

5. Update the __init__.py to expose the settings and constants

6. Write tests to verify the configuration is loaded correctly
```

## Data Ingestion Module

### Step 3: CSV Parser Implementation

```
# CSV Parser Implementation Prompt

Implement a CSV parser module in the data/ directory with the following features:

1. Create data/parsers.py with:
   - A CSVParser class that can:
     - Read a CSV file and convert to a pandas DataFrame
     - Validate basic CSV structure
     - Handle common CSV format issues (delimiters, encodings)
     - Extract column metadata (types, ranges, etc.)

2. Implement error handling for:
   - Invalid file formats
   - Missing required columns
   - Type conversion errors

3. Create data/models.py with:
   - DataFile class to represent an ingested data file
   - DataColumn class to represent column metadata

4. Create utility functions in data/utils.py for:
   - Detecting delimiter types
   - Inferring column types
   - Basic data cleaning

5. Write comprehensive tests in tests/data/ directory:
   - Test with valid CSV files
   - Test with invalid formats
   - Test with missing data
   - Test with different delimiters

Include sample test data files in tests/data/samples/ directory.
```

### Step 4: Data Domain Management

```
# Data Domain Management Prompt

Implement data domain management for clinical data files with the following features:

1. Create data/domains.py with:
   - DataDomain class to represent a clinical data domain (e.g., Demographics, Lab Results)
   - DomainRegistry class to manage multiple domains
   - Functions to detect domain types from file characteristics

2. Update data/models.py to add:
   - Domain-specific metadata
   - Relationships between domains (e.g., subject ID as a key)

3. Implement methods to:
   - Detect common clinical data domains automatically
   - Link related domains together
   - Identify key fields across domains

4. Create a factory pattern in data/factory.py for:
   - Creating appropriate domain objects based on file content
   - Setting up domain-specific validation rules

5. Write tests in tests/data/test_domains.py:
   - Test domain detection
   - Test relationship mapping
   - Test with various domain types
```

### Step 5: Data Ingestion Service

```
# Data Ingestion Service Prompt

Create a comprehensive data ingestion service that ties together parsing and domain management:

1. Implement a DataIngestionService class in data/service.py with:
   - Methods to ingest multiple files
   - Support for directory ingestion
   - Progress tracking during ingestion
   - Validation during ingestion

2. Implement a Project class in data/project.py:
   - To group related data files
   - Store metadata about the ingestion
   - Track file relationships

3. Add error aggregation in data/errors.py:
   - Collect and categorize errors during ingestion
   - Provide error summaries
   - Generate error reports

4. Create a simple command-line interface in data/cli.py:
   - To test ingestion functionality
   - Provide error reports

5. Write integration tests in tests/integration/:
   - Test end-to-end ingestion process
   - Test with multiple related files
   - Test error reporting

Ensure proper error handling and informative error messages throughout.
```

## Data Analysis Module

### Step 6: Basic Statistical Analysis

```
# Basic Statistical Analysis Prompt

Implement basic statistical analysis features for ingested data:

1. Create analysis/stats.py with:
   - Functions for calculating basic statistics (mean, median, range, etc.)
   - Methods for numerical column analysis
   - Methods for categorical column analysis
   - Identification of outliers

2. Create analysis/visualization.py for:
   - Basic distribution plots
   - Data summary visualizations
   - Output statistical reports

3. Create analysis/service.py with:
   - AnalysisService class to orchestrate analysis
   - Methods to analyze entire datasets
   - Methods to analyze specific columns

4. Implement analysis caching in analysis/cache.py:
   - Store analysis results
   - Retrieve cached results
   - Invalidate cache when data changes

5. Write tests in tests/analysis/:
   - Test with numerical data
   - Test with categorical data
   - Test with mixed data types
   - Test caching functionality

Include simple visualization outputs in the tests.
```

### Step 7: Cross-Domain Relationship Analysis

```
# Cross-Domain Relationship Analysis Prompt

Implement functionality to detect and analyze relationships between different data domains:

1. Create analysis/relationships.py with:
   - Functions to detect key relationships between domains
   - Methods to calculate correlation between columns across domains
   - Functions to identify dependent variables

2. Create analysis/temporal.py for:
   - Time-series analysis
   - Temporal pattern detection
   - Sequence analysis for clinical events

3. Update analysis/service.py to:
   - Orchestrate cross-domain analysis
   - Generate relationship maps
   - Identify critical dependencies

4. Create analysis/models.py with:
   - Relationship class to represent detected relationships
   - RelationshipType enum for different relationship types
   - RelationshipStrength class for quantifying relationship strength

5. Write tests in tests/analysis/test_relationships.py:
   - Test relationship detection
   - Test with various relationship types
   - Test with temporal data
   - Test with complex multi-domain data
```

## Data Generation Module

### Step 8: Basic Data Generation Framework

```
# Basic Data Generation Framework Prompt

Implement the core data generation framework:

1. Create generation/base.py with:
   - BaseGenerator abstract class
   - Generator registration mechanism
   - Generator factory methods

2. Create generation/models.py with:
   - GenerationConfig class for configuring generation
   - GenerationResult class for output
   - GenerationStats class for tracking generation metrics

3. Create specific generators in generation/generators/:
   - numerical_generator.py for numerical values
   - categorical_generator.py for categorical values
   - date_generator.py for date/time values
   - text_generator.py for text values

4. Implement generation/utils.py with:
   - Utility functions for random generation
   - Distribution sampling methods
   - Range constraint helpers

5. Write tests in tests/generation/:
   - Test each generator type
   - Test with different configurations
   - Test output validation
```

### Step 9: Subject Generation Service

```
# Subject Generation Service Prompt

Implement subject-level data generation that maintains relationships across domains:

1. Create generation/subject.py with:
   - SubjectGenerator class
   - Methods to generate complete subject data
   - Ensure consistency across domains

2. Create generation/constraints.py with:
   - Constraint classes for enforcing rules during generation
   - Methods to validate generated data against constraints

3. Create generation/service.py with:
   - GenerationService class to orchestrate generation
   - Methods to generate multiple subjects
   - Progress tracking and reporting

4. Update generation/models.py with:
   - SubjectTemplate class for modeling subject patterns
   - FieldRelationship class to maintain cross-domain integrity

5. Write integration tests in tests/integration/test_subject_generation.py:
   - Test complete subject generation
   - Test relationship preservation
   - Test with various constraints
   - Test with multiple domains
```

### Step 10: PII Handling and Randomization

```
# PII Handling and Randomization Prompt

Implement PII (Personally Identifiable Information) handling and randomization:

1. Create generation/pii.py with:
   - PII detection methods
   - PII randomization functions
   - Consistent PII mapping for relationships

2. Create generation/anonymization.py with:
   - Methods for anonymizing various data types
   - Preservation of statistical properties
   - Consistent anonymization across datasets

3. Update generation/service.py to:
   - Incorporate PII handling during generation
   - Apply consistent anonymization

4. Create generation/pii_data/ directory with:
   - Sample anonymization dictionaries
   - Name lists, address patterns, etc.

5. Write tests in tests/generation/test_pii.py:
   - Test PII detection
   - Test randomization consistency
   - Test with various PII types
   - Test relationship preservation after anonymization
```

## Validation Module

### Step 11: Validation Framework

```
# Validation Framework Prompt

Implement a validation framework for generated data:

1. Create validation/base.py with:
   - BaseValidator abstract class
   - ValidationRule class
   - ValidationResult class

2. Create validation/cdisc.py with:
   - CDISC validation rules
   - SDTM compliance checks
   - Standard domain validators

3. Create validation/custom.py with:
   - Custom rule creation interface
   - Rule parsing and execution

4. Create validation/service.py with:
   - ValidationService to orchestrate validation
   - Methods to validate generated data
   - Reporting mechanisms

5. Write tests in tests/validation/:
   - Test with valid data
   - Test with invalid data
   - Test custom rule creation
   - Test CDISC validation
```

## Data Export Module

### Step 12: Data Export Service

```
# Data Export Service Prompt

Implement data export functionality:

1. Create export/csv.py with:
   - Methods to export DataFrames to CSV
   - Formatting options
   - Header management

2. Create export/service.py with:
   - ExportService class
   - Methods to export multiple domains
   - Directory structure creation

3. Create export/models.py with:
   - ExportConfig class
   - ExportResult class
   - ExportFormat enum

4. Implement export/utils.py with:
   - Utility functions for file naming
   - Path management
   - Metadata file creation

5. Write tests in tests/export/:
   - Test CSV export
   - Test with various configurations
   - Test file structure
   - Test with multiple domains
```

## Database Integration

### Step 13: Database Models and ORM

```
# Database Models and ORM Prompt

Implement database models for storing application data:

1. Create db/models.py with:
   - SQLAlchemy ORM models for:
     - Users
     - Projects
     - DataFiles
     - GenerationJobs
     - ValidationResults

2. Create db/database.py with:
   - Database connection management
   - Session factory
   - Migration utilities

3. Create db/repositories/ directory with:
   - Base repository pattern implementation
   - Specific repositories for each model
   - CRUD operations

4. Create db/schemas.py with:
   - Pydantic schemas for database models
   - Validation for database operations

5. Write tests in tests/db/:
   - Test database connection
   - Test CRUD operations
   - Test with sample data
```

## API Development

### Step 14: FastAPI Application Setup

```
# FastAPI Application Setup Prompt

Set up the FastAPI application structure:

1. Create api/app.py with:
   - FastAPI application instance
   - CORS configuration
   - Error handlers
   - Middleware setup

2. Create api/dependencies.py with:
   - Common API dependencies
   - Database session dependency
   - Current user dependency

3. Create api/schemas/ directory with:
   - Request/response schemas for each endpoint
   - Base schema classes

4. Create api/routers/ directory structure

5. Create api/middleware.py with:
   - Authentication middleware
   - Logging middleware
   - Error handling middleware

6. Write tests in tests/api/test_app.py:
   - Test application setup
   - Test middleware
   - Test error handling
```

### Step 15: Authentication API

```
# Authentication API Prompt

Implement authentication endpoints using FastAPI-Users:

1. Create api/auth/ directory with:
   - auth_config.py - Configuration for FastAPI-Users
   - auth_models.py - User model extensions
   - auth_router.py - Router for auth endpoints

2. Implement in auth_router.py:
   - Login endpoint
   - Registration endpoint
   - User management endpoints
   - Role management

3. Create api/auth/dependencies.py with:
   - Current user with specific role dependencies
   - Permission checking functions

4. Update api/app.py to:
   - Include auth router
   - Configure JWT authentication

5. Write tests in tests/api/test_auth.py:
   - Test registration
   - Test login
   - Test permissions
   - Test with different roles
```

### Step 16: Data Ingestion API

```
# Data Ingestion API Prompt

Implement API endpoints for data ingestion:

1. Create api/routers/ingestion.py with endpoints for:
   - File upload
   - Domain mapping
   - Ingestion status
   - File validation

2. Create api/schemas/ingestion.py with:
   - FileUpload schema
   - IngestionResult schema
   - ValidationError schema

3. Create api/services/ingestion_service.py to:
   - Connect API with data ingestion module
   - Handle file uploads
   - Manage temporary files

4. Update api/app.py to include the ingestion router

5. Write tests in tests/api/test_ingestion.py:
   - Test file upload
   - Test with various file types
   - Test error handling
   - Test authentication requirements
```

### Step 17: Data Generation API

```
# Data Generation API Prompt

Implement API endpoints for data generation:

1. Create api/routers/generation.py with endpoints for:
   - Generation configuration
   - Start generation job
   - Generation status
   - Download generated files

2. Create api/schemas/generation.py with:
   - GenerationConfig schema
   - GenerationJob schema
   - GenerationResult schema

3. Create api/services/generation_service.py to:
   - Connect API with data generation module
   - Manage generation jobs
   - Handle background tasks

4. Implement background task processing in api/tasks.py:
   - Generation task
   - Task status tracking
   - Result storage

5. Write tests in tests/api/test_generation.py:
   - Test generation configuration
   - Test job status
   - Test file download
   - Test with authentication
```

## Frontend Development

### Step 18: React Project Setup

```
# React Project Setup Prompt

Set up the React frontend project:

1. Create a new React application using Create React App:
   - Name it "datareplicator-ui"
   - Set up with TypeScript
   - Configure eslint and prettier

2. Install dependencies:
   - React Router for navigation
   - Tailwind UI for styling
   - Axios for API calls
   - React Query for data fetching
   - React Hook Form for forms

3. Create project structure:
   - src/components/ - Reusable UI components
   - src/pages/ - Page components
   - src/api/ - API client code
   - src/hooks/ - Custom hooks
   - src/context/ - React context providers
   - src/types/ - TypeScript type definitions
   - src/utils/ - Utility functions

4. Set up basic styling with Tailwind:
   - Configure tailwind.config.js
   - Set up base styles

5. Create basic tests using React Testing Library
```

### Step 19: Authentication UI

```
# Authentication UI Prompt

Implement authentication UI components:

1. Create auth context in src/context/AuthContext.tsx:
   - User state
   - Login/logout functions
   - Role-based permissions

2. Create auth API client in src/api/auth.ts:
   - Login function
   - Registration function
   - User profile functions

3. Create authentication components in src/components/auth/:
   - LoginForm.tsx
   - RegisterForm.tsx
   - ForgotPassword.tsx

4. Create authentication pages in src/pages/auth/:
   - LoginPage.tsx
   - RegisterPage.tsx
   - ForgotPasswordPage.tsx

5. Implement protected routes in src/components/ProtectedRoute.tsx:
   - Role-based access control
   - Redirect to login

6. Write tests for authentication components and pages
```

### Step 20: Data Upload and Project UI

```
# Data Upload and Project UI Prompt

Implement UI for data upload and project management:

1. Create project context in src/context/ProjectContext.tsx:
   - Current project state
   - Project management functions

2. Create project API client in src/api/projects.ts:
   - Create project function
   - Upload files function
   - Get project status

3. Create project components in src/components/projects/:
   - ProjectForm.tsx
   - FileUpload.tsx
   - ProjectList.tsx
   - ProjectDetail.tsx

4. Create project pages in src/pages/projects/:
   - ProjectsPage.tsx
   - CreateProjectPage.tsx
   - ProjectDetailPage.tsx

5. Implement file upload with:
   - Drag and drop functionality
   - Progress indication
   - Validation feedback

6. Write tests for project components and pages
```

### Step 21: Data Generation UI

```
# Data Generation UI Prompt

Implement UI for data generation configuration and execution:

1. Create generation context in src/context/GenerationContext.tsx:
   - Generation configuration state
   - Generation job status

2. Create generation API client in src/api/generation.ts:
   - Configure generation
   - Start generation job
   - Get generation status
   - Download generated files

3. Create generation components in src/components/generation/:
   - ConfigurationForm.tsx
   - GenerationStatus.tsx
   - DownloadFiles.tsx

4. Create generation pages in src/pages/generation/:
   - ConfigurationPage.tsx
   - GenerationStatusPage.tsx

5. Implement real-time status updates using:
   - Polling or WebSockets
   - Progress indicators
   - Error handling

6. Write tests for generation components and pages
```

### Step 22: Visualization UI

```
# Visualization UI Prompt

Implement basic data visualization components:

1. Install visualization libraries:
   - Chart.js for basic charts
   - react-chartjs-2 for React integration

2. Create visualization API client in src/api/visualization.ts:
   - Get data summary
   - Get completeness metrics
   - Get relationship data

3. Create visualization components in src/components/visualization/:
   - CompletionChart.tsx - For data completeness metrics
   - SubjectCountDisplay.tsx - For subject count visualization
   - DataSummaryTable.tsx - For basic data summary

4. Create visualization page in src/pages/visualization/:
   - DataVisualizationPage.tsx

5. Implement dynamic chart rendering based on:
   - Data types
   - Available metrics
   - User selection

6. Write tests for visualization components and pages
```

### Step 23: Admin UI

```
# Admin UI Prompt

Implement administration UI for user management:

1. Create admin API client in src/api/admin.ts:
   - User management functions
   - System settings functions

2. Create admin components in src/components/admin/:
   - UserList.tsx
   - UserForm.tsx
   - SystemSettings.tsx

3. Create admin pages in src/pages/admin/:
   - UsersPage.tsx
   - SettingsPage.tsx

4. Implement role-based UI rendering:
   - Show admin features only to admin users
   - Restrict access to admin routes

5. Create settings forms for:
   - Registration settings
   - Authentication settings
   - System defaults

6. Write tests for admin components and pages
```

### Step 24: API Integration and Deployment

```
# API Integration and Deployment Prompt

Integrate frontend with backend API and set up deployment:

1. Create environment configuration:
   - .env.development
   - .env.production
   - API URL configuration

2. Update API client base:
   - Add authentication headers
   - Handle token refresh
   - Error handling

3. Create Dockerfile for frontend:
   - Multi-stage build
   - Nginx configuration for serving

4. Create Dockerfile for backend:
   - Python application container
   - Dependency installation
   - Environment configuration

5. Create docker-compose.yml for local development:
   - Frontend service
   - Backend service
   - Database service

6. Write documentation in docs/:
   - Installation guide
   - Development setup
   - Production deployment
   - User guide

7. Create basic CI pipeline configuration:
   - Test automation
   - Build process
   - Deployment steps
```

## Testing and Documentation

### Step 25: End-to-End Testing

```
# End-to-End Testing Prompt

Implement end-to-end tests for the entire application:

1. Set up Cypress for end-to-end testing:
   - Install dependencies
   - Configure test environment

2. Create E2E test scenarios in cypress/integration/:
   - Authentication flow
   - Data upload workflow
   - Generation workflow
   - Export workflow

3. Create test fixtures in cypress/fixtures/:
   - Sample CSV files
   - User data
   - Configuration settings

4. Implement test utilities in cypress/support/:
   - Custom commands
   - Authentication helpers
   - File handling helpers

5. Configure GitHub Actions for:
   - Running E2E tests
   - Reporting results
   - Visual regression tests
```

### Step 26: Documentation

```
# Documentation Prompt

Create comprehensive documentation for the application:

1. Create user documentation:
   - User guide
   - Feature documentation
   - FAQ section
   - Troubleshooting guide

2. Create technical documentation:
   - Architecture overview
   - API documentation
   - Data model documentation
   - Development guide

3. Set up automated API documentation:
   - Configure Swagger UI
   - Integrate with FastAPI

4. Create database schema documentation:
   - ERD diagrams
   - Relationship descriptions
   - Migration guides

5. Create deployment documentation:
   - Installation guide
   - Configuration options
   - Scaling recommendations
   - Security considerations
```

## Final Integration and Review

### Step 27: Final Integration

```
# Final Integration Prompt

Perform final integration and system testing:

1. Create integration tests for complete workflows:
   - End-to-end data replication process
   - Authentication and authorization flows
   - Error handling and recovery

2. Implement system monitoring:
   - Application health checks
   - Error logging
   - Performance metrics

3. Perform security review:
   - Authentication mechanisms
   - Authorization checks
   - Data protection measures

4. Optimize performance:
   - Database query optimization
   - API endpoint performance
   - UI rendering performance

5. Create final deployment scripts:
   - Production setup
   - Database initialization
   - Sample data loading
```

### Step 28: Project Review and Handoff

```
# Project Review and Handoff Prompt

Prepare the project for review and handoff:

1. Create project summary documentation:
   - Project overview
   - Architecture decisions
   - Technology choices
   - Future enhancements

2. Conduct code quality review:
   - Run static analysis tools
   - Address code quality issues
   - Ensure test coverage

3. Create handoff materials:
   - Setup instructions
   - Deployment guide
   - Maintenance procedures
   - Troubleshooting guide

4. Prepare demonstration materials:
   - Demo script
   - Sample datasets
   - Common use cases

5. Document future roadmap:
   - Planned features
   - Known limitations
   - Potential improvements
```

## Implementation Strategy

This plan breaks down the DataReplicator project into manageable, iterative steps. Each step builds upon previous work and includes testing to ensure quality throughout the development process.

The steps are organized to first establish core functionality (data ingestion, analysis, generation) before moving to the API and UI components. This allows for early testing of the core algorithms while providing a foundation for the web application.

The suggested approach prioritizes:
1. Test-driven development
2. Incremental progress with working code at each step
3. Proper separation of concerns
4. Reusable components
5. Comprehensive documentation

By following these prompts in sequence, a code-generation LLM can incrementally build the DataReplicator application while maintaining high-quality code and ensuring that each component properly integrates with the rest of the system.
