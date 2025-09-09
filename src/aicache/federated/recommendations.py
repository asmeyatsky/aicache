"""
Recommendation engine for aicache using federated learning.
Provides personalized recommendations while preserving privacy.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

from . import FederatedLearningClient, FederatedModelUpdate, GlobalModel

logger = logging.getLogger(__name__)

@dataclass
class DeveloperProfile:
    """Represents a developer's profile for recommendations."""
    developer_id: str
    languages: List[str]
    frameworks: List[str]
    tools: List[str]
    preferences: Dict[str, Any]
    activity_history: List[Dict[str, Any]]

@dataclass
class Recommendation:
    """Represents a recommendation."""
    item_id: str
    item_type: str  # 'library', 'tool', 'tutorial', 'snippet', 'documentation'
    confidence: float
    reason: str
    context: Dict[str, Any]

class RecommendationEngine:
    """Personalized recommendation engine using federated learning."""
    
    def __init__(self, client_id: str, server_url: str):
        self.client = FederatedLearningClient(client_id, server_url)
        self.developer_profile = None
        self.recommendation_history = []
        self.local_training_data = []
        
    async def initialize(self, initial_profile: DeveloperProfile, global_weights: Dict[str, Any]):
        """Initialize the recommendation engine."""
        self.developer_profile = initial_profile
        await self.client.initialize_local_model(global_weights)
        logger.info("Recommendation engine initialized")
        
    async def generate_recommendations(self, context: Dict[str, Any]) -> List[Recommendation]:
        """Generate personalized recommendations based on context."""
        if not self.developer_profile or not self.client.local_model:
            logger.warning("Engine not properly initialized")
            return []
            
        # Extract features from context
        features = self._extract_features(context)
        
        # Generate recommendations using local model
        recommendations = await self._generate_local_recommendations(features)
        
        # Log for training data
        self.local_training_data.append({
            'context': context,
            'features': features,
            'recommendations': [asdict(r) for r in recommendations],
            'timestamp': asyncio.get_event_loop().time()
        })
        
        return recommendations
        
    def _extract_features(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from context for recommendation."""
        features = {}
        
        # Time-based features
        features['time_of_day'] = context.get('time_of_day', 'unknown')
        features['day_of_week'] = context.get('day_of_week', 'unknown')
        
        # Project context
        features['language'] = context.get('language', 'unknown')
        features['framework'] = context.get('framework', 'unknown')
        
        # Developer profile
        if self.developer_profile:
            features['preferred_languages'] = self.developer_profile.languages
            features['preferred_frameworks'] = self.developer_profile.frameworks
            
        # Current activity
        features['current_task'] = context.get('task', 'unknown')
        features['recent_queries'] = context.get('recent_queries', [])
        
        return features
        
    async def _generate_local_recommendations(self, features: Dict[str, Any]) -> List[Recommendation]:
        """Generate recommendations using local model."""
        # In practice, this would use the trained model
        # For now, we'll use rule-based recommendations with some randomness
        
        recommendations = []
        language = features.get('language', 'python')
        framework = features.get('framework', 'unknown')
        
        # Rule-based recommendations
        base_recommendations = [
            (f"{language}-best-practices", "tutorial", 0.8, f"Best practices for {language}"),
            (f"{language}-cheat-sheet", "documentation", 0.7, f"{language} cheat sheet"),
            ("debugging-tools", "tool", 0.6, "Debugging tools"),
        ]
        
        # Add framework-specific recommendations
        if framework != 'unknown':
            base_recommendations.append(
                (f"{framework}-tutorial", "tutorial", 0.9, f"{framework} tutorial")
            )
            
        # Create recommendation objects
        for item_id, item_type, confidence, reason in base_recommendations:
            recommendations.append(Recommendation(
                item_id=item_id,
                item_type=item_type,
                confidence=confidence,
                reason=reason,
                context=features
            ))
            
        return recommendations
        
    async def feedback_on_recommendation(self, recommendation_id: str, feedback: str):
        """Provide feedback on a recommendation."""
        # Log feedback for training
        feedback_data = {
            'recommendation_id': recommendation_id,
            'feedback': feedback,  # 'accepted', 'rejected', 'helpful', 'not_helpful'
            'timestamp': asyncio.get_event_loop().time()
        }
        
        self.local_training_data.append(feedback_data)
        logger.info(f"Feedback received for recommendation {recommendation_id}: {feedback}")
        
    async def train_local_model(self):
        """Train local model on accumulated data."""
        if not self.local_training_data:
            logger.info("No training data available")
            return
            
        # Prepare training data
        training_data = self._prepare_training_data()
        
        # Train local model
        updated_weights = await self.client.train_local_model(training_data)
        
        logger.info("Local model trained successfully")
        return updated_weights
        
    def _prepare_training_data(self) -> List[Dict[str, Any]]:
        """Prepare training data from local interactions."""
        # In practice, this would convert interactions to training samples
        # For now, we'll create dummy training data
        training_data = []
        
        for interaction in self.local_training_data:
            if 'context' in interaction:
                # Create a training sample from interaction
                sample = {
                    'features': interaction.get('features', {}),
                    'target': 1.0 if interaction.get('feedback') == 'accepted' else 0.0,
                    'weight': 1.0
                }
                training_data.append(sample)
                
        return training_data
        
    async def create_model_update(self) -> FederatedModelUpdate:
        """Create model update for federated learning."""
        return await self.client.create_model_update()
        
    async def update_local_model(self, global_weights: Dict[str, Any]):
        """Update local model with global weights."""
        await self.client.update_local_model(global_weights)

# Global recommendation service (server-side)
class GlobalRecommendationService:
    """Global service for coordinating recommendations across users."""
    
    def __init__(self, federated_server):
        self.federated_server = federated_server
        self.recommendation_catalog = {}  # In practice, this would be a database
        self.popularity_scores = defaultdict(float)
        
    async def initialize_catalog(self):
        """Initialize the recommendation catalog."""
        # Sample catalog - in practice, this would be populated from various sources
        self.recommendation_catalog = {
            'python-best-practices': {
                'type': 'tutorial',
                'title': 'Python Best Practices',
                'description': 'Learn the best practices for writing Python code',
                'tags': ['python', 'best-practices', 'coding-standards']
            },
            'javascript-cheat-sheet': {
                'type': 'documentation',
                'title': 'JavaScript Cheat Sheet',
                'description': 'Quick reference for JavaScript syntax and features',
                'tags': ['javascript', 'reference', 'cheat-sheet']
            },
            'debugging-tools': {
                'type': 'tool',
                'title': 'Debugging Tools',
                'description': 'Essential debugging tools for developers',
                'tags': ['debugging', 'tools', 'productivity']
            },
            'react-tutorial': {
                'type': 'tutorial',
                'title': 'React Tutorial',
                'description': 'Complete tutorial for learning React',
                'tags': ['javascript', 'react', 'frontend']
            }
        }
        
        logger.info("Recommendation catalog initialized")
        
    async def get_popular_items(self, limit: int = 10) -> List[Tuple[str, float]]:
        """Get popular items based on global usage."""
        # Sort by popularity score and return top items
        sorted_items = sorted(self.popularity_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:limit]
        
    async def update_popularity(self, item_id: str, score: float):
        """Update popularity score for an item."""
        self.popularity_scores[item_id] += score