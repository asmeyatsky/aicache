"""
Configuration management for aicache decentralized identity system
"""

import os
import yaml
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Global configuration instance
_config: Optional[Dict[str, Any]] = None

def get_config() -> Dict[str, Any]:
    """Get the global configuration"""
    global _config
    
    if _config is None:
        _config = load_config()
        
    return _config

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file"""
    global _config
    
    # Use default path if not specified
    if config_path is None:
        config_path = os.environ.get('AICACHE_CONFIG_PATH', './config/default.yaml')
        
    # Check if config file exists
    if not os.path.exists(config_path):
        logger.warning(f"Configuration file not found: {config_path}")
        logger.info("Using default configuration")
        _config = get_default_config()
        return _config
        
    try:
        # Load YAML configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Merge with default configuration
        default_config = get_default_config()
        merged_config = merge_configs(default_config, config)
        
        _config = merged_config
        logger.info(f"Configuration loaded from {config_path}")
        return merged_config
        
    except Exception as e:
        logger.error(f"Error loading configuration from {config_path}: {e}")
        logger.info("Using default configuration")
        _config = get_default_config()
        return _config

def get_default_config() -> Dict[str, Any]:
    """Get default configuration"""
    return {
        'identity': {
            'default_did_method': 'did:key',
            'storage_path': './data/identities',
            'cache_ttl': 3600,
            'max_cache_size': 10000
        },
        'crypto': {
            'default_algorithm': 'ed25519',
            'key_size': 2048,
            'storage_path': './data/keys',
            'encryption_algorithm': 'aes-256-gcm'
        },
        'trust': {
            'default_trust_level': 'medium',
            'storage_path': './data/trust',
            'max_trust_depth': 5,
            'trust_propagation_factor': 0.8
        },
        'resolver': {
            'resolution_timeout': 30,
            'cache_ttl': 3600,
            'supported_methods': ['did:key', 'did:web'],
            'universal_resolver_url': 'https://dev.uniresolver.io/1.0/identifiers/'
        },
        'bridge': {
            'default_method': 'oauth',
            'supported_providers': ['github', 'gitlab', 'google'],
            'mapping_ttl': 86400
        },
        'verification': {
            'default_verification_method': 'zkp',
            'max_verification_attempts': 3,
            'verification_timeout': 60,
            'proof_validity_period': 3600
        },
        'logging': {
            'level': 'INFO',
            'format': 'json',
            'file_path': './logs/decentralized_identity.log',
            'max_file_size': 10485760,
            'backup_count': 5
        },
        'performance': {
            'max_concurrent_resolutions': 10,
            'resolution_batch_size': 50,
            'cache_refresh_interval': 300,
            'gc_interval': 3600
        },
        'security': {
            'enable_encryption': True,
            'enable_signatures': True,
            'enable_zero_knowledge_proofs': True,
            'max_signature_attempts': 3,
            'signature_timeout': 30
        },
        'network': {
            'bind_address': '0.0.0.0',
            'port': 8081,
            'ssl_enabled': False,
            'ssl_cert_path': './certs/server.crt',
            'ssl_key_path': './certs/server.key'
        },
        'database': {
            'type': 'sqlite',
            'path': './data/decentralized_identity.db',
            'max_connections': 20,
            'connection_timeout': 30
        },
        'monitoring': {
            'enable_metrics': True,
            'metrics_port': 9091,
            'enable_tracing': True,
            'trace_sampling_rate': 0.1,
            'enable_profiling': False,
            'profile_interval': 300
        },
        'testing': {
            'enable_test_endpoints': False,
            'test_data_path': './test/data',
            'mock_resolvers': False,
            'mock_crypto': False
        }
    }

def merge_configs(default_config: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user configuration with default configuration"""
    merged = default_config.copy()
    
    for key, value in user_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            merged[key] = merge_configs(merged[key], value)
        else:
            # Override with user value
            merged[key] = value
            
    return merged

def get_config_value(key_path: str, default: Any = None) -> Any:
    """Get configuration value by dot-separated key path"""
    config = get_config()
    
    # Split key path
    keys = key_path.split('.')
    
    # Navigate through nested dictionaries
    current = config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
            
    return current

def set_config_value(key_path: str, value: Any):
    """Set configuration value by dot-separated key path"""
    global _config
    
    if _config is None:
        _config = get_config()
        
    # Split key path
    keys = key_path.split('.')
    
    # Navigate through nested dictionaries
    current = _config
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
        
    # Set final value
    current[keys[-1]] = value
    
    logger.debug(f"Set configuration value {key_path} = {value}")

def reload_config():
    """Reload configuration from file"""
    global _config
    _config = load_config()
    logger.info("Configuration reloaded")