# 🤝 Contributing to AI Cache

We want your help! AI Cache is a community-driven project focused on saving developers money on AI costs. Every contribution helps - whether it's a bug fix, new feature, documentation, or sharing your experience.

## 🚀 Quick Ways to Contribute

### 🎯 Easy First Contributions (Perfect for getting started!)

#### 1. Add New AI Provider Adapters
**What**: Add support for AI tools not yet supported
**Impact**: Immediately helps users of that tool
**Difficulty**: Easy

**Example Implementation:**
```python
# src/aicache/adapters/mistral_adapter.py
from .base import CLIWrapper

class MistralWrapper(CLIWrapper):
    def get_cli_name() -> str:
        return "mistral"
    
    def parse_arguments(self, args: list) -> tuple[str, dict]:
        # Extract prompt from mistral CLI arguments
        return prompt_content, context
    
    async def execute_cli(self, args: list) -> tuple[str, int, str]:
        # Execute mistral CLI and capture output
        return await self._run_cli_command("mistral", args)
```

**Providers We Need:**
- [ ] **Mistral CLI** (`mistral`) - Growing popularity
- [ ] **Llama CLI** (`llama`) - Local LLMs  
- [ ] **Groq CLI** (`groq`) - Fast inference
- [ ] **Cohere CLI** (`cohere`) - Enterprise AI
- [ ] **Perplexity CLI** (`perplexity`) - Search + AI

#### 2. Improve Documentation
**What**: Add examples, tutorials, and clarifications
**Impact**: Makes the project easier to use
**Difficulty**: Easy

**Ideas:**
- [ ] Add more examples to README
- [ ] Create tutorial for custom wrapper creation
- [ ] Document TOON analytics with real examples
- [ ] Add troubleshooting guide

#### 3. Add Integration Tests
**What**: Ensure our features work correctly
**Impact**: Prevents regressions and builds confidence
**Difficulty**: Easy-Medium

**Example Test:**
```python
# tests/test_mistral_adapter.py
import pytest
from aicache.adapters.mistral_adapter import MistralWrapper

def test_mistral_wrapper_basic():
    wrapper = MistralWrapper()
    assert wrapper.get_cli_name() == "mistral"
    
    prompt, context = wrapper.parse_arguments(["--prompt", "hello world"])
    assert prompt == "hello world"
```

### 🔧 Medium Contributions

#### 4. Storage Backend Adapters
**What**: Add new storage options beyond file-based
**Impact**: Better performance and scalability
**Difficulty**: Medium

**Backends We Need:**
- [ ] **Redis Adapter** - Fast in-memory caching
- [ ] **PostgreSQL Adapter** - Persistent and scalable
- [ ] **SQLite Adapter** - Lightweight file-based DB
- [ ] **Memcached Adapter** - Distributed caching

#### 5. Semantic Matching Improvements
**What**: Enhance our semantic caching capabilities
**Impact**: Better hit rates for similar queries
**Difficulty**: Medium

**Ideas:**
- [ ] Better embedding models
- [ ] Hybrid exact + semantic matching
- [ ] Context-aware similarity
- [ ] Domain-specific matching

### 🚀 Advanced Contributions

#### 6. Web Dashboard
**What**: Visual analytics and management interface
**Impact**: Much better user experience
**Difficulty**: Hard

**Features to Build:**
- [ ] Real-time savings dashboard
- [ ] Cache configuration UI
- [ ] TOON analytics visualizations
- [ ] Export tools and reports

#### 7. Editor Integrations
**What**: Integrate with popular code editors
**Impact**: Seamless developer experience
**Difficulty**: Hard

**Editors:**
- [ ] **VS Code Extension** (started, needs completion)
- [ ] **Neovim Plugin** (started, needs completion)
- [ ] **JetBrains IDEs** (started, needs completion)
- [ ] **Emacs/Vim plugins**

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Git
- Preferred AI CLI tools (for testing)

### Quick Setup
```bash
# Clone and setup
git clone https://github.com/asmeyatsky/aicache.git
cd aicache
make setup

# Activate environment
source venv/bin/activate

# Run tests
make test

# Install pre-commit hooks
pre-commit install
```

### Development Workflow
1. **Create Branch**: `git checkout -b feature/your-feature-name`
2. **Make Changes**: Write code, add tests, update docs
3. **Run Tests**: `make test` (ensure everything passes)
4. **Commit**: Follow conventional commit format
5. **Push**: `git push origin feature/your-feature-name`
6. **PR**: Open pull request with detailed description

### Code Style
- **Python**: Follow PEP 8, use `black` for formatting
- **Commit Messages**: Use conventional commits (`feat:`, `fix:`, `docs:`, etc.)
- **Tests**: Write tests for new features, maintain >85% coverage
- **Docs**: Update relevant documentation

### Architecture Guidelines
- **Domain First**: Business logic in `domain/`
- **Ports**: Define interfaces in `domain/ports.py`
- **Adapters**: Implement external integrations in `infrastructure/`
- **Tests**: Mirror package structure in `tests/`

## 🎯 Specific Areas Needing Help

### High Priority
1. **Windows Support**: Currently limited testing on Windows
2. **Performance**: Optimize for large cache sizes
3. **Error Handling**: Better error messages and recovery
4. **Configuration**: More flexible config options

### Medium Priority
1. **Monitoring**: Performance metrics and health checks
2. **Security**: PII detection and data sanitization
3. **Internationalization**: Multi-language support
4. **Accessibility**: Better CLI accessibility

### Low Priority
1. **Plugins**: Plugin system for third-party extensions
2. **Themes**: Customizable CLI themes
3. **Sounds**: Audio feedback for cache events
4. **Integrations**: More third-party tool integrations

## 🐛 Reporting Issues

Found a bug? We want to know!

### Good Bug Reports Include:
- **Clear Description**: What happened and what you expected
- **Steps to Reproduce**: Exact commands to reproduce
- **Environment**: OS, Python version, AI tools used
- **Logs**: Any error messages or output
- **Minimal Example**: Smallest code that reproduces the issue

### Bug Report Template
```markdown
## Description
Brief description of the issue

## Steps to Reproduce
1. Run `aicache init`
2. Execute `claude "test prompt"`
3. Observe X

## Expected Behavior
What should have happened

## Actual Behavior
What actually happened

## Environment
- OS: macOS 14.0
- Python: 3.11.0
- AI Cache: v0.1.0
- AI Tools: claude-cli 1.2.0

## Additional Context
Any other relevant information
```

## 💡 Feature Requests

Have an idea? We'd love to hear it!

### Good Feature Requests Include:
- **Problem Statement**: What problem does this solve?
- **Proposed Solution**: How do you envision it working?
- **Use Cases**: Specific scenarios where this helps
- **Alternatives**: What have you tried instead?

### Feature Request Template
```markdown
## Problem Statement
Current problem or limitation

## Proposed Solution
Description of desired feature

## Use Cases
1. When I do X, I need Y
2. For scenario Z, this would help

## Alternatives Considered
What other approaches have you tried?

## Additional Context
Any relevant information or examples
```

## 📈 Recognition for Contributors

We believe in recognizing contributions!

### Contribution Types
- 🐛 **Bug Hunter**: Finds and reports important bugs
- 📝 **Documentation Hero**: Improves docs and examples  
- 🔧 **Code Contributor**: Submits quality code changes
- 🎨 **Design Expert**: Improves UX and visual design
- 🌟 **Community Leader**: Helps others and provides feedback

### Recognition
- **Contributors List**: Acknowledged in README
- **Release Notes**: Called out in release announcements
- **Community Badges**: Special roles in our Discord
- **Swag**: Stickers, t-shirts for top contributors
- **References**: LinkedIn recommendations for significant contributions

## 💬 Community

### Ways to Connect
- **GitHub**: Issues, PRs, Discussions
- **Discord**: [Invite Link] (coming soon)
- **Reddit**: r/AICache (coming soon)
- **Twitter**: @aicache_dev (coming soon)

### Community Guidelines
- **Be Respectful**: Treat everyone with kindness
- **Be Constructive**: Focus on what helps the project
- **Be Inclusive**: Welcome contributors of all backgrounds
- **Be Patient**: Remember everyone is volunteering

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Every contribution helps AI Cache save developers money and time. Whether you're fixing a typo or adding a major feature, you're making a real difference.

**Ready to contribute? Check out our [Good First Issues](https://github.com/asmeyatsky/aicache/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) to get started!** 🚀

---

*Building the future of AI cost optimization, together.* 💰🚀