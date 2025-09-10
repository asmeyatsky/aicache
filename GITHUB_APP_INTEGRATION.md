# GitHub App Integration for aicache

## Overview
This document describes the design for integrating aicache with GitHub through a GitHub App, enabling seamless caching and collaboration features within the GitHub ecosystem.

## Key Features
1. **Pull Request Integration**: Cache-based code review suggestions
2. **Issue Commenting**: AI-powered responses to issues
3. **Workflow Automation**: Automated caching and optimization
4. **Repository Analytics**: Performance insights and metrics
5. **Team Collaboration**: Shared cache entries across team members
6. **Security Scanning**: Vulnerability detection using cached patterns

## Architecture Components

### 1. GitHub App Core
```
┌─────────────────────────────────────────────────────────┐
│                    GitHub App                           │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │                Webhook Handler                      │ │
│  │  - Process GitHub webhook events                    │ │
│  │  - Route events to appropriate handlers             │ │
│  │  - Validate webhook signatures                      │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Event Processors                       │ │
│  │  - Handle PR events                                 │ │
│  │  - Handle issue events                              │ │
│  │  - Handle push events                               │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 2. Integration Services
```
┌─────────────────────────────────────────────────────────┐
│                 Integration Services                    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              GitHub API Client                      │ │
│  │  - Communicate with GitHub REST API                 │ │
│  │  - Manage authentication tokens                     │ │
│  │  - Handle rate limiting                             │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              aicache Service                        │ │
│  │  - Communicate with local aicache service           │ │
│  │  - Handle authentication and authorization          │ │
│  │  - Manage cache queries and updates                 │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Collaboration Service                  │ │
│  │  - Handle team presence updates                     │ │
│  │  - Manage shared cache entries                      │ │
│  │  - Real-time notifications                          │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 3. UI Components
```
┌─────────────────────────────────────────────────────────┐
│                    UI Components                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Pull Request Comments                  │ │
│  │  - AI-powered code suggestions                      │ │
│  │  - Cache-based optimization recommendations         │ │
│  │  - Performance insights                             │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Issue Responses                        │ │
│  │  - Automated issue responses based on cache         │ │
│  │  - Context-aware help and documentation             │ │
│  │  - Related issue suggestions                        │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Repository Insights                    │ │
│  │  - Performance metrics dashboard                    │ │
│  │  - Cache utilization reports                        │ │
│  │  - Optimization recommendations                     │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Key Modules

### 1. Webhook Handler (`webhook.js`)
- Receive and validate GitHub webhook events
- Route events to appropriate processors
- Handle authentication and security

### 2. Event Processors (`events/`)
- **Pull Request Processor**: Handle PR events and comments
- **Issue Processor**: Handle issue creation and comments
- **Push Processor**: Handle code pushes and updates

### 3. GitHub API Client (`github.js`)
- Communicate with GitHub REST API
- Manage OAuth tokens and authentication
- Handle rate limiting and pagination

### 4. Cache Service (`cache.js`)
- Communicate with local aicache service
- Handle cache queries and updates
- Manage authentication and authorization

### 5. Comment Generator (`comments.js`)
- Generate AI-powered comments for PRs and issues
- Format responses for GitHub markdown
- Apply caching logic for consistent responses

## Integration Points

### 1. GitHub Webhook Events
- **Pull Request Events**: opened, synchronize, closed
- **Issue Events**: opened, edited, closed
- **Push Events**: code pushes to branches
- **Comment Events**: new comments on PRs and issues

### 2. GitHub API Integration
- **Pull Request Comments**: Add comments to PR diffs
- **Issue Comments**: Respond to issues automatically
- **Status Checks**: Report build and test status
- **Repository Insights**: Generate analytics and reports

### 3. aicache Service Integration
- **Cache Queries**: Retrieve cached responses and data
- **Cache Updates**: Store new information from GitHub
- **Collaboration Features**: Share cache entries with team

## Data Flow

```
1. GitHub Event → 2. Webhook Handler → 3. Event Processor → 4. Cache Query → 5. Response Generation → 6. GitHub API Update

┌──────────────┐    ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ GitHub Event │ →  │ Webhook Handler │ →  │ Event Processor  │ →  │ Cache Query │ →  │ Response Gen.    │ →  │ GitHub API      │
└──────────────┘    └─────────────────┘    └──────────────────┘    └─────────────┘    └──────────────────┘    └─────────────────┘
                              ↓                       ↓                    ↓                   ↓                    ↓
                    ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
                    │ Auth Validation │    │ Context Analysis │    │ API Request │    │ Formatting       │    │ Comment Posting │
                    └─────────────────┘    └──────────────────┘    └─────────────┘    └──────────────────┘    └─────────────────┘
```

## Security Considerations
- Webhook signature validation for request authenticity
- OAuth token management with proper scopes
- Rate limiting to prevent abuse
- Data encryption for sensitive information
- Privacy-preserving design for user data

## Performance Optimization
- Caching of frequently accessed GitHub data
- Asynchronous processing of webhook events
- Connection pooling for API requests
- Efficient database queries for analytics

## Development Setup
1. Create GitHub App registration
2. Configure webhook URL and secret
3. Install required dependencies
4. Set up local development environment
5. Test with GitHub sandbox environment

## Testing Strategy
- Unit tests for individual components
- Integration tests for GitHub API communication
- Webhook event simulation for testing
- End-to-end testing with real repositories

## Deployment
- Deploy as web service (e.g., Heroku, AWS, GCP)
- Configure environment variables for secrets
- Set up monitoring and logging
- Implement CI/CD for automatic deployments

## Application Structure

```
aicache-github-app/
├── src/
│   ├── index.js              # Application entry point
│   ├── webhook.js            # Webhook handler
│   ├── github.js             # GitHub API client
│   ├── cache.js              # aicache service client
│   ├── comments.js           # Comment generation
│   ├── events/               # Event processors
│   │   ├── pullRequest.js    # PR event handling
│   │   ├── issue.js          # Issue event handling
│   │   └── push.js           # Push event handling
│   └── utils/                # Utility functions
│       ├── logger.js         # Logging
│       └── config.js         # Configuration
├── test/                     # Test files
│   ├── webhook.test.js
│   ├── events.test.js
│   └── integration.test.js
├── package.json              # Dependencies and scripts
├── README.md                 # Documentation
└── .env.example              # Environment variables example
```

## Package.json Dependencies

```json
{
  "name": "aicache-github-app",
  "version": "0.1.0",
  "description": "GitHub App for aicache integration",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "test": "jest",
    "test:watch": "jest --watch"
  },
  "dependencies": {
    "express": "^4.18.0",
    "axios": "^0.27.0",
    "dotenv": "^16.0.0",
    "jsonwebtoken": "^8.5.1",
    "crypto": "^1.0.1"
  },
  "devDependencies": {
    "jest": "^28.0.0",
    "nodemon": "^2.0.15",
    "supertest": "^6.2.0"
  }
}
```

## Main Application File (`src/index.js`)

```javascript
const express = require('express');
const dotenv = require('dotenv');
const { handleWebhook } = require('./webhook');
const { logger } = require('./utils/logger');

// Load environment variables
dotenv.config();

// Create Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json({
  verify: (req, res, buf) => {
    // Store raw body for webhook signature verification
    req.rawBody = buf.toString();
  }
}));

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Webhook endpoint
app.post('/webhook', handleWebhook);

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  logger.info(`aicache GitHub App listening on port ${PORT}`);
});

module.exports = app;
```

## Webhook Handler (`src/webhook.js`)

```javascript
const crypto = require('crypto');
const { processPullRequestEvent } = require('./events/pullRequest');
const { processIssueEvent } = require('./events/issue');
const { processPushEvent } = require('./events/push');
const { logger } = require('./utils/logger');

// Verify GitHub webhook signature
function verifySignature(req) {
  const signature = req.headers['x-hub-signature-256'];
  const secret = process.env.GITHUB_WEBHOOK_SECRET;
  
  if (!signature || !secret) {
    return false;
  }
  
  const expectedSignature = 'sha256=' + crypto
    .createHmac('sha256', secret)
    .update(req.rawBody)
    .digest('hex');
    
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

// Handle incoming webhook
async function handleWebhook(req, res) {
  try {
    // Verify webhook signature
    if (!verifySignature(req)) {
      logger.warn('Invalid webhook signature');
      return res.status(401).json({ error: 'Unauthorized' });
    }
    
    // Get event type
    const eventType = req.headers['x-github-event'];
    const payload = req.body;
    
    logger.info(`Received ${eventType} event`, {
      action: payload.action,
      repository: payload.repository?.full_name
    });
    
    // Process based on event type
    switch (eventType) {
      case 'pull_request':
        await processPullRequestEvent(payload);
        break;
      case 'issues':
        await processIssueEvent(payload);
        break;
      case 'push':
        await processPushEvent(payload);
        break;
      default:
        logger.info(`Unhandled event type: ${eventType}`);
    }
    
    res.status(200).json({ status: 'processed' });
  } catch (error) {
    logger.error('Error processing webhook:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

module.exports = { handleWebhook };
```

## GitHub API Client (`src/github.js`)

```javascript
const axios = require('axios');
const { logger } = require('./utils/logger');

class GitHubClient {
  constructor(token) {
    this.token = token;
    this.client = axios.create({
      baseURL: 'https://api.github.com',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'aicache-github-app'
      }
    });
  }
  
  // Add comment to pull request
  async addPullRequestComment(owner, repo, prNumber, body, path, position) {
    try {
      const response = await this.client.post(
        `/repos/${owner}/${repo}/pulls/${prNumber}/comments`,
        {
          body,
          path,
          position
        }
      );
      return response.data;
    } catch (error) {
      logger.error('Error adding PR comment:', error);
      throw error;
    }
  }
  
  // Add comment to issue
  async addIssueComment(owner, repo, issueNumber, body) {
    try {
      const response = await this.client.post(
        `/repos/${owner}/${repo}/issues/${issueNumber}/comments`,
        { body }
      );
      return response.data;
    } catch (error) {
      logger.error('Error adding issue comment:', error);
      throw error;
    }
  }
  
  // Get repository information
  async getRepository(owner, repo) {
    try {
      const response = await this.client.get(`/repos/${owner}/${repo}`);
      return response.data;
    } catch (error) {
      logger.error('Error getting repository:', error);
      throw error;
    }
  }
  
  // Get pull request files
  async getPullRequestFiles(owner, repo, prNumber) {
    try {
      const response = await this.client.get(
        `/repos/${owner}/${repo}/pulls/${prNumber}/files`
      );
      return response.data;
    } catch (error) {
      logger.error('Error getting PR files:', error);
      throw error;
    }
  }
}

module.exports = { GitHubClient };
```

## Cache Service Client (`src/cache.js`)

```javascript
const axios = require('axios');
const { logger } = require('./utils/logger');

class AicacheClient {
  constructor(serviceUrl, apiKey) {
    this.serviceUrl = serviceUrl;
    this.apiKey = apiKey;
    this.client = axios.create({
      baseURL: serviceUrl,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });
  }
  
  // Query cache for code suggestions
  async queryCodeSuggestions(prompt, context) {
    try {
      const response = await this.client.post('/cache/query', {
        prompt,
        context: {
          ...context,
          source: 'github'
        }
      });
      return response.data.response;
    } catch (error) {
      logger.error('Error querying code suggestions:', error);
      return null;
    }
  }
  
  // Store new cache entry
  async storeCacheEntry(prompt, response, context) {
    try {
      const result = await this.client.post('/cache/set', {
        prompt,
        response,
        context
      });
      return result.data.cacheKey;
    } catch (error) {
      logger.error('Error storing cache entry:', error);
      throw error;
    }
  }
  
  // Get repository analytics
  async getRepositoryAnalytics(owner, repo) {
    try {
      const response = await this.client.get(
        `/analytics/repo/${owner}/${repo}`
      );
      return response.data;
    } catch (error) {
      logger.error('Error getting repository analytics:', error);
      return null;
    }
  }
}

module.exports = { AicacheClient };
```

## Comment Generator (`src/comments.js`)

```javascript
const { logger } = require('./utils/logger');

class CommentGenerator {
  constructor(aicacheClient) {
    this.aicacheClient = aicacheClient;
  }
  
  // Generate code review comment
  async generateCodeReviewComment(diff, filename, context) {
    const prompt = `Review this code change and provide suggestions for improvement:
    
File: ${filename}
Code diff:
${diff}

Provide specific, actionable feedback. Focus on:
1. Code quality and best practices
2. Performance optimizations
3. Security considerations
4. Readability improvements`;

    const suggestions = await this.aicacheClient.queryCodeSuggestions(
      prompt,
      context
    );
    
    if (suggestions) {
      return `## Code Review Suggestions

${suggestions}

*Generated by aicache*`;
    }
    
    return null;
  }
  
  // Generate issue response
  async generateIssueResponse(issueTitle, issueBody, context) {
    const prompt = `Respond to this GitHub issue:
    
Title: ${issueTitle}
Body: ${issueBody}

Provide a helpful, concise response that:
1. Acknowledges the issue
2. Provides relevant information or solutions
3. Suggests next steps if needed`;

    const response = await this.aicacheClient.queryCodeSuggestions(
      prompt,
      context
    );
    
    if (response) {
      return `Hello! Thanks for opening this issue.

${response}

*Automated response by aicache*`;
    }
    
    return null;
  }
  
  // Generate repository insights
  async generateRepositoryInsights(analytics, context) {
    const prompt = `Summarize these repository analytics:
    
${JSON.stringify(analytics, null, 2)}

Provide insights on:
1. Performance trends
2. Optimization opportunities
3. Usage patterns`;

    const insights = await this.aicacheClient.queryCodeSuggestions(
      prompt,
      context
    );
    
    if (insights) {
      return `## Repository Insights

${insights}

*Generated by aicache*`;
    }
    
    return null;
  }
}

module.exports = { CommentGenerator };
```