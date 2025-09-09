# CCS (Catering Control System) Back-End Documentation

## Project Overview

The CCS Back-End is a comprehensive serverless microservices architecture built for catering and flight management systems. It serves as the backend for a sophisticated airline catering reconciliation and invoice management platform that processes flight data, price reports, invoices, and provides reconciliation capabilities between different data sources.

### System Purpose
- **Flight Data Management**: Process and analyze airline flight information
- **Price Report Analysis**: Handle pricing data from various airline sources
- **Invoice Processing**: Manage catering and airline company invoices
- **Data Reconciliation**: Compare and reconcile data between different sources
- **Annotation System**: Allow users to add notes and annotations to reconciliation data

### Technology Stack Summary
- **Runtime**: Python 3.12 with Flask framework
- **Serverless Platform**: AWS Lambda with Serverless Framework
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: AWS Cognito JWT Authorization
- **File Storage**: Amazon S3
- **Infrastructure**: AWS VPC, API Gateway, CloudFormation
- **Database Migrations**: Alembic
- **Deployment**: AWS CodeBuild with automated CI/CD

---

## Architecture

### Technology Stack

**Backend Framework**
- Python 3.12
- Flask 2.2.3 with Werkzeug 2.2.2
- Flask-Parameter-Validation for request validation
- Flask-Authorize for role-based access control
- Flask-Babel for internationalization
- Serverless-WSGI for AWS Lambda integration

**Database & ORM**
- PostgreSQL (AWS RDS/Aurora)
- SQLAlchemy for ORM
- SQLAlchemy-Pagination for query pagination
- Alembic for database migrations
- AWS-psycopg2 for PostgreSQL connectivity

**AWS Services**
- AWS Lambda (Compute)
- Amazon API Gateway (HTTP API)
- Amazon Cognito (Authentication)
- Amazon S3 (File Storage)
- AWS Secrets Manager (Configuration)
- Amazon VPC (Networking)
- AWS CloudFormation (Infrastructure as Code)

**File Processing**
- PyPDF2 and PyMuPDF for PDF processing
- Pandas for data manipulation
- OpenPyXL for Excel file processing

### Deployment Environments

#### Development Environment
- **Stage**: `dev`
- **AWS Account**: 018061303185
- **VPC**: vpc-03dac6c8184066691
- **Region**: us-east-1
- **Frontend URL**: https://dev.makethefuture.tech
- **Cognito User Pool**: us-east-1_JRwQ9y4Jg
- **EC2 Scheduling**: Disabled

#### QA Environment
- **Stage**: `qa`
- **AWS Account**: 836450907988
- **VPC**: vpc-0f99334641d2742ad
- **Region**: us-east-1
- **Frontend URL**: https://qa.makethefuture.tech
- **Cognito User Pool**: us-east-1_QOe2Jmpv0
- **EC2 Scheduling**: Enabled
__QA environment is not working__

#### Production Environment
- **Stage**: `prod`
- **AWS Account**: 123642328289
- **VPC**: vpc-05a05692560fcbf00
- **Region**: us-east-1
- **Frontend URL**: https://www.makethefuture.tech
- **Cognito User Pool**: us-east-1_7IIETToot
- **EC2 Scheduling**: Enabled

### Infrastructure Details
- **API Gateway**: HTTP API with CORS enabled
- **Rate Limiting**: 5000 requests/month quota, 200 burst limit, 100 requests/second
- **Lambda Configuration**: Individual packaging per function
- **VPC Configuration**: Private subnets with security groups
- **Log Retention**: 30 days
- **Tracing**: X-Ray enabled for API Gateway and Lambda

---

## Microservices Architecture

### 1. Reconciliation API
- **Function**: `reconciliation_api`
- **Image**: `reconciliation_api`
- **Memory**: 3072 MB
- **Timeout**: 60 seconds
- **Authorization**: Cognito JWT Required
- **Description**: Main API for retrieving reconciliation data with advanced filtering and pagination

### 2. Invoice Reports API
- **Function**: `invoice_reports_api`
- **Image**: `invoice_reports_api`
- **Memory**: 3072 MB
- **Timeout**: 60 seconds
- **Authorization**: Cognito JWT Required
- **Description**: API for retrieving air company and catering invoice reports

### 3. Reconciliation Annotation API
- **Function**: `recon_annotation_api`
- **Image**: `recon_annotation_api`
- **Memory**: 1024 MB
- **Timeout**: 60 seconds
- **Authorization**: Cognito JWT Required
- **Description**: CRUD operations for reconciliation annotations and comments

### 4. Analyze Data API
- **Function**: `analyse_data_api`
- **Image**: `analyse_data_api`
- **Memory**: 1024 MB
- **Timeout**: 600 seconds (10 minutes)
- **Authorization**: Cognito JWT Required
- **Description**: Data analysis and comparison service for billing invoices

### 5. Populate Reconciliation API
- **Function**: `populate_reconciliation_table_api`
- **Image**: `populate_reconciliation_api`
- **Memory**: 3072 MB
- **Timeout**: 300 seconds (5 minutes)
- **Authorization**: Cognito JWT Required
- **Description**: Service to populate reconciliation table with processed data

### 6. Airline API
- **Function**: `airline_api`
- **Image**: `airline_api`
- **Memory**: 1024 MB
- **Timeout**: 29 seconds
- **Authorization**: Cognito JWT Required
- **Description**: Flight data management and file upload service

### 7. File Processing Services

#### Analyze Flight File
- **Function**: `analyze_flight_file`
- **Image**: `analyze_flight_file`
- **Description**: Processes airline flight files (TP-006 format)

#### Analyze Price Report
- **Function**: `analyze_price_report`
- **Image**: `analyze_price_report`
- **Description**: Processes price report files (TP-100 format)

#### Analyze Invoice
- **Function**: `analyze_invoice`
- **Image**: `analyze_invoice`
- **Description**: Processes invoice files and extracts relevant data

#### Read Files Reconciliation
- **Function**: `read_files_recon`
- **Image**: `read_files_recon`
- **Description**: Reads and processes files for reconciliation purposes

---

## Database Schema

### Core Business Entities

#### Flight Management
- **Flight**: Core flight information with airline, route, timing, and passenger details
- **FlightDate**: Flight date management and scheduling
- **Configuration**: Flight configuration settings
- **FlightNumberMapping**: Mapping between different flight number formats
- **FlightClassMapping**: Flight class and service type mappings

#### Data Processing
- **DataSource**: Tracks data sources and file pages for flight information
- **PriceReport**: Stores pricing data from airline systems

#### Invoice and Billing
- **InvoiceHistory**: Comprehensive invoice history with detailed line items
- **CateringInvoiceReport**: Catering service invoices and billing details
- **AirCompanyInvoiceReport**: Airline company invoices and financial data
- **BillingInvoiceTotalDifference**: Tracks differences in billing amounts

#### Reconciliation System
- **Reconciliation**: Main reconciliation entity comparing different data sources
- **ReconAnnotation**: User annotations and comments on reconciliation data

### Entity Relationships

#### User Management (Public Schema)
- **User**: System users with role-based access control
- **UserGroup**: User group definitions for authorization
- **UserGroupUser**: Many-to-many relationship between users and groups

#### Audit and Tracking
All main entities include:
- `Id`: UUID primary key
- `DataCriacao`: Creation timestamp
- `DataAtualizacao`: Last update timestamp
- `Ativo`: Active status flag
- `Excluido`: Soft delete flag
- `IdUsuarioAlteracao`: User who made the last change

---

## API Endpoints

### Reconciliation Services

#### Reconciliation Data API
- **GET** `/api/reconciliation/data`
  - **Description**: Retrieve paginated reconciliation data with advanced filtering
  - **Authorization**: Cognito JWT Required
  - **Query Parameters**:
    - `limit` (int): Number of records per page (default: 100)
    - `offset` (int): Number of records to skip (default: 0)
    - `filter_type` (string): Filter type - `all`, `discrepancies`, `air_only`, `cat_only`, `quantity_difference`, `price_difference`
    - `start_date` (string): Start date filter (YYYY-MM-DD)
    - `end_date` (string): End date filter (YYYY-MM-DD)
    - `flight_number` (string): Flight number filter
    - `item_name` (string): Item name filter

#### Populate Reconciliation
- **POST** `/api/reconciliation/populate`
  - **Description**: Populate reconciliation table with processed data
  - **Authorization**: Cognito JWT Required
  - **Query Parameters**:
    - `force_populate` (boolean): Force repopulation (default: false)

### Invoice Reports Services

#### Air Company Reports
- **GET** `/api/invoice-reports/air-company`
  - **Description**: Retrieve air company invoice reports with pagination
  - **Authorization**: Admin role required
  - **Query Parameters**:
    - `limit` (int): Records per page (1-100, default: 50)
    - `offset` (int): Records to skip (default: 0)

#### Catering Reports
- **GET** `/api/invoice-reports/catering`
  - **Description**: Retrieve catering invoice reports with pagination
  - **Authorization**: Admin role required
  - **Query Parameters**:
    - `limit` (int): Records per page (1-100, default: 50)
    - `offset` (int): Records to skip (default: 0)

### Annotation Services

#### Create Annotation
- **POST** `/api/annotations`
  - **Description**: Create a new reconciliation annotation
  - **Authorization**: Admin role required
  - **Request Body**:
    ```json
    {
      "reconciliation_id": "uuid",
      "annotation_text": "string",
      "category": "string"
    }
    ```

#### Get Annotation by ID
- **GET** `/api/annotations/by-id/{annotation_id}`
  - **Description**: Retrieve a specific annotation by ID
  - **Authorization**: Admin role required
  - **Path Parameters**:
    - `annotation_id` (string): UUID of the annotation

#### Update Annotation
- **PUT** `/api/annotations`
  - **Description**: Update an existing annotation
  - **Authorization**: Admin role required
  - **Request Body**:
    ```json
    {
      "id": "uuid",
      "annotation_text": "string",
      "category": "string"
    }
    ```

#### Delete Annotation
- **DELETE** `/api/annotations/{annotation_id}`
  - **Description**: Delete an annotation
  - **Authorization**: Admin role required
  - **Path Parameters**:
    - `annotation_id` (string): UUID of the annotation

### Flight Data Services

#### Upload Airline Data
- **POST** `/flights/upload/airline`
  - **Description**: Upload airline data files
  - **Authorization**: Cognito JWT Required

#### Upload Price Report
- **POST** `/flights/upload/price_report`
  - **Description**: Upload price report files
  - **Authorization**: Cognito JWT Required

#### Delete Price Report
- **DELETE** `/flights/delete/price_report/{id}`
  - **Description**: Delete a price report by ID
  - **Authorization**: Cognito JWT Required
  - **Path Parameters**:
    - `id` (string): UUID of the price report

#### Upload Invoice
- **POST** `/flights/upload/invoice`
  - **Description**: Upload invoice files
  - **Authorization**: Cognito JWT Required

#### Delete Invoice
- **DELETE** `/flights/delete/invoice`
  - **Description**: Delete invoice data
  - **Authorization**: Cognito JWT Required

#### Search Price Report
- **GET** `/flights/search/price_report/{id}`
  - **Description**: Search for a specific price report
  - **Authorization**: Cognito JWT Required
  - **Path Parameters**:
    - `id` (string): UUID of the price report

### Data Analysis Services

#### Compare Data
- **POST** `/analyse_data_api/compare`
  - **Description**: Compare billing invoice data for analysis
  - **Authorization**: Admin role required

---

## Key Features

### Data Reconciliation Engine
- **Multi-Source Comparison**: Compares data between airline systems and catering providers
- **Discrepancy Detection**: Identifies differences in quantities, prices, and billing amounts
- **Advanced Filtering**: Supports multiple filter types for targeted analysis
- **Real-time Processing**: Processes reconciliation data with pagination support

### File Processing Pipeline
- **Multi-format Support**: Handles PDF, Excel, and various airline-specific file formats
- **Automated Extraction**: Extracts flight data, pricing information, and invoice details
- **Data Validation**: Validates data integrity during processing
- **Error Handling**: Comprehensive error handling and logging

### Invoice Management System
- **Dual Invoice Types**: Handles both catering and airline company invoices
- **Financial Tracking**: Tracks payments, variances, and grand totals
- **Historical Data**: Maintains complete invoice history with audit trails
- **Currency Support**: Multi-currency invoice processing

### Annotation System
- **User Comments**: Allows users to add contextual annotations to reconciliation data
- **Category Classification**: Organizes annotations by category for better management
- **Audit Trail**: Tracks annotation changes with user attribution
- **Real-time Updates**: Supports CRUD operations with immediate feedback

---

## Authentication & Authorization

### Authentication Mechanism
- **JWT Tokens**: AWS Cognito JWT tokens for API authentication
- **Multi-Environment**: Separate Cognito user pools per environment
- **Token Validation**: Automatic token validation on protected endpoints

### Authorization Groups
- **Admin Group**: Full access to all APIs and administrative functions
- **Role-based Access**: Fine-grained permissions based on user group membership
- **Resource Protection**: All sensitive endpoints require appropriate authorization

### Security Features
- **CORS Configuration**: Proper CORS headers for cross-origin requests
- **VPC Security**: Lambda functions deployed in private VPC subnets
- **Secrets Management**: Database credentials stored in AWS Secrets Manager
- **API Rate Limiting**: Built-in rate limiting and throttling

---

## Data Models

### Flight Entity Lifecycle
1. **Flight Creation**: Basic flight information (airline, route, timing)
2. **Configuration Assignment**: Flight-specific catering configurations
3. **Data Source Linking**: Associate with file sources and page references
4. **Price Report Association**: Link to pricing data and reports
5. **Invoice Processing**: Generate and process related invoices
6. **Reconciliation**: Compare against catering provider data

### Reconciliation Process Flow
1. **Data Collection**: Gather flight data from multiple sources
2. **Data Normalization**: Standardize formats and structures
3. **Comparison Engine**: Compare airline vs. catering data
4. **Discrepancy Identification**: Flag differences in quantity/price
5. **Annotation Support**: Allow user notes and explanations
6. **Report Generation**: Create reconciliation reports

### Invoice Processing States
- **PROCESSING**: Invoice is being processed
- **READY**: Invoice is ready for review
- **PENDING**: Awaiting approval or action
- **APPROVED**: Invoice has been approved
- **COMPLETED**: Processing completed successfully
- **FAIL**: Processing failed with errors

---

## Environment Configuration

### Development Environment
- **Purpose**: Development and testing
- **Database**: Development PostgreSQL instance
- **S3 Buckets**:
  - `mtw-elementar-dev-018061303185`
  - `mtw-refinado-dev`
  - `mtw-make-the-price-dev-018061303185`
- **Monitoring**: Basic logging and monitoring
- **EC2 Scheduling**: Disabled for cost optimization

### QA Environment
- **Purpose**: Quality assurance and staging
- **Database**: QA PostgreSQL instance with production-like data
- **S3 Buckets**:
  - `mtw-elementar-dev-018061303185` (shared)
  - `mtw-refinado-qa`
  - `mtw-make-the-price-qa-836450907988`
- **Monitoring**: Enhanced monitoring and alerting
- **EC2 Scheduling**: Enabled for resource management
__QA environment is not working__


### Production Environment
- **Purpose**: Live production system
- **Database**: Production PostgreSQL with high availability
- **S3 Buckets**:
  - `mtw-elementar-dev-018061303185` (shared)
  - `mtw-refinado`
  - `mtw-make-the-price-prod-123642328289`
- **Monitoring**: Full monitoring, alerting, and observability
- **EC2 Scheduling**: Enabled for cost optimization

---

## Error Handling

### Exception Management
- **Custom Exceptions**: Application-specific exception classes
- **Global Exception Handler**: Centralized error handling across all services
- **Parameter Validation**: Flask parameter validation with custom handlers
- **Error Response Format**: Standardized error response structure

### Logging Strategy
- **Structured Logging**: JSON-formatted logs for better parsing
- **Log Levels**: INFO level default with configurable levels
- **Correlation IDs**: Request tracking across microservices
- **Error Context**: Detailed error context for debugging

### Response Format
```json
{
  "success": false,
  "error": "Error description",
  "data": null,
  "statusCode": 400
}
```

---

## Pagination

### Implementation
- **Limit/Offset Pattern**: Standard pagination with configurable limits
- **Default Values**: Sensible defaults (limit: 50-100, offset: 0)
- **Maximum Limits**: Protection against excessive data retrieval
- **Response Metadata**: Pagination information in responses

### Usage Examples
```http
GET /api/reconciliation/data?limit=100&offset=200
GET /api/invoice-reports/air-company?limit=50&offset=0
```

---

## File Processing

### Supported File Types
- **PDF Files**: Invoice and report processing with PyPDF2/PyMuPDF
- **Excel Files**: Data import with OpenPyXL
- **CSV Files**: Structured data import
- **Airline-Specific Formats**: TP-006, TP-100 format processors

### Processing Pipeline
1. **File Upload**: S3 storage with metadata tracking
2. **Format Detection**: Automatic file type identification
3. **Data Extraction**: Content parsing and data extraction
4. **Validation**: Data integrity and format validation
5. **Database Storage**: Processed data storage
6. **Cleanup**: Temporary file cleanup and optimization

---

## Monitoring & Logging

### AWS X-Ray Tracing
- **API Gateway Tracing**: Request/response tracing
- **Lambda Tracing**: Function execution tracing
- **Performance Monitoring**: Latency and error tracking

### CloudWatch Integration
- **Log Aggregation**: Centralized log collection
- **Metrics**: Custom application metrics
- **Alarms**: Automated alerting on errors/performance issues
- **Dashboards**: Real-time monitoring dashboards

### Log Retention
- **Retention Period**: 30 days for all Lambda functions
- **Log Levels**: Configurable via environment variables
- **Structured Logging**: JSON format for better analysis

---

## Security Features

### VPC Configuration
- **Private Subnets**: Lambda functions in private subnets
- **Security Groups**: Restrictive network access controls
- **NAT Gateway**: Controlled internet access for Lambda functions

### Data Protection
- **Encryption in Transit**: HTTPS/TLS for all API communications
- **Encryption at Rest**: RDS and S3 encryption enabled
- **Secrets Management**: AWS Secrets Manager for sensitive data
- **IAM Roles**: Least privilege access principles

### API Security
- **JWT Validation**: Cognito JWT token validation
- **CORS Policy**: Configured CORS for web application access
- **Rate Limiting**: API Gateway throttling and usage plans
- **Input Validation**: Parameter validation on all endpoints

---

## Deployment Process

### CI/CD Pipeline
1. **Code Commit**: Developer commits to repository
2. **Build Trigger**: AWS CodeBuild automatically triggered
3. **Dependency Installation**: Node.js and Python dependencies
4. **Database Migration**: Alembic migration execution
5. **Serverless Deployment**: Deploy to target environment
6. **Health Checks**: Post-deployment validation

### Build Configuration
```yaml
# buildspec.yml
version: 0.2
phases:
  install:
    runtime-versions:
      nodejs: 20
    commands:
      - npm install -g serverless
      - npm install
      - pip install alembic
      - pip install psycopg2-binary
      - pip install flask_authorize
  build:
    commands:
      - alembic upgrade head
      - serverless deploy --stage $ENVIRONMENT
```

### Environment Promotion
- **Development**: Automatic deployment on code changes
- **QA**: Automated deployment after development validation
- **Production**: Manual approval required for deployment

---

## Performance Optimization

### Lambda Configuration
- **Memory Allocation**: Optimized per function requirements (1GB-3GB)
- **Timeout Settings**: Appropriate timeouts per function complexity
- **Cold Start Optimization**: Container reuse strategies

### Database Optimization
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Optimized SQLAlchemy queries
- **Pagination**: Efficient data retrieval for large datasets

### Caching Strategy
- **Application Caching**: In-memory caching for frequently accessed data
- **Database Caching**: PostgreSQL query result caching
- **CDN Integration**: Static asset caching via CloudFront

---

## Future Enhancements

### Planned Features
- **Real-time Notifications**: WebSocket integration for live updates
- **Advanced Analytics**: Machine learning for anomaly detection
- **Mobile API**: Mobile-optimized endpoints
- **Batch Processing**: Large-scale data processing capabilities

### Scalability Improvements
- **Event-Driven Architecture**: SQS/SNS integration for asynchronous processing
- **Microservice Decomposition**: Further service separation for better scalability
- **Caching Layer**: Redis/ElastiCache integration
- **Read Replicas**: Database read replica implementation

---

## Technical Specifications

### Database Specifications
- **Engine**: PostgreSQL
- **Schemas**: `ccs` (main), `public` (user management)
- **Connection**: AWS RDS with SSL
- **Migration Tool**: Alembic
- **ORM**: SQLAlchemy 1.4+

### API Specifications
- **Protocol**: HTTP/1.1 and HTTP/2
- **Format**: JSON request/response
- **Authentication**: JWT Bearer tokens
- **CORS**: Enabled for cross-origin requests
- **Rate Limiting**: 100 requests/second, 5000/month quota

### Infrastructure Specifications
- **Compute**: AWS Lambda (Python 3.12 runtime)
- **API Gateway**: HTTP API (v2)
- **Storage**: Amazon S3 with versioning
- **Network**: VPC with private subnets
- **Monitoring**: CloudWatch + X-Ray
- **Deployment**: Serverless Framework v4

---

This documentation provides a comprehensive overview of the CCS Back-End system, covering all aspects from architecture to deployment. The system is designed for scalability, security, and maintainability while providing robust functionality for airline catering reconciliation and management.
