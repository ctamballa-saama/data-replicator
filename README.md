# DataReplicator

A tool for analyzing clinical trial datasets and generating additional synthetic data while maintaining statistical properties, relationships, and domain-specific integrity.

## Current Status (August 27, 2025)

Recent fixes and improvements:
- Fixed frontend JavaScript issues with null/undefined handling in numerical displays
- Resolved backend data generation compatibility issues between numpy and pandas
- Fixed data download functionality for generated synthetic data
- Enhanced error handling and robustness throughout the application
- Improved UI responsiveness and data visualization components

## Overview

DataReplicator is designed to help clinical researchers expand their datasets by analyzing existing clinical trial data and generating new synthetic subjects that preserve statistical properties and relationships between domains. This tool is particularly useful when working with small sample sizes (e.g., around 20 subjects) and needing to generate additional subjects (e.g., up to 100) for testing, training, or simulation purposes.

## Features

- **Data Ingestion**: Upload and validate CSV files across multiple clinical domains
- **Statistical Analysis**: Analyze patterns, distributions, and relationships in existing data
- **Data Generation**: Create synthetic subject data preserving statistical properties
- **Validation**: Ensure generated data meets CDISC standards and custom validation rules
- **Data Export**: Export generated data as organized CSV files
- **Web Interface**: User-friendly UI for uploading data and configuring generation

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/saama-data-gen.git
   cd saama-data-gen
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install frontend dependencies:
   ```
   cd frontend
   npm install
   cd ..
   ```

## Usage

### Option 1: Using the Start Script (Recommended)

We've included a convenience script to start both the backend and frontend simultaneously:

```bash
./start_app.sh
```

This will:
- Start the FastAPI backend on http://localhost:8000
- Start the React frontend on http://localhost:3000
- Log output to the logs/ directory

### Option 2: Manual Startup

#### Backend

```bash
cd saama-data-gen
source venv/bin/activate  # If not already activated
python -m uvicorn datareplicator.api.app:app --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000
API Documentation: http://localhost:8000/docs

#### Frontend

```bash
cd saama-data-gen/frontend
npm start
```

The frontend will be available at http://localhost:3000

### Authentication

The application currently uses a mock authentication system for development purposes. Use the following credentials to log in:

#### Admin User Credentials
- Email: `admin@datareplicator.com` / Password: `admin123`
- Email: `admin` / Password: `password`

Admin users have full access to all features, including the Admin UI at http://localhost:3000/admin

#### Regular User Credentials
- Email: `user@datareplicator.com` / Password: `user123`
- Email: `dev` / Password: `dev` (developer role)

Regular users have limited permissions and cannot access the Admin UI.

## Project Structure

```
project_root/
├── datareplicator/        # Python package for data replication
│   ├── api/              # FastAPI backend application
│   ├── analysis/         # Statistical analysis
│   │   ├── relationships/ # Relationship detection and analysis
│   │   └── statistics/   # Statistical calculation services
│   ├── config/           # Configuration settings
│   ├── core/             # Core functionality and utilities
│   │   └── config/       # Core configuration
│   ├── data/             # Data models and processing
│   │   ├── domain/       # Domain-specific data handling
│   │   ├── ingestion/    # Data ingestion processing
│   │   └── parsing/      # Data parsing utilities
│   ├── db/               # Database models and connections
│   │   └── models/       # Database models
│   ├── domain_registry/  # Domain management
│   ├── export/           # Data export functionality
│   ├── generation/       # Synthetic data generation
│   │   ├── generators/   # Data generator implementations
│   │   ├── models/       # Generation models
│   │   └── utils/        # Generation utilities
│   ├── ingestion/        # Data ingestion services
│   ├── ui/               # Backend UI components
│   └── validation/       # Data validation services
├── frontend/            # React frontend application
│   ├── build/            # Production build output
│   ├── public/           # Static assets
│   └── src/              # React source code
│       ├── components/   # Reusable UI components
│       │   └── admin/    # Admin UI components
│       ├── context/      # React context providers
│       ├── pages/        # Application pages
│       └── services/     # API service modules
├── data/                # Data directory
│   └── sample/           # Sample data files
├── generated_data/      # Output directory for generated data
├── logs/                # Application logs
├── output/              # General output directory
├── sample_data/         # Additional sample data
├── tests/               # Test suite
│   ├── integration/     # Integration tests
│   └── unit/            # Unit tests
├── uploads/             # Directory for uploaded files
└── start_app.sh         # Convenience script to start the application
```


