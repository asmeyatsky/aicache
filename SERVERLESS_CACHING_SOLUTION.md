# Serverless Caching Solution for aicache

## Overview
This document describes the design for a serverless caching solution for aicache, enabling cloud-native deployment and scaling without managing infrastructure.

## Key Features
1. **Function-as-a-Service Deployment**: Deploy caching logic as serverless functions
2. **Auto-scaling**: Automatically scale based on demand
3. **Pay-per-use**: Cost-effective pricing model
4. **Global Distribution**: Deploy closer to users for low latency
5. **Event-driven Architecture**: Respond to events rather than polling
6. **Stateless Design**: Maintain state in external storage services

## Architecture Components

### 1. Serverless Core
```
┌─────────────────────────────────────────────────────────┐
│                 Serverless Architecture                │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              API Gateway                            │ │
│  │  - Handle HTTP requests                             │ │
│  │  - Route to appropriate functions                   │ │
│  │  - Handle authentication and rate limiting          │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Function Runtime                       │ │
│  │  - Execute caching logic                            │ │
│  │  - Handle cache queries and updates                 │ │
│  │  - Process events                                   │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 2. Storage Services
```
┌─────────────────────────────────────────────────────────┐
│                  Storage Services                       │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Object Storage                         │ │
│  │  - Store cached responses                           │ │
│  │  - Handle large file caching                        │ │
│  │  - Provide CDN integration                          │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Database Service                       │ │
│  │  - Store cache metadata                             │ │
│  │  - Handle indexing and search                       │ │
│  │  - Manage cache statistics                          │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Cache Service                          │ │
│  │  - In-memory caching                                │ │
│  │  - Handle hot data                                  │ │
│  │  - Reduce database load                             │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 3. Event Processing
```
┌─────────────────────────────────────────────────────────┐
│                 Event Processing                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Event Queue                            │ │
│  │  - Queue incoming requests                          │ │
│  │  - Handle backpressure                              │ │
│  │  - Ensure reliable delivery                         │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Event Processor                        │ │
│  │  - Process queued events                            │ │
│  │  - Handle batch operations                          │ │
│  │  - Update cache asynchronously                      │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Key Modules

### 1. API Handler (`api_handler.py`)
- Handle HTTP requests from clients
- Route requests to appropriate functions
- Handle authentication and validation

### 2. Cache Engine (`cache_engine.py`)
- Core caching logic
- Handle cache queries and updates
- Manage cache eviction policies

### 3. Storage Adapter (`storage_adapter.py`)
- Interface with storage services
- Handle object storage operations
- Manage database interactions

### 4. Event Processor (`event_processor.py`)
- Process queued events
- Handle batch operations
- Update cache asynchronously

### 5. Configuration Manager (`config_manager.py`)
- Manage service configuration
- Handle environment variables
- Provide runtime settings

## Integration Points

### 1. Cloud Provider Integration
- **AWS**: Lambda, API Gateway, S3, DynamoDB, ElastiCache
- **GCP**: Cloud Functions, Cloud Run, Cloud Storage, Firestore, Memorystore
- **Azure**: Functions, API Management, Blob Storage, Cosmos DB, Redis Cache

### 2. Client Integration
- **HTTP API**: RESTful interface for clients
- **WebSocket**: Real-time updates and streaming
- **SDKs**: Language-specific client libraries

### 3. Monitoring Integration
- **Logging**: Structured logging for observability
- **Metrics**: Performance and usage metrics
- **Tracing**: Distributed tracing for debugging

### 4. Security Integration
- **Authentication**: JWT, OAuth, API keys
- **Authorization**: Role-based access control
- **Encryption**: Data encryption at rest and in transit

## Data Flow

```
1. Client Request → 2. API Gateway → 3. Function Execution → 4. Cache Lookup → 5. Storage Access → 6. Response

┌───────────────┐    ┌──────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────┐
│ Client Request│ →  │ API Gateway  │ →  │ Function Execution│ →  │ Cache Lookup│ →  │ Storage Access│ →  │ Response │
└───────────────┘    └──────────────┘    └──────────────────┘    └─────────────┘    └──────────────┘    └──────────┘
                              ↓                    ↓                    ↓                   ↓                   ↓
                    ┌──────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────┐
                    │ Auth/Rate Limit│    │ Cache Engine    │    │ Memory Cache│    │ Object Store │    │ Format   │
                    └──────────────┘    └──────────────────┘    └─────────────┘    └──────────────┘    └──────────┘
```

## Security Considerations
- End-to-end encryption for data in transit
- Data encryption at rest in storage services
- Authentication and authorization for API access
- Input validation to prevent injection attacks
- Rate limiting to prevent abuse
- Secure secret management for credentials

## Performance Optimization
- In-memory caching for hot data
- CDN integration for global distribution
- Database indexing for fast queries
- Connection pooling for external services
- Asynchronous processing for non-blocking operations

## Development Setup
1. Choose cloud provider (AWS, GCP, Azure)
2. Set up serverless development environment
3. Configure storage services
4. Install required dependencies
5. Set up local development and testing

## Testing Strategy
- Unit tests for individual functions
- Integration tests for storage services
- Performance benchmarks for scalability
- Security tests for authentication
- End-to-end tests with real deployments

## Deployment
- Deploy using Infrastructure as Code (IaC)
- Configure auto-scaling policies
- Set up monitoring and alerting
- Implement CI/CD for automatic deployments
- Plan for multi-region deployment

## System Architecture

```
aicache-serverless/
├── src/
│   ├── handlers/                  # API handlers
│   │   ├── query_handler.py      # Cache query handler
│   │   ├── store_handler.py      # Cache store handler
│   │   └── health_handler.py     # Health check handler
│   ├── engine/                   # Cache engine
│   │   ├── cache_engine.py       # Core caching logic
│   │   ├── eviction_policy.py    # Cache eviction policies
│   │   └── compression.py        # Data compression
│   ├── storage/                  # Storage adapters
│   │   ├── object_storage.py     # Object storage adapter
│   │   ├── database.py           # Database adapter
│   │   └── memory_cache.py       # In-memory cache
│   ├── events/                   # Event processing
│   │   ├── event_processor.py    # Event processor
│   │   └── queue_adapter.py      # Queue adapter
│   ├── utils/                    # Utility functions
│   │   ├── config.py             # Configuration management
│   │   ├── logger.py             # Logging
│   │   └── security.py           # Security utilities
│   └── main.py                   # Function entry points
├── tests/                        # Test files
│   ├── unit/
│   ├── integration/
│   └── performance/
├── infrastructure/               # IaC definitions
│   ├── terraform/               # Terraform configurations
│   └── cloudformation/          # CloudFormation templates
├── requirements.txt              # Python dependencies
├── serverless.yml               # Serverless framework config
├── README.md                    # Documentation
└── .env.example                 # Environment example
```

## Python Dependencies (`requirements.txt`)

```txt
boto3==1.26.0                   # AWS SDK
google-cloud-storage==2.5.0     # GCP Storage
azure-storage-blob==12.14.0     # Azure Blob Storage
redis==4.3.0                    # Redis client
pymongo==4.2.0                  # MongoDB client
sqlalchemy==1.4.0               # Database ORM
aiosqlite==0.17.0               # Async SQLite
fastapi==0.85.0                 # Web framework
uvicorn==0.18.0                 # ASGI server
pydantic==1.10.0                # Data validation
cryptography==38.0.0            # Security utilities
```

## Serverless Framework Configuration (`serverless.yml`)

```yaml
service: aicache-serverless

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  memorySize: 128
  timeout: 30
  environment:
    STAGE: ${opt:stage, 'dev'}
    LOG_LEVEL: INFO

functions:
  queryCache:
    handler: src/main.query_cache
    events:
      - http:
          path: /cache/query
          method: post
          cors: true
    environment:
      CACHE_TABLE: ${self:service}-${opt:stage, 'dev'}-cache

  storeCache:
    handler: src/main.store_cache
    events:
      - http:
          path: /cache/store
          method: post
          cors: true

  healthCheck:
    handler: src/main.health_check
    events:
      - http:
          path: /health
          method: get
          cors: true

resources:
  Resources:
    CacheTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:service}-${opt:stage, 'dev'}-cache
        AttributeDefinitions:
          - AttributeName: cacheKey
            AttributeType: S
        KeySchema:
          - AttributeName: cacheKey
            KeyType: HASH
        BillingMode: PAY_PER_REQUEST

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: non-linux
```

## Main Handler Module (`src/main.py`)

```python
"""
Main handler module for aicache serverless functions
"""

import json
import logging
from typing import Dict, Any

from .engine.cache_engine import CacheEngine
from .storage.database import DatabaseAdapter
from .utils.config import get_config
from .utils.logger import setup_logger

# Global cache engine instance
cache_engine = None
logger = None

def initialize():
    """Initialize the cache engine"""
    global cache_engine, logger
    
    if cache_engine is None:
        # Setup logging
        logger = setup_logger(__name__)
        
        # Get configuration
        config = get_config()
        
        # Initialize database adapter
        db_adapter = DatabaseAdapter(
            table_name=config.get('CACHE_TABLE', 'aicache-dev-cache')
        )
        
        # Initialize cache engine
        cache_engine = CacheEngine(
            storage_adapter=db_adapter,
            config=config
        )
        
        logger.info("Cache engine initialized")

def query_cache(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle cache query requests"""
    try:
        # Initialize if needed
        initialize()
        
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
            
        prompt = body.get('prompt')
        context_data = body.get('context', {})
        
        if not prompt:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing prompt parameter'
                })
            }
        
        # Query cache
        result = cache_engine.query(prompt, context_data)
        
        if result:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'prompt': result['prompt'],
                    'response': result['response'],
                    'context': result['context'],
                    'timestamp': result['timestamp'],
                    'cacheType': result.get('cacheType', 'exact')
                })
            }
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Cache entry not found'
                })
            }
            
    except Exception as e:
        logger.error(f"Error querying cache: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }

def store_cache(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle cache store requests"""
    try:
        # Initialize if needed
        initialize()
        
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
            
        prompt = body.get('prompt')
        response = body.get('response')
        context_data = body.get('context', {})
        
        if not prompt or not response:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required parameters (prompt, response)'
                })
            }
        
        # Store in cache
        cache_key = cache_engine.store(prompt, response, context_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'cacheKey': cache_key,
                'message': 'Cache entry stored successfully'
            })
        }
            
    except Exception as e:
        logger.error(f"Error storing cache: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }

def health_check(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle health check requests"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'healthy',
            'timestamp': __import__('time').time(),
            'service': 'aicache-serverless'
        })
    }
```

## Cache Engine (`src/engine/cache_engine.py`)

```python
"""
Cache engine for aicache serverless
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from ..storage.memory_cache import MemoryCache
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class CacheEntry:
    """Represents a cache entry"""
    cache_key: str
    prompt: str
    response: str
    context: Dict[str, Any]
    timestamp: float
    access_count: int = 0
    last_accessed: float = 0

class CacheEngine:
    """Main cache engine implementation"""
    
    def __init__(self, storage_adapter, config: Dict[str, Any]):
        self.storage_adapter = storage_adapter
        self.config = config
        self.memory_cache = MemoryCache(
            max_size=config.get('MEMORY_CACHE_SIZE', 1000)
        )
        
    def _generate_cache_key(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate cache key from prompt and context"""
        hasher = hashlib.sha256()
        hasher.update(prompt.encode('utf-8'))
        
        # Include key context elements
        key_context = {k: v for k, v in context.items() 
                      if k in ['language', 'framework', 'project']}
        if key_context:
            hasher.update(json.dumps(key_context, sort_keys=True).encode('utf-8'))
            
        return hasher.hexdigest()
        
    def query(self, prompt: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Query cache for entry"""
        cache_key = self._generate_cache_key(prompt, context)
        
        # Check memory cache first
        entry = self.memory_cache.get(cache_key)
        if entry:
            logger.debug(f"Cache hit in memory: {cache_key[:8]}...")
            entry['access_count'] += 1
            entry['last_accessed'] = time.time()
            self.memory_cache.put(cache_key, entry)
            return entry
            
        # Check persistent storage
        try:
            entry = self.storage_adapter.get(cache_key)
            if entry:
                logger.debug(f"Cache hit in storage: {cache_key[:8]}...")
                entry['access_count'] += 1
                entry['last_accessed'] = time.time()
                # Update in storage
                self.storage_adapter.put(cache_key, entry)
                # Also cache in memory
                self.memory_cache.put(cache_key, entry)
                return entry
            else:
                logger.debug(f"Cache miss: {cache_key[:8]}...")
                return None
        except Exception as e:
            logger.error(f"Error querying storage: {e}")
            return None
            
    def store(self, prompt: str, response: str, context: Dict[str, Any]) -> str:
        """Store entry in cache"""
        cache_key = self._generate_cache_key(prompt, context)
        
        entry = {
            'cache_key': cache_key,
            'prompt': prompt,
            'response': response,
            'context': context,
            'timestamp': time.time(),
            'access_count': 0,
            'last_accessed': time.time()
        }
        
        # Store in both memory and persistent storage
        try:
            self.memory_cache.put(cache_key, entry)
            self.storage_adapter.put(cache_key, entry)
            logger.info(f"Cache entry stored: {cache_key[:8]}...")
        except Exception as e:
            logger.error(f"Error storing cache entry: {e}")
            
        return cache_key
        
    def delete(self, cache_key: str) -> bool:
        """Delete entry from cache"""
        try:
            self.memory_cache.delete(cache_key)
            self.storage_adapter.delete(cache_key)
            logger.info(f"Cache entry deleted: {cache_key[:8]}...")
            return True
        except Exception as e:
            logger.error(f"Error deleting cache entry: {e}")
            return False
            
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            storage_stats = self.storage_adapter.get_stats()
            return {
                'memory_cache_size': self.memory_cache.size(),
                'storage_stats': storage_stats
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
```

## Storage Adapter (`src/storage/database.py`)

```python
"""
Database adapter for aicache serverless
"""

import os
import boto3
from typing import Dict, Any, Optional
from boto3.dynamodb.conditions import Key

from ..utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseAdapter:
    """Database adapter for cache storage"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get entry from database"""
        try:
            response = self.table.get_item(
                Key={'cacheKey': cache_key}
            )
            
            if 'Item' in response:
                item = response['Item']
                # Convert DynamoDB types back to Python types
                return {
                    'cache_key': item['cacheKey'],
                    'prompt': item['prompt'],
                    'response': item['response'],
                    'context': item['context'],
                    'timestamp': float(item['timestamp']),
                    'access_count': int(item.get('accessCount', 0)),
                    'last_accessed': float(item.get('lastAccessed', item['timestamp']))
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting item from DynamoDB: {e}")
            return None
            
    def put(self, cache_key: str, entry: Dict[str, Any]) -> bool:
        """Put entry in database"""
        try:
            self.table.put_item(
                Item={
                    'cacheKey': entry['cache_key'],
                    'prompt': entry['prompt'],
                    'response': entry['response'],
                    'context': entry['context'],
                    'timestamp': entry['timestamp'],
                    'accessCount': entry.get('access_count', 0),
                    'lastAccessed': entry.get('last_accessed', entry['timestamp'])
                }
            )
            return True
        except Exception as e:
            logger.error(f"Error putting item in DynamoDB: {e}")
            return False
            
    def delete(self, cache_key: str) -> bool:
        """Delete entry from database"""
        try:
            self.table.delete_item(
                Key={'cacheKey': cache_key}
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting item from DynamoDB: {e}")
            return False
            
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            # Get approximate item count
            response = self.table.scan(
                Select='COUNT'
            )
            return {
                'item_count': response['Count'],
                'scanned_count': response['ScannedCount']
            }
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
```

## Memory Cache (`src/storage/memory_cache.py`)

```python
"""
In-memory cache for aicache serverless
"""

import time
from typing import Dict, Any, Optional
from collections import OrderedDict

from ..utils.logger import get_logger

logger = get_logger(__name__)

class MemoryCache:
    """LRU-based in-memory cache"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get entry from cache"""
        if key in self.cache:
            # Move to end (most recently used)
            entry = self.cache.pop(key)
            self.cache[key] = entry
            return entry
        return None
        
    def put(self, key: str, entry: Dict[str, Any]):
        """Put entry in cache"""
        # Remove if already exists
        if key in self.cache:
            self.cache.pop(key)
            
        # Check if we need to evict
        if len(self.cache) >= self.max_size:
            # Remove least recently used (first item)
            self.cache.popitem(last=False)
            
        # Add new entry
        self.cache[key] = entry
        
    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        if key in self.cache:
            self.cache.pop(key)
            return True
        return False
        
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)
        
    def clear(self):
        """Clear cache"""
        self.cache.clear()
```

## Configuration Manager (`src/utils/config.py`)

```python
"""
Configuration manager for aicache serverless
"""

import os
from typing import Dict, Any

def get_config() -> Dict[str, Any]:
    """Get configuration from environment variables"""
    return {
        # Server configuration
        'STAGE': os.environ.get('STAGE', 'dev'),
        'LOG_LEVEL': os.environ.get('LOG_LEVEL', 'INFO'),
        
        # Cache configuration
        'MEMORY_CACHE_SIZE': int(os.environ.get('MEMORY_CACHE_SIZE', '1000')),
        'CACHE_TTL': int(os.environ.get('CACHE_TTL', '3600')),  # 1 hour
        
        # Storage configuration
        'CACHE_TABLE': os.environ.get('CACHE_TABLE', 'aicache-dev-cache'),
        
        # Performance configuration
        'TIMEOUT': int(os.environ.get('TIMEOUT', '30')),
        'MEMORY_SIZE': int(os.environ.get('MEMORY_SIZE', '128'))
    }
```

## Logger Utility (`src/utils/logger.py`)

```python
"""
Logger utility for aicache serverless
"""

import logging
import os
import json
from typing import Any

def setup_logger(name: str) -> logging.Logger:
    """Setup structured logger"""
    logger = logging.getLogger(name)
    logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))
    
    # Prevent adding multiple handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return setup_logger(name)
```

## Infrastructure as Code (Terraform)

### Main Terraform Configuration (`infrastructure/terraform/main.tf`)

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "stage" {
  description = "Deployment stage"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "memory_size" {
  description = "Lambda function memory size"
  type        = number
  default     = 128
}

variable "timeout" {
  description = "Lambda function timeout"
  type        = number
  default     = 30
}

# DynamoDB table for cache storage
resource "aws_dynamodb_table" "cache_table" {
  name         = "aicache-${var.stage}-cache"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "cacheKey"

  attribute {
    name = "cacheKey"
    type = "S"
  }

  tags = {
    Name  = "aicache-cache-table"
    Stage = var.stage
  }
}

# IAM role for Lambda functions
resource "aws_iam_role" "lambda_role" {
  name = "aicache-${var.stage}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for Lambda functions
resource "aws_iam_role_policy" "lambda_policy" {
  name = "aicache-${var.stage}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.cache_table.arn
      }
    ]
  })
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "cache_api" {
  name = "aicache-${var.stage}-api"
  description = "aicache serverless API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "cache_deployment" {
  depends_on = [
    aws_api_gateway_integration.query_integration,
    aws_api_gateway_integration.store_integration,
    aws_api_gateway_integration.health_integration
  ]

  rest_api_id = aws_api_gateway_rest_api.cache_api.id
  stage_name  = var.stage
}

# Output values
output "api_url" {
  value = aws_api_gateway_deployment.cache_deployment.invoke_url
}

output "cache_table_name" {
  value = aws_dynamodb_table.cache_table.name
}
```

## Key Features Implementation

### 1. Auto-scaling
- AWS Lambda automatically scales based on request volume
- DynamoDB scales automatically with pay-per-request billing
- API Gateway handles traffic spikes

### 2. Cost Optimization
- Pay only for actual usage (requests, compute time, storage)
- Memory cache reduces database operations
- Efficient data compression

### 3. Global Distribution
- Deploy to multiple AWS regions
- Use CloudFront CDN for global content delivery
- Route users to nearest region

### 4. Event-driven Architecture
- Trigger functions based on events
- Process requests asynchronously when possible
- Batch operations for efficiency

### 5. Security
- IAM roles for secure access
- HTTPS encryption for all communications
- Input validation to prevent injection attacks

### 6. Monitoring
- CloudWatch logs for debugging
- CloudWatch metrics for performance monitoring
- X-Ray tracing for request flow analysis

## Usage Examples

### 1. Deploy the Service
```bash
# Install Serverless Framework
npm install -g serverless

# Deploy to AWS
serverless deploy --stage prod
```

### 2. Query Cache
```bash
# Using curl
curl -X POST https://your-api-gateway-url/prod/cache/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "How to implement authentication in Flask?",
    "context": {
      "language": "python",
      "framework": "flask"
    }
  }'
```

### 3. Store in Cache
```bash
# Using curl
curl -X POST https://your-api-gateway-url/prod/cache/store \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "How to implement authentication in Flask?",
    "response": "Use Flask-Login extension...",
    "context": {
      "language": "python",
      "framework": "flask"
    }
  }'
```

### 4. Health Check
```bash
# Using curl
curl https://your-api-gateway-url/prod/health
```

## Multi-cloud Support

### Google Cloud Platform
- Use Cloud Functions instead of Lambda
- Use Cloud Storage instead of S3
- Use Firestore instead of DynamoDB
- Use Cloud CDN for content delivery

### Microsoft Azure
- Use Azure Functions instead of Lambda
- Use Azure Blob Storage instead of S3
- Use Azure Cosmos DB instead of DynamoDB
- Use Azure CDN for content delivery

## CI/CD Integration

### GitHub Actions
```yaml
name: Deploy Serverless
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '14'
      - run: npm install -g serverless
      - run: npm install
      - run: serverless deploy --stage prod
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

This serverless implementation provides a scalable, cost-effective caching solution that can handle varying loads without infrastructure management.