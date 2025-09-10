"""
Performance analyzer for aicache self-healing system
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import statistics
import numpy as np

from ..utils.logger import get_logger

logger = get_logger(__name__)

class PerformanceAnalyzer:
    """Analyzes cache performance and identifies performance bottlenecks"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.performance_metrics = {}
        self.performance_issues = []
        self.trend_analysis = {}
        
    async def initialize(self):
        """Initialize the performance analyzer"""
        logger.info("Initializing performance analyzer")
        
        # Load performance analysis configuration
        self.analysis_config = self.config.get('performance_analysis', {})
        self.analysis_frequency = self.analysis_config.get('analysis_frequency', 300)  # 5 minutes
        self.trend_window = self.analysis_config.get('trend_window', 3600)  # 1 hour
        self.alert_thresholds = self.analysis_config.get('alert_thresholds', {
            'response_time': 0.5,  # seconds
            'cache_hit_rate': 0.8,  # percentage
            'memory_utilization': 0.9,  # percentage
            'cpu_utilization': 0.8,  # percentage
            'error_rate': 0.01  # percentage
        })
        
        logger.info("Performance analyzer initialized")
        
    async def analyze_performance(self) -> List[Dict[str, Any]]:
        """Analyze cache performance and identify bottlenecks"""
        try:
            logger.info("Performing performance analysis")
            
            # Collect current performance metrics
            current_metrics = await self._collect_performance_metrics()
            
            # Store metrics for trend analysis
            await self._store_metrics_for_trend(current_metrics)
            
            # Analyze performance against thresholds
            performance_issues = await self._analyze_against_thresholds(current_metrics)
            
            # Perform trend analysis
            trend_analysis = await self._analyze_performance_trends()
            
            # Combine issues
            all_issues = performance_issues + trend_analysis.get('issues', [])
            
            # Store detected issues
            self.performance_issues.extend(all_issues)
            
            # Keep only recent issues (last 100)
            if len(self.performance_issues) > 100:
                self.performance_issues = self.performance_issues[-100:]
                
            logger.info(f"Performance analysis completed with {len(all_issues)} issues detected")
            return all_issues
            
        except Exception as e:
            logger.error(f"Error performing performance analysis: {e}")
            raise
            
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics"""
        try:
            # In a real implementation, this would collect:
            # - Response times for cache operations
            # - Cache hit/miss rates
            # - Memory and CPU utilization
            # - Network latency and throughput
            # - Database query performance
            # - Error rates and failure counts
            
            # For demonstration, simulate metric collection
            import random
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'response_time': random.uniform(0.05, 0.8),  # seconds
                'cache_hit_rate': random.uniform(0.7, 0.95),  # percentage
                'memory_utilization': random.uniform(0.2, 0.95),  # percentage
                'cpu_utilization': random.uniform(0.1, 0.85),  # percentage
                'network_latency': random.uniform(0.01, 0.3),  # seconds
                'disk_io_wait': random.uniform(0.001, 0.1),  # seconds
                'error_rate': random.uniform(0.0, 0.02),  # percentage
                'throughput': random.uniform(50, 500),  # requests per second
                'concurrent_users': random.randint(5, 100),
                'queue_length': random.randint(0, 20)
            }
            
            # Store metrics
            self.performance_metrics = metrics
            
            logger.debug(f"Collected performance metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            raise
            
    async def _store_metrics_for_trend(self, metrics: Dict[str, Any]):
        """Store metrics for trend analysis"""
        try:
            # In a real implementation, this would:
            # - Store metrics in time-series database
            # - Maintain sliding window of historical metrics
            # - Calculate moving averages and trends
            
            # For now, store in memory
            if 'historical_metrics' not in self.trend_analysis:
                self.trend_analysis['historical_metrics'] = []
                
            self.trend_analysis['historical_metrics'].append(metrics)
            
            # Keep only recent metrics (last 1000 entries)
            if len(self.trend_analysis['historical_metrics']) > 1000:
                self.trend_analysis['historical_metrics'] = self.trend_analysis['historical_metrics'][-1000:]
                
        except Exception as e:
            logger.error(f"Error storing metrics for trend: {e}")
            
    async def _analyze_against_thresholds(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze performance against configured thresholds"""
        try:
            issues = []
            
            # Response time analysis
            response_time = metrics.get('response_time', 0)
            threshold = self.alert_thresholds.get('response_time', 0.5)
            if response_time > threshold:
                severity = 'high' if response_time > threshold * 1.5 else 'medium'
                issues.append({
                    'type': 'high_response_time',
                    'description': f'Response time degradation detected: {response_time:.3f}s (threshold: {threshold:.3f}s)',
                    'severity': severity,
                    'details': {
                        'current_response_time': response_time,
                        'threshold': threshold,
                        'degradation_percentage': ((response_time - threshold) / threshold) * 100
                    },
                    'detected_at': metrics['timestamp']
                })
                
            # Cache hit rate analysis
            cache_hit_rate = metrics.get('cache_hit_rate', 1.0)
            threshold = self.alert_thresholds.get('cache_hit_rate', 0.8)
            if cache_hit_rate < threshold:
                severity = 'high' if cache_hit_rate < threshold * 0.5 else 'medium'
                issues.append({
                    'type': 'low_cache_hit_rate',
                    'description': f'Cache hit rate below threshold: {cache_hit_rate:.3f} (threshold: {threshold:.3f})',
                    'severity': severity,
                    'details': {
                        'current_hit_rate': cache_hit_rate,
                        'threshold': threshold,
                        'impact_percentage': ((threshold - cache_hit_rate) / threshold) * 100
                    },
                    'detected_at': metrics['timestamp']
                })
                
            # Memory utilization analysis
            memory_utilization = metrics.get('memory_utilization', 0)
            threshold = self.alert_thresholds.get('memory_utilization', 0.9)
            if memory_utilization > threshold:
                severity = 'critical' if memory_utilization > 0.95 else 'high'
                issues.append({
                    'type': 'high_memory_utilization',
                    'description': f'Memory utilization high: {memory_utilization:.3f} (threshold: {threshold:.3f})',
                    'severity': severity,
                    'details': {
                        'current_utilization': memory_utilization,
                        'threshold': threshold,
                        'utilization_percentage': memory_utilization * 100
                    },
                    'detected_at': metrics['timestamp']
                })
                
            # CPU utilization analysis
            cpu_utilization = metrics.get('cpu_utilization', 0)
            threshold = self.alert_thresholds.get('cpu_utilization', 0.8)
            if cpu_utilization > threshold:
                severity = 'high' if cpu_utilization > 0.9 else 'medium'
                issues.append({
                    'type': 'high_cpu_utilization',
                    'description': f'CPU utilization high: {cpu_utilization:.3f} (threshold: {threshold:.3f})',
                    'severity': severity,
                    'details': {
                        'current_utilization': cpu_utilization,
                        'threshold': threshold,
                        'utilization_percentage': cpu_utilization * 100
                    },
                    'detected_at': metrics['timestamp']
                })
                
            # Error rate analysis
            error_rate = metrics.get('error_rate', 0)
            threshold = self.alert_thresholds.get('error_rate', 0.01)
            if error_rate > threshold:
                severity = 'critical' if error_rate > threshold * 2 else 'high'
                issues.append({
                    'type': 'high_error_rate',
                    'description': f'Error rate elevated: {error_rate:.4f} (threshold: {threshold:.4f})',
                    'severity': severity,
                    'details': {
                        'current_error_rate': error_rate,
                        'threshold': threshold,
                        'error_percentage': error_rate * 100
                    },
                    'detected_at': metrics['timestamp']
                })
                
            return issues
            
        except Exception as e:
            logger.error(f"Error analyzing performance against thresholds: {e}")
            return []
            
    async def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        try:
            # Get historical metrics
            if 'historical_metrics' not in self.trend_analysis:
                return {'issues': [], 'trends': {}}
                
            historical_metrics = self.trend_analysis['historical_metrics']
            
            if len(historical_metrics) < 10:  # Need minimum data points
                return {'issues': [], 'trends': {}}
                
            # Calculate trends for key metrics
            trends = {}
            issues = []
            
            # Response time trend
            response_times = [m['response_time'] for m in historical_metrics[-10:]]
            response_time_trend = self._calculate_trend(response_times)
            trends['response_time'] = response_time_trend
            
            # Check for concerning trends
            if response_time_trend['slope'] > 0.01:  # Increasing trend
                issues.append({
                    'type': 'response_time_trend',
                    'description': f'Response time showing increasing trend: {response_time_trend["slope"]:.4f}',
                    'severity': 'medium',
                    'details': {
                        'current_value': response_times[-1],
                        'trend_slope': response_time_trend['slope'],
                        'trend_direction': 'increasing' if response_time_trend['slope'] > 0 else 'decreasing'
                    },
                    'detected_at': datetime.now().isoformat()
                })
                
            # Cache hit rate trend
            hit_rates = [m['cache_hit_rate'] for m in historical_metrics[-10:]]
            hit_rate_trend = self._calculate_trend(hit_rates)
            trends['cache_hit_rate'] = hit_rate_trend
            
            # Check for concerning trends
            if hit_rate_trend['slope'] < -0.01:  # Decreasing trend
                issues.append({
                    'type': 'hit_rate_trend',
                    'description': f'Cache hit rate showing decreasing trend: {hit_rate_trend["slope"]:.4f}',
                    'severity': 'medium',
                    'details': {
                        'current_value': hit_rates[-1],
                        'trend_slope': hit_rate_trend['slope'],
                        'trend_direction': 'increasing' if hit_rate_trend['slope'] > 0 else 'decreasing'
                    },
                    'detected_at': datetime.now().isoformat()
                })
                
            # Memory utilization trend
            memory_utilizations = [m['memory_utilization'] for m in historical_metrics[-10:]]
            memory_trend = self._calculate_trend(memory_utilizations)
            trends['memory_utilization'] = memory_trend
            
            # Check for concerning trends
            if memory_trend['slope'] > 0.02:  # Rapidly increasing trend
                issues.append({
                    'type': 'memory_utilization_trend',
                    'description': f'Memory utilization showing rapidly increasing trend: {memory_trend["slope"]:.4f}',
                    'severity': 'high',
                    'details': {
                        'current_value': memory_utilizations[-1],
                        'trend_slope': memory_trend['slope'],
                        'trend_direction': 'increasing' if memory_trend['slope'] > 0 else 'decreasing'
                    },
                    'detected_at': datetime.now().isoformat()
                })
                
            return {
                'issues': issues,
                'trends': trends
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return {'issues': [], 'trends': {}}
            
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate linear trend for a series of values"""
        try:
            if len(values) < 2:
                return {'slope': 0, 'r_squared': 0}
                
            # Calculate linear regression
            x = list(range(len(values)))
            slope, intercept = np.polyfit(x, values, 1)
            
            # Calculate R-squared
            y_pred = [slope * xi + intercept for xi in x]
            ss_res = sum((yi - ypi) ** 2 for yi, ypi in zip(values, y_pred))
            ss_tot = sum((yi - statistics.mean(values)) ** 2 for yi in values)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            return {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_squared,
                'correlation': 'positive' if slope > 0 else 'negative' if slope < 0 else 'neutral'
            }
            
        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return {'slope': 0, 'r_squared': 0}
            
    async def get_performance_issues(self) -> List[Dict[str, Any]]:
        """Get detected performance issues"""
        return self.performance_issues.copy()
        
    async def clear_resolved_issues(self):
        """Clear resolved performance issues"""
        self.performance_issues.clear()
        logger.info("Cleared resolved performance issues")
        
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report"""
        try:
            # Calculate statistics
            total_issues = len(self.performance_issues)
            critical_issues = len([i for i in self.performance_issues if i['severity'] == 'critical'])
            high_issues = len([i for i in self.performance_issues if i['severity'] == 'high'])
            medium_issues = len([i for i in self.performance_issues if i['severity'] == 'medium'])
            low_issues = len([i for i in self.performance_issues if i['severity'] == 'low'])
            
            # Calculate issue types distribution
            issue_types = {}
            for issue in self.performance_issues:
                issue_type = issue['type']
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
                
            # Get current metrics
            current_metrics = self.performance_metrics.copy() if self.performance_metrics else {}
            
            # Get trend analysis
            trend_analysis = self.trend_analysis.get('trends', {})
            
            report = {
                'total_issues': total_issues,
                'critical_issues': critical_issues,
                'high_issues': high_issues,
                'medium_issues': medium_issues,
                'low_issues': low_issues,
                'issue_types_distribution': issue_types,
                'current_metrics': current_metrics,
                'trend_analysis': trend_analysis,
                'last_analysis': datetime.now().isoformat(),
                'analysis_frequency': self.analysis_frequency
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {
                'total_issues': 0,
                'critical_issues': 0,
                'high_issues': 0,
                'medium_issues': 0,
                'low_issues': 0,
                'issue_types_distribution': {},
                'current_metrics': {},
                'trend_analysis': {},
                'last_analysis': datetime.now().isoformat(),
                'analysis_frequency': self.analysis_frequency
            }