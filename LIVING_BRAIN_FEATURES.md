# Living Brain Feature Documentation

## Overview
The Living Brain functionality enables aicache to maintain persistent context across different AI providers (Claude, Gemini, Qwen) and persist that context throughout the lifetime of working on an application. It acts as a "living brain" of the solution that remembers and connects knowledge from all AI interactions.

## Key Features

### 1. Cross-AI Session Continuity
- **Persistent Sessions**: Start a session for a project that persists across AI provider switches
- **Provider Tracking**: Automatically tracks which AI providers were used in each session
- **Context Preservation**: Maintains conversation history and context when switching between providers

### 2. Cross-AI Concept Storage
- **Unified Knowledge Base**: Concepts learned from Claude, Gemini, and Qwen are stored in a unified system
- **Provider Attribution**: Each concept remembers which AI provider it came from
- **Importance Scoring**: Automatically assigns importance scores to concepts based on relevance

### 3. Semantic Search Across Providers
- **Cross-Provider Search**: Find concepts regardless of which AI provider generated them
- **Contextual Relevance**: Uses semantic search to find related concepts across providers
- **Tagging System**: Automatically tags concepts with relevant metadata

### 4. CLI Integration
- `aicache brain init <project-id>`: Initialize a new brain session for a project
- `aicache brain switch <provider>`: Switch AI providers while maintaining context
- `aicache brain concepts add`: Add a concept manually to the brain
- `aicache brain concepts search <query>`: Search for relevant concepts across providers
- `aicache brain stats`: View project statistics and AI provider usage

### 5. Automatic Context Capture
- **Cache Integration**: Every cached response automatically becomes a concept in the brain
- **Q&A Storage**: Both questions and answers are preserved for future reference
- **Intelligent Filtering**: Distinguishes between cache hits (high importance) and misses (lower importance)

## Use Case: Token Limit Workaround

The Living Brain solves your specific use case:

1. **Start Session**: Initialize a brain session for your application project
   ```bash
   aicache brain init my-application
   ```

2. **Work with Claude**: Use Claude as your primary AI assistant
   ```bash
   claude "How do I implement auth in my Django app?"
   ```

3. **Token Exhaustion**: When Claude tokens run out, switch to Gemini
   ```bash
   aicache brain switch gemini
   gemini "Continue helping with Django auth - here's what Claude suggested..."
   ```

4. **Context Continuity**: The brain maintains context from Claude, so Gemini continues with the same knowledge.

5. **Qwen Integration**: Later switch to Qwen with full context preservation
   ```bash
   aicache brain switch qwen
   qwen "How do I optimize the auth system we designed?"
   ```

6. **Persistent Knowledge**: All knowledge from all providers is preserved in the living brain for the duration of the project.

## Technical Implementation

### Core Components
- `BrainSession`: Manages continuous working sessions per project
- `ProjectContext`: Maintains persistent project-specific knowledge
- `CrossAIConcept`: Stores knowledge that spans multiple AI providers
- `PersistentContext`: Maintains context across AI switches
- `BrainStateManager`: Manages the persistent state of the brain system

### Database Schema
- SQLite database stores sessions, projects, and cross-AI concepts
- Automatic indexing for fast retrieval
- Pruning of inactive sessions to manage growth

### Integration Points
- Enhanced cache get/set operations automatically add to brain
- Semantic cache integration for intelligent concept retrieval
- Behavioral analysis system augmentation

## Benefits

1. **Context Continuity**: Never lose context when switching between AI providers
2. **Knowledge Accumulation**: Build a persistent knowledge base across all interactions
3. **Provider Flexibility**: Seamlessly switch between Claude, Gemini, Qwen as needed
4. **Growth Management**: Intelligent pruning prevents unbounded growth
5. **Project Focus**: Maintain project-specific context throughout development lifecycle

## Architecture Flow

```
AI Interaction → Cache Operation → Brain Integration → Persistent Storage
      ↓              ↓                  ↓                    ↓
  Provider A    Cache Hit/Miss    Concept Storage    Cross-AI Knowledge
  Provider B    Context Enriched  Importance Scoring  Semantic Search
  Provider C    ...               ...                Unified View
```

The Living Brain ensures that your AI-assisted development workflow is continuous, persistent, and grows more valuable over time as it accumulates knowledge from multiple AI providers.