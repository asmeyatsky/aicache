"""
AI Cache CLI - Modern, magical command-line interface.

Simplified CLI focused on developer experience with quick setup
and real-time cost savings visualization.
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

try:
    import yaml
except ImportError:
    yaml = None

# Import lightweight core
try:
    from .core.cache import CoreCache, get_cache
except (ImportError, ValueError):
    # Fallback for development - try direct import
    try:
        from core.cache import CoreCache, get_cache
    except ImportError:
        # Last resort - use the file directly
        sys.path.insert(0, os.path.dirname(__file__))
        import cache as cache_module
        CoreCache = cache_module.CoreCache
        get_cache = cache_module.get_cache

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="aicache")
def cli():
    """
    🚀 AI Cache - Stop paying for duplicate AI queries
    
    Automatic CLI caching with real-time cost savings.
    """
    pass


@cli.command()
@click.option('--force', is_flag=True, help='Force reinitialization')
def init(force):
    """🎯 One-time magical setup with auto-detection"""
    console.print(Panel.fit(
        "[bold blue]🚀 Welcome to AI Cache![/bold blue]\n\n"
        "Let's set you up for automatic AI CLI caching\n"
        "and start saving money on every query.",
        title="AI Cache Setup"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Check existing setup
        task = progress.add_task("Checking current setup...", total=None)
        cache_dir = Path.home() / ".cache" / "aicache"
        
        if cache_dir.exists() and not force:
            progress.update(task, description="Found existing setup...")
            time.sleep(1)
            if not Confirm.ask("Found existing cache. Reset and reinitialize?"):
                console.print("✅ Setup cancelled, keeping existing configuration.")
                return
        
        progress.update(task, description="Creating cache directories...")
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create config
        progress.update(task, description="Creating configuration...")
        config = {
            "cache_dir": str(cache_dir),
            "default_ttl": 3600,
            "max_size_mb": 1000,
            "semantic_threshold": 0.85,
            "auto_optimize": True,
            "created_at": time.time(),
            "version": "0.1.0"
        }
        
        config_file = Path.home() / ".config" / "aicache" / "config.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            if yaml:
                yaml.dump(config, f, default_flow_style=False)
            else:
                json.dump(config, f, indent=2)
        
        progress.update(task, description="Detecting AI CLI tools...")
        time.sleep(1)
        
        # Detect common AI CLI tools
        detected_tools = []
        common_tools = ['claude', 'openai', 'gemini', 'gcloud', 'llm', 'qwen', 'ollama']
        
        for tool in common_tools:
            if shutil.which(tool):
                detected_tools.append(tool)
        
        progress.update(task, description="Finalizing setup...")
        time.sleep(1)
    
    # Show results
    console.print("\n✅ [bold green]Setup Complete![/bold green]")
    
    if detected_tools:
        console.print(f"\n🔍 Detected AI CLI tools: {', '.join(detected_tools)}")
        console.print("💡 Run 'aicache install --setup-wrappers' to enable automatic caching")
    else:
        console.print("⚠️  No common AI CLI tools detected. Install tools first, then run:")
        console.print("   aicache install --setup-wrappers")
    
    console.print(f"\n📁 Cache directory: {cache_dir}")
    console.print(f"⚙️  Configuration: {config_file}")
    
    # Quick demo
    console.print("\n🎯 [bold]Quick Demo:[/bold]")
    console.print("   aicache status    # Show current savings")
    console.print("   aicache list      # View cached queries")
    console.print("   aicache optimize  # Get optimization tips")


@cli.command()
@click.option('--days', default=7, help='Days of data to analyze')
def status(days):
    """📊 Show today's savings and cache performance"""
    cache = get_cache()
    stats = cache.stats()
    
    # Create beautiful stats display
    title = f"📊 AI Cache Status - Last {days} days"
    
    panel_content = f"""
[bold]Cache Performance[/bold]
• Total Entries: {stats['total_entries']}
• Total Accesses: {stats['total_accesses']}
• Cache Size: {stats['cache_size_mb']} MB
• Cache Directory: {stats['cache_dir']}

[bold]💰 Estimated Savings[/bold]
• Daily Queries Saved: ~{stats['total_accesses'] // max(days, 1)}
• Estimated Cost Saved: ${stats['total_accesses'] * 0.002:.2f}
• Monthly Projection: ${stats['total_accesses'] * 0.002 * 30:.2f}
    """
    
    console.print(Panel.fit(panel_content, title=title, border_style="blue"))
    
    # Show recent entries if any
    entries = cache.list(limit=5)
    if entries:
        console.print("\n[bold]🕒 Recent Cache Activity:[/bold]")
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Time", style="dim")
        table.add_column("Query Preview")
        table.add_column("Accesses")
        
        for entry in entries[:5]:
            created_time = entry.get('created_at_readable', 'Unknown')
            preview = entry.get('prompt_preview', 'No preview')[:50]
            accesses = entry.get('access_count', 0)
            table.add_row(created_time, preview, str(accesses))
        
        console.print(table)


@cli.command()
@click.option('--aggressive', is_flag=True, help='Aggressive optimization')
def optimize(aggressive):
    """🧠 Get intelligent cache optimization recommendations"""
    cache = get_cache()
    stats = cache.stats()
    
    console.print(Panel.fit(
        "[bold blue]🧠 AI Cache Optimization Analysis[/bold blue]",
        title="Optimization Center"
    ))
    
    recommendations = []
    
    # Analyze cache performance
    if stats['total_entries'] == 0:
        recommendations.append(("🎯 First Setup", "Install CLI wrappers to start caching", "aicache install --setup-wrappers"))
    elif stats['total_accesses'] < 10:
        recommendations.append(("📈 Low Usage", "Use your AI CLI tools more to benefit from caching", "Try: claude 'help me debug'"))
    else:
        hit_rate = min(stats['total_accesses'] / max(stats['total_entries'], 1), 1.0)
        if hit_rate < 0.5:
            recommendations.append(("⚡ Low Hit Rate", "Consider increasing TTL or semantic matching", "aicache config set ttl 7200"))
        elif hit_rate > 0.8:
            recommendations.append(("🎉 Great Performance!", "Your cache is working excellently", "Keep up the good work!"))
    
    # Size recommendations
    if stats['cache_size_mb'] > 500:
        recommendations.append(("💾 Large Cache", "Consider pruning old entries", "aicache prune --days=30"))
    
    if aggressive:
        recommendations.append(("🚀 Power User", "Enable semantic features for better hit rates", "pip install aicache[semantic]"))
    
    # Display recommendations
    for i, (title, desc, action) in enumerate(recommendations, 1):
        console.print(f"\n[bold]{i}. {title}[/bold]")
        console.print(f"   {desc}")
        console.print(f"   [dim cyan]→ {action}[/dim cyan]")
    
    # Quick actions
    console.print(f"\n[bold]🔧 Quick Actions:[/bold]")
    console.print("• Clear old cache: [cyan]aicache prune --days=7[/cyan]")
    console.print("• View all entries: [cyan]aicache list --verbose[/cyan]")
    console.print("• Export analytics: [cyan]aicache analytics export[/cyan]")


@cli.command()
@click.option('--limit', default=10, help='Number of entries to show')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information')
def list(limit, verbose):
    """📋 View cached queries and responses"""
    cache = get_cache()
    entries = cache.list(limit=limit)
    
    if not entries:
        console.print("📭 [yellow]No cached entries yet.[/yellow]")
        console.print("💡 Start using your AI CLI tools to populate the cache.")
        return
    
    console.print(f"📋 [bold]Showing {len(entries)} recent cache entries:[/bold]")
    
    if verbose:
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Cache Key", style="dim")
        table.add_column("Created")
        table.add_column("Last Accessed")
        table.add_column("Accesses")
        table.add_column("Preview")
        
        for entry in entries:
            key = entry['cache_key'][:12] + "..."
            created = entry.get('created_at_readable', 'Unknown')
            accessed = entry.get('last_accessed_readable', 'Never')
            accesses = entry.get('access_count', 0)
            preview = entry.get('prompt_preview', 'No preview')[:40]
            
            table.add_row(key, created, accessed, str(accesses), preview)
    else:
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Time")
        table.add_column("Query Preview")
        table.add_column("Accesses", justify="right")
        
        for entry in entries:
            created_time = entry.get('created_at_readable', 'Unknown')
            preview = entry.get('prompt_preview', 'No preview')[:60]
            accesses = entry.get('access_count', 0)
            
            table.add_row(created_time, preview, str(accesses))
    
    console.print(table)


@cli.command()
@click.option('--interactive', '-i', is_flag=True, help='Interactive selection')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def clear(interactive, confirm):
    """🧹 Clear cache entries"""
    cache = get_cache()
    stats = cache.stats()
    
    if stats['total_entries'] == 0:
        console.print("📭 [yellow]Cache is already empty.[/yellow]")
        return
    
    if interactive:
        entries = cache.list()
        console.print(f"📋 Found {len(entries)} cache entries:")
        
        for i, entry in enumerate(entries, 1):
            preview = entry.get('prompt_preview', 'No preview')[:50]
            accesses = entry.get('access_count', 0)
            console.print(f"  {i:2}. {preview} (accessed {accesses}x)")
        
        if not Confirm.ask(f"\n🗑️  Delete all {len(entries)} entries?"):
            console.print("❌ Cancelled.")
            return
    
    if not confirm and not interactive:
        if not Confirm.ask(f"🗑️  Clear {stats['total_entries']} cache entries?"):
            console.print("❌ Cancelled.")
            return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Clearing cache...", total=None)
        cleared = cache.clear()
        progress.update(task, description=f"Cleared {cleared} entries...")
    
    console.print(f"✅ [bold green]Cleared {cleared} cache entries[/bold green]")


@cli.command()
@click.option('--days', default=30, help='Delete entries older than N days')
@click.option('--size', help='Keep cache under N MB')
def prune(days, size):
    """✂️ Remove old or large cache entries"""
    cache = get_cache()
    
    console.print("✂️ [bold]Pruning cache entries...[/bold]")
    
    # For now, use simple clearing. In full version, implement selective pruning
    stats_before = cache.stats()
    
    if days:
        console.print(f"🗓️  Removing entries older than {days} days...")
        # TODO: Implement age-based pruning
    
    if size:
        console.print(f"💾 Reducing cache size to under {size} MB...")
        # TODO: Implement size-based pruning
    
    console.print("💡 [yellow]Full pruning implementation coming soon![/yellow]")
    console.print("   For now, use 'aicache clear --interactive' for selective cleanup")


@cli.command()
@click.argument('cache_key', required=False)
def inspect(cache_key):
    """🔍 Inspect a specific cache entry"""
    cache = get_cache()
    
    if not cache_key:
        # Show recent entries for inspection
        entries = cache.list(limit=5)
        if not entries:
            console.print("📭 [yellow]No entries to inspect.[/yellow]")
            return
        
        console.print("📋 [bold]Recent entries for inspection:[/bold]")
        for i, entry in enumerate(entries, 1):
            preview = entry.get('prompt_preview', 'No preview')[:40]
            key = entry['cache_key'][:12] + "..."
            console.print(f"  {i}. {preview} ({key})")
        
        choice = int(Prompt.ask("Select entry to inspect (1-5)"))
        if 1 <= choice <= len(entries):
            cache_key = entries[choice-1]['cache_key']
        else:
            console.print("❌ Invalid selection.")
            return
    
    # In core cache, we need to implement inspection
    console.print(f"🔍 [yellow]Full inspection details coming soon![/yellow]")
    console.print(f"   Cache key: {cache_key[:12]}...")


def main():
    """Entry point for the CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()