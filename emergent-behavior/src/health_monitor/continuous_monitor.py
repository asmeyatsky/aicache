"""
Health monitor for aicache self-healing system
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

from ..utils.logger import get_logger

logger = get_logger(__name__)

class HealthIssue:
    """Represents a detected health issue"""
    
    def __init__(
        self,
        issue_id: str,
        issue_type: str,
        description: str,
        severity: str,
        details: Dict[str, Any],
        detected_at: datetime
    ):
        self.issue_id = issue_id
        self.issue_type = issue_type
        self.description = description
        self.severity = severity  # 'low', 'medium', 'high', 'critical'
        self.details = details
        self.detected_at = detected_at
        self.handled = False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'issue_id': self.issue_id,
            'issue_type': self.issue_type,
            'description': self.description,
            'severity': self.severity,
            'details': self.details,
            'detected_at': self.detected_at.isoformat(),
            'handled': self.handled
        }

class ContinuousMonitor:
    """Continuously monitors cache health and performance"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.monitoring_active = False
        self.detected_issues = []
        self.performance_metrics = {}
        self.health_checks = []
        
    async def initialize(self):
        """Initialize the health monitor"""
        logger.info("Initializing continuous health monitor")
        
        # Load monitoring configuration
        self.monitoring_config = self.config.get('monitoring', {})
        self.check_interval = self.monitoring_config.get('check_interval', 30)  # seconds
        self.alert_thresholds = self.monitoring_config.get('alert_thresholds', {})
        
        logger.info("Continuous health monitor initialized")
        
    async def start_monitoring(self):
        """Start continuous monitoring"""
        self.monitoring_active = True
        logger.info("Starting continuous cache health monitoring")
        
        try:
            while self.monitoring_active:
                # Perform health checks
                await self._perform_health_checks()
                
                # Analyze performance metrics
                await self._analyze_performance()
                
                # Detect anomalies
                await self._detect_anomalies()
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
        except asyncio.CancelledError:
            logger.info("Health monitoring cancelled")
        except Exception as e:
            logger.error(f"Error in health monitoring: {e}")
            raise
        finally:
            self.monitoring_active = False
            logger.info("Continuous health monitoring stopped")
            
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        logger.info("Stopping continuous health monitoring")
        
    async def _perform_health_checks(self):
        """Perform comprehensive health checks"""
        try:
            # Cache consistency check
            consistency_issues = await self._check_cache_consistency()
            
            # Data integrity check
            integrity_issues = await self._check_data_integrity()
            
            # Index health check
            index_issues = await self._check_index_health()
            
            # Performance health check
            performance_issues = await self._check_performance_health()
            
            # Combine all issues
            all_issues = consistency_issues + integrity_issues + index_issues + performance_issues
            
            # Add timestamp and severity
            for issue in all_issues:
                issue['detected_at'] = datetime.now().isoformat()
                issue['severity'] = self._assess_severity(issue)
                
            # Store detected issues
            self.detected_issues.extend(all_issues)
            
            if all_issues:
                logger.warning(f"Detected {len(all_issues)} health issues")
                
        except Exception as e:
            logger.error(f"Error performing health checks: {e}")
            
    async def _check_cache_consistency(self) -> List[Dict[str, Any]]:
        """Check cache consistency"""
        issues = []
        
        try:
            # Simulate cache consistency check
            # In a real implementation, this would check:
            # - Cache entry count vs expected count
            # - Cache size vs storage limits
            # - Entry expiration consistency
            # - Reference integrity between cache entries
            
            # For demonstration, randomly generate some issues
            import random
            if random.random() < 0.1:  # 10% chance of consistency issue
                issues.append({
                    'type': 'cache_consistency',
                    'description': 'Cache entry count mismatch detected',
                    'details': {
                        'expected_count': 1000,
                        'actual_count': 985,
                        'difference': -15
                    }
                })
                
        except Exception as e:
            logger.error(f"Error checking cache consistency: {e}")
            
        return issues
        
    async def _check_data_integrity(self) -> List[Dict[str, Any]]:
        """Check data integrity"""
        issues = []
        
        try:
            # Simulate data integrity check
            # In a real implementation, this would check:
            # - Checksum verification of cache entries
            # - Schema validation of stored data
            # - Encoding and serialization consistency
            # - Cryptographic hash verification
            
            # For demonstration, randomly generate some issues
            import random
            if random.random() < 0.05:  # 5% chance of integrity issue
                issues.append({
                    'type': 'data_integrity',
                    'description': 'Checksum mismatch detected in cache entry',
                    'details': {
                        'entry_id': 'entry_12345',
                        'expected_checksum': 'abc123',
                        'actual_checksum': 'def456'
                    }
                })
                
        except Exception as e:
            logger.error(f"Error checking data integrity: {e}")
            
        return issues
        
    async def _check_index_health(self) -> List[Dict[str, Any]]:
        """Check cache index health"""
        issues = []
        
        try:
            # Simulate index health check
            # In a real implementation, this would check:
            # - Index completeness and accuracy
            # - Index fragmentation and optimization
            # - Index update consistency
            # - Search performance of indexes
            
            # For demonstration, randomly generate some issues
            import random
            if random.random() < 0.08:  # 8% chance of index issue
                issues.append({
                    'type': 'index_health',
                    'description': 'Index fragmentation detected',
                    'details': {
                        'fragmentation_level': 0.75,
                        'recommended_action': 'rebuild_index'
                    }
                })
                
        except Exception as e:
            logger.error(f"Error checking index health: {e}")
            
        return issues
        
    async def _check_performance_health(self) -> List[Dict[str, Any]]:
        """Check performance health"""
        issues = []
        
        try:
            # Simulate performance health check
            # In a real implementation, this would check:
            # - Response time degradation
            # - Throughput reduction
            # - Resource utilization patterns
            # - Latency outliers
            
            # Collect performance metrics (simulated)
            await self._collect_performance_metrics()
            
            # Analyze metrics for issues
            if self.performance_metrics:
                avg_response_time = self.performance_metrics.get('avg_response_time', 0)
                cache_hit_rate = self.performance_metrics.get('cache_hit_rate', 1.0)
                
                # Check for performance degradation
                if avg_response_time > 0.5:  # > 500ms average response time
                    issues.append({
                        'type': 'performance_degradation',
                        'description': 'Average response time degradation detected',
                        'details': {
                            'current_avg_response_time': avg_response_time,
                            'threshold': 0.5,
                            'degradation_percentage': ((avg_response_time - 0.5) / 0.5) * 100
                        }
                    })
                    
                if cache_hit_rate < 0.8:  # < 80% cache hit rate
                    issues.append({
                        'type': 'low_cache_hit_rate',
                        'description': 'Cache hit rate below optimal threshold',
                        'details': {
                            'current_hit_rate': cache_hit_rate,
                            'threshold': 0.8,
                            'impact_percentage': ((0.8 - cache_hit_rate) / 0.8) * 100
                        }
                    })
                    
        except Exception as e:
            logger.error(f"Error checking performance health: {e}")
            
        return issues
        
    async def _collect_performance_metrics(self):
        """Collect performance metrics"""
        try:
            # Simulate performance metric collection
            # In a real implementation, this would collect:
            # - Response times for cache operations
            # - Cache hit/miss rates
            # - Memory and CPU utilization
            # - Network latency and throughput
            # - Database query performance
            
            import random
            
            # Generate simulated metrics
            self.performance_metrics = {
                'avg_response_time': random.uniform(0.1, 0.8),
                'cache_hit_rate': random.uniform(0.7, 0.95),
                'memory_utilization': random.uniform(0.3, 0.9),
                'cpu_utilization': random.uniform(0.1, 0.8),
                'disk_io_wait': random.uniform(0.01, 0.2),
                'network_latency': random.uniform(0.05, 0.3)
            }
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            
    async def _analyze_performance(self):
        """Analyze collected performance metrics"""
        try:
            if not self.performance_metrics:
                await self._collect_performance_metrics()
                
            # Store metrics for trend analysis
            metric_record = {
                'timestamp': datetime.now().isoformat(),
                'metrics': self.performance_metrics.copy()
            }
            self.health_checks.append(metric_record)
            
            # Keep only recent metrics (last 1000 checks)
            if len(self.health_checks) > 1000:
                self.health_checks.pop(0)
                
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            
    async def _detect_anomalies(self):
        """Detect anomalies in performance metrics"""
        try:
            if len(self.health_checks) < 10:  # Need minimum data points
                return
                
            # Simple anomaly detection based on standard deviation
            recent_metrics = self.health_checks[-10:]  # Last 10 checks
            
            # Calculate mean and standard deviation for each metric
            import statistics
            metrics_analysis = {}
            for metric_name in self.performance_metrics.keys():
                values = [check['metrics'][metric_name] for check in recent_metrics]
                mean_val = statistics.mean(values)
                std_dev = statistics.stdev(values) if len(values) > 1 else 0
                
                current_value = self.performance_metrics[metric_name]
                z_score = abs((current_value - mean_val) / std_dev) if std_dev > 0 else 0
                
                metrics_analysis[metric_name] = {
                    'current_value': current_value,
                    'mean': mean_val,
                    'std_dev': std_dev,
                    'z_score': z_score,
                    'is_anomaly': z_score > 2.5  # 2.5 standard deviations threshold
                }
                
            # Log anomalies
            anomalies = [metric for metric, analysis in metrics_analysis.items() if analysis['is_anomaly']]
            if anomalies:
                logger.warning(f"Detected anomalies in metrics: {', '.join(anomalies)}")
                
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            
    def _assess_severity(self, issue: Dict[str, Any]) -> str:
        """Assess the severity of a detected issue"""
        issue_type = issue['type']
        details = issue.get('details', {})
        
        # Severity assessment based on issue type and details
        if issue_type == 'data_integrity':
            return 'critical'
        elif issue_type == 'cache_consistency':
            difference = details.get('difference', 0)
            if abs(difference) > 100:
                return 'high'
            elif abs(difference) > 50:
                return 'medium'
            else:
                return 'low'
        elif issue_type == 'performance_degradation':
            degradation = details.get('degradation_percentage', 0)
            if degradation > 50:
                return 'high'
            elif degradation > 25:
                return 'medium'
            else:
                return 'low'
        elif issue_type == 'low_cache_hit_rate':
            impact = details.get('impact_percentage', 0)
            if impact > 30:
                return 'high'
            elif impact > 15:
                return 'medium'
            else:
                return 'low'
        elif issue_type == 'index_health':
            fragmentation = details.get('fragmentation_level', 0)
            if fragmentation > 0.8:
                return 'high'
            elif fragmentation > 0.6:
                return 'medium'
            else:
                return 'low'
        else:
            return 'medium'
            
    async def get_detected_issues(self) -> List[Dict[str, Any]]:
        """Get currently detected issues"""
        return self.detected_issues.copy()
        
    async def clear_handled_issues(self):
        """Clear handled issues from the detected list"""
        self.detected_issues.clear()
        logger.info("Cleared handled issues from detection list")
        
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of current health status"""
        return {
            'status': 'healthy' if not self.detected_issues else 'degraded',
            'issue_count': len(self.detected_issues),
            'critical_issues': len([i for i in self.detected_issues if i.get('severity') == 'critical']),
            'high_severity_issues': len([i for i in self.detected_issues if i.get('severity') == 'high']),
            'last_check': datetime.now().isoformat(),
            'performance_metrics': self.performance_metrics
        }