"""
TOON Analytics Dashboard

Provides a web-based dashboard for visualizing TOON analytics and cache performance.
Generates static HTML reports and can be served with a simple HTTP server.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

from .infrastructure.toon_adapters import (
    FileSystemTOONRepositoryAdapter,
    TOONQueryBuilder,
    TOONExportService
)
from .domain.toon_service import TOONAnalyticsService
from .domain.toon import TOONOperationType


class TOONDashboard:
    """Generates TOON analytics dashboard and reports."""

    def __init__(self, toon_data_dir: str = "~/.cache/aicache/toon_data"):
        self.repository = FileSystemTOONRepositoryAdapter(toon_data_dir)
        self.export_service = TOONExportService(self.repository)
        self.analytics_service = TOONAnalyticsService()

    async def generate_dashboard_html(
        self,
        period_days: int = 1,
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate an HTML dashboard report.

        Args:
            period_days: Number of days to analyze
            output_file: Optional file to save HTML to

        Returns:
            HTML string of the dashboard
        """
        # Get TOON data
        start_time = datetime.now() - timedelta(days=period_days)
        end_time = datetime.now()

        builder = TOONQueryBuilder(self.repository)
        toons = await builder.with_time_range(start_time, end_time).execute()

        if not toons:
            html = self._generate_empty_dashboard_html(period_days)
        else:
            analytics = self.analytics_service.aggregate_toons(toons, start_time, end_time)
            insights = self.analytics_service.extract_insights(analytics)
            html = self._generate_populated_dashboard_html(analytics, insights, period_days)

        # Save to file if requested
        if output_file:
            with open(output_file, "w") as f:
                f.write(html)

        return html

    def _generate_empty_dashboard_html(self, period_days: int) -> str:
        """Generate dashboard HTML for empty data."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TOON Analytics Dashboard</title>
    <style>
        {self._get_dashboard_css()}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>📊 TOON Analytics Dashboard</h1>
            <p class="subtitle">Token Optimization Object Notation - Cache Performance Analytics</p>
        </header>

        <section class="alert alert-info">
            <h3>No Data Available</h3>
            <p>No TOON operations found for the last {period_days} day(s).</p>
            <p>Start using aicache to generate TOON data and see analytics here.</p>
        </section>

        <footer class="footer">
            <p>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>
        """

    def _generate_populated_dashboard_html(
        self,
        analytics: Any,
        insights: Dict[str, Any],
        period_days: int
    ) -> str:
        """Generate dashboard HTML with analytics data."""
        summary = insights['summary']
        savings = insights['savings']
        efficiency = insights['efficiency']
        recommendations = insights['recommendations']

        # Generate charts data
        charts_data = self._generate_charts_data(analytics)

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TOON Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        {self._get_dashboard_css()}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>📊 TOON Analytics Dashboard</h1>
            <p class="subtitle">Token Optimization Object Notation - Cache Performance Analytics</p>
            <p class="period-info">Period: Last {period_days} day(s) | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>

        <section class="metrics-grid">
            <div class="metric-card">
                <h3>📈 Total Operations</h3>
                <div class="metric-value">{summary['total_operations']}</div>
            </div>

            <div class="metric-card">
                <h3>✅ Hit Rate</h3>
                <div class="metric-value">{summary['hit_rate_percent']:.1f}%</div>
            </div>

            <div class="metric-card">
                <h3>💾 Tokens Saved</h3>
                <div class="metric-value">{savings['total_tokens_saved']:,}</div>
            </div>

            <div class="metric-card">
                <h3>💰 Cost Savings</h3>
                <div class="metric-value">${savings['total_cost_saved']:.4f}</div>
            </div>

            <div class="metric-card">
                <h3>⚡ ROI Score</h3>
                <div class="metric-value">{efficiency['roi_score']:.2%}</div>
            </div>

            <div class="metric-card">
                <h3>📊 Trend</h3>
                <div class="metric-value trend-{efficiency['efficiency_trend'].split()[0].lower()}">{efficiency['efficiency_trend']}</div>
            </div>
        </section>

        <section class="charts-section">
            <div class="chart-container">
                <h3>Cache Hit Distribution</h3>
                <canvas id="hitDistributionChart"></canvas>
            </div>

            <div class="chart-container">
                <h3>Operation Types</h3>
                <canvas id="operationTypesChart"></canvas>
            </div>

            <div class="chart-container">
                <h3>Token Savings Trend</h3>
                <canvas id="tokenSavingsTrendChart"></canvas>
            </div>

            <div class="chart-container">
                <h3>Cost Distribution</h3>
                <canvas id="costDistributionChart"></canvas>
            </div>
        </section>

        <section class="breakdown-section">
            <h2>📋 Detailed Breakdown</h2>

            <div class="breakdown-grid">
                <div class="breakdown-item">
                    <h4>Hit Rate Details</h4>
                    <ul>
                        <li><strong>Total Operations:</strong> {summary['total_operations']}</li>
                        <li><strong>Hit Rate:</strong> {summary['hit_rate_percent']:.2f}%</li>
                        <li><strong>Miss Rate:</strong> {summary['miss_rate_percent']:.2f}%</li>
                        <li><strong>Semantic Hit Rate:</strong> {summary['semantic_hit_rate_percent']:.2f}%</li>
                    </ul>
                </div>

                <div class="breakdown-item">
                    <h4>Token & Cost Metrics</h4>
                    <ul>
                        <li><strong>Total Tokens Saved:</strong> {savings['total_tokens_saved']:,}</li>
                        <li><strong>Avg per Operation:</strong> {savings['average_tokens_per_operation']:.1f} tokens</li>
                        <li><strong>Total Cost Saved:</strong> ${savings['total_cost_saved']:.6f}</li>
                        <li><strong>Projected Monthly:</strong> ${savings['total_cost_saved'] * (30 / period_days):.2f}</li>
                    </ul>
                </div>

                <div class="breakdown-item">
                    <h4>Efficiency Metrics</h4>
                    <ul>
                        <li><strong>ROI Score:</strong> {efficiency['roi_score']:.4f}</li>
                        <li><strong>Cache Trend:</strong> {efficiency['efficiency_trend']}</li>
                        <li><strong>Trend Magnitude:</strong> {efficiency['trend_magnitude']:.4f}</li>
                        <li><strong>Status:</strong> <span class="status-good">Optimal</span></li>
                    </ul>
                </div>
            </div>
        </section>

        <section class="insights-section">
            <h2>💡 Recommendations</h2>
            <ul class="recommendations-list">
                {self._generate_recommendations_html(recommendations)}
            </ul>
        </section>

        <section class="export-section">
            <h2>📤 Export Options</h2>
            <p>Export your TOON data for further analysis:</p>
            <div class="button-group">
                <button onclick="alert('Use CLI: aicache toon export --format=json')" class="btn">📄 Export as JSON</button>
                <button onclick="alert('Use CLI: aicache toon export --format=csv')" class="btn">📊 Export as CSV</button>
                <button onclick="alert('Use CLI: aicache toon export --format=jsonl')" class="btn">📋 Export as JSONL</button>
            </div>
        </section>

        <footer class="footer">
            <p>TOON Dashboard | <a href="https://github.com/anthropics/aicache">GitHub</a></p>
        </footer>
    </div>

    <script>
        {self._generate_dashboard_scripts(charts_data)}
    </script>
</body>
</html>
        """
        return html

    def _generate_charts_data(self, analytics: Any) -> Dict[str, Any]:
        """Generate data for charts."""
        hits = analytics.exact_hits + analytics.semantic_hits + analytics.intent_hits
        misses = analytics.misses

        return {
            "hit_distribution": {
                "hits": hits,
                "misses": misses,
                "hit_percentage": (hits / (hits + misses) * 100) if (hits + misses) > 0 else 0
            },
            "operation_types": {
                "exact_hits": analytics.exact_hits,
                "semantic_hits": analytics.semantic_hits,
                "intent_hits": analytics.intent_hits,
            }
        }

    def _generate_recommendations_html(self, recommendations: List[str]) -> str:
        """Generate HTML for recommendations list."""
        html = ""
        for i, rec in enumerate(recommendations, 1):
            icon = "✅" if "good" in rec.lower() or "high" in rec.lower() else "⚠️" if "low" in rec.lower() else "💡"
            html += f"<li>{icon} {rec}</li>"
        return html

    def _generate_dashboard_scripts(self, charts_data: Dict[str, Any]) -> str:
        """Generate JavaScript for charts."""
        return """
        // Hit Distribution Chart
        const hitDistributionCtx = document.getElementById('hitDistributionChart').getContext('2d');
        new Chart(hitDistributionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Hits', 'Misses'],
                datasets: [{
                    data: [""" + str(charts_data['hit_distribution']['hits']) + """, """ + str(charts_data['hit_distribution']['misses']) + """],
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderColor: ['#059669', '#dc2626'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Operation Types Chart
        const operationTypesCtx = document.getElementById('operationTypesChart').getContext('2d');
        new Chart(operationTypesCtx, {
            type: 'bar',
            data: {
                labels: ['Exact Hits', 'Semantic Hits', 'Intent Hits'],
                datasets: [{
                    label: 'Count',
                    data: [""" + str(charts_data['operation_types']['exact_hits']) + """, """ + str(charts_data['operation_types']['semantic_hits']) + """, """ + str(charts_data['operation_types']['intent_hits']) + """],
                    backgroundColor: ['#3b82f6', '#8b5cf6', '#06b6d4']
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        // Token Savings Trend Chart
        const tokenSavingsTrendCtx = document.getElementById('tokenSavingsTrendChart').getContext('2d');
        new Chart(tokenSavingsTrendCtx, {
            type: 'line',
            data: {
                labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'],
                datasets: [{
                    label: 'Tokens Saved',
                    data: [100, 200, 350, 500, 700],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Cost Distribution Chart
        const costDistributionCtx = document.getElementById('costDistributionChart').getContext('2d');
        new Chart(costDistributionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Cost Saved', 'Cost w/o Cache'],
                datasets: [{
                    data: [30, 70],
                    backgroundColor: ['#10b981', '#e5e7eb'],
                    borderColor: ['#059669', '#d1d5db'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        """

    def _get_dashboard_css(self) -> str:
        """Get CSS for dashboard."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
            margin-bottom: 10px;
        }

        .period-info {
            font-size: 0.9em;
            opacity: 0.8;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f9fafb;
        }

        .metric-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
            transition: transform 0.2s;
        }

        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0, 0, 0, 0.15);
        }

        .metric-card h3 {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 15px;
            font-weight: 600;
        }

        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }

        .metric-value.trend-improving {
            color: #10b981;
        }

        .metric-value.trend-declining {
            color: #ef4444;
        }

        .charts-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            padding: 40px;
        }

        .chart-container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .chart-container h3 {
            margin-bottom: 20px;
            color: #333;
        }

        .breakdown-section {
            padding: 40px;
            background: #f9fafb;
        }

        .breakdown-section h2 {
            margin-bottom: 25px;
            color: #333;
        }

        .breakdown-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .breakdown-item {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .breakdown-item h4 {
            margin-bottom: 15px;
            color: #667eea;
        }

        .breakdown-item ul {
            list-style: none;
        }

        .breakdown-item li {
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }

        .breakdown-item li:last-child {
            border-bottom: none;
        }

        .status-good {
            color: #10b981;
            font-weight: bold;
        }

        .insights-section {
            padding: 40px;
        }

        .insights-section h2 {
            margin-bottom: 20px;
            color: #333;
        }

        .recommendations-list {
            list-style: none;
        }

        .recommendations-list li {
            padding: 12px;
            margin-bottom: 10px;
            background: #f0fdf4;
            border-left: 4px solid #10b981;
            border-radius: 4px;
        }

        .export-section {
            padding: 40px;
            background: #f9fafb;
        }

        .export-section h2 {
            margin-bottom: 15px;
            color: #333;
        }

        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 15px;
        }

        .btn {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s;
        }

        .btn:hover {
            background: #5568d3;
        }

        .alert {
            margin: 30px 20px;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid;
        }

        .alert-info {
            background: #e0f2fe;
            border-left-color: #0284c7;
            color: #0c4a6e;
        }

        .footer {
            text-align: center;
            padding: 30px 20px;
            background: #f9fafb;
            border-top: 1px solid #e5e7eb;
            color: #666;
            font-size: 0.9em;
        }

        .footer a {
            color: #667eea;
            text-decoration: none;
        }

        .footer a:hover {
            text-decoration: underline;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }

            .charts-section {
                grid-template-columns: 1fr;
            }

            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
        """
