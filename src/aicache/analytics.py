"""
Advanced analytics and optimization for aicache.
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
import threading
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Individual performance measurement."""
    timestamp: float
    metric_name: str
    value: float
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class OptimizationRecommendation:
    """Cache optimization recommendation."""
    type: str  # 'threshold_adjustment', 'eviction_policy', 'storage_optimization'
    priority: str  # 'low', 'medium', 'high', 'critical'
    title: str
    description: str
    current_value: Any
    recommended_value: Any
    expected_improvement: str
    implementation_effort: str  # 'low', 'medium', 'high'

class TimeSeriesBuffer:
    """Circular buffer for time series data."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        self._lock = threading.RLock()
    
    def add(self, metric: PerformanceMetric):
        """Add a new metric to the buffer."""
        with self._lock:
            self.buffer.append(metric)
    
    def get_recent(self, seconds: int = 3600) -> List[PerformanceMetric]:
        """Get metrics from the last N seconds."""
        cutoff = time.time() - seconds
        with self._lock:
            return [m for m in self.buffer if m.timestamp >= cutoff]
    
    def get_all(self) -> List[PerformanceMetric]:
        """Get all metrics in buffer."""
        with self._lock:
            return list(self.buffer)

class CacheAnalyzer:
    """Analyzes cache performance and provides insights."""
    
    def __init__(self, cache):
        self.cache = cache
        self.metrics_buffer = TimeSeriesBuffer()
        self.cost_models = {
            'gpt-4': {'input': 0.03, 'output': 0.06},  # per 1K tokens
            'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
            'claude-3': {'input': 0.015, 'output': 0.075},
            'gemini-pro': {'input': 0.001, 'output': 0.002}
        }
        
    def record_cache_hit(self, cache_type: str, response_time: float, 
                        context: Dict[str, Any] = None):
        """Record a cache hit event."""
        metric = PerformanceMetric(
            timestamp=time.time(),
            metric_name=f"cache_hit_{cache_type}",
            value=response_time,
            context=context or {}
        )
        self.metrics_buffer.add(metric)
    
    def record_cache_miss(self, response_time: float, cost: float = 0.0,
                         context: Dict[str, Any] = None):
        """Record a cache miss event."""
        metrics = [
            PerformanceMetric(
                timestamp=time.time(),
                metric_name="cache_miss",
                value=response_time,
                context=context or {}
            ),
            PerformanceMetric(
                timestamp=time.time(),
                metric_name="api_cost",
                value=cost,
                context=context or {}
            )
        ]
        
        for metric in metrics:
            self.metrics_buffer.add(metric)
    
    def calculate_hit_rate(self, hours: int = 24) -> Dict[str, float]:
        """Calculate hit rates for different time periods."""
        recent_metrics = self.metrics_buffer.get_recent(hours * 3600)
        
        hit_counts = defaultdict(int)
        miss_count = 0
        
        for metric in recent_metrics:
            if metric.metric_name.startswith('cache_hit'):
                cache_type = metric.metric_name.split('_')[-1]
                hit_counts[cache_type] += 1
            elif metric.metric_name == 'cache_miss':
                miss_count += 1
        
        total_hits = sum(hit_counts.values())
        total_requests = total_hits + miss_count
        
        if total_requests == 0:
            return {'overall': 0.0, 'exact': 0.0, 'semantic': 0.0}
        
        return {
            'overall': total_hits / total_requests,
            'exact': hit_counts['exact'] / total_requests,
            'semantic': hit_counts['semantic'] / total_requests,
            'total_requests': total_requests
        }
    
    def calculate_cost_savings(self, hours: int = 24) -> Dict[str, float]:
        """Calculate cost savings from caching."""
        recent_metrics = self.metrics_buffer.get_recent(hours * 3600)
        
        total_cost = 0.0
        cache_hits = 0
        
        for metric in recent_metrics:
            if metric.metric_name == 'api_cost':
                total_cost += metric.value
            elif metric.metric_name.startswith('cache_hit'):
                cache_hits += 1
                # Estimate cost that would have been incurred
                model = metric.context.get('model', 'gpt-3.5-turbo')
                estimated_cost = self._estimate_query_cost(model, metric.context)
                total_cost += estimated_cost  # This represents saved cost
        
        return {
            'total_saved': total_cost,
            'saved_requests': cache_hits,
            'avg_cost_per_request': total_cost / cache_hits if cache_hits > 0 else 0.0
        }
    
    def _estimate_query_cost(self, model: str, context: Dict[str, Any]) -> float:
        """Estimate cost of a query based on model and context."""
        if model not in self.cost_models:
            return 1.0  # Default estimate
        
        # Rough estimation based on prompt length
        prompt_length = len(context.get('prompt', ''))
        estimated_tokens = prompt_length / 4  # Rough approximation
        
        cost_per_1k = self.cost_models[model]['input']
        return (estimated_tokens / 1000) * cost_per_1k
    
    def analyze_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        recent_metrics = self.metrics_buffer.get_recent(hours * 3600)
        
        if not recent_metrics:
            return {'trend': 'insufficient_data'}
        
        # Group metrics by hour
        hourly_stats = defaultdict(lambda: {'hits': 0, 'misses': 0, 'response_times': []})
        
        for metric in recent_metrics:
            hour = int(metric.timestamp // 3600)
            
            if metric.metric_name.startswith('cache_hit'):
                hourly_stats[hour]['hits'] += 1
                hourly_stats[hour]['response_times'].append(metric.value)
            elif metric.metric_name == 'cache_miss':
                hourly_stats[hour]['misses'] += 1
                hourly_stats[hour]['response_times'].append(metric.value)
        
        # Calculate trends
        hit_rates = []
        avg_response_times = []
        
        for hour in sorted(hourly_stats.keys()):
            stats = hourly_stats[hour]
            total_requests = stats['hits'] + stats['misses']
            
            if total_requests > 0:
                hit_rate = stats['hits'] / total_requests
                hit_rates.append(hit_rate)
                
                if stats['response_times']:
                    avg_response_time = np.mean(stats['response_times'])
                    avg_response_times.append(avg_response_time)
        
        # Calculate trends using linear regression
        trend_analysis = {}
        
        if len(hit_rates) >= 2:
            x = np.arange(len(hit_rates))
            hit_rate_trend = np.polyfit(x, hit_rates, 1)[0]  # Slope of the trend
            trend_analysis['hit_rate_trend'] = 'improving' if hit_rate_trend > 0.01 else 'declining' if hit_rate_trend < -0.01 else 'stable'
        
        if len(avg_response_times) >= 2:
            x = np.arange(len(avg_response_times))
            response_time_trend = np.polyfit(x, avg_response_times, 1)[0]
            trend_analysis['response_time_trend'] = 'improving' if response_time_trend < -0.01 else 'declining' if response_time_trend > 0.01 else 'stable'
        
        return {
            'trend': trend_analysis,
            'current_hit_rate': hit_rates[-1] if hit_rates else 0.0,
            'current_response_time': avg_response_times[-1] if avg_response_times else 0.0,
            'data_points': len(hit_rates)
        }
    
    def identify_optimization_opportunities(self) -> List[OptimizationRecommendation]:
        """Identify cache optimization opportunities."""
        recommendations = []
        
        # Analyze current performance
        hit_rates = self.calculate_hit_rate(24)
        trends = self.analyze_performance_trends(24)
        cache_stats = self.cache.get_stats()
        
        # Check hit rate thresholds
        if hit_rates['overall'] < 0.3:
            recommendations.append(OptimizationRecommendation(
                type='threshold_adjustment',
                priority='high',
                title='Low Cache Hit Rate',
                description='Overall cache hit rate is below 30%, indicating poor cache effectiveness',
                current_value=f"{hit_rates['overall']:.1%}",
                recommended_value='50%+',
                expected_improvement='Reduce API costs by 20-40%',
                implementation_effort='low'
            ))
        
        # Check semantic vs exact hit distribution
        if hit_rates['semantic'] / hit_rates['overall'] < 0.2 and hit_rates['overall'] > 0:
            recommendations.append(OptimizationRecommendation(
                type='threshold_adjustment',
                priority='medium',
                title='Low Semantic Cache Utilization',
                description='Semantic cache is contributing less than 20% of hits. Consider lowering similarity threshold.',
                current_value='0.85 (assumed)',
                recommended_value='0.80',
                expected_improvement='Increase hit rate by 10-15%',
                implementation_effort='low'
            ))
        
        # Check cache size and storage efficiency
        storage_stats = cache_stats.get('storage', {})
        if storage_stats.get('total_size', 0) > 500 * 1024 * 1024:  # > 500MB
            compression_ratio = storage_stats.get('avg_compression', 1.0)
            if compression_ratio > 0.7:
                recommendations.append(OptimizationRecommendation(
                    type='storage_optimization',
                    priority='medium',
                    title='Improve Compression',
                    description='Cache is large but compression ratio could be improved',
                    current_value=f"{compression_ratio:.2f}",
                    recommended_value='<0.5',
                    expected_improvement='Reduce storage by 20-30%',
                    implementation_effort='medium'
                ))
        
        # Check for expired entries
        expired_count = storage_stats.get('expired_entries', 0)
        total_entries = storage_stats.get('total_entries', 0)
        if expired_count > 0.2 * total_entries and total_entries > 0:
            recommendations.append(OptimizationRecommendation(
                type='eviction_policy',
                priority='medium',
                title='High Expired Entry Ratio',
                description='More than 20% of cache entries are expired. Consider more aggressive pruning.',
                current_value=f"{expired_count} / {total_entries}",
                recommended_value='<10% expired',
                expected_improvement='Improve cache efficiency',
                implementation_effort='low'
            ))
        
        # Check performance trends
        if trends.get('trend', {}).get('hit_rate_trend') == 'declining':
            recommendations.append(OptimizationRecommendation(
                type='threshold_adjustment',
                priority='high',
                title='Declining Hit Rate Trend',
                description='Cache hit rate has been declining over the past 24 hours',
                current_value='Declining trend detected',
                recommended_value='Stable or improving',
                expected_improvement='Prevent further performance degradation',
                implementation_effort='medium'
            ))
        
        return recommendations

class DashboardData:
    """Generates data for analytics dashboard."""
    
    def __init__(self, cache, analyzer: CacheAnalyzer):
        self.cache = cache
        self.analyzer = analyzer
    
    def get_overview_data(self) -> Dict[str, Any]:
        """Get high-level overview data for dashboard."""
        hit_rates = self.analyzer.calculate_hit_rate(24)
        cost_savings = self.analyzer.calculate_cost_savings(24)
        trends = self.analyzer.analyze_performance_trends(24)
        cache_stats = self.cache.get_stats()
        
        return {
            'performance': {
                'hit_rate_24h': hit_rates['overall'],
                'exact_hit_rate': hit_rates['exact'],
                'semantic_hit_rate': hit_rates['semantic'],
                'total_requests': hit_rates.get('total_requests', 0),
                'trend': trends.get('trend', {})
            },
            'cost_savings': {
                'total_saved_24h': cost_savings['total_saved'],
                'saved_requests': cost_savings['saved_requests'],
                'avg_cost_per_request': cost_savings['avg_cost_per_request']
            },
            'storage': cache_stats.get('storage', {}),
            'semantic_cache': cache_stats.get('semantic_cache', {}),
            'last_updated': time.time()
        }
    
    def get_detailed_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get detailed metrics for analysis."""
        recent_metrics = self.analyzer.metrics_buffer.get_recent(hours * 3600)
        
        # Group by metric type
        grouped_metrics = defaultdict(list)
        for metric in recent_metrics:
            grouped_metrics[metric.metric_name].append(metric)
        
        # Prepare time series data
        time_series = {}
        for metric_name, metrics in grouped_metrics.items():
            time_series[metric_name] = [
                {'timestamp': m.timestamp, 'value': m.value, 'context': m.context}
                for m in sorted(metrics, key=lambda x: x.timestamp)
            ]
        
        return {
            'time_series': time_series,
            'total_metrics': len(recent_metrics),
            'metric_types': list(grouped_metrics.keys()),
            'time_range': {
                'start': min(m.timestamp for m in recent_metrics) if recent_metrics else 0,
                'end': max(m.timestamp for m in recent_metrics) if recent_metrics else 0
            }
        }
    
    def get_optimization_dashboard(self) -> Dict[str, Any]:
        """Get optimization recommendations and analysis."""
        recommendations = self.analyzer.identify_optimization_opportunities()
        
        # Group by priority
        by_priority = defaultdict(list)
        for rec in recommendations:
            by_priority[rec.priority].append(asdict(rec))
        
        return {
            'recommendations': {
                'critical': by_priority['critical'],
                'high': by_priority['high'],
                'medium': by_priority['medium'],
                'low': by_priority['low']
            },
            'total_recommendations': len(recommendations),
            'priority_counts': {
                'critical': len(by_priority['critical']),
                'high': len(by_priority['high']),
                'medium': len(by_priority['medium']),
                'low': len(by_priority['low'])
            }
        }

class AnalyticsExporter:
    """Exports analytics data to various formats."""
    
    def __init__(self, dashboard_data: DashboardData):
        self.dashboard_data = dashboard_data
    
    def export_json(self, filepath: str, hours: int = 24):
        """Export analytics data to JSON file."""
        data = {
            'overview': self.dashboard_data.get_overview_data(),
            'detailed_metrics': self.dashboard_data.get_detailed_metrics(hours),
            'optimization': self.dashboard_data.get_optimization_dashboard(),
            'export_timestamp': time.time(),
            'export_hours': hours
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_csv_metrics(self, filepath: str, hours: int = 24):
        """Export metrics to CSV format."""
        import csv
        
        detailed_metrics = self.dashboard_data.get_detailed_metrics(hours)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'metric_name', 'value', 'context'])
            
            for metric_name, metrics in detailed_metrics['time_series'].items():
                for metric in metrics:
                    writer.writerow([
                        metric['timestamp'],
                        metric_name,
                        metric['value'],
                        json.dumps(metric['context'])
                    ])
    
    def generate_report(self, filepath: str):
        """Generate a text-based performance report."""
        overview = self.dashboard_data.get_overview_data()
        optimization = self.dashboard_data.get_optimization_dashboard()
        
        with open(filepath, 'w') as f:
            f.write("# aicache Performance Report\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Performance overview
            f.write("## Performance Overview (24h)\n\n")
            perf = overview['performance']
            f.write(f"- Overall Hit Rate: {perf['hit_rate_24h']:.1%}\n")
            f.write(f"- Exact Matches: {perf['exact_hit_rate']:.1%}\n")
            f.write(f"- Semantic Matches: {perf['semantic_hit_rate']:.1%}\n")
            f.write(f"- Total Requests: {perf['total_requests']}\n\n")
            
            # Cost savings
            f.write("## Cost Savings\n\n")
            cost = overview['cost_savings']
            f.write(f"- Total Saved (24h): ${cost['total_saved_24h']:.2f}\n")
            f.write(f"- Requests Saved: {cost['saved_requests']}\n")
            f.write(f"- Avg Cost per Request: ${cost['avg_cost_per_request']:.3f}\n\n")
            
            # Storage info
            f.write("## Storage Statistics\n\n")
            storage = overview['storage']
            f.write(f"- Total Entries: {storage.get('total_entries', 0)}\n")
            f.write(f"- Total Size: {storage.get('total_size', 0) / 1024 / 1024:.1f} MB\n")
            f.write(f"- Avg Compression: {storage.get('avg_compression', 1.0):.2f}\n\n")
            
            # Recommendations
            f.write("## Optimization Recommendations\n\n")
            recs = optimization['recommendations']
            
            for priority in ['critical', 'high', 'medium', 'low']:
                if recs[priority]:
                    f.write(f"### {priority.title()} Priority\n\n")
                    for rec in recs[priority]:
                        f.write(f"**{rec['title']}**\n")
                        f.write(f"{rec['description']}\n")
                        f.write(f"- Current: {rec['current_value']}\n")
                        f.write(f"- Recommended: {rec['recommended_value']}\n")
                        f.write(f"- Expected Improvement: {rec['expected_improvement']}\n\n")

# Factory function for easy instantiation
def create_analytics_system(cache) -> Tuple[CacheAnalyzer, DashboardData, AnalyticsExporter]:
    """Create a complete analytics system for the given cache."""
    analyzer = CacheAnalyzer(cache)
    dashboard = DashboardData(cache, analyzer)
    exporter = AnalyticsExporter(dashboard)
    
    return analyzer, dashboard, exporter