#!/bin/bash
# Simple AI Cache Installation Script

echo "🚀 Installing AI Cache for immediate use..."

# Create a simple symlink approach
mkdir -p ~/.local/bin

# Create aicache wrapper script
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

# Add to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Adding ~/.local/bin to PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "✅ Added to PATH. Restart your shell or run: source ~/.zshrc"
fi

echo "✅ AI Cache installed!"
echo "📍 Command: aicache"
echo "🎯 Test: aicache --help"