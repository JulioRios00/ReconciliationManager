# ReconciliationManager

A comprehensive backend service for financial data reconciliation, built with Python and AWS services. This project provides APIs for reconciling invoices, flight data, and billing information across multiple data sources.

## Features

- **Multi-source Data Reconciliation**: Handles reconciliation between different data sources including flight data, invoices, and billing reports
- **RESTful APIs**: Provides clean REST APIs for reconciliation operations
- **AWS Integration**: Leverages AWS Lambda, API Gateway, S3, and PostgreSQL for scalable cloud deployment
- **Modular Architecture**: Well-structured codebase with separate services, repositories, and models
- **Automated Code Quality**: Pre-commit hooks for code formatting (Black), import sorting (isort), and linting (Flake8)

## Tech Stack

- **Language**: Python 3.8+
- **Framework**: Flask
- **Database**: PostgreSQL (via SQLAlchemy)
- **Cloud Services**: AWS Lambda, API Gateway, S3, Secrets Manager
- **Deployment**: Serverless Framework
- **Code Quality**: Pre-commit, Black, isort, Flake8

## Project Structure

```
├── src/
│   ├── app/
│   │   ├── extract_data_app/
│   │   ├── recon_annotation_api/
│   │   ├── reconciliation_api/
│   │   └── common/
│   ├── models/          # Database models
│   ├── repositories/    # Data access layer
│   ├── services/        # Business logic
│   ├── enums/           # Enumerations
│   └── requirements.txt # Python dependencies
├── resources/
│   └── api_gateway/     # API Gateway configurations
├── tests/               # Unit tests
├── alembic/             # Database migrations
├── serverless.yml       # Serverless deployment config
└── .pre-commit-config.yaml # Code quality hooks
```

## Dependencies

This project uses two requirements files:

- **`requirements.txt`** (root): Contains all dependencies including production, development, and testing tools
- **`src/requirements.txt`**: Contains only production dependencies for deployment

For development, use `pip install -r requirements.txt` to get all tools needed.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JulioRios00/ReconciliationManager.git
   cd ReconciliationManager
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install all dependencies (production + development):**
   ```bash
   pip install -r requirements.txt
   ```

   Or install only production dependencies:
   ```bash
   pip install -r src/requirements.txt
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Configure environment variables:**
   Create a `.env` file or set environment variables for:
   - Database connection strings
   - AWS credentials
   - API keys and secrets

## Usage

### Local Development

1. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

2. **Start the Flask application:**
   ```bash
   cd src
   python -m flask run
   ```

3. **Run tests:**
   ```bash
   python -m pytest tests/
   ```

### Deployment

1. **Install Serverless Framework:**
   ```bash
   npm install -g serverless
   ```

2. **Deploy to AWS:**
   ```bash
   serverless deploy
   ```

## API Endpoints

The service provides several APIs:

- **Reconciliation API**: `/reconciliation` - Main reconciliation operations
- **Annotation API**: `/recon-annotation` - Data annotation services
- **Data Extraction**: `/extract-data` - Data extraction from various sources

## Code Quality

This project uses pre-commit hooks to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Linting
- **Pre-commit hooks**: Trailing whitespace, YAML validation, large file checks

Run all checks manually:
```bash
pre-commit run --all-files
```
