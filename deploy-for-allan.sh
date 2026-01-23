#!/bin/bash
# AI Cache Installation Script for YOU
# Ready to start saving money across ALL your projects

echo "🚀 Installing AI Cache for Allan..."

# Create wrappers for your detected tools
mkdir -p ~/.local/bin

# Create claude wrapper
cat > ~/.local/bin/claude << 'EOF'
#!/bin/bash
cd /Users/allansmeyatsky/aicache
source venv/bin/activate
python3 -c "
import sys
sys.path.insert(0, 'src')
from aicache.core.cache import CoreCache
from aicache.plugins.base import CLIWrapper
import asyncio

class ClaudeWrapper(CLIWrapper):
    def get_cli_name(self):
        return 'claude'
    
    def parse_arguments(self, args):
        prompt = ''
        context = {}
        i = 0
        while i < len(args):
            if args[i] in ['-p', '--prompt']:
                if i + 1 < len(args):
                    prompt = args[i + 1]
                    break
            elif args[i] in ['-m', '--model']:
                if i + 1 < len(args):
                    context['model'] = args[i + 1]
            i += 1
        
        return prompt, context
    
    async def execute_cli(self, args):
        return await self._run_cli_command('claude', args)

# Execute original CLI with caching
wrapper = ClaudeWrapper()
prompt, context = wrapper.parse_arguments(sys.argv[1:])

cache = CoreCache()
cached_response = cache.get(prompt, context)

if cached_response:
    print('--- (aicache HIT) ---')
    print(cached_response)
else:
    print('--- (aicache MISS) ---')
    result = asyncio.run(wrapper.execute_cli(sys.argv[1:]))
    if result[1] == 0:  # Success
        cache.set(prompt, result[0], context)
        print(result[0])
    else:
        print(result[2], file=sys.stderr)
        sys.exit(result[1])
" "$@"
EOF

# Create openai wrapper
cat > ~/.local/bin/openai << 'EOF'
#!/bin/bash
cd /Users/allansmeyatsky/aicache
source venv/bin/activate
python3 -c "
import sys
sys.path.insert(0, 'src')
from aicache.core.cache import CoreCache
from aicache.plugins.base import CLIWrapper
import asyncio

class OpenAIWrapper(CLIWrapper):
    def get_cli_name(self):
        return 'openai'
    
    def parse_arguments(self, args):
        prompt = ''
        context = {}
        i = 0
        while i < len(args):
            if args[i] in ['-p', '--prompt']:
                if i + 1 < len(args):
                    prompt = args[i + 1]
                    break
            elif args[i] in ['-m', '--model']:
                if i + 1 < len(args):
                    context['model'] = args[i + 1]
            i += 1
        
        return prompt, context
    
    async def execute_cli(self, args):
        return await self._run_cli_command('openai', args)

# Execute original CLI with caching
wrapper = OpenAIWrapper()
prompt, context = wrapper.parse_arguments(sys.argv[1:])

cache = CoreCache()
cached_response = cache.get(prompt, context)

if cached_response:
    print('--- (aicache HIT) ---')
    print(cached_response)
else:
    print('--- (aicache MISS) ---')
    result = asyncio.run(wrapper.execute_cli(sys.argv[1:]))
    if result[1] == 0:  # Success
        cache.set(prompt, result[0], context)
        print(result[0])
    else:
        print(result[2], file=sys.stderr)
        sys.exit(result[1])
" "$@"
EOF

# Create gemini wrapper
cat > ~/.local/bin/gemini << 'EOF'
#!/bin/bash
cd /Users/allansmeyatsky/aicache
source venv/bin/activate
python3 -c "
import sys
sys.path.insert(0, 'src')
from aicache.core.cache import CoreCache
from aicache.plugins.base import CLIWrapper
import asyncio

class GeminiWrapper(CLIWrapper):
    def get_cli_name(self):
        return 'gemini'
    
    def parse_arguments(self, args):
        prompt = ''
        context = {}
        i = 0
        while i < len(args):
            if args[i] in ['-p', '--prompt']:
                if i + 1 < len(args):
                    prompt = args[i + 1]
                    break
            elif args[i] in ['-m', '--model']:
                if i + 1 < len(args):
                    context['model'] = args[i + 1]
            i += 1
        
        return prompt, context
    
    async def execute_cli(self, args):
        return await self._run_cli_command('gemini', args)

# Execute original CLI with caching
wrapper = GeminiWrapper()
prompt, context = wrapper.parse_arguments(sys.argv[1:])

cache = CoreCache()
cached_response = cache.get(prompt, context)

if cached_response:
    print('--- (aicache HIT) ---')
    print(cached_response)
else:
    print('--- (aicache MISS) ---')
    result = asyncio.run(wrapper.execute_cli(sys.argv[1:]))
    if result[1] == 0:  # Success
        cache.set(prompt, result[0], context)
        print(result[0])
    else:
        print(result[2], file=sys.stderr)
        sys.exit(result[1])
" "$@"
EOF

# Make them executable
chmod +x ~/.local/bin/claude ~/.local/bin/openai ~/.local/bin/gemini

# Create main aicache command
cat > ~/.local/bin/aicache << 'EOF'
#!/bin/bash
cd /Users/allansmeyatsky/aicache
source venv/bin/activate
python3 -c "
import sys
sys.path.insert(0, 'src')
from aicache.modern_cli import main
main()
" "$@"
EOF

chmod +x ~/.local/bin/aicache

echo "✅ Created AI CLI tool wrappers:"
echo "   📝 claude  - Anthropic Claude"
echo "   🤖 openai  - OpenAI GPT"
echo "   💎 gemini  - Google Gemini"
echo ""
echo "✅ Main aicache command created"
echo ""

# Check PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Adding ~/.local/bin to your PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "✅ Added to PATH. Please restart your shell or run: source ~/.zshrc"
fi

echo ""
echo "🎯 READY TO START SAVING MONEY!"
echo ""
echo "💡 Test it now:"
echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
echo "   claude --prompt 'what is python?'"
echo "   openai --prompt 'same question'  ← CACHE HIT!"
echo ""
echo "📊 Track your savings:"
echo "   aicache status"
echo ""
echo "🍔 Your dog food budget thanks you! 💰"