# Lead Meld AI - Intelligent Lead Generation Platform

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A comprehensive, AI-powered **lead generation and analysis platform** for discovering, analyzing, and connecting with potential clients from IT service reviews. This platform leverages **semantic search**, **vector embeddings**, and **natural language processing** to extract actionable insights from customer reviews and company profiles.

## 🏗️ Architecture Overview

This system implements a modern **microservices architecture** built on **Python FastAPI** and **Azure services**, designed to handle intelligent data extraction, semantic search, and AI-powered analysis at scale.

### Core Architectural Principles

- **RESTful & GraphQL APIs**: Flexible query interface with both REST and GraphQL endpoints
- **Vector Search**: Semantic search using Azure Cognitive Search with embeddings
- **AI-Powered Analysis**: OpenAI integration for intelligent content analysis and summarization
- **Microservices Design**: Separated API and UI services for independent scaling
- **Async Processing**: Non-blocking operations for high-performance data processing
- **Multi-Storage Strategy**: MongoDB for operational data, Azure Search for vector search

## 🎯 System Capabilities

### 1. **Intelligent Company Profile Discovery**
- **Web Scraping**: Automated extraction from Clutch.co and similar platforms
- **Profile Enrichment**: Company profile data with reviews, ratings, and metadata
- **LinkedIn Integration**: Automated LinkedIn profile discovery and enrichment
- **Data Transformation**: JSONata-based data mapping and transformation

### 2. **Semantic Search & Vector Search**

```
User Query → Embedding Generation → Vector Search → Semantic Ranking → Results
```

**Search Capabilities:**
- **Semantic Search**: Natural language queries with semantic understanding
- **Vector Similarity**: K-nearest neighbor search using embeddings
- **Hybrid Search**: Combination of keyword and vector search
- **Advanced Filtering**: Industry, company size, project budget, date ranges
- **Multi-field Search**: Background, challenges, solutions, and feedback analysis

### 3. **AI-Powered Analysis**

- **Review Analysis**: Intelligent extraction of insights from customer reviews
- **Structured Summarization**: Background, challenges, solutions, and feedback extraction
- **Query-Based Analysis**: Custom analysis based on user queries
- **Chunked Processing**: Efficient processing of large review datasets
- **Multi-level Insights**: Intermediate and final analysis aggregation

### 4. **RAG (Retrieval-Augmented Generation) System**

The platform implements a sophisticated RAG architecture that combines vector search with AI-powered analysis to provide intelligent insights from customer reviews.

**RAG Pipeline Flow:**
```
1. User Query Input
   ↓
2. Query Embedding Generation (Azure OpenAI)
   ↓
3. Hybrid Vector Search (Azure Cognitive Search)
   - Semantic search with vector similarity
   - Keyword matching for exact terms
   - Semantic ranking for relevance
   ↓
4. Context Retrieval
   - Top 25 most relevant reviews retrieved
   - Filtered by industry, company size, budget, date
   - Structured content extraction (background, challenges, solutions, feedback)
   ↓
5. Chunked Analysis (Two-Stage Processing)
   - Stage 1: Parallel processing of review chunks (3 reviews per chunk)
   - Stage 2: Final aggregation and synthesis
   ↓
6. AI-Powered Response Generation
   - Context-aware analysis using retrieved reviews
   - Structured insights extraction
   - Query-specific answer generation
```

**Key RAG Components:**

- **Embedding Generation**: Converts natural language queries into high-dimensional vectors using Azure OpenAI's embedding models (text-embedding-3-small)
- **Vector Search**: Performs semantic similarity search using cosine similarity in Azure Cognitive Search
- **Hybrid Search**: Combines vector search with keyword search for improved accuracy
- **Context Retrieval**: Retrieves top-k most relevant reviews (k=25) based on semantic similarity
- **Chunked Processing**: Processes large review sets in parallel chunks for efficiency
- **Two-Stage Analysis**: 
  - Intermediate analysis: Summarizes individual review chunks
  - Final synthesis: Combines insights into comprehensive answer
- **Structured Extraction**: Extracts specific information (background, challenges, solutions, feedback) from unstructured review text

**RAG Benefits:**
- **Accuracy**: Retrieves contextually relevant information before generating responses
- **Transparency**: Responses are grounded in actual review data
- **Efficiency**: Chunked processing handles large datasets efficiently
- **Scalability**: Vector search scales to millions of documents
- **Flexibility**: Supports complex queries with multiple filters

### 5. **Multi-Storage Architecture**

| Storage Type | Use Case | Technology |
|-------------|----------|------------|
| **MongoDB** | Primary operational data (Company profiles, reviews) | Document database for flexible schemas |
| **Azure Cognitive Search** | Vector search and semantic search | Full-text and vector search capabilities |
| **Azure OpenAI** | Embeddings and completions | AI model services for embeddings and analysis |

### 6. **GraphQL API**

- **Flexible Queries**: Client-defined data fetching
- **Type Safety**: Strongly typed schema with Strawberry GraphQL
- **Aggregations**: Built-in aggregation capabilities (industries, locations, project sizes)
- **Filtering**: Complex filtering across multiple dimensions
- **Profile Search**: Advanced profile search with multiple criteria

### 7. **Streamlit Web Interface**

- **Interactive UI**: User-friendly interface for search and analysis
- **OAuth Integration**: Google OAuth2 authentication
- **Real-time Search**: Live search results with filtering
- **Analysis Dashboard**: Visual representation of insights
- **Contact Management**: LinkedIn profile discovery and management

## 📦 Services & Components

### **FastAPI Backend Service**
**Purpose**: Core API service for data processing and analysis

**Responsibilities:**
- GraphQL API endpoint
- REST API endpoints for search and analysis
- Company profile management
- User authentication and management
- Background task processing

**Technologies:**
- FastAPI (Web framework)
- Strawberry GraphQL (GraphQL implementation)
- Motor (Async MongoDB driver)
- Azure OpenAI (Embeddings and completions)
- Azure Cognitive Search (Vector search)

### **Streamlit Frontend Service**
**Purpose**: Interactive web interface for users

**Responsibilities:**
- User authentication via OAuth2
- Search interface
- Analysis visualization
- Contact discovery and management
- Usage tracking

**Technologies:**
- Streamlit (Web framework)
- OAuth2 integration
- Pandas (Data manipulation)
- Requests (API communication)

### **Background Tasks**
**Purpose**: Asynchronous data processing

**Responsibilities:**
- Company profile scraping
- LinkedIn profile discovery
- Data enrichment
- Batch processing

**Technologies:**
- Apify Client (Web scraping)
- Async processing

## 🔄 Data Flow

### Search & Analysis Flow

```
1. User submits query via Streamlit UI
   ↓
2. Query sent to FastAPI backend
   ↓
3. Query embedded using Azure OpenAI
   ↓
4. Vector search in Azure Cognitive Search
   ↓
5. Results filtered and ranked
   ↓
6. AI analysis of review content
   ↓
7. Structured insights returned to user
```

### Profile Discovery Flow

```
1. Background task triggered
   ↓
2. Apify scraper collects company profiles
   ↓
3. Data transformed using JSONata
   ↓
4. Profiles stored in MongoDB
   ↓
5. LinkedIn profiles discovered
   ↓
6. Profiles enriched with LinkedIn data
```

## 🗄️ Data Storage Strategy

### MongoDB (Primary Operational Store)
- **Company Profiles**: Complete company information with reviews
- **Reviews**: Customer reviews with structured content
- **Schema**: Flexible document model for evolving requirements
- **Indexing**: Optimized indexes for search performance

### Azure Cognitive Search
- **Vector Search**: Semantic similarity search
- **Full-Text Search**: Keyword-based search
- **Hybrid Search**: Combined vector and keyword search
- **Semantic Ranking**: AI-powered result ranking

### Azure OpenAI
- **Embeddings**: Text-to-vector conversion
- **Completions**: AI-powered content analysis
- **Models**: GPT-4, GPT-4o-mini for different use cases

## 🚀 Deployment & Infrastructure

### Containerization
- **Docker**: Both API and Streamlit services containerized
- **Multi-stage builds**: Optimized image sizes
- **Docker Compose**: Local development orchestration

### Cloud Deployment
- **Azure App Service**: Web API hosting (optional)
- **Azure Container Instances**: Container hosting (optional)
- **Azure Cognitive Search**: Search service
- **Azure OpenAI**: AI model services

### Environment Configuration
- **Environment Variables**: Secure configuration management
- **.env Files**: Local development configuration
- **Docker Environment**: Container-based configuration

## 🛠️ Technology Stack

### Backend
- **Python 3.9+**: Primary programming language
- **FastAPI**: Modern, fast web framework
- **Strawberry GraphQL**: GraphQL implementation
- **Motor**: Async MongoDB driver
- **Pydantic**: Data validation and settings management

### AI & Search
- **Azure OpenAI**: Embeddings and completions
- **Azure Cognitive Search**: Vector and semantic search
- **OpenAI SDK**: Python client for OpenAI services
- **Tiktoken**: Token counting and management

### Data & Storage
- **MongoDB**: Document database
- **Motor**: Async MongoDB operations

### Frontend
- **Streamlit**: Rapid web app development
- **Pandas**: Data manipulation and analysis
- **OAuth2**: Authentication integration

### Development Tools
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **VS Code**: Development environment
- **Pytest**: Testing framework

## 📊 Key Features Demonstrated

### ✅ Enterprise Patterns
- **RESTful API Design**: Standard HTTP methods and status codes
- **GraphQL API**: Flexible query interface
- **Async/Await**: Non-blocking operations
- **Service Separation**: Independent API and UI services
- **Error Handling**: Comprehensive error management

### ✅ Scalability & Performance
- **Async Processing**: Non-blocking I/O operations
- **Vector Search**: Efficient semantic similarity search
- **Chunked Processing**: Efficient handling of large datasets
- **Connection Pooling**: Optimized database connections

### ✅ AI & Machine Learning
- **Semantic Search**: Natural language understanding
- **Vector Embeddings**: Text-to-vector conversion
- **AI Analysis**: Intelligent content summarization
- **Multi-level Processing**: Chunked analysis for large datasets
- **Context-Aware Queries**: Semantic query understanding

### ✅ Data Processing
- **Web Scraping**: Automated data collection
- **Data Transformation**: JSONata-based mapping
- **Profile Enrichment**: LinkedIn integration
- **Batch Processing**: Efficient bulk operations

## 📈 Search & Analysis Capabilities

The system provides sophisticated search and analysis capabilities:

1. **Semantic Search**
   - Natural language queries
   - Vector similarity matching
   - Hybrid keyword + vector search
   - Semantic ranking

2. **Advanced Filtering**
   - Industry filtering
   - Company size filtering
   - Project budget filtering
   - Date range filtering
   - Multi-criteria combinations

3. **AI-Powered Analysis**
   - Review summarization
   - Insight extraction
   - Structured data extraction
   - Query-based analysis

4. **Profile Discovery**
   - Company profile search
   - LinkedIn profile matching
   - Reviewer information extraction
   - Contact discovery

## 🔐 Security & Compliance

- **OAuth2 Authentication**: Secure user authentication
- **JWT Tokens**: Token-based authentication
- **Environment Variables**: Secure configuration management
- **HTTPS**: Encrypted communication (production)
- **Input Validation**: Pydantic-based validation

## 📝 Configuration

### Environment Variables

Required environment variables for the API service:

```plaintext
# Database
MONGO_URI=mongodb://root:example@localhost:27017
MONGO_DB_NAME=mydatabase

# Apify (for scraping)
APIFY_API_KEY=your_apify_key

# Azure Cognitive Search
SEARCH_INDEX_NAME=your_index_name
SEARCH_SERVICE_NAME=your_service_name
SEARCH_API_KEY=your_search_key
SEARCH_ENDPOINT=https://your-service.search.windows.net
VECTOR_SEARCH_DIM=1536

# Azure OpenAI
EMBEDDING_ENDPOINT=https://your-endpoint.openai.azure.com
EMBEDDING_KEY=your_embedding_key
EMBEDDING_API_VERSION=2024-02-15-preview
EMBEDDING_MODEL_NAME=text-embedding-3-small
AZURE_COMPLETION_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_KEY=your_completion_key
COMPLETION_API_VERSION=2024-02-15-preview

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id

# Data Transformation
COMPANY_PROFILE_JSON_MAPPING_QUERY=your_jsonata_query
```

## 🧪 Testing Strategy

- **Unit Tests**: Service logic, utilities
- **Integration Tests**: API endpoints, database operations
- **API Tests**: End-to-end API validation
- **Test Data**: Isolated test databases

## 📚 Project Structure

```
lead-meld-ai/
├── app/                          # FastAPI application
│   ├── api/                      # API routes
│   │   ├── background_api.py     # Background task endpoints
│   │   ├── chat_api.py           # Chat/analysis endpoints
│   │   └── user_api.py           # User management endpoints
│   ├── graphql/                  # GraphQL implementation
│   │   ├── schema.py             # GraphQL schema
│   │   └── types.py              # GraphQL types
│   ├── services/                 # Business logic
│   │   ├── chat_service.py       # AI analysis service
│   │   ├── company_profile_service.py  # Profile management
│   │   └── user_service.py       # User management
│   ├── tasks/                    # Background tasks
│   │   ├── company_scraper.py    # Web scraping tasks
│   │   └── linkedin_profile_finder.py  # LinkedIn discovery
│   ├── utils/                    # Utilities
│   │   ├── auth.py               # Authentication utilities
│   │   └── utils.py              # General utilities
│   ├── config.py                 # Configuration
│   ├── db.py                     # Database connection
│   └── main.py                   # FastAPI application entry
├── streamlit/                    # Streamlit frontend
│   └── app.py                    # Main Streamlit application
├── utils/                        # Utility scripts
│   ├── api_tests.py              # API testing utilities
│   ├── data-clearing.py          # Data management
│   ├── rag.ipynb                 # RAG experiments
│   └── token-calculation.py      # Token utilities
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile.Api                # API Dockerfile
├── Dockerfile.Streamlit         # Streamlit Dockerfile
├── requirements-api.txt          # API dependencies
├── requirements-streamlit.txt    # Streamlit dependencies
└── README.md                     # This file
```

## 🎓 Learning Outcomes

This project demonstrates:

1. **Modern Python Web Development**: FastAPI, async/await patterns
2. **GraphQL Implementation**: Flexible API design
3. **Vector Search**: Semantic search with embeddings
4. **AI Integration**: OpenAI for embeddings and analysis
5. **Microservices Architecture**: Service separation and scaling
6. **Cloud-Native Development**: Azure services integration
7. **Data Processing**: Web scraping and data transformation

## 🚦 Getting Started

### Prerequisites

Ensure you have the following installed on your machine:

- [Python 3.9+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started)
- [VS Code](https://code.visualstudio.com/) (optional)
- [Python Extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python) (optional)

### 1. Setting Up the Project

#### Clone the Repository
```bash
git clone <repository-url>
cd lead-meld-ai
```

#### Create and Configure `.env` File

Create a `.env` file in the `app/` directory with the following content:

```plaintext
# Database Configuration
MONGO_URI=mongodb://root:example@localhost:27017
MONGO_DB_NAME=mydatabase

# Apify API (for web scraping)
APIFY_API_KEY=your_apify_api_key

# Azure Cognitive Search
SEARCH_INDEX_NAME=your_index_name
SEARCH_SERVICE_NAME=your_service_name
SEARCH_API_KEY=your_search_api_key
SEARCH_ENDPOINT=https://your-service.search.windows.net
VECTOR_SEARCH_DIM=1536

# Azure OpenAI
EMBEDDING_ENDPOINT=https://your-endpoint.openai.azure.com
EMBEDDING_KEY=your_embedding_key
EMBEDDING_API_VERSION=2024-02-15-preview
EMBEDDING_MODEL_NAME=text-embedding-3-small
AZURE_COMPLETION_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_KEY=your_completion_key
COMPLETION_API_VERSION=2024-02-15-preview

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id

# Data Transformation Query (JSONata)
COMPANY_PROFILE_JSON_MAPPING_QUERY="$map($, function($v, $i, $a) {\n   {\n       \"url\": $v.url,\n       \"summary\": {\n           \"name\": $v.\"summary\".\"name\",\n           \"rating\": $v.\"summary\".\"rating\",\n           \"noOfReviews\": $v.\"summary\".\"noOfReviews\",\n           \"description\": $v.\"summary\".\"description\",\n           \"minProjectSize\": $v.\"summary\".\"minProjectSize\",\n           \"averageHourlyRate\": $v.\"summary\".\"averageHourlyRate\",\n           \"employees\": $v.\"summary\".\"employees\",\n           \"addresses\": $v.\"summary\".\"address\"\n        },\n        \"focus\": $reduce($v.focus, function($acc, $current) {\n            $append($acc, [$current.title] ~> $append($map($current.values, function($v) { $v.name })))\n        }, []),\n        \"serviceProvided\": $v.serviceProvided,\n        \"reviews\": $v.reviews\n   }\n})"
```

Create a `.env` file in the `streamlit/` directory for the frontend:

```plaintext
API_BASE_URL=http://localhost:8000
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
REDIRECT_URL=http://localhost:8501
AUTH_COOKIE_KEY=auth_token
```

### 2. Running Dependencies with Docker Compose

#### Build and Start Services
Run the following commands to start the services using `docker-compose`:

```bash
docker-compose build
docker-compose up -d
```

This will start:
- FastAPI service on port 8000
- Streamlit service on port 8501

### 3. Running FastAPI Locally

#### Install Dependencies
Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements-api.txt
```

#### Run FastAPI
Start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **GraphQL**: http://localhost:8000/graphql
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Running Streamlit Locally

#### Install Dependencies
```bash
pip install -r requirements-streamlit.txt
```

#### Run Streamlit
```bash
streamlit run streamlit/app.py
```

The UI will be available at http://localhost:8501

### 5. Setting Up Debugging in VS Code

#### Configure `launch.json`
1. Open VS Code.
2. Navigate to the `Run and Debug` panel (`Ctrl+Shift+D` or `Cmd+Shift+D` on Mac).
3. Click **"Create a launch.json file"** or the gear icon.
4. Add the following configuration:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI (Uvicorn)",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload"
            ],
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

#### Debug the Application
1. Select **"Python: FastAPI (Uvicorn)"** in the debug configuration dropdown.
2. Press **F5** to start debugging.

## 📄 API Documentation

### Routes

- **GraphQL Endpoint**: [http://localhost:8000/graphql](http://localhost:8000/graphql)
- **FastAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### GraphQL Playground

Use the `/graphql` endpoint for interactive GraphQL queries. The GraphQL schema supports:

- **get_profiles**: Search company profiles with advanced filtering
- **Aggregations**: Get aggregated data by industries, locations, project sizes
- **Type Safety**: Strongly typed queries and responses

### REST API Endpoints

- **POST /api/search/**: Semantic search for reviews and profiles
- **POST /api/analyze/**: AI-powered analysis of review content
- **GET /api/user/usage/**: Get user usage statistics
- **POST /api/user/register/**: Register new user

## 📄 License

[Specify your license here]

## 👥 Contributing

[Contributing guidelines]

---

**Built with ❤️ using Python, FastAPI, Azure, and modern AI technologies**

This project showcases enterprise-level software architecture suitable for intelligent lead generation, semantic search, and AI-powered analysis. It demonstrates proficiency in building modern, scalable systems with cloud-native technologies and AI integration.
