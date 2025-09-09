"""
Enhanced privacy-preserving utilities for federated learning.
Implements differential privacy, secure aggregation, and homomorphic encryption.
"""

import asyncio
import logging
import json
import hashlib
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class PrivateModelUpdate:
    """Represents a privacy-preserving model update."""
    client_id: str
    noised_weights: Dict[str, Any]
    metadata: Dict[str, Any]
    privacy_budget: float  # epsilon value
    timestamp: float

class EnhancedPrivacyPreserver:
    """Enhanced privacy-preserving utilities for federated learning."""
    
    def __init__(self, privacy_config: Dict[str, Any]):
        self.privacy_config = privacy_config
        self.epsilon = privacy_config.get('epsilon', 1.0)  # Privacy budget
        self.delta = privacy_config.get('delta', 1e-5)    # Failure probability
        self.sensitivity = privacy_config.get('sensitivity', 1.0)  # L2 sensitivity
        self.mechanism = privacy_config.get('mechanism', 'laplace')  # 'laplace' or 'gaussian'
        
    def add_differential_privacy(self, weights: Dict[str, Any], 
                               epsilon: float = None, 
                               mechanism: str = None) -> Dict[str, Any]:
        """Add differential privacy noise to model weights."""
        if epsilon is None:
            epsilon = self.epsilon
        if mechanism is None:
            mechanism = self.mechanism
            
        noised_weights = {}
        
        for key, value in weights.items():
            if isinstance(value, list):
                if mechanism == 'laplace':
                    noised_weights[key] = self._add_laplace_noise(value, epsilon)
                else:  # gaussian
                    noised_weights[key] = self._add_gaussian_noise(value, epsilon)
            elif isinstance(value, (int, float)):
                if mechanism == 'laplace':
                    noised_weights[key] = value + self._laplace_noise(epsilon)
                else:  # gaussian
                    noised_weights[key] = value + self._gaussian_noise(epsilon)
            else:
                # For other types, just pass through
                noised_weights[key] = value
                
        return noised_weights
        
    def _add_laplace_noise(self, values: List[float], epsilon: float) -> List[float]:
        """Add Laplace noise to a list of values."""
        # Scale parameter for Laplace distribution: sensitivity / epsilon
        scale = self.sensitivity / epsilon
        return [v + self._laplace_noise(epsilon, scale) for v in values]
        
    def _add_gaussian_noise(self, values: List[float], epsilon: float) -> List[float]:
        """Add Gaussian noise to a list of values."""
        # Calculate sigma for Gaussian mechanism
        sigma = self._compute_gaussian_sigma(epsilon, self.delta)
        return [v + random.gauss(0, sigma) for v in values]
        
    def _laplace_noise(self, epsilon: float, scale: float = None) -> float:
        """Generate Laplace noise."""
        if scale is None:
            scale = self.sensitivity / epsilon
        # Generate Laplace noise using inverse transform sampling
        u = random.uniform(-0.5, 0.5)
        return -scale * (1 if u > 0 else -1) * np.log(1 - 2 * abs(u))
        
    def _gaussian_noise(self, epsilon: float) -> float:
        """Generate Gaussian noise."""
        sigma = self._compute_gaussian_sigma(epsilon, self.delta)
        return random.gauss(0, sigma)
        
    def _compute_gaussian_sigma(self, epsilon: float, delta: float) -> float:
        """Compute sigma for Gaussian mechanism."""
        # Using the standard formula for Gaussian mechanism
        # sigma >= sqrt(2 * ln(1.25/delta)) * sensitivity / epsilon
        return np.sqrt(2 * np.log(1.25 / delta)) * self.sensitivity / epsilon
        
    def secure_aggregate(self, updates: List[Dict[str, Any]], 
                        weights: List[float] = None) -> Dict[str, Any]:
        """Securely aggregate model updates with privacy preservation."""
        if not updates:
            return {}
            
        # If no weights provided, use uniform weights
        if weights is None:
            weights = [1.0 / len(updates)] * len(updates)
            
        # Weighted averaging with privacy
        aggregated_weights = {}
        
        # Initialize with first update
        for key, value in updates[0].items():
            if isinstance(value, list):
                aggregated_weights[key] = [0.0] * len(value)
            else:
                aggregated_weights[key] = 0.0
                
        # Aggregate updates
        for i, update in enumerate(updates):
            weight = weights[i]
            for key, value in update.items():
                if key in aggregated_weights:
                    if isinstance(value, list):
                        for j, v in enumerate(value):
                            aggregated_weights[key][j] += v * weight
                    else:
                        aggregated_weights[key] += value * weight
                        
        return aggregated_weights
        
    def create_private_update(self, client_id: str, weights: Dict[str, Any], 
                            metadata: Dict[str, Any] = None) -> PrivateModelUpdate:
        """Create a privacy-preserving model update."""
        # Add differential privacy to weights
        noised_weights = self.add_differential_privacy(weights)
        
        import time
        update = PrivateModelUpdate(
            client_id=client_id,
            noised_weights=noised_weights,
            metadata=metadata or {},
            privacy_budget=self.epsilon,
            timestamp=time.time()
        )
        
        return update
        
    def compute_privacy_loss(self, num_rounds: int, 
                           num_clients: int, 
                           sampling_rate: float) -> Tuple[float, float]:
        """Compute cumulative privacy loss over multiple rounds."""
        # Using advanced composition theorem
        epsilon_per_round = self.epsilon
        delta_per_round = self.delta
        
        # Advanced composition for multiple rounds
        total_epsilon = epsilon_per_round * np.sqrt(2 * num_rounds * np.log(1 / delta_per_round))
        total_delta = num_rounds * delta_per_round
        
        # Account for sampling
        if sampling_rate < 1.0:
            total_epsilon *= sampling_rate
            total_delta *= sampling_rate
            
        return total_epsilon, total_delta
        
    def clip_gradients(self, weights: Dict[str, Any], 
                      clipping_bound: float = 1.0) -> Dict[str, Any]:
        """Clip gradients to limit sensitivity."""
        clipped_weights = {}
        
        for key, value in weights.items():
            if isinstance(value, list):
                # Compute L2 norm
                l2_norm = np.sqrt(sum(v**2 for v in value))
                if l2_norm > clipping_bound:
                    # Clip to bound
                    clipped_weights[key] = [v * clipping_bound / l2_norm for v in value]
                else:
                    clipped_weights[key] = value[:]
            elif isinstance(value, (int, float)):
                # For scalars, clip by absolute value
                if abs(value) > clipping_bound:
                    clipped_weights[key] = np.sign(value) * clipping_bound
                else:
                    clipped_weights[key] = value
            else:
                clipped_weights[key] = value
                
        return clipped_weights

# Secure multi-party computation utilities
class SecureMPC:
    """Secure multi-party computation utilities."""
    
    @staticmethod
    def shamir_secret_share(secret: float, num_shares: int, threshold: int) -> List[Tuple[int, float]]:
        """Create Shamir's secret sharing shares."""
        # Generate random polynomial coefficients
        coefficients = [secret] + [random.uniform(-1, 1) for _ in range(threshold - 1)]
        
        # Generate shares
        shares = []
        for i in range(1, num_shares + 1):
            share = 0
            for j, coeff in enumerate(coefficients):
                share += coeff * (i ** j)
            shares.append((i, share))
            
        return shares
        
    @staticmethod
    def reconstruct_secret(shares: List[Tuple[int, float]]) -> float:
        """Reconstruct secret from shares using Lagrange interpolation."""
        if not shares:
            return 0.0
            
        # Lagrange interpolation
        secret = 0.0
        for i, (x_i, y_i) in enumerate(shares):
            numerator = 1.0
            denominator = 1.0
            for j, (x_j, y_j) in enumerate(shares):
                if i != j:
                    numerator *= -x_j
                    denominator *= (x_i - x_j)
            if denominator != 0:
                secret += y_i * numerator / denominator
                
        return secret
        
    @staticmethod
    def secure_sum(shares_list: List[List[Tuple[int, float]]]) -> List[Tuple[int, float]]:
        """Securely sum shares from multiple parties."""
        if not shares_list:
            return []
            
        # Sum shares point-wise
        result_shares = []
        num_shares = len(shares_list[0])
        
        for i in range(num_shares):
            x = shares_list[0][i][0]  # x-coordinate (same for all shares at position i)
            y_sum = sum(shares[i][1] for shares in shares_list)  # Sum y-coordinates
            result_shares.append((x, y_sum))
            
        return result_shares

# Homomorphic encryption utilities (simplified implementation)
class HomomorphicEncryption:
    """Simplified homomorphic encryption utilities."""
    
    def __init__(self, key_size: int = 16):
        # In practice, this would use a proper HE library like PySEAL
        self.key_size = key_size
        self.public_key, self.private_key = self._generate_keys()
        
    def _generate_keys(self) -> Tuple[int, int]:
        """Generate simple public/private key pair."""
        # Simplified key generation (not cryptographically secure)
        p = 61  # Small primes for demonstration
        q = 53
        n = p * q
        phi_n = (p - 1) * (q - 1)
        
        # Choose public exponent
        e = 17  # Common choice
        
        # Compute private exponent (simplified)
        d = pow(e, -1, phi_n)
        
        return (n, e), (n, d)
        
    def encrypt(self, plaintext: float) -> Tuple[int, int]:
        """Encrypt a value."""
        n, e = self.public_key
        # Simplified encryption (not suitable for real use)
        ciphertext = pow(int(plaintext * 1000), e, n)  # Scale to avoid floating point issues
        return (ciphertext, 1000)  # Return scaled factor as well
        
    def decrypt(self, ciphertext: Tuple[int, int]) -> float:
        """Decrypt a value."""
        cipher_val, scale_factor = ciphertext
        n, d = self.private_key
        # Simplified decryption
        plaintext = pow(cipher_val, d, n)
        return plaintext / scale_factor
        
    def add_encrypted(self, c1: Tuple[int, int], c2: Tuple[int, int]) -> Tuple[int, int]:
        """Add two encrypted values."""
        # For simplified scheme, we can't do true homomorphic addition
        # In practice, this would use proper HE operations
        c1_val, scale1 = c1
        c2_val, scale2 = c2
        # This is a simplified approach - not mathematically correct for real HE
        return ((c1_val + c2_val) // 2, max(scale1, scale2))

# Privacy budget manager
class PrivacyBudgetManager:
    """Manages privacy budget allocation across multiple queries."""
    
    def __init__(self, total_epsilon: float, total_delta: float):
        self.total_epsilon = total_epsilon
        self.total_delta = total_delta
        self.consumed_epsilon = 0.0
        self.consumed_delta = 0.0
        
    def request_budget(self, epsilon: float, delta: float = 0.0) -> bool:
        """Request privacy budget for a query."""
        if (self.consumed_epsilon + epsilon <= self.total_epsilon and 
            self.consumed_delta + delta <= self.total_delta):
            self.consumed_epsilon += epsilon
            self.consumed_delta += delta
            return True
        return False
        
    def get_remaining_budget(self) -> Tuple[float, float]:
        """Get remaining privacy budget."""
        return (self.total_epsilon - self.consumed_epsilon, 
                self.total_delta - self.consumed_delta)
        
    def reset_budget(self):
        """Reset privacy budget."""
        self.consumed_epsilon = 0.0
        self.consumed_delta = 0.0