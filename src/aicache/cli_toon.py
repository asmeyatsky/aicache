"""
TOON CLI Commands

Provides command-line interface for TOON operations:
- Inspecting TOON objects
- Listing recent TOONs
- Viewing TOON analytics
- Exporting TOON data
- Querying TOONs with filters
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import logging

from .infrastructure.toon_adapters import (
    FileSystemTOONRepositoryAdapter,
    TOONExportService,
    TOONQueryBuilder
)
from .domain.toon_service import TOONAnalyticsService
from .domain.toon import TOONOperationType, TOONOptimizationLevel

logger = logging.getLogger(__name__)


class TOONCLIHandler:
    """Handles TOON-related CLI commands."""

    def __init__(self, toon_data_dir: str = "~/.cache/aicache/toon_data"):
        self.repository = FileSystemTOONRepositoryAdapter(toon_data_dir)
        self.export_service = TOONExportService(self.repository)
        self.analytics_service = TOONAnalyticsService()

    async def handle_inspect(self, operation_id: str) -> None:
        """Inspect a specific TOON operation."""
        toon = await self.repository.get_toon(operation_id)

        if not toon:
            print(f"❌ TOON not found: {operation_id}", file=sys.stderr)
            return

        # Display formatted TOON
        print("\n" + "=" * 80)
        print(f"TOON Operation: {operation_id}")
        print("=" * 80)

        toon_dict = toon.to_dict()

        print(f"\n📊 Operation Metadata")
        print(f"  Type: {toon_dict['operation_type']}")
        print(f"  Strategy: {toon_dict['strategy_used']}")
        print(f"  Timestamp: {toon_dict['timestamp']}")
        print(f"  Duration: {toon_dict['duration_ms']:.2f}ms")

        print(f"\n🔍 Query")
        print(f"  Original: {toon_dict['query']['original']}")
        print(f"  Normalized: {toon_dict['query']['normalized']}")
        print(f"  Hash: {toon_dict['query']['hash'][:16]}...")

        print(f"\n💾 Tokens & Cost")
        tokens = toon_dict['tokens']
        print(f"  Without Cache: {tokens['without_cache']['total']} tokens (${tokens['costs']['without_cache']:.6f})")
        print(f"  With Cache: {tokens['with_cache']['total']} tokens (${tokens['costs']['with_cache']:.6f})")
        print(f"  Saved: {tokens['saved']['total']} tokens ({tokens['saved']['percent']:.1f}%) (${tokens['costs']['saved']:.6f})")

        if toon_dict['semantic_match']['enabled']:
            print(f"\n🧠 Semantic Match")
            sem = toon_dict['semantic_match']
            print(f"  Similarity: {sem['similarity_score']:.4f}")
            print(f"  Confidence: {sem['confidence']:.4f}")
            print(f"  Threshold: {sem['threshold_used']}")
            print(f"  Matched Entry: {sem['matched_entry_key'][:16]}..." if sem['matched_entry_key'] else "")

        print(f"\n💡 Optimization Insights")
        insights = toon_dict['optimization_insights']
        print(f"  Level: {insights['optimization_level']}")
        print(f"  ROI Score: {insights['roi_score']:.4f}")
        print(f"  Efficiency Score: {insights['cache_efficiency_score']:.4f}")
        print(f"  Predictability: {insights['predictability_score']:.4f}")
        if insights['suggested_actions']:
            print(f"  Suggestions:")
            for action in insights['suggested_actions']:
                print(f"    • {action}")

        print("\n" + "=" * 80 + "\n")

    async def handle_list(self, limit: int = 50, verbose: bool = False) -> None:
        """List recent TOON operations."""
        toons = await self.repository.get_all_toons(limit=limit)

        if not toons:
            print("No TOON operations found.", file=sys.stderr)
            return

        print(f"\n📋 Recent TOON Operations ({len(toons)} total)")
        print("-" * 120)

        header = "ID (first 12) | Type            | Strategy   | Tokens Saved | Cost Saved  | ROI   | Similarity"
        print(header)
        print("-" * 120)

        for toon in reversed(toons):  # Most recent first
            op_id = toon.operation_id[:12]
            op_type = toon.operation_type.value.ljust(15)
            strategy = toon.strategy_used.value.ljust(10)
            tokens = str(toon.token_delta.saved_total).ljust(12)
            cost = f"${toon.token_delta.cost_saved:.6f}".ljust(11)
            roi = f"{toon.optimization_insight.roi_score:.2f}".ljust(5)
            sim = (
                f"{toon.semantic_data.similarity_score:.4f}"
                if toon.semantic_data.similarity_score
                else "N/A"
            )

            print(f"{op_id} | {op_type} | {strategy} | {tokens} | {cost} | {roi} | {sim}")

        print("-" * 120)

        if verbose:
            print("\nDetailed Breakdown:")
            hits = sum(1 for t in toons if "hit" in t.operation_type.value)
            misses = sum(1 for t in toons if "miss" in t.operation_type.value)
            exact = sum(1 for t in toons if t.operation_type == TOONOperationType.EXACT_HIT)
            semantic = sum(1 for t in toons if t.operation_type == TOONOperationType.SEMANTIC_HIT)

            print(f"  Total Hits: {hits}")
            print(f"    • Exact: {exact}")
            print(f"    • Semantic: {semantic}")
            print(f"  Total Misses: {misses}")
            print(f"  Total Tokens Saved: {sum(t.token_delta.saved_total for t in toons)}")
            print(f"  Total Cost Saved: ${sum(t.token_delta.cost_saved for t in toons):.6f}")

        print()

    async def handle_analytics(self, days: int = 1, period: str = "1d") -> None:
        """Show TOON analytics."""
        # Parse period
        if period.endswith("d"):
            days = int(period[:-1])
        elif period.endswith("w"):
            days = int(period[:-1]) * 7
        elif period.endswith("m"):
            days = int(period[:-1]) * 30
        elif period.endswith("h"):
            days = int(period[:-1]) / 24

        # Get TOON data
        start_time = datetime.now() - timedelta(days=days)
        end_time = datetime.now()

        builder = TOONQueryBuilder(self.repository)
        toons = await builder.with_time_range(start_time, end_time).execute()

        if not toons:
            print(f"No TOON data for the last {days} days.", file=sys.stderr)
            return

        # Aggregate analytics
        analytics = self.analytics_service.aggregate_toons(toons, start_time, end_time)
        insights = self.analytics_service.extract_insights(analytics)

        # Display analytics
        print("\n" + "=" * 80)
        print(f"📊 TOON Analytics - Last {period}")
        print("=" * 80)

        summary = insights['summary']
        print(f"\n📈 Operations Summary")
        print(f"  Total Operations: {summary['total_operations']}")
        print(f"  Hit Rate: {summary['hit_rate_percent']:.2f}%")
        print(f"  Miss Rate: {summary['miss_rate_percent']:.2f}%")
        print(f"  Semantic Hit Rate: {summary['semantic_hit_rate_percent']:.2f}%")

        savings = insights['savings']
        print(f"\n💰 Token & Cost Savings")
        print(f"  Total Tokens Saved: {savings['total_tokens_saved']:,}")
        print(f"  Average per Operation: {savings['average_tokens_per_operation']:.1f} tokens")
        print(f"  Total Cost Saved: ${savings['total_cost_saved']:.6f}")

        efficiency = insights['efficiency']
        print(f"\n⚡ Efficiency Metrics")
        print(f"  ROI Score: {efficiency['roi_score']:.4f}")
        print(f"  Trend: {efficiency['efficiency_trend']}")
        print(f"  Trend Magnitude: {efficiency['trend_magnitude']:.4f}")

        print(f"\n💡 Recommendations")
        for i, rec in enumerate(insights['recommendations'], 1):
            print(f"  {i}. {rec}")

        print("\n" + "=" * 80 + "\n")

    async def handle_query(
        self,
        operation_type: Optional[str] = None,
        min_tokens: int = 0,
        min_similarity: float = 0.0,
        since_hours: int = 24,
        limit: int = 50
    ) -> None:
        """Query TOON operations with filters."""
        builder = TOONQueryBuilder(self.repository)

        # Apply filters
        if operation_type:
            try:
                op_type = TOONOperationType[operation_type.upper()]
                builder = builder.with_operation_type(op_type)
            except KeyError:
                print(f"❌ Invalid operation type: {operation_type}", file=sys.stderr)
                print(f"Valid types: {', '.join(t.name.lower() for t in TOONOperationType)}")
                return

        if min_tokens > 0:
            builder = builder.with_min_tokens_saved(min_tokens)

        if min_similarity > 0:
            builder = builder.with_min_similarity(min_similarity)

        start_time = datetime.now() - timedelta(hours=since_hours)
        end_time = datetime.now()
        builder = builder.with_time_range(start_time, end_time)

        # Execute query
        results = await builder.execute()

        if not results:
            print(f"❌ No TOON operations match the criteria.", file=sys.stderr)
            return

        # Display results
        print(f"\n📋 Query Results ({len(results)} operations)")
        print("-" * 120)

        header = "ID (first 12) | Type            | Tokens | Cost      | Similarity | Time"
        print(header)
        print("-" * 120)

        for toon in results[-limit:]:
            op_id = toon.operation_id[:12]
            op_type = toon.operation_type.value.ljust(15)
            tokens = str(toon.token_delta.saved_total).ljust(6)
            cost = f"${toon.token_delta.cost_saved:.6f}".ljust(9)
            sim = (
                f"{toon.semantic_data.similarity_score:.4f}"
                if toon.semantic_data.similarity_score
                else "N/A".ljust(10)
            )
            time_str = toon.timestamp.strftime("%H:%M:%S")

            print(f"{op_id} | {op_type} | {tokens} | {cost} | {sim} | {time_str}")

        print("-" * 120 + "\n")

    async def handle_export(
        self,
        format: str = "json",
        limit: Optional[int] = None,
        output_file: Optional[str] = None
    ) -> None:
        """Export TOON data."""
        valid_formats = ["json", "jsonl", "csv", "msgpack"]
        if format not in valid_formats:
            print(f"❌ Invalid format: {format}", file=sys.stderr)
            print(f"Valid formats: {', '.join(valid_formats)}")
            return

        print(f"📤 Exporting TOONs as {format.upper()}...", file=sys.stderr)

        try:
            if format == "json":
                data = await self.export_service.export_to_json(limit)
            elif format == "jsonl":
                data = await self.export_service.export_to_jsonl(limit)
            elif format == "csv":
                data = await self.export_service.export_to_csv(limit)
            elif format == "msgpack":
                data = await self.export_service.export_to_msgpack(limit)

            if output_file:
                mode = "wb" if isinstance(data, bytes) else "w"
                with open(output_file, mode) as f:
                    f.write(data)
                print(f"✅ Exported to {output_file}", file=sys.stderr)
            else:
                if isinstance(data, bytes):
                    sys.stdout.buffer.write(data)
                else:
                    print(data)

        except Exception as e:
            print(f"❌ Export failed: {e}", file=sys.stderr)
            return

    async def handle_last(self) -> None:
        """Show the last TOON operation."""
        toons = await self.repository.get_all_toons(limit=1)

        if not toons:
            print("No TOON operations found.", file=sys.stderr)
            return

        await self.handle_inspect(toons[0].operation_id)

    async def handle_delete(self, operation_id: str) -> None:
        """Delete a specific TOON operation."""
        success = await self.repository.delete_toon(operation_id)

        if success:
            print(f"✅ Deleted TOON: {operation_id}")
        else:
            print(f"❌ TOON not found: {operation_id}", file=sys.stderr)

    async def handle_clear(self, confirm: bool = False) -> None:
        """Clear all TOON operations."""
        if not confirm:
            print("⚠️  This will delete all TOON data. Use --confirm to proceed.", file=sys.stderr)
            return

        count = await self.repository.clear_all_toons()
        print(f"✅ Cleared {count} TOON operations")

    async def handle_insights(self, days: int = 1) -> None:
        """Show actionable insights from TOON data."""
        start_time = datetime.now() - timedelta(days=days)
        end_time = datetime.now()

        builder = TOONQueryBuilder(self.repository)
        toons = await builder.with_time_range(start_time, end_time).execute()

        if not toons:
            print(f"No TOON data for the last {days} days.", file=sys.stderr)
            return

        analytics = self.analytics_service.aggregate_toons(toons, start_time, end_time)
        insights = self.analytics_service.extract_insights(analytics)

        print("\n" + "=" * 80)
        print("💡 TOON Insights & Recommendations")
        print("=" * 80)

        print(f"\nPeriod: {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}")
        print(f"Operations: {insights['summary']['total_operations']}")

        print("\n🎯 Key Findings:")
        print(f"  • Hit Rate: {insights['summary']['hit_rate_percent']:.1f}%")
        print(f"  • Cost Saved: ${insights['savings']['total_cost_saved']:.4f}")
        print(f"  • ROI Score: {insights['efficiency']['roi_score']:.4f}")
        print(f"  • Efficiency Trend: {insights['efficiency']['efficiency_trend']}")

        print("\n💬 Recommendations:")
        for i, rec in enumerate(insights['recommendations'], 1):
            print(f"  {i}. {rec}")

        print("\n" + "=" * 80 + "\n")


def add_toon_subparsers(subparsers):
    """Add TOON subcommands to the main parser."""

    # TOON inspect command
    inspect_parser = subparsers.add_parser(
        "toon",
        help="TOON (Token Optimization Object Notation) commands"
    )
    toon_subparsers = inspect_parser.add_subparsers(dest="toon_command")

    # toon inspect
    toon_inspect = toon_subparsers.add_parser("inspect", help="Inspect a specific TOON operation")
    toon_inspect.add_argument("operation_id", help="TOON operation ID")

    # toon list
    toon_list = toon_subparsers.add_parser("list", help="List recent TOON operations")
    toon_list.add_argument("--limit", type=int, default=50, help="Number of recent TOONs to show")
    toon_list.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # toon last
    toon_last = toon_subparsers.add_parser("last", help="Show the most recent TOON operation")

    # toon analytics
    toon_analytics = toon_subparsers.add_parser("analytics", help="Show TOON analytics")
    toon_analytics.add_argument(
        "--period",
        default="1d",
        help="Time period (1d, 7d, 30d, 1w, 1m, 24h, etc.)"
    )

    # toon query
    toon_query = toon_subparsers.add_parser("query", help="Query TOON operations with filters")
    toon_query.add_argument("--type", help="Operation type (exact_hit, semantic_hit, etc.)")
    toon_query.add_argument("--min-tokens", type=int, default=0, help="Minimum tokens saved")
    toon_query.add_argument("--min-similarity", type=float, default=0.0, help="Minimum similarity score")
    toon_query.add_argument("--since", type=int, default=24, help="Hours to look back")
    toon_query.add_argument("--limit", type=int, default=50, help="Maximum results")

    # toon export
    toon_export = toon_subparsers.add_parser("export", help="Export TOON data")
    toon_export.add_argument("--format", default="json", help="Export format (json, csv, jsonl, msgpack)")
    toon_export.add_argument("--limit", type=int, help="Limit number of TOONs")
    toon_export.add_argument("-o", "--output", help="Output file")

    # toon insights
    toon_insights = toon_subparsers.add_parser("insights", help="Show TOON insights and recommendations")
    toon_insights.add_argument("--days", type=int, default=1, help="Number of days to analyze")

    # toon delete
    toon_delete = toon_subparsers.add_parser("delete", help="Delete a TOON operation")
    toon_delete.add_argument("operation_id", help="TOON operation ID to delete")

    # toon clear
    toon_clear = toon_subparsers.add_parser("clear", help="Clear all TOON operations")
    toon_clear.add_argument("--confirm", action="store_true", help="Confirm deletion")


async def handle_toon_command(args):
    """Handle TOON CLI commands."""
    handler = TOONCLIHandler()

    if args.toon_command == "inspect":
        await handler.handle_inspect(args.operation_id)
    elif args.toon_command == "list":
        await handler.handle_list(limit=args.limit, verbose=args.verbose)
    elif args.toon_command == "last":
        await handler.handle_last()
    elif args.toon_command == "analytics":
        await handler.handle_analytics(period=args.period)
    elif args.toon_command == "query":
        await handler.handle_query(
            operation_type=args.type,
            min_tokens=args.min_tokens,
            min_similarity=args.min_similarity,
            since_hours=args.since,
            limit=args.limit
        )
    elif args.toon_command == "export":
        await handler.handle_export(
            format=args.format,
            limit=args.limit,
            output_file=args.output
        )
    elif args.toon_command == "insights":
        await handler.handle_insights(days=args.days)
    elif args.toon_command == "delete":
        await handler.handle_delete(args.operation_id)
    elif args.toon_command == "clear":
        await handler.handle_clear(confirm=args.confirm)
    else:
        print("❌ Unknown TOON command", file=sys.stderr)
