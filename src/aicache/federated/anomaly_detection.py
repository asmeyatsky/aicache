"""
Anomaly detection system for aicache using federated learning.
Detects bugs, security vulnerabilities, and performance issues.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib

from . import FederatedLearningClient, FederatedModelUpdate, GlobalModel

logger = logging.getLogger(__name__)

@dataclass
class Anomaly:
    """Represents a detected anomaly."""
    anomaly_id: str
    type: str  # 'bug', 'security_vulnerability', 'performance_issue'
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    context: Dict[str, Any]
    confidence: float
    timestamp: float
    affected_components: List[str]

@dataclass
class AnomalyPattern:
    """Represents a pattern of anomalies."""
    pattern_id: str
    pattern_hash: str
    type: str
    examples: List[Dict[str, Any]]
    frequency: int
    first_seen: float
    last_seen: float

class AnomalyDetector:
    """Anomaly detection system using federated learning."""
    
    def __init__(self, client_id: str, server_url: str):
        self.client = FederatedLearningClient(client_id, server_url)
        self.detected_anomalies = []
        self.anomaly_patterns = {}
        self.local_training_data = []
        
    async def initialize(self, global_weights: Dict[str, Any]):
        """Initialize the anomaly detector."""
        await self.client.initialize_local_model(global_weights)
        logger.info("Anomaly detector initialized")
        
    async def detect_anomalies(self, data: Dict[str, Any]) -> List[Anomaly]:
        """Detect anomalies in the provided data."""
        # Extract features from data
        features = self._extract_features(data)
        
        # Detect anomalies using local model
        anomalies = await self._detect_local_anomalies(features)
        
        # Store detected anomalies
        self.detected_anomalies.extend(anomalies)
        
        # Log for training data
        self.local_training_data.append({
            'data': data,
            'features': features,
            'detected_anomalies': [self._anomaly_to_dict(a) for a in anomalies],
            'timestamp': asyncio.get_event_loop().time()
        })
        
        return anomalies
        
    def _extract_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from data for anomaly detection."""
        features = {}
        
        # Code-related features
        features['code_length'] = len(data.get('code', ''))
        features['function_count'] = len(data.get('functions', []))
        features['class_count'] = len(data.get('classes', []))
        features['import_count'] = len(data.get('imports', []))
        
        # Error-related features
        features['error_count'] = len(data.get('errors', []))
        features['warning_count'] = len(data.get('warnings', []))
        
        # Performance features
        features['execution_time'] = data.get('execution_time', 0)
        features['memory_usage'] = data.get('memory_usage', 0)
        
        # Context features
        features['language'] = data.get('language', 'unknown')
        features['framework'] = data.get('framework', 'unknown')
        
        return features
        
    async def _detect_local_anomalies(self, features: Dict[str, Any]) -> List[Anomaly]:
        """Detect anomalies using local model."""
        # In practice, this would use the trained model
        # For now, we'll use rule-based detection with some randomness
        
        anomalies = []
        import time
        
        # Rule-based anomaly detection
        if features.get('error_count', 0) > 5:
            anomalies.append(Anomaly(
                anomaly_id=hashlib.sha256(f"error_{time.time()}".encode()).hexdigest()[:16],
                type='bug',
                severity='high',
                description=f"High number of errors detected ({features['error_count']})",
                context=features,
                confidence=0.8,
                timestamp=time.time(),
                affected_components=['code_quality']
            ))
            
        if features.get('execution_time', 0) > 10.0:  # 10 seconds
            anomalies.append(Anomaly(
                anomaly_id=hashlib.sha256(f"performance_{time.time()}".encode()).hexdigest()[:16],
                type='performance_issue',
                severity='medium',
                description=f"Slow execution time detected ({features['execution_time']}s)",
                context=features,
                confidence=0.7,
                timestamp=time.time(),
                affected_components=['performance']
            ))
            
        # Check for common security patterns (simplified)
        if features.get('import_count', 0) > 50:
            anomalies.append(Anomaly(
                anomaly_id=hashlib.sha256(f"security_{time.time()}".encode()).hexdigest()[:16],
                type='security_vulnerability',
                severity='low',
                description=f"High number of imports may indicate dependency issues",
                context=features,
                confidence=0.6,
                timestamp=time.time(),
                affected_components=['security']
            ))
            
        return anomalies
        
    def _anomaly_to_dict(self, anomaly: Anomaly) -> Dict[str, Any]:
        """Convert Anomaly to dictionary."""
        return {
            'anomaly_id': anomaly.anomaly_id,
            'type': anomaly.type,
            'severity': anomaly.severity,
            'description': anomaly.description,
            'context': anomaly.context,
            'confidence': anomaly.confidence,
            'timestamp': anomaly.timestamp,
            'affected_components': anomaly.affected_components
        }
        
    async def report_anomaly(self, anomaly: Anomaly):
        """Report an anomaly for global learning."""
        # In practice, this would send the anomaly to the global system
        # For now, we'll just log it
        logger.info(f"Anomaly reported: {anomaly.type} - {anomaly.description}")
        
    async def identify_patterns(self) -> List[AnomalyPattern]:
        """Identify patterns in detected anomalies."""
        if not self.detected_anomalies:
            return []
            
        # Group anomalies by type and context
        pattern_groups = defaultdict(list)
        for anomaly in self.detected_anomalies:
            # Create a simple pattern key
            pattern_key = f"{anomaly.type}_{anomaly.context.get('language', 'unknown')}"
            pattern_groups[pattern_key].append(anomaly)
            
        # Create pattern objects
        patterns = []
        import time
        
        for pattern_key, anomalies in pattern_groups.items():
            if len(anomalies) >= 2:  # Need at least 2 occurrences to form a pattern
                pattern_hash = hashlib.sha256(pattern_key.encode()).hexdigest()[:16]
                pattern_id = hashlib.sha256(f"pattern_{time.time()}".encode()).hexdigest()[:16]
                
                patterns.append(AnomalyPattern(
                    pattern_id=pattern_id,
                    pattern_hash=pattern_hash,
                    type=anomalies[0].type,
                    examples=[self._anomaly_to_dict(a) for a in anomalies[:5]],  # Limit to 5 examples
                    frequency=len(anomalies),
                    first_seen=min(a.timestamp for a in anomalies),
                    last_seen=max(a.timestamp for a in anomalies)
                ))
                
        return patterns
        
    async def train_local_model(self):
        """Train local model on accumulated anomaly data."""
        if not self.local_training_data:
            logger.info("No training data available")
            return
            
        # Prepare training data
        training_data = self._prepare_training_data()
        
        # Train local model
        updated_weights = await self.client.train_local_model(training_data)
        
        logger.info("Local anomaly detection model trained successfully")
        return updated_weights
        
    def _prepare_training_data(self) -> List[Dict[str, Any]]:
        """Prepare training data from local anomalies."""
        # In practice, this would convert anomalies to training samples
        # For now, we'll create dummy training data
        training_data = []
        
        for interaction in self.local_training_data:
            if 'detected_anomalies' in interaction:
                # Create training samples from anomalies
                for anomaly in interaction['detected_anomalies']:
                    sample = {
                        'features': interaction.get('features', {}),
                        'target': 1.0,  # Anomaly detected
                        'weight': anomaly.get('confidence', 0.5)
                    }
                    training_data.append(sample)
                    
        return training_data
        
    async def create_model_update(self) -> FederatedModelUpdate:
        """Create model update for federated learning."""
        return await self.client.create_model_update()
        
    async def update_local_model(self, global_weights: Dict[str, Any]):
        """Update local model with global weights."""
        await self.client.update_local_model(global_weights)

# Global anomaly detection service (server-side)
class GlobalAnomalyService:
    """Global service for coordinating anomaly detection across users."""
    
    def __init__(self, federated_server):
        self.federated_server = federated_server
        self.global_patterns = {}  # In practice, this would be a database
        self.threat_intelligence = {}
        
    async def initialize_patterns(self):
        """Initialize known anomaly patterns."""
        # Sample patterns - in practice, this would be populated from various sources
        self.global_patterns = {
            'sql_injection_pattern': {
                'type': 'security_vulnerability',
                'description': 'Common SQL injection patterns',
                'severity': 'high',
                'indicators': ['SELECT * FROM', 'DROP TABLE', 'UNION SELECT']
            },
            'memory_leak_pattern': {
                'type': 'performance_issue',
                'description': 'Memory leak patterns in code',
                'severity': 'high',
                'indicators': ['malloc without free', 'circular references']
            }
        }
        
        logger.info("Global anomaly patterns initialized")
        
    async def submit_pattern(self, pattern: AnomalyPattern):
        """Submit a new pattern to the global database."""
        self.global_patterns[pattern.pattern_hash] = {
            'pattern': pattern,
            'reports': 1,
            'first_seen': pattern.first_seen,
            'last_seen': pattern.last_seen
        }
        
        logger.info(f"New pattern submitted: {pattern.pattern_hash}")
        
    async def get_threat_intelligence(self) -> Dict[str, Any]:
        """Get current threat intelligence."""
        return self.threat_intelligence