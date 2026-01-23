#!/bin/bash
# AI Cache Quick Install Script
# One-command setup for AI Cache

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    print_success "Python $PYTHON_VERSION detected ✓"
else
    print_error "Python $PYTHON_VERSION detected. Python $REQUIRED_VERSION+ is required."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is required but not installed. Please install pip3 first."
    exit 1
fi

# Welcome message
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                        🚀 AI Cache Installer                          ║"
echo "║               Stop paying for duplicate AI queries                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Ask for installation type
echo ""
echo "Choose your installation type:"
echo "1) Basic - File-based caching (recommended for getting started)"
echo "2) Semantic - With AI-powered semantic matching"
echo "3) Full - All features enabled"
echo ""

read -p "Enter choice [1-3] (default: 1): " INSTALL_TYPE
INSTALL_TYPE=${INSTALL_TYPE:-1}

case $INSTALL_TYPE in
    1)
        PACKAGE="aicache[basic]"
        print_status "Installing AI Cache Basic..."
        ;;
    2)
        PACKAGE="aicache[semantic]"
        print_status "Installing AI Cache with Semantic features..."
        ;;
    3)
        PACKAGE="aicache[full]"
        print_status "Installing AI Cache Full version..."
        ;;
    *)
        print_error "Invalid choice. Installing basic version."
        PACKAGE="aicache[basic]"
        ;;
esac

# Install AI Cache
print_status "Installing $PACKAGE..."
pip3 install --user --upgrade "$PACKAGE"

if [ $? -eq 0 ]; then
    print_success "AI Cache installed successfully! ✓"
else
    print_error "Failed to install AI Cache. Please check the error above."
    exit 1
fi

# Check if installation worked
if command -v aicache &> /dev/null; then
    print_success "AI Cache CLI is available! ✓"
else
    print_warning "AI Cache was installed but not found in PATH."
    print_status "Adding to local bin directory..."
    
    # Create local bin if it doesn't exist
    mkdir -p ~/.local/bin
    
    # Get the location of aicache
    AICACHE_PATH=$(python3 -c "import aicache; import os; print(os.path.dirname(aicache.__file__))")
    
    # Create symlink
    if [ -f "$AICACHE_PATH/modern_cli.py" ]; then
        ln -sf "$AICACHE_PATH/modern_cli.py" ~/.local/bin/aicache
        chmod +x ~/.local/bin/aicache
        print_success "Created symlink in ~/.local/bin/aicache"
    else
        print_error "Could not find AI Cache executable."
    fi
fi

# Update PATH if needed
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    print_warning "~/.local/bin is not in your PATH."
    echo ""
    echo "Add this to your ~/.bashrc, ~/.zshrc, or shell config:"
    echo -e "${GREEN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo ""
    echo "Then restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
fi

# Detect AI CLI tools
print_status "Detecting AI CLI tools..."
DETECTED_TOOLS=""

for tool in claude openai gemini ollama gcloud llm qwen; do
    if command -v $tool &> /dev/null; then
        if [ -z "$DETECTED_TOOLS" ]; then
            DETECTED_TOOLS="$tool"
        else
            DETECTED_TOOLS="$DETECTED_TOOLS, $tool"
        fi
    fi
done

if [ -n "$DETECTED_TOOLS" ]; then
    print_success "Detected AI tools: $DETECTED_TOOLS ✓"
else
    print_warning "No common AI CLI tools detected."
    echo "Install tools like claude, openai, or gemini to get the most value."
fi

# Initialize AI Cache
echo ""
print_status "Running initial setup..."
if command -v aicache &> /dev/null; then
    aicache init --force
else
    python3 -m aicache.modern_cli init --force
fi

if [ $? -eq 0 ]; then
    print_success "AI Cache setup completed! ✓"
else
    print_warning "Setup completed with warnings. You can run 'aicache init' manually."
fi

# Show next steps
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                        🎉 Installation Complete!                   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Quick Start:${NC}"
echo "1. Check your setup:     ${YELLOW}aicache status${NC}"
echo "2. See optimizations:    ${YELLOW}aicache optimize${NC}"
echo "3. View cache:          ${YELLOW}aicache list${NC}"
echo ""
echo -e "${BLUE}Example Usage:${NC}"
echo -e "  ${YELLOW}$ claude 'help me debug this code'${NC}"
echo -e "  ${YELLOW}$ claude 'help me debug this code'  # Cached!${NC}"
echo ""
echo -e "${BLUE}Learn More:${NC}"
echo "- Documentation: https://github.com/asmeyatsky/aicache"
echo "- Report Issues: https://github.com/asmeyatsky/aicache/issues"
echo "- Join Community: [Discord link coming soon]"
echo ""
echo -e "${GREEN}🚀 Start saving on your AI costs today!${NC}"
echo -e "${GREEN}💰 Users report 30-70% cost reduction.${NC}"