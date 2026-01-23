#!/bin/bash
# AI Cache Quick Start Script
# Get started saving money on AI queries RIGHT NOW!

echo "🚀 AI Cache Quick Start - Your Dog Food is Served!"
echo ""

# Check if aicache is available
if ! command -v aicache &> /dev/null; then
    echo "❌ AI Cache not found. Installing now..."
    ./quick-install.sh
    echo ""
    echo "✅ AI Cache installed! Please restart your shell and run this again."
    exit 1
fi

echo "✅ AI Cache is ready!"
echo ""

# Show current status
echo "📊 Current savings status:"
export PATH="$HOME/.local/bin:$PATH"
aicache status

echo ""
echo "🎯 Start saving money NOW:"
echo "   1. Go to any project: cd ~/path/to/your/project"
echo "   2. Use your AI tools normally:"
echo "      claude 'your question here'"
echo "      openai 'another question'"
echo "      gemini 'yet another question'"
echo ""
echo "   💰 SAME QUESTION = INSTANT CACHE HIT!"
echo "   💰 Different projects = SAME SAVINGS!"
echo ""

echo "🌟 Example workflow:"
echo "   ~/project-api$ claude 'how to implement JWT auth?'"
echo "   ~/project-frontend$ claude 'how to implement JWT auth?'  ← CACHE HIT!"
echo "   ~/project-mobile$ claude 'how to implement JWT auth?'  ← CACHE HIT!"
echo ""

echo "📈 Track your success:"
echo "   aicache status    # See your growing savings"
echo "   aicache optimize  # Get optimization tips"
echo ""

echo "🍔 Your wallet will thank you! Enjoy the savings!"