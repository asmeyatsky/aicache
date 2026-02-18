"""
AI Cache CLI - Unified Command-Line Interface.

This is the primary CLI for aicache. It provides:
- Quick setup with auto-detection
- Cache management (list, inspect, clear, prune, stats)
- TOON analytics integration
- Plugin/wrapper management

All commands use the Rich library for beautiful output.
"""

import os
import sys
import json
import time
import shutil
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich import box

try:
    import yaml
except ImportError:
    yaml = None

from .core.cache import CoreCache, get_cache
from .config import get_config, get_config_manager

console = Console()


def print_deprecation_warning():
    """Print deprecation warning for old CLI."""
    console.print("[yellow]⚠️  The legacy CLI (aicache.cli) is deprecated.[/yellow]")
    console.print("[dim]Use 'aicache --help' for the new unified interface.[/dim]\n")


@click.group()
@click.version_option(version="0.2.0", prog_name="aicache")
def cli():
    """
    🚀 AI Cache - Stop paying for duplicate AI queries

    Automatic CLI caching with real-time cost savings and TOON analytics.
    """
    pass


@cli.command()
@click.option("--force", is_flag=True, help="Force reinitialization")
def init(force):
    """One-time magical setup with auto-detection"""
    console.print(
        Panel.fit(
            "[bold blue]🚀 Welcome to AI Cache![/bold blue]\n\n"
            "Let's set you up for automatic AI CLI caching\n"
            "and start saving money on every query.",
            title="AI Cache Setup",
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
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
            "security": {"encrypt_sensitive": True, "anonymize_logs": True},
            "created_at": time.time(),
            "version": "0.2.0",
        }

        config_file = Path.home() / ".config" / "aicache" / "config.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, "w") as f:
            if yaml:
                yaml.dump(config, f, default_flow_style=False)
            else:
                json.dump(config, f, indent=2)

        progress.update(task, description="Detecting AI CLI tools...")
        time.sleep(1)

        detected_tools = []
        common_tools = ["claude", "openai", "gemini", "gcloud", "llm", "qwen", "ollama"]

        for tool in common_tools:
            if shutil.which(tool):
                detected_tools.append(tool)

        progress.update(task, description="Finalizing setup...")
        time.sleep(1)

    console.print("\n✅ [bold green]Setup Complete![/bold green]")

    if detected_tools:
        console.print(f"\n🔍 Detected AI CLI tools: {', '.join(detected_tools)}")
        console.print(
            "💡 Run 'aicache install --setup-wrappers' to enable automatic caching"
        )
    else:
        console.print("⚠️  No common AI CLI tools detected.")

    console.print(f"\n📁 Cache directory: {cache_dir}")
    console.print(f"⚙️  Configuration: {config_file}")

    console.print("\n🎯 [bold]Quick Commands:[/bold]")
    console.print("   aicache status    # Show current savings")
    console.print("   aicache list     # View cached queries")
    console.print("   aicache stats    # View detailed statistics")


@cli.command()
@click.option("--days", default=7, help="Days of data to analyze")
def status(days):
    """Show today's savings and cache performance"""
    cache = get_cache()
    stats = cache.stats()

    title = f"📊 AI Cache Status - Last {days} days"

    # Calculate estimated savings (rough estimate: $0.002 per cached response)
    estimated_saved = stats["total_accesses"] * 0.002

    panel_content = f"""
[bold]Cache Performance[/bold]
• Total Entries: {stats["total_entries"]}
• Total Accesses: {stats["total_accesses"]}
• Cache Size: {stats["cache_size_mb"]} MB

[bold green]💰 Estimated Savings[/bold green]
• Queries Served from Cache: {stats["total_accesses"]}
• Estimated Cost Saved: ${estimated_saved:.2f}
• Monthly Projection: ${estimated_saved * 30:.2f}

[dim]Cache Directory: {stats["cache_dir"]}[/dim]
    """

    console.print(Panel.fit(panel_content, title=title, border_style="blue"))

    entries = cache.list(limit=5, verbose=True)
    if entries:
        console.print("\n[bold]🕒 Recent Cache Activity:[/bold]")
        table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
        table.add_column("Time", style="dim", width=18)
        table.add_column("Query Preview", width=40)
        table.add_column("Accesses", justify="right", width=8)

        for entry in entries[:5]:
            created_time = entry.get("created_at_readable", "Unknown")
            preview = entry.get("prompt_preview", "No preview")[:38]
            accesses = entry.get("access_count", 0)
            table.add_row(created_time, preview, str(accesses))

        console.print(table)


@cli.command()
def stats():
    """Show detailed cache statistics"""
    cache = get_cache()
    stats = cache.stats()

    console.print(
        Panel.fit(
            f"""[bold]Cache Statistics[/bold]

Entries:     {stats["total_entries"]}
Accesses:    {stats["total_accesses"]}
Size:        {stats["cache_size_mb"]} MB ({stats["cache_size_bytes"]:,} bytes)
Directory:   {stats["cache_dir"]}""",
            title="📈 Detailed Stats",
            border_style="green",
        )
    )


@cli.command()
@click.option("--aggressive", is_flag=True, help="Aggressive optimization")
def optimize(aggressive):
    """Get intelligent cache optimization recommendations"""
    cache = get_cache()
    stats = cache.stats()

    console.print(
        Panel.fit(
            "[bold blue]🧠 AI Cache Optimization Analysis[/bold blue]",
            title="Optimization Center",
        )
    )

    recommendations = []

    if stats["total_entries"] == 0:
        recommendations.append(
            (
                "🎯 First Setup",
                "Install CLI wrappers to start caching",
                "aicache install --setup-wrappers",
            )
        )
    elif stats["total_accesses"] < 10:
        recommendations.append(
            (
                "📈 Low Usage",
                "Use your AI CLI tools more to benefit from caching",
                "Try: claude 'help me debug'",
            )
        )
    else:
        hit_rate = min(stats["total_accesses"] / max(stats["total_entries"], 1), 1.0)
        if hit_rate < 0.5:
            recommendations.append(
                (
                    "⚡ Low Hit Rate",
                    "Consider increasing TTL or semantic matching",
                    "aicache config set ttl 7200",
                )
            )
        elif hit_rate > 0.8:
            recommendations.append(
                (
                    "🎉 Great Performance!",
                    "Your cache is working excellently",
                    "Keep up the good work!",
                )
            )

    if stats["cache_size_mb"] > 500:
        recommendations.append(
            (
                "💾 Large Cache",
                "Consider pruning old entries",
                "aicache prune --days=30",
            )
        )

    if aggressive:
        recommendations.append(
            (
                "🚀 Power User",
                "Enable semantic features for better hit rates",
                "pip install aicache[semantic]",
            )
        )

    for i, (title, desc, action) in enumerate(recommendations, 1):
        console.print(f"\n[bold]{i}. {title}[/bold]")
        console.print(f"   {desc}")
        console.print(f"   [dim cyan]→ {action}[/dim cyan]")


@cli.command()
@click.option("--limit", default=10, help="Number of entries to show")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def list(limit, verbose):
    """View cached queries and responses"""
    cache = get_cache()
    entries = cache.list(limit=limit)

    if not entries:
        console.print("📭 [yellow]No cached entries yet.[/yellow]")
        console.print("💡 Start using your AI CLI tools to populate the cache.")
        return

    console.print(f"📋 [bold]Showing {len(entries)} cache entries:[/bold]")

    table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)

    if verbose:
        table.add_column("Cache Key", style="dim", width=14)
        table.add_column("Created", width=18)
        table.add_column("Last Accessed", width=18)
        table.add_column("Accesses", justify="right", width=8)
        table.add_column("Preview", width=35)

        for entry in entries:
            key = entry["cache_key"][:12] + "..."
            created = entry.get("created_at_readable", "Unknown")
            accessed = entry.get("last_accessed_readable", "Never")
            accesses = entry.get("access_count", 0)
            preview = entry.get("prompt_preview", "No preview")[:33]
            table.add_row(key, created, accessed, str(accesses), preview)
    else:
        table.add_column("Time", width=18)
        table.add_column("Query Preview", width=55)
        table.add_column("Accesses", justify="right", width=8)

        for entry in entries:
            created_time = entry.get("created_at_readable", "Unknown")
            preview = entry.get("prompt_preview", "No preview")[:53]
            accesses = entry.get("access_count", 0)
            table.add_row(created_time, preview, str(accesses))

    console.print(table)


@cli.command()
@click.argument("cache_key", required=False)
def inspect(cache_key):
    """Inspect a specific cache entry"""
    cache = get_cache()

    if not cache_key:
        entries = cache.list(limit=5)
        if not entries:
            console.print("📭 [yellow]No entries to inspect.[/yellow]")
            return

        console.print("📋 [bold]Recent entries for inspection:[/bold]")
        for i, entry in enumerate(entries, 1):
            preview = entry.get("prompt_preview", "No preview")[:45]
            key = entry["cache_key"][:12] + "..."
            console.print(f"  {i}. {preview} ({key})")

        try:
            choice = int(Prompt.ask("Select entry to inspect (1-5)", default="1"))
            if 1 <= choice <= len(entries):
                cache_key = entries[choice - 1]["cache_key"]
            else:
                console.print("❌ Invalid selection.")
                return
        except ValueError:
            console.print("❌ Invalid selection.")
            return

    # Read the full cache entry
    cache_file = cache._get_cache_file(cache_key)
    if not cache_file.exists():
        console.print(f"❌ Cache entry not found: {cache_key[:12]}...")
        return

    try:
        with open(cache_file, "r") as f:
            data = json.load(f)

        console.print(
            Panel.fit(
                f"""[bold]Cache Entry Details[/bold]

[bold]Key:[/bold] {data.get("key", "N/A")[:16]}...
[bold]Created:[/bold] {datetime.fromtimestamp(data.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M:%S")}
[bold]TTL:[/bold] {data.get("ttl_seconds", "None")} seconds
[bold]Accesses:[/bold] {data.get("access_count", 0)}

[bold]Prompt Preview:[/bold]
{data.get("value", "N/A")[:200]}...""",
                title=f"🔍 Inspection: {cache_key[:12]}...",
                border_style="yellow",
            )
        )
    except Exception as e:
        console.print(f"❌ Error reading cache entry: {e}")


@cli.command()
@click.option("--interactive", "-i", is_flag=True, help="Interactive selection")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def clear(interactive, confirm):
    """Clear cache entries"""
    cache = get_cache()
    stats = cache.stats()

    if stats["total_entries"] == 0:
        console.print("📭 [yellow]Cache is already empty.[/yellow]")
        return

    if interactive:
        entries = cache.list()
        console.print(f"📋 Found {len(entries)} cache entries:")

        for i, entry in enumerate(entries, 1):
            preview = entry.get("prompt_preview", "No preview")[:50]
            accesses = entry.get("access_count", 0)
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
@click.option("--days", default=30, help="Delete entries older than N days")
@click.option("--size", "size_mb", type=int, help="Keep cache under N MB")
@click.option("--confirm", is_flag=True, help="Skip confirmation")
def prune(days, size_mb, confirm):
    """Remove old or large cache entries"""
    cache = get_cache()
    entries = cache.list()

    if not entries:
        console.print("📭 [yellow]No entries to prune.[/yellow]")
        return

    cutoff_time = time.time() - (days * 86400)
    entries_to_delete = []

    for entry in entries:
        created_at = entry.get("created_at")
        if created_at and created_at < cutoff_time:
            entries_to_delete.append(entry["cache_key"])

    # Also check size if specified
    if size_mb:
        stats = cache.stats()
        if stats["cache_size_bytes"] > size_mb * 1024 * 1024:
            # Sort by last accessed, delete oldest first
            sorted_entries = sorted(entries, key=lambda x: x.get("last_accessed", 0))
            current_size = stats["cache_size_bytes"]
            target_size = size_mb * 1024 * 1024

            for entry in sorted_entries:
                if current_size <= target_size:
                    break
                if entry["cache_key"] not in entries_to_delete:
                    entries_to_delete.append(entry["cache_key"])
                    current_size -= entry.get("response_length", 1000)

    if not entries_to_delete:
        console.print("✅ [green]No entries match prune criteria.[/green]")
        return

    console.print(f"📋 Found {len(entries_to_delete)} entries to prune")

    if not confirm and not Confirm.ask(f"🗑️  Delete {len(entries_to_delete)} entries?"):
        console.print("❌ Cancelled.")
        return

    deleted = 0
    for key in entries_to_delete:
        if cache.delete(key):
            deleted += 1

    console.print(f"✅ [bold green]Pruned {deleted} entries[/bold green]")


@cli.group()
def install():
    """Manage CLI wrappers and configuration"""
    pass


@install.command("wrappers")
@click.option("--force", is_flag=True, help="Force overwrite existing wrappers")
def install_wrappers(force):
    """Install CLI wrappers for automatic caching"""
    from .installer import AICacheInstaller

    installer = AICacheInstaller()
    common_tools = ["claude", "openai", "gemini", "gcloud", "llm", "qwen", "ollama"]

    console.print("🔍 [bold]Scanning for AI CLI tools...[/bold]\n")

    installed = []
    skipped = []

    for tool in common_tools:
        if shutil.which(tool):
            success = installer.install_wrapper(tool, force=force)
            if success:
                installed.append(tool)
                console.print(f"  ✅ {tool}")
            else:
                skipped.append(tool)
                console.print(f"  ⏭️  {tool} (already installed)")
        else:
            skipped.append(tool)

    console.print(f"\n✅ [bold]Installed {len(installed)} wrappers[/bold]")
    if skipped:
        console.print(f"⏭️  [dim]Skipped: {', '.join(skipped)}[/dim]")


@install.command("config")
def install_config():
    """Create default configuration file"""
    config_manager = get_config_manager()
    config_path = config_manager.config_path

    console.print(f"✅ [bold green]Configuration created at {config_path}[/bold green]")


@install.command("list")
def install_list():
    """List available CLI tools"""
    from .installer import AICacheInstaller

    installer = AICacheInstaller()
    wrappers = installer.list_wrappers()

    table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
    table.add_column("Tool", width=12)
    table.add_column("Status", width=12)
    table.add_column("Description", width=40)

    for wrapper in wrappers:
        status = (
            "[green]✓ Installed[/green]"
            if wrapper["status"] == "installed"
            else "[dim]Not installed[/dim]"
        )
        table.add_row(wrapper["name"], status, wrapper["description"])

    console.print(table)


@cli.group()
def toon():
    """TOON (Token Optimization Object Notation) analytics"""
    pass


@toon.command("list")
@click.option("--limit", default=10, help="Number of TOONs to show")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def toon_list(limit, verbose):
    """List recent TOON operations"""
    from .infrastructure.toon_adapters import FileSystemTOONRepositoryAdapter

    try:
        repo = FileSystemTOONRepositoryAdapter()
    except Exception as e:
        console.print(f"[yellow]⚠ TOON data not available: {e}[/yellow]")
        console.print(
            "[dim]TOON tracking requires running cache operations first.[/dim]"
        )
        return

    import asyncio

    try:
        toons = asyncio.run(repo.get_all_toons(limit=limit))
    except Exception as e:
        console.print(f"[yellow]⚠ Error loading TOON data: {e}[/yellow]")
        return

    if not toons:
        console.print("📭 [yellow]No TOON operations recorded yet.[/yellow]")
        console.print("[dim]TOON tracks token savings on cache hits.[/dim]")
        return

    console.print(f"📋 [bold]Recent TOON Operations ({len(toons)} total)[/bold]\n")

    table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
    table.add_column("ID", style="dim", width=14)
    table.add_column("Type", width=15)
    table.add_column("Tokens Saved", justify="right", width=12)
    table.add_column("Cost Saved", justify="right", width=12)
    table.add_column("Similarity", width=10)

    for t in reversed(toons):
        op_id = t.operation_id[:12]
        op_type = t.operation_type.value
        tokens = str(t.token_delta.saved_total)
        cost = f"${t.token_delta.cost_saved:.4f}"
        sim = (
            f"{t.semantic_data.similarity_score:.2f}"
            if t.semantic_data.similarity_score
            else "N/A"
        )

        table.add_row(op_id, op_type, tokens, cost, sim)

    console.print(table)

    if verbose:
        total_tokens = sum(t.token_delta.saved_total for t in toons)
        total_cost = sum(t.token_delta.cost_saved for t in toons)
        console.print(
            f"\n[bold]Totals:[/bold] {total_tokens} tokens saved, ${total_cost:.4f} saved"
        )


@toon.command("analytics")
@click.option("--period", default="7d", help="Time period (1d, 7d, 30d)")
def toon_analytics(period):
    """Show TOON analytics summary"""
    from .domain.toon_service import TOONAnalyticsService
    from .infrastructure.toon_adapters import (
        FileSystemTOONRepositoryAdapter,
        TOONQueryBuilder,
    )

    try:
        repo = FileSystemTOONRepositoryAdapter()
    except Exception as e:
        console.print(f"[yellow]⚠ TOON data not available: {e}[/yellow]")
        return

    # Parse period
    days_map = {"1d": 1, "7d": 7, "30d": 30, "1w": 7, "1m": 30}
    days = days_map.get(period, 7)

    start_time = datetime.now() - timedelta(days=days)
    end_time = datetime.now()

    import asyncio

    try:
        builder = TOONQueryBuilder(repo)
        toons = asyncio.run(builder.with_time_range(start_time, end_time).execute())

        if not toons:
            console.print(f"[yellow]No TOON data for the last {days} days.[/yellow]")
            return

        analytics_service = TOONAnalyticsService()
        analytics = analytics_service.aggregate_toons(toons, start_time, end_time)
        insights = analytics_service.extract_insights(analytics)
    except Exception as e:
        console.print(f"[yellow]⚠ Error analyzing TOON data: {e}[/yellow]")
        return

    summary = insights["summary"]
    savings = insights["savings"]
    efficiency = insights["efficiency"]

    console.print(
        Panel.fit(
            f"""[bold]📊 TOON Analytics - Last {period}[/bold]

[bold]Operations Summary[/bold]
Total: {summary["total_operations"]}
Hit Rate: {summary["hit_rate_percent"]:.1f}%
Semantic Hit Rate: {summary["semantic_hit_rate_percent"]:.1f}%

[bold green]💰 Savings[/bold green]
Tokens Saved: {savings["total_tokens_saved"]:,}
Cost Saved: ${savings["total_cost_saved"]:.4f}
Avg per Operation: {savings["average_tokens_per_operation"]:.1f} tokens

[bold]⚡ Efficiency[/bold]
ROI Score: {efficiency["roi_score"]:.4f}
Trend: {efficiency["efficiency_trend"]}""",
            title="📈 TOON Analytics",
            border_style="green",
        )
    )

    if insights["recommendations"]:
        console.print("\n[bold]💡 Recommendations:[/bold]")
        for rec in insights["recommendations"][:3]:
            console.print(f"  • {rec}")


@toon.command("last")
def toon_last():
    """Show the most recent TOON operation"""
    from .infrastructure.toon_adapters import FileSystemTOONRepositoryAdapter

    try:
        repo = FileSystemTOONRepositoryAdapter()
    except Exception as e:
        console.print(f"[yellow]⚠ TOON data not available: {e}[/yellow]")
        return

    import asyncio

    try:
        toons = asyncio.run(repo.get_all_toons(limit=1))
        if not toons:
            console.print("[yellow]No TOON operations recorded yet.[/yellow]")
            return

        toon = toons[0]
        console.print(
            Panel.fit(
                f"""[bold]Most Recent TOON Operation[/bold]

[bold]ID:[/bold] {toon.operation_id}
[bold]Type:[/bold] {toon.operation_type.value}
[bold]Strategy:[/bold] {toon.strategy_used.value}
[bold]Timestamp:[/bold] {toon.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

[bold]Tokens Saved:[/bold] {toon.token_delta.saved_total} ({toon.token_delta.saved_percent:.1f}%)
[bold]Cost Saved:[/bold] ${toon.token_delta.cost_saved:.6f}

[bold]ROI Score:[/bold] {toon.optimization_insight.roi_score:.4f}""",
                title="🔍 Last TOON",
                border_style="yellow",
            )
        )
    except Exception as e:
        console.print(f"[yellow]⚠ Error: {e}[/yellow]")


@cli.group()
def mcp():
    """MCP (Model Context Protocol) integration"""
    pass


@mcp.command("start")
@click.option(
    "--mode", type=click.Choice(["stdio", "tcp"]), default="stdio", help="Server mode"
)
@click.option("--port", type=int, default=8765, help="TCP port")
def mcp_start(mode, port):
    """Start the MCP server"""
    from .mcp_server import AICacheMCPServer

    console.print(f"🚀 [bold]Starting AI Cache MCP Server ({mode} mode)[/bold]")

    if mode == "stdio":
        console.print("[dim]Running in stdio mode...[/dim]")
        console.print(
            "[dim]This server can be connected to Claude Desktop or other MCP clients.[/dim]"
        )
        server = AICacheMCPServer(port=port)
        try:
            server.run_stdio()
        except KeyboardInterrupt:
            console.print("\n👋 Server stopped.")
    else:
        console.print(f"[dim]Running on port {port}...[/dim]")
        server = AICacheMCPServer(port=port)
        server.run_tcp()


@mcp.command("config")
def mcp_config():
    """Show MCP configuration for Claude Desktop"""
    config_path = Path.home() / ".config" / "aicache"

    console.print(
        Panel.fit(
            """[bold]MCP Configuration for Claude Desktop[/bold]

Add this to your Claude Desktop config:

{
  "mcpServers": {
    "aicache": {
      "command": "python",
      "args": ["-m", "aicache.mcp_server"],
      "env": {}
    }
  }
}

Config location: ~/Library/Application Support/Claude/settings.json (macOS)
or %APPDATA%\\Claude\\settings.json (Windows)
""",
            title="🔌 MCP Setup",
            border_style="green",
        )
    )


@cli.group()
def config():
    """Configuration management"""
    pass


@config.command("get")
@click.argument("key", required=False)
def config_get(key):
    """Get configuration value"""
    config_manager = get_config_manager()
    value = config_manager.get(key)

    if value is None:
        console.print(f"[yellow]Configuration key not found: {key}[/yellow]")
        return

    if isinstance(value, dict):
        console.print(
            yaml.dump(value, default_flow_style=False)
            if yaml
            else json.dumps(value, indent=2)
        )
    else:
        console.print(str(value))


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set configuration value"""
    config_manager = get_config_manager()

    # Try to parse value as JSON for booleans/numbers
    try:
        parsed_value = json.loads(value)
    except json.JSONDecodeError:
        parsed_value = value

    success = config_manager.set(key, parsed_value)

    if success:
        console.print(f"✅ [green]Set {key} = {parsed_value}[/green]")
    else:
        console.print(f"❌ [red]Failed to set configuration[/red]")


@config.command("validate")
def config_validate():
    """Validate configuration"""
    config_manager = get_config_manager()
    result = config_manager.validate_config()

    if result["valid"]:
        console.print("✅ [green]Configuration is valid[/green]")
    else:
        console.print("❌ [red]Configuration has errors:[/red]")
        for error in result["errors"]:
            console.print(f"  • {error}")

    if result["warnings"]:
        console.print("\n⚠️  [yellow]Warnings:[/yellow]")
        for warning in result["warnings"]:
            console.print(f"  • {warning}")


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


if __name__ == "__main__":
    main()
