"""
TOON Automated Report Generation

Generates daily, weekly, and monthly TOON analytics reports.
Can be scheduled to run automatically via cron or task scheduler.
"""

import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

from .infrastructure.toon_adapters import (
    FileSystemTOONRepositoryAdapter,
    TOONQueryBuilder,
    TOONExportService
)
from .domain.toon_service import TOONAnalyticsService
from .dashboard import TOONDashboard

logger = logging.getLogger(__name__)


class TOONReportGenerator:
    """Generates TOON analytics reports for specified periods."""

    def __init__(
        self,
        toon_data_dir: str = "~/.cache/aicache/toon_data",
        reports_dir: str = "~/.cache/aicache/reports"
    ):
        self.repository = FileSystemTOONRepositoryAdapter(toon_data_dir)
        self.export_service = TOONExportService(self.repository)
        self.analytics_service = TOONAnalyticsService()
        self.dashboard = TOONDashboard(toon_data_dir)
        self.reports_dir = Path(reports_dir).expanduser()
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    async def generate_daily_report(self, date: Optional[datetime] = None) -> str:
        """
        Generate a daily TOON report.

        Args:
            date: Date to generate report for (defaults to yesterday)

        Returns:
            Path to generated report file
        """
        if date is None:
            date = datetime.now() - timedelta(days=1)

        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)

        report = await self._generate_report(
            start_time=start_time,
            end_time=end_time,
            period_name=f"Daily Report - {date.strftime('%Y-%m-%d')}",
            filename=f"daily_report_{date.strftime('%Y%m%d')}.json"
        )

        logger.info(f"Generated daily report: {report}")
        return report

    async def generate_weekly_report(self, date: Optional[datetime] = None) -> str:
        """
        Generate a weekly TOON report.

        Args:
            date: Date in the week to generate report for (defaults to last week)

        Returns:
            Path to generated report file
        """
        if date is None:
            date = datetime.now() - timedelta(weeks=1)

        # Get Monday of the week
        start_time = date - timedelta(days=date.weekday())
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=7)

        week_str = start_time.strftime('%Y_W%V')
        report = await self._generate_report(
            start_time=start_time,
            end_time=end_time,
            period_name=f"Weekly Report - {week_str}",
            filename=f"weekly_report_{week_str}.json"
        )

        logger.info(f"Generated weekly report: {report}")
        return report

    async def generate_monthly_report(self, date: Optional[datetime] = None) -> str:
        """
        Generate a monthly TOON report.

        Args:
            date: Date in the month to generate report for (defaults to last month)

        Returns:
            Path to generated report file
        """
        if date is None:
            date = datetime.now() - timedelta(days=30)

        # Get first day of month
        start_time = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Get first day of next month
        if start_time.month == 12:
            end_time = start_time.replace(year=start_time.year + 1, month=1)
        else:
            end_time = start_time.replace(month=start_time.month + 1)

        month_str = start_time.strftime('%Y_%m')
        report = await self._generate_report(
            start_time=start_time,
            end_time=end_time,
            period_name=f"Monthly Report - {start_time.strftime('%B %Y')}",
            filename=f"monthly_report_{month_str}.json"
        )

        logger.info(f"Generated monthly report: {report}")
        return report

    async def generate_custom_report(
        self,
        start_time: datetime,
        end_time: datetime,
        period_name: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Generate a custom period TOON report.

        Args:
            start_time: Report start time
            end_time: Report end time
            period_name: Human-readable period name
            filename: Optional custom filename

        Returns:
            Path to generated report file
        """
        if filename is None:
            filename = f"custom_report_{start_time.strftime('%Y%m%d_%H%M%S')}.json"

        report = await self._generate_report(
            start_time=start_time,
            end_time=end_time,
            period_name=period_name,
            filename=filename
        )

        return report

    async def _generate_report(
        self,
        start_time: datetime,
        end_time: datetime,
        period_name: str,
        filename: str
    ) -> str:
        """
        Internal method to generate a report for a time period.

        Args:
            start_time: Report start time
            end_time: Report end time
            period_name: Human-readable period name
            filename: Output filename

        Returns:
            Path to generated report file
        """
        # Get TOON data for period
        builder = TOONQueryBuilder(self.repository)
        toons = await builder.with_time_range(start_time, end_time).execute()

        # Aggregate analytics
        if toons:
            analytics = self.analytics_service.aggregate_toons(toons, start_time, end_time)
            insights = self.analytics_service.extract_insights(analytics)
        else:
            analytics = None
            insights = None

        # Create report structure
        report_data = {
            "report_type": "TOON Analytics Report",
            "period": {
                "name": period_name,
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
            },
            "generated_at": datetime.now().isoformat(),
            "toon_count": len(toons),
        }

        if analytics and insights:
            report_data["analytics"] = analytics.to_dict()
            report_data["insights"] = insights

        # Save report
        report_path = self.reports_dir / filename
        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        return str(report_path)

    async def generate_report_html(
        self,
        period_days: int = 1,
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate HTML report (dashboard).

        Args:
            period_days: Days to include in report
            output_file: Optional output file path

        Returns:
            HTML content or file path
        """
        if output_file is None:
            output_file = str(
                self.reports_dir / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )

        html = await self.dashboard.generate_dashboard_html(
            period_days=period_days,
            output_file=output_file
        )

        logger.info(f"Generated HTML report: {output_file}")
        return output_file

    async def generate_text_summary_report(
        self,
        days: int = 1,
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate a plain text summary report.

        Args:
            days: Number of days to analyze
            output_file: Optional output file path

        Returns:
            Text report content or file path
        """
        start_time = datetime.now() - timedelta(days=days)
        end_time = datetime.now()

        builder = TOONQueryBuilder(self.repository)
        toons = await builder.with_time_range(start_time, end_time).execute()

        # Generate report text
        report_lines = [
            "=" * 80,
            "TOON Analytics Text Report",
            "=" * 80,
            f"\nPeriod: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total TOON Operations: {len(toons)}",
            "\n" + "-" * 80,
        ]

        if toons:
            analytics = self.analytics_service.aggregate_toons(toons, start_time, end_time)
            insights = self.analytics_service.extract_insights(analytics)

            # Add summary
            report_lines.extend([
                "\n📊 OPERATIONS SUMMARY",
                "-" * 80,
                f"Total Operations:     {insights['summary']['total_operations']}",
                f"Hit Rate:             {insights['summary']['hit_rate_percent']:.2f}%",
                f"Miss Rate:            {insights['summary']['miss_rate_percent']:.2f}%",
                f"Semantic Hit Rate:    {insights['summary']['semantic_hit_rate_percent']:.2f}%",

                "\n💰 TOKEN & COST SAVINGS",
                "-" * 80,
                f"Total Tokens Saved:   {insights['savings']['total_tokens_saved']:,}",
                f"Avg per Operation:    {insights['savings']['average_tokens_per_operation']:.1f} tokens",
                f"Total Cost Saved:     ${insights['savings']['total_cost_saved']:.6f}",

                "\n⚡ EFFICIENCY METRICS",
                "-" * 80,
                f"ROI Score:            {insights['efficiency']['roi_score']:.4f}",
                f"Cache Trend:          {insights['efficiency']['efficiency_trend']}",
                f"Trend Magnitude:      {insights['efficiency']['trend_magnitude']:.4f}",

                "\n💡 RECOMMENDATIONS",
                "-" * 80,
            ])

            for rec in insights['recommendations']:
                report_lines.append(f"• {rec}")
        else:
            report_lines.extend([
                "\n⚠️  No TOON operations found for this period.",
                "Start using aicache to generate TOON data.",
            ])

        report_lines.extend([
            "\n" + "=" * 80,
            "End of Report",
            "=" * 80,
        ])

        report_text = "\n".join(report_lines)

        # Save to file if requested
        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                f.write(report_text)
            logger.info(f"Generated text report: {output_file}")
            return output_file
        else:
            return report_text

    def list_reports(self) -> List[Dict[str, Any]]:
        """List all generated reports."""
        reports = []

        for report_file in sorted(self.reports_dir.glob("*.json"), reverse=True):
            try:
                with open(report_file, "r") as f:
                    data = json.load(f)
                reports.append({
                    "filename": report_file.name,
                    "path": str(report_file),
                    "period": data.get("period", {}).get("name", "Unknown"),
                    "generated_at": data.get("generated_at", "Unknown"),
                    "toon_count": data.get("toon_count", 0),
                })
            except Exception as e:
                logger.warning(f"Error reading report {report_file}: {e}")

        return reports

    def delete_old_reports(self, days: int = 90) -> int:
        """
        Delete reports older than specified days.

        Args:
            days: Age in days to consider for deletion

        Returns:
            Number of reports deleted
        """
        deleted = 0
        cutoff_time = datetime.now() - timedelta(days=days)

        for report_file in self.reports_dir.glob("*.json"):
            try:
                file_time = datetime.fromtimestamp(report_file.stat().st_mtime)
                if file_time < cutoff_time:
                    report_file.unlink()
                    deleted += 1
                    logger.info(f"Deleted old report: {report_file.name}")
            except Exception as e:
                logger.warning(f"Error deleting report {report_file}: {e}")

        return deleted


class TOONReportScheduler:
    """Schedules automatic TOON report generation."""

    def __init__(self, generator: TOONReportGenerator):
        self.generator = generator

    async def schedule_daily_reports(self, run_time: str = "00:00") -> None:
        """
        Schedule daily report generation.

        Args:
            run_time: Time to run in HH:MM format (24-hour)

        Example:
            scheduler = TOONReportScheduler(generator)
            asyncio.create_task(scheduler.schedule_daily_reports("09:00"))
        """
        while True:
            now = datetime.now()
            target_time = datetime.strptime(run_time, "%H:%M").time()
            target_datetime = datetime.combine(now.date(), target_time)

            # If target time has passed today, schedule for tomorrow
            if target_datetime <= now:
                target_datetime += timedelta(days=1)

            wait_seconds = (target_datetime - now).total_seconds()
            logger.info(f"Daily report scheduled for {target_datetime}")

            await asyncio.sleep(wait_seconds)

            # Generate report
            try:
                await self.generator.generate_daily_report()
                logger.info("Daily report generated successfully")
            except Exception as e:
                logger.error(f"Error generating daily report: {e}")

    async def schedule_weekly_reports(self, day: int = 0, run_time: str = "09:00") -> None:
        """
        Schedule weekly report generation.

        Args:
            day: Day of week (0=Monday, 6=Sunday)
            run_time: Time to run in HH:MM format

        Example:
            # Generate reports every Monday at 9 AM
            scheduler = TOONReportScheduler(generator)
            asyncio.create_task(scheduler.schedule_weekly_reports(day=0, run_time="09:00"))
        """
        while True:
            now = datetime.now()
            target_time = datetime.strptime(run_time, "%H:%M").time()

            # Calculate next occurrence
            days_ahead = day - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7

            target_datetime = datetime.combine(
                now.date() + timedelta(days=days_ahead),
                target_time
            )

            wait_seconds = (target_datetime - now).total_seconds()
            logger.info(f"Weekly report scheduled for {target_datetime}")

            await asyncio.sleep(wait_seconds)

            # Generate report
            try:
                await self.generator.generate_weekly_report()
                logger.info("Weekly report generated successfully")
            except Exception as e:
                logger.error(f"Error generating weekly report: {e}")

    async def schedule_monthly_reports(self, day: int = 1, run_time: str = "09:00") -> None:
        """
        Schedule monthly report generation.

        Args:
            day: Day of month (1-31)
            run_time: Time to run in HH:MM format

        Example:
            # Generate reports on the 1st of each month at 9 AM
            scheduler = TOONReportScheduler(generator)
            asyncio.create_task(scheduler.schedule_monthly_reports(day=1, run_time="09:00"))
        """
        while True:
            now = datetime.now()
            target_time = datetime.strptime(run_time, "%H:%M").time()

            # Calculate next occurrence
            if now.day < day:
                target_datetime = datetime.combine(
                    datetime(now.year, now.month, day),
                    target_time
                )
            else:
                # Next month
                if now.month == 12:
                    target_datetime = datetime.combine(
                        datetime(now.year + 1, 1, day),
                        target_time
                    )
                else:
                    target_datetime = datetime.combine(
                        datetime(now.year, now.month + 1, day),
                        target_time
                    )

            wait_seconds = (target_datetime - now).total_seconds()
            logger.info(f"Monthly report scheduled for {target_datetime}")

            await asyncio.sleep(wait_seconds)

            # Generate report
            try:
                await self.generator.generate_monthly_report()
                logger.info("Monthly report generated successfully")
            except Exception as e:
                logger.error(f"Error generating monthly report: {e}")
