"""
Federated learning system for aicache.
Enables collaborative intelligence while preserving user privacy.
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Import privacy utilities
from .privacy import EnhancedPrivacyPreserver, PrivacyBudgetManager

logger = logging.getLogger(__name__)

@dataclass
class FederatedModelUpdate:
    """Represents a model update from a client."""
    client_id: str
    model_weights: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: float
    update_size: int
    privacy_budget_used: Optional[float] = None
    
@dataclass
class GlobalModel:
    """Represents the global model."""
    model_id: str
    weights: Dict[str, Any]
    version: int
    created_at: float
    updated_at: float
    client_count: int
    performance_metrics: Dict[str, float]
    total_privacy_budget: float = 0.0

class FederatedLearningServer:
    """Central server for federated learning coordination."""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.model_config = model_config
        self.global_model = None
        self.client_updates = []
        self.client_registry = {}
        self.aggregation_strategy = model_config.get('aggregation_strategy', 'fedavg')
        self.privacy_preserver = EnhancedPrivacyPreserver(model_config.get('privacy', {}))
        self.privacy_budget_manager = PrivacyBudgetManager(
            model_config.get('total_epsilon', 10.0),
            model_config.get('total_delta', 1e-3)
        )
        
    async def initialize_global_model(self):
        """Initialize the global model."""
        import time
        model_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
        
        # Initialize with default weights (in practice, this would be a trained model)
        self.global_model = GlobalModel(
            model_id=model_id,
            weights={'bias': 0.0, 'weights': [0.1, 0.2, 0.3]},  # Placeholder weights
            version=1,
            created_at=time.time(),
            updated_at=time.time(),
            client_count=0,
            performance_metrics={'accuracy': 0.0, 'loss': 0.0},
            total_privacy_budget=0.0
        )
        
        logger.info(f"Initialized global model {self.global_model.model_id}")
        
    async def register_client(self, client_id: str, client_info: Dict[str, Any]) -> bool:
        """Register a new client."""
        self.client_registry[client_id] = {
            'info': client_info,
            'last_seen': asyncio.get_event_loop().time(),
            'status': 'active'
        }
        
        logger.info(f"Registered client {client_id}")
        return True
        
    async def submit_model_update(self, update: FederatedModelUpdate) -> bool:
        """Receive model update from client."""
        # Validate update
        if not self._validate_update(update):
            logger.warning(f"Invalid update from client {update.client_id}")
            return False
            
        # Store update
        self.client_updates.append(update)
        self.client_registry[update.client_id]['last_seen'] = update.timestamp
        
        # Update privacy budget tracking
        if update.privacy_budget_used:
            self.global_model.total_privacy_budget += update.privacy_budget_used
            
        logger.info(f"Received update from client {update.client_id}")
        return True
        
    def _validate_update(self, update: FederatedModelUpdate) -> bool:
        """Validate model update."""
        # Basic validation
        if not update.client_id or not update.model_weights:
            return False
            
        # Check client is registered
        if update.client_id not in self.client_registry:
            return False
            
        return True
        
    async def aggregate_model_updates(self) -> Optional[GlobalModel]:
        """Aggregate client updates to update global model."""
        if not self.client_updates:
            logger.info("No updates to aggregate")
            return self.global_model
            
        logger.info(f"Aggregating {len(self.client_updates)} updates")
        
        if self.aggregation_strategy == 'fedavg':
            new_weights = await self._federated_averaging()
        else:
            # Default to simple averaging
            new_weights = await self._simple_averaging()
            
        # Update global model
        import time
        self.global_model.weights = new_weights
        self.global_model.version += 1
        self.global_model.updated_at = time.time()
        self.global_model.client_count = len(self.client_updates)
        
        # Clear processed updates
        self.client_updates.clear()
        
        logger.info(f"Global model updated to version {self.global_model.version}")
        return self.global_model
        
    async def _federated_averaging(self) -> Dict[str, Any]:
        """Perform federated averaging of model updates."""
        if not self.client_updates:
            return self.global_model.weights
            
        # Extract weights and apply privacy preservation
        private_updates = []
        for update in self.client_updates:
            # Apply additional privacy if needed
            private_weights = self.privacy_preserver.add_differential_privacy(
                update.model_weights
            )
            private_updates.append(private_weights)
            
        # Simple averaging for demonstration
        total_updates = len(private_updates)
        aggregated_weights = {}
        
        # Initialize with global model weights
        for key, value in self.global_model.weights.items():
            if isinstance(value, list):
                aggregated_weights[key] = [0.0] * len(value)
            else:
                aggregated_weights[key] = 0.0
                
        # Aggregate updates
        for update in private_updates:
            for key, value in update.items():
                if key in aggregated_weights:
                    if isinstance(value, list):
                        for i, v in enumerate(value):
                            aggregated_weights[key][i] += v / total_updates
                    else:
                        aggregated_weights[key] += value / total_updates
                        
        return aggregated_weights
        
    async def _simple_averaging(self) -> Dict[str, Any]:
        """Simple averaging of model updates."""
        return await self._federated_averaging()
        
    async def get_global_model(self) -> GlobalModel:
        """Get the current global model."""
        return self.global_model
        
    async def get_client_status(self) -> Dict[str, Any]:
        """Get status of all registered clients."""
        return self.client_registry
        
    async def get_privacy_stats(self) -> Dict[str, Any]:
        """Get privacy-related statistics."""
        remaining_epsilon, remaining_delta = self.privacy_budget_manager.get_remaining_budget()
        return {
            'total_epsilon': self.privacy_budget_manager.total_epsilon,
            'consumed_epsilon': self.privacy_budget_manager.consumed_epsilon,
            'remaining_epsilon': remaining_epsilon,
            'total_delta': self.privacy_budget_manager.total_delta,
            'consumed_delta': self.privacy_budget_manager.consumed_delta,
            'remaining_delta': remaining_delta,
            'model_total_privacy': self.global_model.total_privacy_budget
        }

class FederatedLearningClient:
    """Client-side federated learning component."""
    
    def __init__(self, client_id: str, server_url: str, privacy_config: Dict[str, Any] = None):
        self.client_id = client_id
        self.server_url = server_url
        self.local_model = None
        self.training_data = []
        self.privacy_preserver = EnhancedPrivacyPreserver(privacy_config or {})
        self.privacy_budget_manager = PrivacyBudgetManager(
            privacy_config.get('epsilon', 1.0) if privacy_config else 1.0,
            privacy_config.get('delta', 1e-5) if privacy_config else 1e-5
        )
        
    async def initialize_local_model(self, initial_weights: Dict[str, Any]):
        """Initialize local model with global weights."""
        self.local_model = {
            'weights': initial_weights,
            'version': 1
        }
        
        logger.info(f"Initialized local model for client {self.client_id}")
        
    async def train_local_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train local model on private data."""
        if not self.local_model:
            raise ValueError("Local model not initialized")
            
        # In practice, this would be actual model training
        # For now, we'll simulate training by making small adjustments
        import random
        
        # Simulate training by adding small random adjustments
        updated_weights = {}
        for key, value in self.local_model['weights'].items():
            if isinstance(value, list):
                updated_weights[key] = [v + random.uniform(-0.1, 0.1) for v in value]
            else:
                updated_weights[key] = value + random.uniform(-0.1, 0.1)
                
        # Clip gradients to limit sensitivity
        updated_weights = self.privacy_preserver.clip_gradients(updated_weights)
                
        self.local_model['weights'] = updated_weights
        self.local_model['version'] += 1
        
        logger.info(f"Trained local model for client {self.client_id}")
        return updated_weights
        
    async def create_model_update(self) -> FederatedModelUpdate:
        """Create model update for submission to server."""
        import time
        
        if not self.local_model:
            raise ValueError("Local model not initialized")
            
        # Request privacy budget
        epsilon = self.privacy_preserver.epsilon
        if self.privacy_budget_manager.request_budget(epsilon):
            # Add differential privacy to weights
            private_weights = self.privacy_preserver.add_differential_privacy(
                self.local_model['weights']
            )
            
            update = FederatedModelUpdate(
                client_id=self.client_id,
                model_weights=private_weights,
                metadata={
                    'model_version': self.local_model['version'],
                    'training_samples': len(self.training_data)
                },
                timestamp=time.time(),
                update_size=len(str(private_weights)),
                privacy_budget_used=epsilon
            )
        else:
            logger.warning(f"Privacy budget exceeded for client {self.client_id}")
            # Send update without additional privacy (not recommended in practice)
            update = FederatedModelUpdate(
                client_id=self.client_id,
                model_weights=self.local_model['weights'],
                metadata={
                    'model_version': self.local_model['version'],
                    'training_samples': len(self.training_data),
                    'privacy_budget_exceeded': True
                },
                timestamp=time.time(),
                update_size=len(str(self.local_model['weights']))
            )
        
        return update
        
    async def update_local_model(self, global_weights: Dict[str, Any]):
        """Update local model with global weights."""
        if not self.local_model:
            await self.initialize_local_model(global_weights)
        else:
            self.local_model['weights'] = global_weights
            self.local_model['version'] += 1
            
        logger.info(f"Updated local model for client {self.client_id}")

# Privacy-preserving utilities (maintained for backward compatibility)
class PrivacyPreserver:
    """Utilities for privacy-preserving federated learning."""
    
    @staticmethod
    def add_differential_privacy(weights: Dict[str, Any], epsilon: float = 1.0) -> Dict[str, Any]:
        """Add differential privacy noise to model weights."""
        import random
        
        noisy_weights = {}
        for key, value in weights.items():
            if isinstance(value, list):
                noisy_weights[key] = [
                    v + random.uniform(-epsilon, epsilon) for v in value
                ]
            else:
                noisy_weights[key] = value + random.uniform(-epsilon, epsilon)
                
        return noisy_weights
        
    @staticmethod
    def secure_aggregate(updates: List[FederatedModelUpdate]) -> Dict[str, Any]:
        """Securely aggregate model updates."""
        # In practice, this would use secure multi-party computation
        # For now, we'll do a simple aggregation with privacy
        if not updates:
            return {}
            
        # Simple averaging with privacy
        total_updates = len(updates)
        aggregated_weights = {}
        
        # Initialize with first update
        for key, value in updates[0].model_weights.items():
            if isinstance(value, list):
                aggregated_weights[key] = [0.0] * len(value)
            else:
                aggregated_weights[key] = 0.0
                
        # Aggregate updates
        for update in updates:
            for key, value in update.model_weights.items():
                if key in aggregated_weights:
                    if isinstance(value, list):
                        for i, v in enumerate(value):
                            aggregated_weights[key][i] += v / total_updates
                    else:
                        aggregated_weights[key] += value / total_updates
                        
        return aggregated_weights